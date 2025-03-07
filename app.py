from flask import Flask, render_template, request, jsonify
import os
import base64
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

@app.route('/')
def index():
    return render_template("index.html")


#@app.route('/save-photos', methods=['POST'])
#def save_photo():
    # Saving
    # return jsonify({'success': True, 'filename': filename})




if __name__ == '__main__':
    app.run(debug=True)