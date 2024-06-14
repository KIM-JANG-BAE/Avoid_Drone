from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)


UPLOAD_FOLDER = '/home/jeonjunsu/obj'

@app.route('/api/obj/<filename>', methods=['GET'])
def get_obj_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5261)