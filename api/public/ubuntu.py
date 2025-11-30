from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if username == "" and password == "":
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=16003, ssl_context=('nexcode.kr.cer', 'nexcode.kr.key'))
