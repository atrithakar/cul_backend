from flask import Flask, send_from_directory, send_file
import os
from pathlib import Path

app = Flask(__name__)

BASE_DIR = "c_cpp_modules"  # Directory to serve files from

@app.route('/files', methods=['GET'])
def serve_files():
    try:
        # Send a ZIP file containing all the files from BASE_DIR
        zip_filename = 'all_files.zip'
        zip_path = Path(BASE_DIR) / zip_filename

        # Create a zip file containing all files in the BASE_DIR
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(BASE_DIR):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), BASE_DIR))
        
        return send_file(zip_path, as_attachment=True)
    except Exception as e:
        print(f"Error: {e}")
        return "Error occurred while serving files", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
