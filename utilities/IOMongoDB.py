import os
import boto3
import uuid
import pymongo
import dns
import pandas as pd

from IOBase import IOBase
        
class IOMongoDB(IOBase):
    
    def __init__(self, url='mongodb+srv://jeremy-ma:Temporary?1@user-aohd5.mongodb.net/test?retryWrites=true&w=majority',
                 db_name='aai_user_dev'):
        self.client = pymongo.MongoClient(url)
        self.db = self.client[db_name]
 
    def list_collection_names(self):
        return self.db.list_collection_names()
        
    def read(self, collection, query, field={}, logger=None, **kwargs):
        field = {**{'_id': False}, **field}
        return self.db[collection].find_one(query, field)
    
    def to(self, collection, data, logger=None, **kwargs):
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(**kwargs)
        if isinstance(data, list):
            res = self.db[collection].insert_many(data)
            return res.inserted_ids
        elif isinstance(data, dict):
            res = self.db[collection].insert_one(data)
            return res.inserted_id
    
    def update(self, collection, query, operation, logger=None, **kwargs):
        self.db[collection].update_one(query, operation, **kwargs)

    def remove(self, collection, query, **kwargs):
        self.db[collection].remove(query, **kwargs)
    