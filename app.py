

from flask import Flask, request, jsonify
import os
import pytesseract
from pdf2image import convert_from_path

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

# pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


def remove_all_files(directory):
    # Ensure the directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"The directory {directory} does not exist or is not a directory.")

    # List all files and directories in the specified directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if it is a file
        if os.path.isfile(file_path):
            os.remove(file_path)  # Remove the file
            print(f"Removed file: {file_path}")
        else:
            print(f"Skipped: {file_path} (not a file)")


def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

@app.route('/convert-to-text/', methods=['POST'])
def convert_to_text():
    try:
        directory_path = 'tmp'
        remove_all_files(directory_path)
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        try:
            file_path = os.path.join("tmp", file.filename)
            file.save(file_path)
        except OSError as e:
            return jsonify({"error": f"Write error: {e}"}), 400

        if file.filename == '':
            return jsonify({"error": "No file selected for uploading"}), 400

        if file.filename[-3:].lower() == 'pdf':
            # pages = convert_from_path(file_path, 500) not used

            # output_str = extract_text(file_path)
            output_str = extract_text_from_pdf(file_path)
        else:
            output_str = pytesseract.image_to_string(file_path,lang='eng')

        os.remove(file_path)
        return jsonify({"extracted_data": output_str}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)