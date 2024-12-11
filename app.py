from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from database import add_pdf_file, add_text_file
from assistant import process_query

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def print_message_with_time(message: str, time_format: str = "%Y-%m-%d %H:%M:%S"):
    current_datetime = datetime.now().strftime(time_format)
    print(f"{current_datetime}: {message}")

@app.route('/upload', methods=['POST'])
def upload_file():
    """API to upload either raw text or a file (PDF or text file)."""
    print_message_with_time("Received a request for upload")

    # Check if raw text is provided in the request
    file_type = "unknown"
    file_path = ""
    if request.is_json:
        json_data = request.get_json()
        if "text" in json_data:
            raw_text = json_data["text"]
            filename = f"{uuid.uuid4()}.txt"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(raw_text)
            print_message_with_time(f"Raw text saved to {file_path}")
            file_type = "text"

    # Check if a file is provided in the request
    if 'file' in request.files:
        file = request.files['file']
        print_message_with_time(f"File received: {file.filename}")

        if file.filename == '':
            print_message_with_time("Error: No file selected")
            return jsonify({"error": "No file selected"}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(file_path)
        print_message_with_time(f"File saved to {file_path}")

        # Determine file type based on extension

        if filename.lower().endswith('.pdf'):
            file_type = "pdf"
        elif filename.lower().endswith('.txt'):
            file_type = "text"
        print_message_with_time(f"File type recognized as: {file_type}")

    if file_type == "unknown":
        # If neither text nor file is provided
        print_message_with_time("Error: No text or file provided")
        return jsonify({"error": "No text or file provided", "isSuccess": False}), 400

    if file_type == "pdf":
        add_pdf_file(file_path)

    if file_type == "text":
        add_text_file(file_path)

    os.unlink(file_path)

    return jsonify({"isSuccess": True})


@app.route('/process', methods=['POST'])
def process_text():
    """API to reverse the input text."""
    print_message_with_time("Received a request to process text")

    text = None
    if request.is_json:
        json_data = request.get_json()
        if "text" in json_data:
            text = json_data["text"]

    if not text:
        print_message_with_time("Error: No text provided")
        return jsonify({"result": "No text provided", "isSuccess": False}), 400

    print_message_with_time(f"Original text: {text}")

    result = process_query(text)
    if result is None:
        return jsonify({"result": "Internal server error, please check application logs", "isSuccess": False}), 500
    print_message_with_time(f"Result: {result}")
    return jsonify({"result": result, "isSuccess": True})

if __name__ == '__main__':
    print_message_with_time("Starting Flask server")
    app.run(debug=True)
