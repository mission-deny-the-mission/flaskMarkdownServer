import glob
from time import sleep

from flask import Flask, json, request, abort
import os
import string
import random
import json
import shutil

app = Flask(__name__)

@app.route('/register')
def register():
    letters = string.ascii_lowercase + string.ascii_uppercase
    random_word = ''.join([random.choice(letters) for _ in range(10)])
    dirs = [x[0] for x in os.walk('workspace')]
    while random_word in dirs:
        random_word = ''.join([random.choice(letters) for _ in range(10)])
    try:
        os.mkdir(os.path.join("workspace", random_word))
    except OSError as err:
        return "error creating directory", 405
    else:
        return random_word

@app.route('/upload/<dir>/<filename>', methods=["GET", "POST"])
def upload(dir, filename):
    if (request.method == "GET"):
        return "", 200
    if not os.path.isdir(os.path.join("workspace", dir)):
        abort(405, "workspace name not found")
    with open(os.path.join("workspace", dir, filename), "wb") as fp:
        fp.write(request.data)

    return "", 201

@app.route('/CompileMDtoHTML/<dir>/<filename>')
def compile_MD_to_HTML(dir, filename):
    if filename[-3:] == ".md":
        input_file_name = os.path.join("workspace", dir, filename)
        output_file_name = os.path.join("workspace", dir, filename[0:-3] + ".html")
        os.system("pandoc -f markdown -t html {0} > {1}".format(input_file_name, output_file_name))
        file = open(output_file_name, 'r')
        return file.read()

@app.route('/CompileMDtoPDF/<dir>/<filename>')
def compile_MD_to_PDF(dir, filename):
    if filename[-3:] == ".md":
        input_file_name = os.path.join("workspace", dir, filename)
        output_file_name = os.path.join("workspace", dir, filename[0:-3] + ".pdf")
        os.system("pandoc -f markdown {0} -o {1}".format(input_file_name, output_file_name))
        file = open(output_file_name, 'rb')
        return file.read()

@app.route('/CompileLaTeXtoPDF/<dir>/<filename>')
def compile_LaTeX_to_PDF(dir, filename):
    if filename[-4:] == ".tex":
        output_file_name = os.path.join("workspace", dir, filename[0:-4] + ".pdf")
        os.chdir(os.path.join("workspace", dir))
        os.system("pdflatex " + filename)
        os.chdir("../..")
        file = open(output_file_name, 'rb')
        return file.read()

@app.route('/Delete/<dir>')
def delete(dir):
    os.system("rm -r " + os.path.join("workspace", dir))
    return "", 200

@app.route('/ListFiles/<workspace>')
def listFiles(workspace):
    os.chdir(os.path.join('workspace', workspace))
    files = []
    for file in glob.glob('*'):
        stats = os.stat(file)
        files.append({"name": file, "size": stats.st_size})
    os.chdir('../../')
    return json.dumps(files)

@app.route('/Download/<workspace>/<file>')
def downloadFile(workspace, file):
    file = open(os.path.join(workspace, file), 'rb')
    return file.read()

@app.route('/')
def index():
    return "Hello world!", 200

if __name__ == '__main__':
    app.run()
