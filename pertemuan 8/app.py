from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
Bootstrap(app)

# Koneksi ke MongoDB
# Sesuaikan dengan URL MongoDB Anda
client = MongoClient("mongodb://localhost:27017/") 
db = client["crud_database"]
collection = db["items"]

# Route untuk menampilkan semua data
@app.route('/')
def index():
    # Mengambil semua data dari MongoDB
    items = collection.find() 
    return render_template('index.html', items=items)

# Route untuk menambahkan data baru
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        jumlah = request.form['jumlah']
        
        # Menyimpan data ke MongoDB
        collection.insert_one({
            'kode': kode, 
            'nama': nama, 
            'harga': harga, 
            'jumlah': jumlah
        }) 
        
        return redirect(url_for('index'))
        
    return render_template('add.html')
# Route untuk mengedit data
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    # Mengambil dokumen berdasarkan ObjectId (untuk mengisi formulir edit)
    item = collection.find_one({'_id': ObjectId(id)})

    if request.method == 'POST':
        # 1. Ambil data dari formulir POST
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        jumlah = request.form['jumlah']

        # 2. Update dokumen di MongoDB
        # Query: cari dokumen dengan '_id' yang sesuai
        # Operator $set: ubah nilai-nilai field yang baru
        collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': {'kode': kode, 'nama': nama, 'harga': harga, 'jumlah': jumlah}}
        )
        
        return redirect(url_for('index'))

    # Jika method adalah GET, tampilkan formulir edit dengan data item
    return render_template('edit.html', item=item)


# Route untuk menghapus data
@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    # Menghapus dokumen berdasarkan ObjectId
    collection.delete_one({'_id': ObjectId(id)}) 
    
    return redirect(url_for('index'))

# Bagian untuk menjalankan aplikasi Flask (Wajib ada)
if __name__ == '__main__':
    app.run(debug=True)
