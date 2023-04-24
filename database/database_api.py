import pymongo
from bson.objectid import ObjectId
from typing import Optional, List
import json

class DataabseAPI:

    def __init__(self, uri: str, database: str):
        self.database_uri = uri
        self.mongo_connection = pymongo.MongoClient(self.database_uri)
        self.database_connection = self.mongo_connection[database]

    def createRecord(self, data: dict, collection: str):
        collection = self.database_connection[collection]
        monog_obj = collection.insert_one(data)
        return monog_obj.inserted_id
    
    def getRecordById(self, recid: dict, collection: str) -> Optional[List]|dict:
        collection = self.database_connection[collection]
        monog_obj = collection.find_one({"_id": recid})
        return monog_obj
    
    def updateRecord(self, recid: str, data: dict, collection: str) -> Optional[dict]:
        collection = self.database_connection[collection]
        monog_obj = collection.update_one({'_id':recid}, { '$set':data})
        return monog_obj
    
    def deleteRecordById(self, recid: str, collection: str) -> dict:
        doc = self.getRecordById(recid, collection)
        collection = self.database_connection[collection]
        collection.delete_one({'_id':recid})
        return doc
    
    def getRecords(self, data: dict, collection: str) -> List[dict]:
        collection = self.database_connection[collection]
        object_list = list(collection.find(data))
        return object_list

