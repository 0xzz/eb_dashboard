import json
import pandas as pd

def load_140_485_by_FY():

    # load 140/485 number
    df = pd.read_csv('./data/num_140_485_by_FY.csv')
    #cols = ['FY','140Rec','140Approve','485Rec','485Approve','485Pending']
    #df = df[cols]

    return df

def load_vb_dates():

    df_eb1 = pd.read_csv('./data/eb1_final_action_days.csv')
    df_eb2 = pd.read_csv('./data/eb2_final_action_days.csv')
    df_eb3 = pd.read_csv('./data/eb3_final_action_days.csv')

    df = pd.merge(pd.merge(df_eb1, df_eb2, on='date'), df_eb3, on='date')
    return df_eb1, df_eb2, df_eb3, df