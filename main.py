import threading
from utils.tgstreamer import work_loads, multi_clients
import asyncio
import json
from pyrogram import Client, idle
from werkzeug.utils import secure_filename
import os
from utils.db import is_hash_in_db, save_file_in_db
from utils.file import allowed_file, delete_cache, get_file_hash
from utils.tgstreamer import media_streamer
from utils.upload import upload_file_to_channel
from utils.upload import PROGRESS


from aiohttp import web

app = web.Application()


def render_template(name):
    with open(f"templates/{name}") as f:
        return f.read()


async def upload_file(request):
    global UPLOAD_TASK

    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename

    if field is None:
        return web.Response(text="No file uploaded.", content_type="text/plain")

    if allowed_file(filename):
        if filename == "":
            return web.Response(
                text="No file selected.", content_type="text/plain", status=400
            )

        filename = secure_filename(filename)
        extension = filename.rsplit(".", 1)[1]
        hash = get_file_hash(extension)

        while is_hash_in_db(hash):
            hash = get_file_hash(filename.rsplit(".", 1)[1])
            print(hash)

        try:
            with open(
                os.path.join("static/uploads", hash + "." + extension), "wb"
            ) as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception as e:
            return web.Response(
                text=f"Error saving file: {str(e)}",
                status=500,
                content_type="text/plain",
            )

        save_file_in_db(filename, hash)
        UPLOAD_TASK.append((hash, filename, extension))
        return web.Response(text=hash, content_type="text/plain", status=200)
    else:
        return web.Response(
            text="File type not allowed", status=400, content_type="text/plain"
        )


async def home(_):
    return web.Response(text=render_template("minhome.html"), content_type="text/html")


async def file_html(request):
    hash = request.match_info["hash"]
    download_link = f"http://64.227.157.55:8061/dl/{hash}"
    filename = is_hash_in_db(hash)["filename"]

    return web.Response(
        text=render_template("minfile.html")
        .replace("FILE_NAME", filename)
        .replace("DOWNLOAD_LINK", download_link),
        content_type="text/html",
    )


async def static_files(request):
    return web.FileResponse(f"static/{request.match_info['file']}")


async def process(request):
    global PROGRESS
    hash = request.match_info["hash"]

    data = PROGRESS.get(hash)
    if data:
        if data.get("message"):
            data = {"message": data["message"]}
            return web.json_response(data)
        else:
            data = {"current": data["done"], "total": data["total"]}
            return web.json_response(data)

    else:
        return web.Response(text="Not Found", status=404, content_type="text/plain")


async def download(request: web.Request):
    hash = request.match_info["hash"]
    id = is_hash_in_db(hash)
    if id:
        id = id["msg_id"]
        return await media_streamer(request, id)


UPLOAD_TASK = []


async def upload_task_spawner():
    global UPLOAD_TASK
    while True:
        if len(UPLOAD_TASK) > 0:
            task = UPLOAD_TASK.pop(0)
            loop = asyncio.get_event_loop()
            loop.create_task(upload_file_to_channel(*task))
            print("Task created", task)
        await asyncio.sleep(1)


async def generate_clients():
    global multi_clients, work_loads

    print("Generating Clients")

    multi_clients[0] = bot0
    work_loads[0] = 0
    print("Client 0 generated")

    for i in range(1, len(BOT_TOKENS)):
        bot = Client(
            f"bot{i}",
            api_id=API_KEY,
            api_hash=API_HASH,
            bot_token=BOT_TOKENS[i],
        )
        await bot.start()
        multi_clients[i] = bot
        work_loads[i] = 0
        print(f"Client {i} generated")


from config import *

if __name__ == "__main__":
    delete_cache()
    bot0 = Client(
        "bot0",
        api_id=API_KEY,
        api_hash=API_HASH,
        bot_token=BOT_TOKENS[0],
    )
    bot0.start()
    loop = asyncio.get_event_loop()
    task = loop.create_task(generate_clients())
    task = loop.create_task(upload_task_spawner())

    app.router.add_get("/", home)
    app.router.add_get("/static/{file}", static_files)
    app.router.add_get("/dl/{hash}", download)
    app.router.add_get("/file/{hash}", file_html)
    app.router.add_post("/upload", upload_file)
    app.router.add_get("/process/{hash}", process)

    threading.Thread(target=web.run_app, args=(app,), daemon=True).start()
    idle()
    bot0.stop()
