from flask import Flask, request, jsonify
import uuid

data_log = {}
app= Flask(__name__)
@app.route("/register", methods = ['PUT'])
def store():
    global data_log
    data_log[request.form['uuid']] = {'cand': request.form['cand'], 'sdp': request.form['sdp']}
    
    return "", 201

@app.route("/request", methods = ['GET'])
def send():
    global data_log
    uuid = request.args.get('uuid')
    try:
        return jsonify(data_log[str(uuid)])
    except KeyError:
        return "UUID not found", 404
        
if __name__=="__main__":
    app.run()
    
