from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://techzbots:4tQYI1SD64nr8jz5@rankingsbot.h5std55.mongodb.net/?retryWrites=true&w=majority"
)

db = client["techzcloud"]
filesdb = db["files"]


def save_file_in_db(filename, hash, msg_id=None):
    filesdb.update_one(
        {
            "hash": hash,
        },
        {"$set": {"filename": filename, "msg_id": msg_id}},
        upsert=True,
    )


def is_hash_in_db(hash):
    data = filesdb.find_one({"hash": hash})
    if data:
        return data
    else:
        return None
