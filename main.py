from flask import request, Flask, render_template, make_response, jsonify
from werkzeug.utils import secure_filename
import os
from utils.file import allowed_file

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1 GB
app.config["UPLOAD_FOLDER"] = "uploads"


@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "media" in request.files:
        file = request.files["media"]
        if not file:
            return "No file uploaded", 400

        if allowed_file(file.filename):
            if file.filename == "":
                return "No selected file", 400

            filename = secure_filename(file.filename)
            try:
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            except Exception as e:
                return f"Error saving file: {str(e)}", 500

            return "File uploaded successfully"
        else:
            return "File type not allowed", 400

    else:
        return "Something Went Wrong, Try Again", 400


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
