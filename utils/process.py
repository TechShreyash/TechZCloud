import threading
from pyrogram import Client
import time
import os

PROGRESS = {}


def start_processing(app, hash, filename, extension):
    thread = threading.Thread(
        target=upload_file_to_channel,
        args=(
            app,
            hash,
            filename,
            extension,
        ),
        daemon=True,
    )
    thread.start()


def upload_file_to_channel(app: Client, hash, filename, extension):
    global PROGRESS
    print("Uploading file to channel")
    PROGRESS[hash] = {}
    file = app.send_document(
        -1001901516995,
        f"static/uploads/{hash}.{extension}",
        caption=f"{hash} | {filename}",
        progress=upload_progress,
        progress_args=(hash,),
    )
    PROGRESS[hash]["message"] = file.id
    print("Uploaded file to channel")
    os.remove(f"static/uploads/{hash}.{extension}")


def upload_progress(current, total, hash):
    global PROGRESS
    t1 = PROGRESS[hash].get("t1", 1)

    t2 = time.time()
    if t2 - t1 > 1:
        try:
            PROGRESS[hash]["t1"] = t2
            PROGRESS[hash]["done"] = current
            PROGRESS[hash]["total"] = total
        except Exception as e:
            print(e)
