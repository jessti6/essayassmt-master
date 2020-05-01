import os

from flask import Response
from flask import flash, request, redirect, render_template

import essay_comparison
from app import app

Extensions = 'txt'
Allowed_extensions = set([Extensions])

key_file = ''
student_file = ''

matches = ''
out_file_name = ''
out_directory = os.path.expanduser('~').replace('\\', '\\\\')

q_repeated = False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Allowed_extensions


def check_inputs(file1, file2):
    if file1.filename == '':
        return 'No key file selected for uploading'
    elif file2.filename == '':
        return 'No student data file selected for uploading'
    elif not allowed_file(file1.filename):
        return 'Allowed key files have ' + Extensions + ' extension'
    elif not allowed_file(file2.filename):
        return 'Allowed student data files have ' + Extensions + ' extension'
    return ''


@app.route('/')
def upload_form():
    context = {'repeated': q_repeated, 'key_file': key_file, 'student_file': student_file}
    return render_template('upload.html', context=context)


@app.route('/', methods=['POST'])
def upload_file():
    global key_file, student_file, matches, out_file_name
    if request.method == 'POST':
        key_file = request.files['key_file']
        student_file = request.files['student_file']
        key_file.save(os.path.join(app.config['UPLOAD_FOLDER'], key_file.filename))
        student_file.save(os.path.join(app.config['UPLOAD_FOLDER'], student_file.filename))
        if check_inputs(key_file, student_file) != '':
            flash(check_inputs(key_file, student_file))
            return redirect(request.url)
        matches = essay_comparison.return_matches(key_file.filename, student_file.filename)
        out_file_name = essay_comparison.set_output_path(key_file.filename, student_file.filename)
        return redirect('/out')


@app.route("/out")
def get():
    with open(out_file_name, 'w') as f:
        for i in matches:
            f.write(i)
            f.write('\n')
        f.close()
    global q_repeated
    q_repeated = True
    return render_template('download.html')


@app.route("/get_download")
def get_download():
    with open(out_file_name) as f:
        match = f.read()
    return Response(
        match,
        mimetype="text",
        headers={"Content-disposition": "attachment; filename=match.txt"})


if __name__ == "__main__":
    app.debug = True
    # app.run(host='0.0.0.0', port=8080)
    app.run()
