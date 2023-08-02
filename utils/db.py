from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://techzbots:4tQYI1SD64nr8jz5@rankingsbot.h5std55.mongodb.net/?retryWrites=true&w=majority"
)

db = client["techzcloud"]
filesdb = db["files"]


def save_file_in_db(filename, hash):
    filesdb.insert_one({"filename": filename, "hash": hash})


def is_hash_in_db(hash):
    return filesdb.find_one({"hash": hash}) is not None
