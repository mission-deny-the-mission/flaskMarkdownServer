import glob

from flask import Flask, json, request, abort
import os
import string
import random
import json
import password_hashing

app = Flask(__name__)

# This URL is used for registering a new directory
# WHen we register a new directory we also get the user to set a password in order to access that directory
@app.route('/register/', methods=["GET", "POST"])
def register():
    # the request with the password come in the form of a json file
    contents = request.get_json()
    password = contents["password"]
    # each workspace is randomly assigned a name using a random word generating function
    letters = string.ascii_lowercase + string.ascii_uppercase
    random_word = ''.join([random.choice(letters) for _ in range(10)])
    # here we make sure a directory with the same name does not already exist
    dirs = [x[0] for x in os.walk('workspace')]
    # if the directory already exists then try another directory name
    while random_word in dirs:
        random_word = ''.join([random.choice(letters) for _ in range(10)])
    # try and create a new directory using OS commands
    try:
        os.mkdir(os.path.join("workspace", random_word))
        # if creating the directory succeeded then create a password hash file, make a hash,
        # then save and close the hash file
        file = open(os.path.join("workspace", random_word, "password.hash"), 'wb')
        file.write(password_hashing.hash_password(password))
        file.close()
    except OSError as _:
        # if there was a problem creating the directory then report an error to the user
        return "error creating directory", 405
    else:
        return random_word

# This function is used for uploading files to a directory
@app.route('/upload', methods=["GET", "POST"])
def upload():
    # the json file given by the caller contains the workspace, password, and filename
    if "json" not in request.files:
        return "Missing JSON", 400
    contents = json.loads(request.files["json"].read())
    # here we do a presence check for the workspace, password, and filename and then put them in separate variables
    if not all(key in contents for key in ["workspace", "password", "filename"]):
        return "Missing information in JSON file", 400
    workspace = contents["workspace"]
    password = contents["password"]
    filename = contents["filename"]
    # make sure the file the caller is trying to upload is actually present or give an error response if not
    if filename not in request.files:
        return "Missing file", 400
    # if the workspace is missing then we send an error response to the caller
    if not os.path.isdir(os.path.join("workspace", workspace)):
        return "workspace name not found", 400
    # if the password is incorrect send an error response to the caller
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    if request.method == "GET":
        return "", 200

    try:
        # try and write the file to the disk
        with open(os.path.join("workspace", workspace, filename), "wb") as fp:
            fp.write(request.files[filename].read())
    except IOError as _:
        # if the file cannot be written to the disk then give an error response
        return "Could not create file on server", 500

    # if all went correctly then give a 201 reponse for success
    return "", 201

# this is the function for compiling a MarkDown document to HTML
@app.route('/CompileMDtoHTML/', methods=["POST", "GET"])
def compile_MD_to_HTML():
    # get the json file containing the necessary information required to compile the document
    contents = request.get_json()
    if contents is None:
        return "Missing JSON", 400
    # we need the workspace, password, and filename to compile
    # if we don't have these then an error needs to be produced
    elif not all(key in contents for key in ["workspace", "password", "filename"]):
        return "Missing parameter in JSON", 400
    # separate out this information from the caller into variables to be used later
    workspace = contents["workspace"]
    password = contents["password"]
    filename = contents["filename"]
    # if the password is incorrect then give an error response
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    # check the file extension is correct for a markdown file
    if filename[-3:] == ".md":
        # determine the full length file name
        input_file_name = os.path.join("workspace", workspace, filename)
        output_file_name = os.path.join("workspace", workspace, filename[0:-3] + ".html")
        # check if the file actually exists and give an error response to the caller if not
        if not os.path.isfile(input_file_name):
            return "The file you are trying to compile does not exist", 400
        # compile the file
        os.system("pandoc -f markdown -t html {0} > {1}".format(input_file_name, output_file_name))
        # here the success of the compilation is determined by simply checking if it gave an output file
        # this is a somwhat naive approach and might be impoved upon
        if not os.path.isfile(output_file_name):
            return "Compilation failed", 500
        # read and return the compiled file to the caller if it succeeded
        file = open(output_file_name, 'r')
        return file.read()

# this is the function for compiling a markdown file to a PDF document
@app.route('/CompileMDtoPDF/', methods=["POST", "GET"])
def compile_MD_to_PDF():
    # first get the json document with the neccessary fields
    contents = request.get_json()
    if contents is None:
        # return an error response to the caller if the json document is not present
        return "Missing JSON", 400
    # make sure the file has the required fields necessary for locating and compiling the document
    # otherwise return an error response to the caller
    elif not all(key in contents for key in ["workspace", "password", "filename"]):
        return "Missing parameter in JSON", 400
    # separate out the required info into separate variables
    workspace = contents["workspace"]
    password = contents["password"]
    filename = contents["filename"]
    # check that the password is correct for the workspace
    # if not give an error response and quit
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    # make sure the file extension is correct
    if filename[-3:] == ".md":
        # determine the full path of the file to be compiled and what it's result should be
        input_file_name = os.path.join("workspace", workspace, filename)
        output_file_name = os.path.join("workspace", workspace, filename[0:-3] + ".pdf")
        # if the file the caller is trying to compile does not exist then give an error message
        if not os.path.isfile(input_file_name):
            return "The file you are trying to compile does not exist", 400
        # compile the file in question
        os.system("pandoc -f markdown {0} -o {1}".format(input_file_name, output_file_name))
        # check if an output file has been generated by the compiler, this is a simple but naive test to check if
        # the compilation has succeeded
        if not os.path.isfile(output_file_name):
            return "Compilation failed", 500
        # if the compilation succeeded it is read and submitted to the caller
        file = open(output_file_name, 'rb')
        return file.read()

