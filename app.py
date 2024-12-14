from flask import Flask, send_from_directory, abort, send_file
import os
from pathlib import Path
import zipfile
import io

app = Flask(__name__)

BASE_DIR = "c_cpp_modules"  # Directory containing all modules and versions

@app.route('/files/<module_name>/<version>', methods=['GET'])
def serve_files(module_name, version):
    module_dir = os.path.join(BASE_DIR, module_name, version)

    try:
        # Create an in-memory zip file
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, 'w') as zipf:
            for root, dirs, files in os.walk(module_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, module_dir))

        zip_stream.seek(0)  # Go back to the start of the stream
        return send_file(zip_stream, as_attachment=True, download_name=f"{module_name}_{version}.zip")
    except Exception as e:
        print(f"Error: {e}")
        return "Error occurred while serving files", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
