import json
from pyrogram import Client, idle
import threading
from flask import request, Flask, render_template, make_response, jsonify, redirect
from werkzeug.utils import secure_filename
import os
from utils.db import is_hash_in_db, save_file_in_db
from utils.file import allowed_file, delete_cache, get_file_hash
from utils.process import start_processing
from utils.process import PROGRESS

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1 GB
app.config["UPLOAD_FOLDER"] = "static/uploads"


@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" in request.files:
        file = request.files["file"]
        if not file:
            return "No file uploaded", 400

        if allowed_file(file.filename):
            if file.filename == "":
                return "No selected file", 400

            filename = secure_filename(file.filename)
            extension = filename.rsplit(".", 1)[1]

            hash = get_file_hash(extension)
            while is_hash_in_db(hash):
                hash = get_file_hash(filename.rsplit(".", 1)[1])
                print(hash)

            try:
                file.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], hash + "." + extension)
                )
            except Exception as e:
                return f"Error saving file: {str(e)}", 500

            save_file_in_db(filename, hash)
            start_processing(bot, hash, filename, extension)

            return hash
        else:
            return "File type not allowed", 400

    else:
        return "Something Went Wrong, Try Again", 400


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/process/<hash>", methods=["GET"])
def process(hash):
    global PROGRESS

    data = PROGRESS.get(hash)
    if data:
        if data.get("message"):
            data = {"message": data["message"]}
            return json.dumps(data, separators=(",", ":"))
        else:
            data = {"current": data["done"], "total": data["total"]}
            return json.dumps(data, separators=(",", ":"))
    else:
        return "File not found", 400


if __name__ == "__main__":
    delete_cache()
    bot = Client(
        "bot",
        api_id=23636845,
        api_hash="d757ec9d2b7f09f474947ad3a2befd00",
        bot_token="6135734682:AAGtmEzHCQfq2VbDtQnXfPUDuq2PcKPw8ZM",
    )
    bot.start()
    threading.Thread(target=app.run, daemon=True).start()
    idle()
    bot.stop()
