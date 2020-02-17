import os
import boto3
import uuid

from botocore.exceptions import ClientError

from IOBase import IOBase

def temp_file_s3(extension):
    return 'temp/' + str(uuid.uuid1()) + extension
            
class IOS3(IOBase):
    
    def __init__(self, bucket=None):
        if bucket is None:
            bucket = 'aai-platform'
        self.client_s3 = boto3.client('s3')
        self.s3 = boto3.resource('s3')
        self.bucket = bucket
 
    def list_buckets(self):
        response = self.client_s3.list_buckets()
        return [bucket['Name'] for bucket in response['Buckets']]

    def list_objects(self):
        response = self.client_s3.list_objects(Bucket=self.bucket)
        return [obj['Key'] for obj in response['Contents']] 

    def upload(self, fn, key=None):
        if key is None:
            extension = os.path.splitext(fn)[1]
            key = temp_file_s3(extension)
            self.client_s3.upload_file(fn, self.bucket, key)
        else:
            self.client_s3.upload_file(fn, self.bucket, key)
        return key

    def download(self, key, fn):
        self.client_s3.download_file(self.bucket, key, fn)

    def exists(self, key):
        try:
            self.s3.Object(self.bucket, key).load()
            self.get_obj(key)
        except ClientError as e:
            return int(e.response['Error']['Code']) != 404
        return True
        
    def read(self, key, logger=None, **kwargs):
        extension = os.path.splitext(key)[1]
        obj = self.get_obj(key)
        if logger is not None:
            logger.print('Reading from S3: '+ key)
        return self.bytes_to_data(obj, extension, **kwargs)
    
    def to(self, df, key=None, logger=None, **kwargs):
        if key is None:
            key = temp_file_s3('.pkl')
        elif key.startswith('.'):
            key = temp_file_s3(key)
        if logger is not None:
            logger.print('Saving to S3: '+ key)
        extension = os.path.splitext(key)[1]
        data = self.data_to_bytes(df, extension, **kwargs)
        self.put_obj(data, key)
        return key

    def get_obj(self, key):
        response = self.client_s3.get_object(
            Bucket = self.bucket,
            Key=key,
        )
        if response:
            return response['Body'].read()
       
    def put_obj(self, body, key):
        self.client_s3.put_object(
            Body = body,
            Bucket = self.bucket,
            Key=key,
        )

    def del_obj(self, key):
        self.s3.Object(self.bucket, key).delete()
    