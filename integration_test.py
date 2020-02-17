from uuid import uuid1
from bson.objectid import ObjectId
import boto3
import json
import time

from async_lambda_invocation import invoke_all
from IOMongoDB import IOMongoDB
from IOS3 import IOS3

_id = ObjectId("0" * 24) # 0: boston housing 1: iris
InvocationType = 'RequestResponse'
lambda_client = boto3.client('lambda')
iodb = IOMongoDB()
ios3 = IOS3()

def preprocess_and_trigger_train():
    uid = _id
    pid = _id

    sqs_client = boto3.client('sqs')
    response = sqs_client.get_queue_url(QueueName='EC2-Job-Main')
    job_queue_url = response['QueueUrl']
    response = sqs_client.get_queue_url(QueueName='EC2-Job-HeavyPreprocessing')
    heavy_preprocessing_queue_url = response['QueueUrl']

    data_fid = _id # fid
    setting_id = _id # fid

    ## user select data file
    iodb.update("project", {"_id": pid}, {"$set": {"default_fid" : data_fid}})


    ## create a working preprocessing pipeline
    data_fid = iodb.read("project", {'_id': pid}, {"default_fid": 1})['default_fid']

    iodb.remove('preprocessing_pipeline', {'_id': _id})
    iodb.remove('case', {'_id': _id})

    ppp_data = {
            "_id": _id,
            "pid": pid,
            "status": "working",
            "uid_working": uid,
            "parent_pppid": "",
            "changed": True,
            "data_fid": data_fid,
            "s3_locs": {},
            "key_columns": {},
            "cases":[],
            "ops": [],
            "redoable_ops": []
    }
    pppid = iodb.to("preprocessing_pipeline", ppp_data)    

    # add the created preprocessing pipeline to the user session folder
    query = {"_id": pid}
    operation = {'$pull': {"users": {'uid':uid}}}
    iodb.update('project', query, operation) # delete uid from array
    operation = {'$push': {"users": {'uid':uid, 'pppid': pppid}}}
    iodb.update('project', query, operation)

    s3_pppl_folder = "/".join(["PPPLs", str(pppid)])
    user_input_filename = "user_input.json"
    df_all_raw_filename = "df_all_raw.csv"
    user_input_loc = "/".join([s3_pppl_folder, user_input_filename])
    df_all_raw_loc = "/".join([s3_pppl_folder, df_all_raw_filename])

    # !!! now assume user input is predefined, interactivity requires modifications of inputs to each lambda function
    data = iodb.read('user_setting', {"_id": setting_id})
    ios3.to(data, user_input_loc)
    # clone df_all_raw into pppl folder
    data_loc = iodb.read('filenew', {'_id': data_fid}, {'loc_s3': 1})['loc_s3']
    df_all_raw = ios3.read(data_loc)

    ios3.to(df_all_raw, df_all_raw_loc, index=True)

    iodb.update("preprocessing_pipeline", {'_id': pppid}, {"$set":  {"s3_locs.df_all_raw": df_all_raw_loc}})

    # invoke lambda function: define target variable
    target_column = iodb.read('user_setting', {"_id": setting_id}, {"target_column": 1})["target_column"]
    iodb.update("preprocessing_pipeline", {'_id': pppid}, {"$set":  {"key_columns.target": target_column}})


    # check if validation folds column exists or will be created
    predefined_validation_col = iodb.read('user_setting', {"_id": setting_id})["predefined_validation"]
    if predefined_validation_col is not None:
        _val_folds_column = predefined_validation_col
    else:
        _val_folds_column = "_val_folds"
    iodb.update("preprocessing_pipeline", {'_id': pppid}, {"$set":  {"key_columns._val_folds": _val_folds_column}})    
    protected_columns = {'target': target_column, '_val_folds': _val_folds_column}

    model_type = iodb.read('user_setting', {"_id": setting_id}, {"type": 1})["type"]
    if model_type == 'CLASSIFICATION':
        data_in_loc = df_all_raw_loc
        data_out_loc = f"{s3_pppl_folder}/df_all_encoded_raw.csv"
        encoder_loc = f"{s3_pppl_folder}/encoder.pickle"
        payload = {
            "data_in": data_in_loc,
            "data_out": data_out_loc,
            "target": target_column,
            "encoder": encoder_loc,
            }
        function = 'automl_transform_target'
        response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))
        iodb.update("preprocessing_pipeline", {'_id': pppid}, {"$set":  {"s3_locs.df_all_raw": data_out_loc}})
        df_all_raw = data_out_loc

    # call preprocessing recommendation
    payload = {
        "df_all_raw_loc": df_all_raw_loc,
        "target": target_column,
        "userInput": user_input_filename,
        "folder": s3_pppl_folder,
    }

    function = 'automl_get_preprocessing_recommendations' # xlsx to json !!!!!!!!!
    response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))

    # here we just use recommended pipelines without modifications
    key = '/'.join([s3_pppl_folder, 'preprocessing_recommendations.json'])
    preprocessing_pipeline = ios3.read(key)

    # preprocess data
    function = 'automl_preprocessing_pipeline'
    payload_ctr = -1
    iodb.update("preprocessing_pipeline", {'_id': pppid}, {"$set":  {"s3_locs.last_op_ptr": payload_ctr}})
    ec2_operations = [] # @@@ UNCOMMENT ['ImputeContinuous', 'FeatureSelection']
    ec2_payload_list = []
    for payload in preprocessing_pipeline:
        payload_ctr = payload_ctr+1
        iodb.update("preprocessing_pipeline", {'_id': pppid}, {"$set":  {"s3_locs.last_op_ptr": payload_ctr}})
        if "kwargs" in payload and "df_test_raw_loc" in payload["kwargs"]:
            iodb.update("preprocessing_pipeline", {'_id': pppid}, {"$set":  {"s3_locs.df_test_raw": payload["kwargs"]["df_test_raw_loc"]}})
        if payload['operation'] not in ec2_operations:
            lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))
        else:
            # assume ec2 operations are the last to be performed and
            # will occur sequentially
            ec2_payload_list.append(payload)
    if len(ec2_payload_list) > 0:
        # send ec2 payloads to sqs together so they are performed sequentially
        json_str = json.dumps(ec2_payload_list)
        sqs_client.send_message(QueueUrl=heavy_preprocessing_queue_url, MessageBody=json_str)

    df_train_processed_loc = f"{s3_pppl_folder}/df_train_{payload_ctr}.csv"
    iodb.update("preprocessing_pipeline", {'_id': pppid}, {"$set":  {"s3_locs.df_train_processed": df_train_processed_loc}})

    pppl_pending = 1
    while pppl_pending:
        time.sleep(1)
        pppl_pending = 1 - ios3.exists(df_train_processed_loc)

    # preprocess test
    df_test_processed_loc = f"{s3_pppl_folder}/df_test_processed.csv"

    payload = {
        "data_in": iodb.read("preprocessing_pipeline", {'_id': pppid})['s3_locs']['df_test_raw'],
        "data_out": df_test_processed_loc,
        "preprocessing_pkl": f"{s3_pppl_folder}/preprocessing_pipeline_lambda.pkl",
    }
        
    function = 'automl_preprocess_with_fitted_pipeline' # xlsx to json !!!!!!!!!
    response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))
    iodb.update("preprocessing_pipeline", {'_id': pppid}, {"$set":  {"s3_locs.df_test_processed": df_test_processed_loc}})

    ## training 
    # create case
    case_data = {
            "_id": _id,
            "pppid": pppid,
            "base_models": {},
            "en_model": {},
            "jobs_to_do":[],
            "jobs_finished":[],
            "en_jobs_finished":[],
            "training_completed":0,
    }
    caseid = iodb.to("case", case_data)

    s3_case_folder = "/".join(["Cases", str(caseid)])


    # !!! now assume user input is predefined, interactivity requires modifications of inputs to each lambda function
    data = iodb.read('user_setting', {"_id": setting_id})
    user_input_loc = "/".join([s3_case_folder, user_input_filename])
    ios3.to(data, user_input_loc)

    payload = {
        "df_train": df_train_processed_loc,
        "df_test": df_test_processed_loc,
        "protected_columns": protected_columns,
        "case_folder": s3_case_folder,
    }    
    function = 'automl_prepare_data_dict'
    response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))

    # invoke get grid search to get joblist, kfold and initialized model
    x_train = '/'.join([s3_case_folder, 'X_train.csv'])
    y_train = '/'.join([s3_case_folder, 'y_train.csv'])
    y_all = '/'.join([s3_case_folder, 'y_all.csv'])
    job_list_out = '/'.join([s3_case_folder, '_job_list.json'])
    model_init_out = '/'.join([s3_case_folder, '_model_init.pickle'])
    payload = {
        "X_train": x_train,
        "y_train": y_train,
        "y_all": y_all,
        "user_input": user_input_loc,
        "job_list_out": job_list_out,
        "model_init_out": model_init_out,
    }
    function = 'automl_get_grid_search_config'
    response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))

    # push jobs to database case (assign jobid)
    job_list = ios3.read(job_list_out)
    for job in job_list:
        # create job in database
        job_full = {**{"caseid": caseid,
                    "model_dir": s3_case_folder,
                    "x_train_path":x_train,
                    "y_train_path":y_train,
                    "prefix":""}, **job}

        jobid = iodb.to('job', job_full)
        iodb.update("case", {'_id': caseid}, {"$push":  {"jobs_to_do": jobid}})

        job_full['_id'] = str(job_full['_id'])
        job_full['caseid'] = str(job_full['caseid'])
        json_str = json.dumps(job_full)
        sqs_client.send_message(QueueUrl=job_queue_url, MessageBody=json_str)

