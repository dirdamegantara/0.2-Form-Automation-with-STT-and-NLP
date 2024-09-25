from flask import Flask, render_template, request, jsonify
import cohere
from datetime import datetime
import os
import json

app = Flask(__name__)

# Configure Cohere API key
cohere_api_key = 'tKmNcPgRmJQlDFZV8T2tiZM2YbZcqUBeb8W4i25p'  # Replace with your actual key
co = cohere.Client(cohere_api_key)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

data_file = 'data.json'

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    
    nama = request.form['nama']
    tempat_lahir = request.form['tempat_lahir']
    tanggal_lahir = request.form['tanggal_lahir']
    tanggungan = request.form['tanggungan']
    status = request.form['status']
    alamat = request.form['alamat']

    return f"""
        <h1>Form Submitted</h1>
        <p><strong>Nama:</strong> {nama}</p>
        <p><strong>Tempat Lahir:</strong> {tempat_lahir}</p>
        <p><strong>Tanggal Lahir:</strong> {tanggal_lahir}</p>
        <p><strong>Jumlah Tanggungan Keluarga:</strong> {tanggungan}</p>
        <p><strong>Status Perkawinan:</strong> {status}</p>
        <p><strong>Alamat:</strong> {alamat}</p>
    """

@app.route('/log_transcript', methods=['POST'])
def log_transcript():
    data = request.get_json()
    transcript = data.get('transcript', '')

    if transcript:
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file_path = os.path.join(log_dir, f'voicelog_{date_str}.txt')
        general_log_path = 'voicelog.txt'

        with open(log_file_path, 'a') as log_file:
            log_file.write(f"{transcript}\n")

        with open(general_log_path, 'w') as general_log_file:
            general_log_file.write(transcript)

        return jsonify({"message": "Transcript logged successfully"}), 200
    else:
        return jsonify({"message": "No transcript provided"}), 400

@app.route('/process_voicelog', methods=['POST'])
def process_voicelog():
    log_file_path = 'voicelog.txt'

    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            transcript = log_file.read().strip()

        try:
            # Call Cohere API to process the voicelog
            cohere_response = call_cohere_api(transcript)
            print(f"Cohere Response: {cohere_response}")  # Log the response
            
            # Extract data from the Cohere response
            extracted_data = extract_data(cohere_response)
            
            # Write extracted data to data.json
            with open(data_file, 'w') as json_file:
                json.dump(extracted_data, json_file)

            # Send the extracted data as response
            return jsonify({"message": "Voicelog processed", "response": extracted_data}), 200
        except Exception as e:
            print(f"Error: {str(e)}")  # Log the error
            return jsonify({"error": f"Error processing voicelog: {str(e)}"}), 500
    else:
        return jsonify({"error": "voicelog.txt not found"}), 404

def call_cohere_api(transcript):
    # Improved prompt for Cohere to extract data from the transcript
    prompt = f"""
    Extract the following fields from the given transcript:
    - Nama
    - Tempat Lahir
    - Tanggal Lahir (format: YYYY-MM-DD)
    - Tanggungan (integer)(if mentioned, otherwise leave empty)
    - Status (Lajang, Kawin, Cerai Pisah, Cerai Mati)(if mentioned, otherwise leave empty)
    - Alamat (if mentioned, otherwise leave empty)
    Set the value to null if empty.

    Transcript: {transcript}

    Format the response like this:
    Nama: <nama>
    Tempat Lahir: <tempat_lahir>
    Tanggal Lahir: <tanggal_lahir>
    Tanggungan: <tanggungan>
    Status: <status>
    Alamat: <alamat>
    """

    response = co.generate(
        model='command-r-plus',  # Use a lightweight model
        prompt=prompt,
        max_tokens=150,
        temperature=0.5,
    )

    return response.generations[0].text.strip()

def extract_data(cohere_response):
    # Initialize empty form data
    form_data = {
        'nama': '',
        'tempat_lahir': '',
        'tanggal_lahir': '',
        'tanggungan': '',
        'status': '',
        'alamat': ''
    }

    # Split response into lines and extract fields
    lines = cohere_response.split("\n")
    for line in lines:
        if "Nama" in line:
            form_data['nama'] = line.split(":")[1].strip() if "null" not in line else ''
        elif "Tempat Lahir" in line:
            form_data['tempat_lahir'] = line.split(":")[1].strip() if "null" not in line else ''
        elif "Tanggal Lahir" in line:
            date_value = line.split(":")[1].strip()
            form_data['tanggal_lahir'] = date_value if "null" not in line else ''
        elif "Tanggungan" in line:
            form_data['tanggungan'] = line.split(":")[1].strip() if "null" not in line else ''
        elif "Status" in line:
            form_data['status'] = line.split(":")[1].strip() if "null" not in line else ''
        elif "Alamat" in line:
            form_data['alamat'] = line.split(":")[1].strip() if "null" not in line else ''

    # Return the cleaned form data
    return form_data


if __name__ == '__main__':
    app.run(debug=True)
