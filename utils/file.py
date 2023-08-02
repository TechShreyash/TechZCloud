ALLOWED_EXTENSIONS = {
    "avi",
    "mp4",
    "zip",
    "xls",
    "mkv",
    "png",
    "xlsx",
    "mp3",
    "pdf",
    "jpeg",
    "docx",
    "jpg",
    "wma",
    "doc",
    "txt",
    "gif",
    "rtf",
    "csv",
    "rar",
    "mpg",
    "flv",
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


from string import ascii_letters, digits
import os, random


def get_file_hash(extension):
    while True:
        hash = "".join([random.choice(ascii_letters + digits) for n in range(10)])
        if not os.path.exists(f"static/uploads/{hash}.{extension}"):
            return hash

def delete_cache():
    for file in os.listdir("static/uploads"):
        if file != 'exists.txt':
            os.remove(f"static/uploads/{file}")