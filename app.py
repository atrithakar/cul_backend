from flask import Flask, send_from_directory, abort, send_file
import os
from pathlib import Path
import zipfile

app = Flask(__name__)

BASE_DIR = "c_cpp_modules"  # Directory containing all modules and versions

@app.route('/files/<module_name>/<version>', methods=['GET'])
def serve_files(module_name, version):
    module_dir = os.path.join(BASE_DIR, module_name, version)

    try:
        # Send a ZIP file containing all the files from the specified module version directory
        zip_filename = f'{module_name}_{version}.zip'
        zip_path = Path(module_dir) / zip_filename

        # Create a zip file containing all files in the module version directory
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(module_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), module_dir))
        
        return send_file(zip_path, as_attachment=True)
    except Exception as e:
        print(f"Error: {e}")
        return "Error occurred while serving files", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
