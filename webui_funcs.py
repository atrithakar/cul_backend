from flask import request, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import db
from models import User, Module

def login_webui():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return render_template('index.html', error="Invalid email or password")

    session['email'] = email
    return redirect(url_for('main_page'))

def signup_user_webui():
    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    hashed_password = generate_password_hash(password)

    user = User(email=email, password=hashed_password, first_name=first_name, last_name=last_name, username=username)

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return render_template('signup.html', error="User already exists")
    
    user_name_exists = User.query.filter_by(username=username).first()
    if user_name_exists:
        return render_template('signup.html', error="Username already exists, pick a different username.")

    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))

def change_password_webui():
    profile = User.query.filter_by(email=session.get('email')).first()
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    is_old_password_correct = check_password_hash(profile.password, old_password)
    if not is_old_password_correct:
        return render_template('profile.html', error="Old password is incorrect",profile=profile)
    User.query.filter_by(email=session.get('email')).update({'password': generate_password_hash(new_password)})
    db.session.commit()
    return render_template('profile.html', success="Password changed successfully", profile=profile)

def main_page_webui():
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

def upload_modules_webui():
    if request.method == 'GET':
        return render_template('upload_modules.html')
    elif request.method == 'POST':
        module_url = request.form.get('github_repo_link')
        # assuming module_url is in the format: https://github.com/username/repo
        module_name = module_url.split('/')[-1]
        # check if the module already exists
        module = Module.query.filter_by(module_name=module_name).first()
        if module:
            return render_template('upload_modules.html', error="Module already exists")
        # check if module exists at provided url

        # clone the repo into the c_cpp_modules directory
        cloned_status = os.system(f"git clone {module_url} {os.path.join(BASE_DIR, module_name)}")
        if cloned_status != 0:
            return render_template('upload_modules.html', error="Error cloning the repository")
        module = Module(module_name=module_name, module_url=module_url, associated_user=session.get('email'))
        db.session.add(module)
        db.session.commit()
        return render_template('main_page.html')

def delete_module_webui(module_id):
    module = Module.query.filter_by(module_id=module_id).first()
    if not module:
        return render_template('profile.html', error="Module not found")
    os.system(f"rm -rf {os.path.join(BASE_DIR, module.module_name)}")
    db.session.delete(module)
    db.session.commit()
    return render_template('profile.html')

def update_module_webui(module_id):
    module = Module.query.filter_by(module_id=module_id).first()
    if not module:
        return render_template('profile.html', error="Module not found")
    os.system(f"cd {os.path.join(BASE_DIR, module.module_name)} && git pull")
    return render_template('profile.html')

def get_module_info_webui(module, version):
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
