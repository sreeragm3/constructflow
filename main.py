from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Directory where images will be saved
UPLOAD_FOLDER = "uploaded_images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check file extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def showcase():
    return render_template('admin.html')

@app.route('/upload', methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "files[]" not in request.files:
            return "No files part"
        
        files = request.files.getlist("files[]")
        saved_files = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = file.filename
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)
                saved_files.append(filename)

        return f"Uploaded successfully: {', '.join(saved_files)}"

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
