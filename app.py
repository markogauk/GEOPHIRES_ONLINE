from flask import Flask, render_template, request, send_file, send_from_directory
from wtforms import Form, FloatField, validators, FileField
import math
import os
from werkzeug.utils import secure_filename
from GEOPHIRESv2 import geophires
import numpy as np
from datetime import date

# Application object
app = Flask(__name__)

class GEOPHIRES(Form):
    filename = FileField(validators=[validators.InputRequired()])

# Relative path of directory for uploaded files
UPLOAD_DIR = 'uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.secret_key = 'MySecretKey'

if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

# Allowed file types for file upload
ALLOWED_EXTENSIONS = set(['txt', 'dat', 'npy'])


def allowed_file(filename):
    """Does filename have the right extension?"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Path to the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    global result
    line_labels = []
    line_values = []
    max_x = 400
    form = GEOPHIRES(request.form)
    filename = None  # default
    if request.method == 'POST':

        # Save uploaded file on server if it exists and is valid
        if request.files:
            file = request.files[form.filename.name]
            if file and allowed_file(file.filename):
                # Make a valid version of filename for any file ystem
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        result = geophires(filename)
        line_labels=result[0]
        line_values=result[1]
        max_x = np.amax(result[1])
    else:
        result = None
    
    
    return render_template("view.html", form=form, result=result, title='Remaining Reservoir Heat Content vs Plant Lifetime',max=max_x, labels=line_labels, values=line_values)

@app.route('/download')
def downloadFile ():
    path = "./results.txt"
    return send_file(path, as_attachment=True,cache_timeout=0)

@app.route('/example1')
def exampleFile ():
    path = "./uploads/example1.txt"
    return send_file(path, as_attachment=True)

@app.route('/line')
def line():
    line_labels=result[0]
    line_values=result[1]
    max_x = np.amax(result[1])
    return render_template('line_chart.html', title='Remaining Reservoir Heat Content vs Plant Lifetime',max=max_x, labels=line_labels, values=line_values)


if __name__ == '__main__':
    app.run(debug=True)
