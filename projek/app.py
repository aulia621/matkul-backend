from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import pymysql
import os, math
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'aulia28'

# Koneksi Database
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='aulia28',
    database='restoran_db',
    port=3307,
    cursorclass=pymysql.cursors.Cursor
)

# Konfigurasi Folder Upload
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = ('png', 'jpg', 'jpeg')

# Buat folder UPLOAD kalau belum ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Cek file ekstensi
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# INDEX (READ + SEARCH + PAGINATION)
@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    cur = conn.cursor()

    if search_query:
        cur.execute("""
            SELECT COUNT(*) FROM makanan 
            WHERE kode_makanan LIKE %s OR nama_makanan LIKE %s OR kategori LIKE %s
        """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
    else:
        cur.execute("SELECT COUNT(*) FROM makanan")

    total_rows = cur.fetchone()[0]
    total_pages = math.ceil(total_rows / per_page)

    if search_query:
        cur.execute("""
            SELECT * FROM makanan 
            WHERE kode_makanan LIKE %s OR nama_makanan LIKE %s OR kategori LIKE %s
            LIMIT %s OFFSET %s
        """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", per_page, offset))
    else:
        cur.execute("SELECT * FROM makanan LIMIT %s OFFSET %s", (per_page, offset))

    data = cur.fetchall()
    cur.close()
    
    return render_template('index.html', files=data, search_query=search_query, page=page, total_pages=total_pages)


# TAMPIL GAMBAR
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# TAMBAH DATA
@app.route('/add', methods=['GET', 'POST'])
def add_file():
    if request.method == 'POST':
        kode_makanan = request.form['kode_makanan']
        nama_makanan = request.form['nama_makanan']
        kategori = request.form['kategori']
        harga = request.form['harga']
        stok = request.form['stok']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cur = conn.cursor()
            cur.execute("INSERT INTO makanan (kode_makanan, nama_makanan, kategori, harga, stok, filename) VALUES (%s, %s, %s, %s, %s, %s)",
                        (kode_makanan, nama_makanan, kategori, harga, stok, filename))
            conn.commit()
            cur.close()

            flash('Data makanan berhasil ditambahkan!', 'success')
            return redirect(url_for('index'))

        flash('Format file tidak valid! Gunakan png, jpg, jpeg.', 'warning')

    return render_template('add.html')


# HAPUS DATA
@app.route('/delete/<id>', methods=['GET'])
def delete_file(id):
    cur = conn.cursor()
    cur.execute("SELECT filename FROM makanan WHERE kode_makanan = %s", (id,))
    file_data = cur.fetchone()

    if file_data:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[0])
        if os.path.exists(file_path):
            os.remove(file_path)

        cur.execute("DELETE FROM makanan WHERE kode_makanan = %s", (id,))
        conn.commit()
        flash('Data makanan berhasil dihapus!', 'success')

    cur.close()
    return redirect(url_for('index'))


# EDIT DATA
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_file(id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM makanan WHERE kode_makanan = %s", (id,))
    file_data = cur.fetchone()

    if not file_data:
        flash('Data tidak ditemukan!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        kode_makanan = request.form['kode_makanan']
        nama_makanan = request.form['nama_makanan']
        kategori = request.form['kategori']
        harga = request.form['harga']
        stok = request.form['stok']
        new_file = request.files.get('file')

        if new_file and new_file.filename != '' and allowed_file(new_file.filename):
            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[5])
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

            filename = secure_filename(new_file.filename)
            new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cur.execute("""
                UPDATE makanan SET kode_makanan=%s, nama_makanan=%s, kategori=%s, harga=%s, stok=%s, filename=%s 
                WHERE kode_makanan=%s
            """, (kode_makanan, nama_makanan, kategori, harga, stok, filename, id))
        else:
            cur.execute("""
                UPDATE makanan SET kode_makanan=%s, nama_makanan=%s, kategori=%s, harga=%s, stok=%s 
                WHERE kode_makanan=%s
            """, (kode_makanan, nama_makanan, kategori, harga, stok, id))

        conn.commit()
        cur.close()
        flash('Data makanan berhasil diperbarui!', 'success')
        return redirect(url_for('index'))

    cur.close()
    return render_template('edit.html', file=file_data)


if __name__ == '__main__':
    app.run(debug=True)
