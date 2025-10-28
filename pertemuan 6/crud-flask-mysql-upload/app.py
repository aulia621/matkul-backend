from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'secret123'

# KONFIGURASI MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'aulia'
app.config['MYSQL_DB'] = 'crud_db'

# KONFIGURASI UPLOAD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stok")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', files=data)


@app.route('/upload/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/add', methods=['GET', 'POST'])
def add_file():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO stok (kode, nama, harga, filename) VALUES (%s, %s, %s, %s)", 
                        (kode, nama, harga, filename))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('index'))
    
    return render_template('add.html')


@app.route('/delete/<id>', methods=['GET'])
def delete_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT filename FROM stok WHERE kode = %s", (id,))
    file_data = cur.fetchone()
    if file_data:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[0])
        if os.path.exists(file_path):
            os.remove(file_path)
        cur.execute("DELETE FROM stok WHERE kode = %s", (id,))
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stok WHERE kode = %s", (id,))
    file_data = cur.fetchone()

    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        new_file = request.files['file']

        if new_file and allowed_file(new_file.filename):
            # Hapus file lama
            if file_data and file_data[3]:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[3])
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(new_file.filename)
            new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("UPDATE stok SET kode=%s, nama=%s, harga=%s, filename=%s WHERE kode=%s", 
                        (kode, nama, harga, filename, id))
        else:
            cur.execute("UPDATE stok SET kode=%s, nama=%s, harga=%s WHERE kode=%s", 
                        (kode, nama, harga, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    
    cur.close()
    return render_template('edit.html', file=file_data)


if __name__ == '__main__':
    app.run(debug=True)
