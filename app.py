from flask import Flask, json, request, abort
import os
import string
import random
import shutil

app = Flask(__name__)

dirs = []

@app.route('/register')
def register():
    letters = string.ascii_lowercase + string.ascii_uppercase
    random_word = ''.join([random.choice(letters) for _ in range(10)])
    while random_word in dirs:
        random_word = ''.join([random.choice(letters) for _ in range(10)])
    dirs.append(random_word)
    os.mkdir(os.path.join("workspace", random_word))
    return random_word

@app.route('/upload/<dir>/<filename>', methods=["POST"])
def upload(dir, filename):
    if dir not in dirs:
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

if __name__ == '__main__':
    app.run()