# function to compile LaTeX documents to PDFs
@app.route('/CompileLaTeXtoPDF/', methods=["GET", "POST"])
def Compile_LaTeX_to_PDF():
    # get the file with the necessary parameters to locate and compile the file
    contents = request.get_json()
    # if these are missing then return an error response
    if contents == None:
        return "Missing JSON", 400
    elif not all(key in contents for key in ["workspace", "password", "filename"]):
        return "Missing parameter in JSON", 400
    # separate out the parameters into variables
    workspace = contents["workspace"]
    password = contents["password"]
    filename = contents["filename"]
    # check that the password is correct otherwise give an error response
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    # verify the filename has the correct extension for a LaTeX document
    if filename[-4:] == ".tex":
        # switch to workspace folder
        output_file_name = os.path.join("workspace", workspace, filename[0:-4] + ".pdf")
        os.chdir(os.path.join("workspace", workspace))
        # if the main file to be compiled does not exist then send an error response
        if not os.path.isfile(filename):
            return "The file you are trying to compile does not exist", 400
        # compile the file
        os.system("pdflatex " + filename)
        # then return to the original directory
        os.chdir("../..")
        # check if the output file exists to determine if the compilation succeeded or not
        if not os.path.isfile(output_file_name):
            return "Compilation failed", 500
        # open the output file and send it to the caller
        file = open(output_file_name, 'rb')
        return file.read()

# function to delete the workspace
@app.route('/Delete/', methods=["GET", "POST"])
def delete():
    # make sure the caller submitted the necessary information in the form of a JSON document
    contents = request.get_json()
    if contents == None:
        return "Missing JSON document", 400
    elif not all(parameterName in contents for parameterName in ["workspace", "password"]):
        return "Missing paramters in JSON", 400
    # seperate necessary fields out into variables
    dir = os.path.join("workspace", contents["workspace"])
    password = contents["password"]
    # verify the workspace the user is trying to delete actually exists
    if not os.path.isdir(dir):
        return "workspace does not exist", 400
    # check the password is correct, if it is incorrect then return an error response
    if not password_hashing.check_password(contents["workspace"], password):
        return "Incorrect password", 401
    # delete the workspace using an OS command
    os.system("rm -r " + dir)
    return "", 200

# function to list files in a workspace
@app.route('/ListFiles/', methods=["GET", "POST"])
def listFiles():
    # get required fields
    contents = request.get_json()
    if contents == None:
        return "missing JSON document with function parameters", 400
    elif not all(parameterName in contents for parameterName in ["workspace", "password"]):
        return "missing paramters in JSON document", 400
    workspace = contents["workspace"]
    password = contents["password"]
    # verify that the workspace actually exists and if not send an error response
    if not os.path.isdir(os.path.join("workspace", workspace)):
        return "Workspace does not exist", 400
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    # change to the workspace directory
    os.chdir(os.path.join('workspace', workspace))
    files = []
    # get a list of all the files in teh directory and their sizes
    for file in glob.glob('*'):
        stats = os.stat(file)
        files.append({"name": file, "size": stats.st_size})
    # go back to the original directory
    os.chdir('../../')
    # return the directory info back to the caller
    return json.dumps(files)

# function to download a file from the workspace
@app.route('/Download/<workspace>/<password>/<file>')
def downloadFile(workspace, password, file):
    # check the password had is correct
    if not password_hashing.check_password(workspace, password):
        return "Incorrect password", 401
    # make sure the file actually exists before trying to open it
    if os.path.isdir(os.path.join(workspace, file)):
        return "File does not exist", 400
    # open the file and read it back to the user
    try:
        file = open(os.path.join(workspace, file), 'rb')
    except IOError as _:
        # if the file could not be opened give an error instead
        return "Could not open file", 500
    return file.read()

# function to create a sub folder in a workspace
@app.route('/CreateSubFolder/', methods=["GET", "POST"])
def createSubFolder():
    contents = request.get_json()
    # make sure the necessary parameters have been provided by the caller
    if contents == None:
        return "Missing JSON document with function parameters", 400
    if not all(requiredParameter in contents for requiredParamter in ["workspace", "password", "folderpath"]):
        return "Missing required parameters from JSON document", 400
    # separate parameters into separate variables
    workspace = os.path.join("workspace", contents["workspace"])
    password = contents["password"]
    folderpath = contents["subfolder"]
    # verify the workspace actually exists
    if not os.path.isdir(workspace):
        return "Workspace does not exist", 400
    # check that the password submitted is correct and if not give an error response
    if not password_hashing.check_password(contents["workspace"], password):
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
