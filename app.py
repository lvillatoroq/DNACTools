# Import Section
from flask import Flask, render_template, request, url_for, redirect
import backend
import csv
import os
from time import ctime

# Global Variables
app = Flask(__name__)
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Methods

def propagate_backend_exception(backend_response):
    """
    This function checks the backend response for ERROR indicators to raise an frontend
    exception and thereby display a customized error message in case of an backend error.
    """
    if 'ERROR' in str(backend_response):
        raise Exception(str(backend_response))


# Routes
@app.route('/')
@app.route('/index')
def index():
    return render_template('hello.html')


@app.route('/templateList', methods=['GET'])
def templateList():
    try:
        if request.method == 'GET':
            templates = backend.get_all_templates()
            propagate_backend_exception(templates)
            return render_template('templateList.html', template_list=templates)
    except Exception as e:
        print(e)
        return render_template('templateList.html', error=True, errorcode=e, reloadlink='/')


@app.route('/imageList', methods=['GET'])
def imageList():
    try:
        if request.method == 'GET':
            images = backend.get_all_images()
            propagate_backend_exception(images)
            return render_template('imageList.html', image_list=images)
    except Exception as e:
        print(e)
        return render_template('imageList.html', error=True, errorcode=e, reloadlink='/')


@app.route('/claimDevice', methods=['GET', 'POST'])
def claimDevice():
    try:
        if request.method == 'GET':
            devices = backend.get_all_pnp_device()
            propagate_backend_exception(devices)
            return render_template('claimDevice.html', pnp_list=devices, claimed=False)
        elif request.method == 'POST':
            submit_type = request.form.get("upload_submit")
            if submit_type == "Upload":
                upload = request.files['file']
                if upload.filename != '':
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], upload.filename)
                    # set the file path
                    upload.save(file_path)
                with open(file_path) as reader:
                    claim_list = csv.DictReader(reader)
                    return render_template('claimDevice.html', claim_list=claim_list, uploaded=True)

    except Exception as e:
        print(e)
        return render_template('claimDevice.html', error=True, errorcode=e, reloadlink='/')


# Main Function
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