def model_evaluation(caseid):
    case_folder = 'Cases/' + str(caseid)
    function = 'automl_evaluate'

    for mode in ['train', 'test']:
        for model_type in ['base_models', 'en_model']:
            payload = {
                "user_input": f"{case_folder}/user_input.json",
                "X": f"{case_folder}/X_{mode}.csv",
                "y": f"{case_folder}/y_{mode}.csv",
                "model_group": f"{case_folder}/fitted_{model_type}_train.pickle"
            }
            response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))
            res = json.loads(response['Payload'].read(), encoding='utf-8')
            for key in res:
                operation = {"$set": {f"{model_type}.opt_configs.{key}.{mode}_evaluation": res[key]}}
                iodb.update('case', {'_id': caseid}, operation)

def model_explanation(pppid, caseid, shuffle=True, data_range=50):
    # s3_pppl_folder = f"PPPLs/{str(pppid)}", 
    s3_case_folder = f"Cases/{str(caseid)}"

    x_all_loc = f"{s3_case_folder}/X_all.csv"
    
    if shuffle and isinstance(data_range, list):
        x_all_shuffled_loc = f"{s3_case_folder}/X_all_shuffled.csv" 
        payload = {
          "X": x_all_loc,
          "X_out": x_all_shuffled_loc,
        }
        function = 'automl_shuffle'
        response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))
        x_all_loc = x_all_shuffled_loc

    # get explanation joblist
    # invoke get grid search to get joblist, kfold and initialized model

    model_explain_job_list = f"{s3_case_folder}/model_explain_job_list.json"
    model_names = list(iodb.read("case", {"_id": caseid}, {'base_models.opt_configs': 1})['base_models']['opt_configs'].keys())
    payload = {
          "case_dir": s3_case_folder,
          "X": x_all_loc,
          "data_range": data_range,
          "model_names": model_names,
          "job_list_loc": model_explain_job_list,
    }
    function = 'automl_model_explain_job_generation'
    response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))

    # execute each job
    job_list =  ios3.read(model_explain_job_list)
    jobs = [job for js in job_list.values() for job in js]
    
    function = 'automl_model_explain_individually'
    invoke_all([json.dumps(job) for job in jobs], function)
    
    shap_value_locs = {model_name: [j['shap_value_out'] for j in js] for model_name, js in job_list.items()}

    payload = {
        "user_input": f"{s3_case_folder}/user_input.json",
        "en_model": f"{s3_case_folder}/fitted_en_model_train.pickle",
        "models": shap_value_locs,
        "base_models": f"{s3_case_folder}/fitted_base_models_train.pickle", #!! fix xgboost, shap bug
        "X_train": f"{s3_case_folder}/X_train.csv", #!! fix xgboost, shap bug
        "shap_values": f"{s3_case_folder}/shap_values.json",       
    }
    function = 'automl_model_explain_ensemble'
    response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))

