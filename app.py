import glob

from flask import Flask, json, request, abort
import os
import string
import random
import json
import password_hashing

app = Flask(__name__)


@app.route('/register/', methods=["GET", "POST"])
def register():
    contents = request.get_json()
    password = contents["password"]
    letters = string.ascii_lowercase + string.ascii_uppercase
    random_word = ''.join([random.choice(letters) for _ in range(10)])
    dirs = [x[0] for x in os.walk('workspace')]
    while random_word in dirs:
        random_word = ''.join([random.choice(letters) for _ in range(10)])
    try:
        os.mkdir(os.path.join("workspace", random_word))
        file = open(os.path.join("workspace", random_word, "password.hash"), 'wb')
        file.write(password_hashing.hash_password(password))
        file.close()
    except OSError as _:
        return "error creating directory", 405
    else:
        return random_word


@app.route('/upload', methods=["GET", "POST"])
def upload():
    if "json" not in request.files:
        return "Missing JSON", 400
    contents = json.loads(request.files["json"].read())
    if not all(key in contents for key in ["workspace", "password", "filename"]):
        return "Missing information in JSON file", 400
    workspace = contents["workspace"]
    password = contents["password"]
    filename = contents["filename"]
    if filename not in request.files:
        return "Missing file", 400
    if not os.path.isdir(os.path.join("workspace", workspace)):
        return "workspace name not found", 400
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    if request.method == "GET":
        return "", 200

    try:
        with open(os.path.join("workspace", workspace, filename), "wb") as fp:
            fp.write(request.files[filename].read())
    except IOError as _:
        return "Could not create file on server", 500

    return "", 201


@app.route('/CompileMDtoHTML/', methods=["POST", "GET"])
def compile_MD_to_HTML():
    contents = request.get_json()
    if contents is None:
        return "Missing JSON", 400
    elif not all(key in contents for key in ["workspace", "password", "filename"]):
        return "Missing parameter in JSON", 400
    workspace = contents["workspace"]
    password = contents["password"]
    filename = contents["filename"]
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    if filename[-3:] == ".md":
        input_file_name = os.path.join("workspace", workspace, filename)
        output_file_name = os.path.join("workspace", workspace, filename[0:-3] + ".html")
        if not os.path.isfile(input_file_name):
            return "The file you are trying to compile does not exist", 400
        os.system("pandoc -f markdown -t html {0} > {1}".format(input_file_name, output_file_name))
        if not os.path.isfile(output_file_name):
            return "Compilation failed", 500
        file = open(output_file_name, 'r')
        return file.read()


@app.route('/CompileMDtoPDF/', methods=["POST", "GET"])
def compile_MD_to_PDF():
    contents = request.get_json()
    if contents is None:
        return "Missing JSON", 400
    elif not all(key in contents for key in ["workspace", "password", "filename"]):
        return "Missing parameter in JSON", 400
    workspace = contents["workspace"]
    password = contents["password"]
    filename = contents["filename"]
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    if filename[-3:] == ".md":
        input_file_name = os.path.join("workspace", workspace, filename)
        output_file_name = os.path.join("workspace", workspace, filename[0:-3] + ".pdf")
        if not os.path.isfile(input_file_name):
            return "The file you are trying to compile does not exist", 400
        os.system("pandoc -f markdown {0} -o {1}".format(input_file_name, output_file_name))
        if not os.path.isfile(output_file_name):
            return "Compilation failed", 500
        file = open(output_file_name, 'rb')
        return file.read()


@app.route('/CompileLaTeXtoPDF/', methods=["GET", "POST"])
def Compile_LaTeX_to_PDF():
    contents = request.get_json()
    if contents == None:
        return "Missing JSON", 400
    elif not all(key in contents for key in ["workspace", "password", "filename"]):
        return "Missing parameter in JSON", 400
    workspace = contents["workspace"]
    password = contents["password"]
    filename = contents["filename"]
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    if filename[-4:] == ".tex":
        output_file_name = os.path.join("workspace", workspace, filename[0:-4] + ".pdf")
        os.chdir(os.path.join("workspace", workspace))
        if not os.path.isfile(filename):
            return "The file you are trying to compile does not exist", 400
        os.system("pdflatex " + filename)
        os.chdir("../..")
        if not os.path.isfile(output_file_name):
            return "Compilation failed", 500
        file = open(output_file_name, 'rb')
        return file.read()


@app.route('/Delete/', methods=["GET", "POST"])
def delete():
    contents = request.get_json()
    dir = contents["workspace"]
    password = contents["password"]
    if not password_hashing.check_password(dir, password):
        return "Incorrect password", 401
    os.system("rm -r " + os.path.join("workspace", dir))
    return "", 200


@app.route('/ListFiles/', methods=["GET", "POST"])
def listFiles():
    contents = request.get_json()
    workspace = contents["workspace"]
    password = contents["password"]
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    os.chdir(os.path.join('workspace', workspace))
    files = []
    for file in glob.glob('*'):
        stats = os.stat(file)
        files.append({"name": file, "size": stats.st_size})
    os.chdir('../../')
    return json.dumps(files)


@app.route('/Download/<workspace>/<password>/<file>')
def downloadFile(workspace, password, file):
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    file = open(os.path.join(workspace, file), 'rb')
    return file.read()


@app.route('/CreateSubFolder/', methods=["GET", "POST"])
def createSubFolder():
    contents = request.get_json()
    workspace = contents["workspace"]
    password = contents["password"]
    folderpath = contents["subfolder"]
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    try:
        os.mkdir(os.path.join(workspace, folderpath))
    except Exception as exp:
        return "Error creating folder", 500
    else:
        return "", 200


@app.route('/')
def index():
    return "Hello world!", 200

if __name__ == '__main__':
    app.run()
