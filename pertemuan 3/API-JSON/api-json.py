from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    data=[{
        'nama': 'Mr. Sodron',
        'pekerjaan' : 'Web Progammer',
        'pesan': 'Menerima pesanan pembuatan WEB'
    }]
    return make_response(jsonify({'data' : data}),200)

@app.route('/karyawan', methods=['GET','POST','PUT', 'DELETE'])
def karyawan():
    try:
        if request.method == 'GET':
            data =[{
                'nama': 'Mr. Sodron',
                'pekerjaan' : 'Web Progammer',
                'pesan': 'Menerima pesanan pembuatan WEB'
    }]
        elif request.method == 'POST' :
            data =[{
                'nama': 'Mr. Sodron',
                'pekerjaan' : 'Web Progammer',
                'pesan': 'Menerima pesanan pembuatan WEB'
   
            }]
        elif request.method == 'PUT' :
            data =[{
                'nama': 'Mr. Sodron',
                'pekerjaan' : 'Web Progammer',
                'pesan': 'Menerima pesanan pembuatan WEB'
   
            }]
        else: 
            data =[{
                'nama': 'Mr. Sodron',
                'pekerjaan' : 'Web Progammer',
                'pesan': 'Menerima pesanan pembuatan WEB'
   
            }]
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)
    return make_response(jsonify({'data': data}), 200)

if __name__ == '__main__':
    app.run(debug=True) 
