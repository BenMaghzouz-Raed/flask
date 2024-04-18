from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from subprocess import Popen, PIPE
import sys


app = Flask(__name__)

@app.route('/')
def index():
  return jsonify({'Result': 'Server Running'}), 200

# Error handler for 404 Not Found error
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'API Not Found'}), 404

# Error handler for 400 Bad Request error
@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': 'Bad Request'}), 400

# Error handler for all other HTTP errors
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(port=5000)
