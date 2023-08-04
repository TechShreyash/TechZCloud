import threading
from pyrogram import Client
import time
import os
import asyncio

from utils.db import save_file_in_db

PROGRESS = {}
from utils.tgstreamer import work_loads, multi_clients


async def upload_file_to_channel(hash, filename, extension):
    global PROGRESS, multi_clients, work_loads

    index = min(work_loads, key=work_loads.get)
    app = multi_clients[index]
    work_loads[index] += 1

    print("Uploading file to channel")
    PROGRESS[hash] = {}
    file = await app.send_document(
        -1001901516995,
        f"static/uploads/{hash}.{extension}",
        caption=f"{hash} | {filename}",
        progress=upload_progress,
        progress_args=(hash,),
    )
    save_file_in_db(filename, hash, file.id)
    work_loads[index] -= 1

    PROGRESS[hash]["message"] = file.id
    print("Uploaded file to channel")
    os.remove(f"static/uploads/{hash}.{extension}")


async def upload_progress(current, total, hash):
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
