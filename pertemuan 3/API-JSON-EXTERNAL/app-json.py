from flask import Flask,jsonify
import json

app = Flask(__name__)

def load_data():
    with open('data','json','r') as f:
        return json.load(f)
    
@app.route('/',methods=['GET'])
def get_users():
    data= load_data()
    return jsonify(data)

@app.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    data = load_data()
    user = next((item for item in data if item["id"] == user_id), None)
    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "user tidak ditemukan"}),404
    
if __name__ == '__main__':
    app.run(debug=True)