def predict(pppid, caseid, n_workers=4):
    s3_pppl_folder = f"PPPLs/{str(pppid)}"
    s3_case_folder = f"Cases/{str(caseid)}"
    
    # get prediction joblist
    prediction_job_list = f"{s3_case_folder}/prediction_job_list.json"
    payload = {
        "case_dir": s3_case_folder,
        "X": f"{s3_case_folder}/X_test.csv",
        "model_loc": f"{s3_case_folder}/fitted_base_models_all.pickle",
        "pppl_loc": f"{s3_pppl_folder}/preprocessing_pipeline_lambda.pkl",
        "n_workers": n_workers,
        "job_list_loc": prediction_job_list,
    }
    function = 'automl_predict_job_generation'
    response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))

    # execute each job
    jobs =  ios3.read(prediction_job_list)
    function = 'automl_prediction'
    invoke_all([json.dumps(job) for job in jobs], function)
    
    # consolidate
    payload = {
        "job_list_loc": prediction_job_list,
        "pred_out_all": f"{s3_case_folder}/prediction.csv",
    }
    function = 'automl_predict_consolidate'
    response = lambda_client.invoke(FunctionName=function, InvocationType=InvocationType, Payload=json.dumps(payload))

def plot():
    pass

def report():
    pass

if __name__ == "__main__":
    preprocess_and_trigger_train()
    # model_evaluation(_id)
    # model_explanation(_id, _id)
    # predict(_id, _id)
    



    
    


