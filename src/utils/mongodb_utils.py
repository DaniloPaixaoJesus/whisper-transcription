"""
import os
from pymongo import MongoClient

def get_database():
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongodb_uri)
    return client["transcription_db"]

def init_transcription(uuid, video_filename, transcription_filename, summary_filename):
    db = get_database()
    collection = db["transcriptions"]
    document = {
        "_id": uuid,
        "video_filename": video_filename,
        "transcription_filename": transcription_filename,
        "summary_filename": summary_filename,
        "status": "INIT"
    }
    collection.insert_one(document)

def update_transcription_status(uuid, status):
    db = get_database()
    collection = db["transcriptions"]
    collection.update_one({"_id": uuid}, {"$set": {"status": status}})
"""