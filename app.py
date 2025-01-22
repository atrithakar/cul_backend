from flask import Flask, send_file, jsonify, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import zipfile
import io
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cul_db.db'
db = SQLAlchemy(app)
app.secret_key = "Atri Thakar"

# create a class for the database
class User(db.Model):
    email = db.Column(db.String(80), primary_key = True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<email: {self.email}\npassword: {self.password}>"

with app.app_context():
    db.create_all()

BASE_DIR = "c_cpp_modules"  # Directory containing all modules and versions

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/',methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return render_template('index.html', error="Invalid email or password")

    session['email'] = email
    return redirect(url_for('main_page'))

@app.route('/signup',methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup',methods=['POST'])
def signup_user():
    email = request.form.get('email')
    password = request.form.get('password')
    hashed_password = generate_password_hash(password)
    user = User(email=email, password=hashed_password)
    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return render_template('signup.html', error="User already exists")
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/main_page', methods=['GET', 'POST'])
def main_page():
    if not session.get('email'):
        return redirect(url_for('index'))
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
        return render_template('main_page.html', versions=versions,module=module_name, error=error)
    elif request.method == 'GET':
        return render_template('main_page.html')

@app.route('/info/<module>/<version>')
def get_module_info(module, version):
    # Replace this with your logic to fetch module details
    module_info_file_path = os.path.join(BASE_DIR, module, version, 'module_info.json')
    if not os.path.exists(module_info_file_path):
        return "<h1>Error 404: Module/Version not found.</h1>", 404
    module_info = None
    with open(module_info_file_path, 'r') as file:
        module_info = json.load(file)
    deps = module_info.get('requires', [])
    data = {
        "ModuleName": module,
        "Version": version,
        "Author": module_info.get('author'),
        "Description": module_info.get('description'),
        "License": module_info.get('license'),
        "Dependencies": {dep.split('==')[0]: dep.split('==')[1] for dep in deps} if deps else None,

    }
    # print(data)
    # print(jsonify(data))
    # return jsonify(data)
    return render_template('version_info.html', data=data)

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
            print(data)
            return jsonify(data)
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the versions.json file."}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred."}), 500

@app.route('/latest_version/<module_name>', methods=['GET'])
def get_latest_version(module_name):
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
