import json
import pandas as pd
def load_data():

    # load 140/485 number
    df = pd.read_csv('num_140_485_by_FY.csv')
    #cols = ['FY','140Rec','140Approve','485Rec','485Approve','485Pending']
    #df = df[cols]

    return df
