import os
import openai
import json
import requests
from flask import Flask, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
from flask_cors import CORS
from flask import jsonify
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
from flask import Flask
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
@cross_origin()
def helloWorld():
  return "Hello, cross-origin-world!"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"

openai.api_key = "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"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
        return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def generate_summary(text):
    model_engine = "text-davinci-003"
    max_chunk_size = 1990
    summary = ''
    for i in range(0, len(text), max_chunk_size):
        chunk = text[i:i+max_chunk_size]
        prompt = f"Please summarize the following text: {chunk}"
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=1.5,
        )
        summary += response.choices[0].text.strip() + ' '
    return summary

def generate_objectives(summary):
    model_engine = "text-davinci-003"
    prompt = f"Please generate 5  short objectives  for the OKR system, without any date or time based on the following: {summary}" 
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.5,
    )
    mlobjectives = response.choices[0].text.strip()
    return mlobjectives.split('\n')


@app.route('/objectives/', methods=['POST'])
@cross_origin()
def handle_objectives():
    if request.method == 'POST':
        data = request.json
        # Now data is a dictionary which contains the post data. 
        # You can handle the data as you like.
        print(data)
        return jsonify({"message": "Received the objective data"})
    return jsonify({"error": "Unsupported method"})


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            if file_ext == 'pdf':
                text = extract_text_from_pdf(file_path)
            elif file_ext == 'docx':
                text = extract_text_from_docx(file_path)
            else:
                return jsonify({"error": "Unsupported file format"})

            summary = generate_summary(text)
            mlobjectives = generate_objectives(summary)

            return jsonify({"mlobjectives": mlobjectives})
    return '''
    <!doctype html>
    <title

    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
    <input type=file name=file>
    <input type=submit value=Upload>
    </form>
    '''




if __name__ == '__main__':
    app.run(debug=True)
    
