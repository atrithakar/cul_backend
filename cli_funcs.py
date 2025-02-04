import os
import json
import io

def get_latest_version_cli(module_name):
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
            return jsonify({"latest": data.get('latest')})
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the versions.json file."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred."}), 500

def get_versions_cli(module_name):
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
            print(data)
            return jsonify(data)
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the versions.json file."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred."}), 500