from flask import Flask, send_file, jsonify, request, render_template
import os
import zipfile
import io
import json

app = Flask(__name__)

BASE_DIR = "c_cpp_modules"  # Directory containing all modules and versions



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        module_name = request.form.get('module_name')
        versions_json = os.path.join(BASE_DIR, module_name, 'versions.json')
        versions = None
        error = None
        if os.path.exists(versions_json):
            with open(versions_json, 'r') as file:
                versions = json.load(file)
                versions = [item['version'] for item in versions.get('versions')]
        else:
            error = "Module not found"
        return render_template('index.html', versions=versions,module=module_name, error=error)
    elif request.method == 'GET':
        return render_template('index.html')

@app.route('/files/<module_name>/<version>', methods=['GET'])
def serve_files(module_name, version):
    module_dir = os.path.join(BASE_DIR, module_name, version)
    module_dir_wo_version = os.path.join(BASE_DIR, module_name)
    # Check if the module directory exists
    if not os.path.exists(module_dir_wo_version):
        return jsonify({"error": f"Module '{module_name}' not found."}), 404
    if not os.path.exists(module_dir):
        return jsonify({"error": f"Module '{module_name}' with version {version} not found."}), 404

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
        return jsonify({"error": "Error occurred while serving files."}), 500


@app.route('/files/<module_name>/', methods=['GET'])
def serve_files_2(module_name):
    versions_file_path = os.path.join(BASE_DIR, module_name, 'versions.json')
    
    # Check if the module directory exists
    if not os.path.exists(os.path.join(BASE_DIR, module_name)):
        return jsonify({"error": f"Module '{module_name}' not found."}), 404

    # Check if the versions.json file exists
    if not os.path.exists(versions_file_path):
        return jsonify({"error": "The versions.json file is missing for the specified module."}), 404

    try:
        with open(versions_file_path, 'r') as file:
            data = json.load(file)
            latest_path = data.get('latest_path')
            version = data.get('latest')

            if latest_path:
                module_dir = os.path.join(BASE_DIR, latest_path)

                if not os.path.exists(module_dir):
                    return jsonify({"error": f"The latest module path '{latest_path}' does not exist."}), 404

                # Create an in-memory zip file
                zip_stream = io.BytesIO()
                with zipfile.ZipFile(zip_stream, 'w') as zipf:
                    for root, dirs, files in os.walk(module_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, os.path.relpath(file_path, module_dir))

                zip_stream.seek(0)  # Go back to the start of the stream
                return send_file(zip_stream, as_attachment=True, download_name=f"{module_name}_{version}.zip")
            else:
                return jsonify({"error": "The 'latest_path' key is missing in the versions.json file."}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the versions.json file."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred."}), 500


@app.route('/versions/<module_name>', methods=['GET'])
def get_versions(module_name):
    versions_file_path = os.path.join(BASE_DIR, module_name, 'versions.json')
    
    # Check if the module directory exists
    if not os.path.exists(os.path.join(BASE_DIR, module_name)):
        return jsonify({"error": f"Module '{module_name}' not found."}), 404

    # Check if the versions.json file exists
    if not os.path.exists(versions_file_path):
        return jsonify({"error": "The versions.json file is missing for the specified module."}), 404

    try:
        with open(versions_file_path, 'r') as file:
            data = json.load(file)
            return jsonify(data)
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the versions.json file."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred."}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
