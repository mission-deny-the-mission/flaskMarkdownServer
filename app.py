from flask import Flask, json, request, abort
import os
import string
import random

app = Flask(__name__)

dictionaryOfDirs = {}

@app.route('/register/<name>')
def register(name):
    letters = string.ascii_lowercase + string.ascii_uppercase
    randomWord = ''.join([random.choice(letters) for _ in range(10)])
    while randomWord in dictionaryOfDirs:
        randomWord = ''.join([random.choice(letters) for _ in range(10)])
    dictionaryOfDirs[name] = randomWord
    os.mkdir(os.path.join("workspace", randomWord))
    return "submitted correctly"

@app.route('/upload/<name>/<filename>', methods=["POST"])
def upload(name, filename):
    if name not in dictionaryOfDirs:
        abort(405, "workspace name not found")
    with open(os.path.join("workspace", dictionaryOfDirs[name], filename), "wb") as fp:
        fp.write(request.data)

    return "", 201

@app.route('/compile/<name>/<filename>/')
def compile(name, filename):
    if filename[-3:] == ".md":
        directory = dictionaryOfDirs[name]
        os.system("pandoc -f markdown -t html " + os.path.join("workspace", directory, filename))
        filenameHTML = filename[0:-3] + ".html"
        file = open(filenameHTML, 'r')
        return file.read()


if __name__ == '__main__':
    app.run()
