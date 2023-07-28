ALLOWED_EXTENSIONS = {'avi', 'mp4', 'zip', 'xls', 'mkv', 'png', 'xlsx', 'mp3', 'pdf', 'jpeg', 'docx', 'jpg', 'wma', 'doc', 'txt', 'gif', 'rtf', 'csv', 'rar', 'mpg', 'flv'}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
