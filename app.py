from flask import Flask, send_from_directory, abort
import os

app = Flask(__name__)

BASE_DIR = "c_cpp_modules"  # Directory to serve files from

@app.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    try:
        return send_from_directory(BASE_DIR, filename)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
