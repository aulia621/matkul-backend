from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename
import time

# =====================================
# KONFIGURASI APLIKASI
# =====================================
app = Flask(__name__)
app.secret_key = 'kulinerku-secret-key-2024-change-this'
Bootstrap(app)

# Konfigurasi Upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB

# Buat folder upload jika belum ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =====================================
# KONEKSI DATABASE MONGODB
# =====================================
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.server_info()  # Test koneksi
    db = client["crud_makanan"]
    collection = db["items"]
    print("✓ Koneksi MongoDB berhasil!")
except Exception as e:
    print(f"✗ Error koneksi MongoDB: {e}")
    exit(1)

# =====================================
# HELPER FUNCTIONS
# =====================================
def allowed_file(filename):
    """Cek apakah file memiliki ekstensi yang diizinkan"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_file(filename):
    """Hapus file foto dari folder uploads"""
    if filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Error menghapus file: {e}")
                return False
    return False

# =====================================
# ROUTES
# =====================================

@app.route('/')
def index():
    """Halaman utama dengan daftar menu, search, dan pagination"""
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 5
    skip = (page - 1) * per_page

    # Query untuk search
    query = {}
    if search:
        query = {
            "$or": [
                {"kode": {"$regex": search, "$options": "i"}},
                {"nama makanan": {"$regex": search, "$options": "i"}},
                {"kategori": {"$regex": search, "$options": "i"}}
            ]
        }

    # Hitung total items dan pages
    total_items = collection.count_documents(query)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Ambil data dengan pagination
    items = collection.find(query).skip(skip).limit(per_page)

    return render_template(
        'index.html',
        items=items,
        page=page,
        total_pages=total_pages,
        search=search,
        total_items=total_items
    )


@app.route('/add', methods=['GET', 'POST'])
def add():
    """Tambah menu baru"""
    if request.method == 'POST':
        try:
            # Ambil data dari form
            kode = request.form.get('kode', '').strip().upper()
            nama_makanan = request.form.get('nama_makanan', '').strip()
            kategori = request.form.get('kategori', '').strip()
            harga = request.form.get('harga', '').strip()
            jumlah = int(request.form.get('jumlah', 0))
            deskripsi = request.form.get('deskripsi', '').strip()
            bahan = request.form.get('bahan', '').strip()
            tersedia = request.form.get('tersedia') == 'true'
            
            # Validasi field wajib
            if not all([kode, nama_makanan, kategori, harga]):
                flash('Semua field wajib harus diisi!', 'danger')
                return render_template('add.html')
            
            # Cek duplikasi kode produk
            existing = collection.find_one({'kode': kode})
            if existing:
                flash(f'Kode produk "{kode}" sudah digunakan! Gunakan kode lain.', 'danger')
                return render_template('add.html')
            
            # Process bahan (split by comma)
            bahan_list = [b.strip() for b in bahan.split(',') if b.strip()]
            
            # Data yang akan disimpan
            data = {
                "kode": kode,
                "nama makanan": nama_makanan,
                "kategori": kategori,
                "harga": harga,
                "jumlah": jumlah,
                "deskripsi": deskripsi,
                "bahan": bahan_list,
                "tersedia": tersedia,
                "foto": None
            }

            # Handle file upload dengan error handling
            if 'foto' in request.files:
                file = request.files['foto']
                print(f"File diterima: {file.filename}")  # Debug
                
                if file and file.filename != '':
                    if allowed_file(file.filename):
                        try:
                            # Pastikan folder uploads ada
                            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                                os.makedirs(app.config['UPLOAD_FOLDER'])
                                print(f"Folder {app.config['UPLOAD_FOLDER']} dibuat")
                            
                            filename = secure_filename(file.filename)
                            # Tambahkan timestamp untuk menghindari duplikat
                            filename = f"{int(time.time())}_{filename}"
                            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            
                            # Save file
                            file.save(filepath)
                            print(f"File disimpan di: {filepath}")
                            
                            # Cek apakah file benar-benar tersimpan
                            if os.path.exists(filepath):
                                data['foto'] = filename
                                print(f"✓ File berhasil disimpan: {filename}")
                            else:
                                print("✗ File gagal disimpan")
                                flash('Gagal menyimpan foto', 'warning')
                        
                        except Exception as e:
                            print(f"Error saat upload: {str(e)}")
                            flash(f'Error upload foto: {str(e)}', 'warning')
                    else:
                        flash('Format file tidak diizinkan! Gunakan: PNG, JPG, JPEG, GIF', 'warning')

            # Insert ke database
            result = collection.insert_one(data)
            print(f"Data disimpan dengan foto: {data.get('foto')}")
            
            flash(f'Menu "{nama_makanan}" berhasil ditambahkan!', 'success')
            return redirect(url_for('detail', id=result.inserted_id))
        
        except Exception as e:
            print(f"Error di route add: {str(e)}")
            flash(f'Error: {str(e)}', 'danger')
            return render_template('add.html')

    return render_template('add.html')


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    """Edit menu yang sudah ada"""
    try:
        item = collection.find_one({'_id': ObjectId(id)})
        
        if not item:
            flash('Menu tidak ditemukan!', 'danger')
            return redirect(url_for('index'))

        if request.method == 'POST':
            try:
                # Ambil data dari form (kode tidak bisa diubah)
                kode = item['kode']  # Gunakan kode lama
                nama_makanan = request.form.get('nama_makanan', '').strip()
                kategori = request.form.get('kategori', '').strip()
                harga = request.form.get('harga', '').strip()
                jumlah = int(request.form.get('jumlah', 0))
                deskripsi = request.form.get('deskripsi', '').strip()
                bahan = request.form.get('bahan', '').strip()
                tersedia = request.form.get('tersedia') == 'true'
                
                # Validasi field wajib
                if not all([nama_makanan, kategori, harga]):
                    flash('Semua field wajib harus diisi!', 'danger')
                    return render_template('edit.html', item=item)
                
                # Process bahan (split by comma)
                bahan_list = [b.strip() for b in bahan.split(',') if b.strip()]
                
                # Data yang akan diupdate
                update_data = {
                    'kode': kode,
                    'nama makanan': nama_makanan,
                    'kategori': kategori,
                    'harga': harga,
                    'jumlah': jumlah,
                    'deskripsi': deskripsi,
                    'bahan': bahan_list,
                    'tersedia': tersedia
                }

                # Handle file upload
                foto_lama = item.get('foto')
                file = request.files.get('foto')
                
                if file and file.filename != '' and allowed_file(file.filename):
                    # Hapus foto lama
                    if foto_lama:
                        delete_file(foto_lama)
                    
                    # Simpan foto baru
                    filename = secure_filename(file.filename)
                    filename = f"{int(time.time())}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    update_data['foto'] = filename
                else:
                    # Tetap gunakan foto lama
                    if foto_lama:
                        update_data['foto'] = foto_lama

                # Update ke database
                collection.update_one(
                    {'_id': ObjectId(id)},
                    {'$set': update_data}
                )

                flash(f'Menu "{nama_makanan}" berhasil diupdate!', 'success')
                return redirect(url_for('detail', id=id))
            
            except Exception as e:
                flash(f'Error saat update: {str(e)}', 'danger')
                return render_template('edit.html', item=item)

        return render_template('edit.html', item=item)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))


@app.route('/detail/<id>')
def detail(id):
    """Halaman detail menu"""
    try:
        item = collection.find_one({'_id': ObjectId(id)})
        if item:
            return render_template('detail.html', item=item)
        else:
            flash('Menu tidak ditemukan!', 'danger')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))


@app.route('/delete/<id>')
def delete(id):
    """Hapus menu"""
    try:
        item = collection.find_one({'_id': ObjectId(id)})
        
        if item:
            nama = item.get('nama makanan', 'Menu')
            
            # Hapus file foto jika ada
            if item.get('foto'):
                delete_file(item['foto'])
            
            # Hapus data dari database
            collection.delete_one({'_id': ObjectId(id)})
            flash(f'Menu "{nama}" berhasil dihapus!', 'success')
        else:
            flash('Menu tidak ditemukan!', 'danger')
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('index'))


# =====================================
# API ENDPOINTS (Optional - untuk AJAX)
# =====================================

@app.route('/api/check-kode/<kode>')
def check_kode(kode):
    """API untuk cek apakah kode sudah digunakan"""
    existing = collection.find_one({'kode': kode.upper()})
    return {'exists': existing is not None}


@app.route('/api/stats')
def stats():
    """API untuk statistik menu"""
    total = collection.count_documents({})
    tersedia = collection.count_documents({'tersedia': True})
    
    # Group by kategori
    pipeline = [
        {
            '$group': {
                '_id': '$kategori',
                'count': {'$sum': 1}
            }
        }
    ]
    kategori_stats = list(collection.aggregate(pipeline))
    
    return {
        'total': total,
        'tersedia': tersedia,
        'tidak_tersedia': total - tersedia,
        'kategori': kategori_stats
    }


# =====================================
# ERROR HANDLERS
# =====================================

@app.errorhandler(404)
def page_not_found(e):
    """Handler untuk error 404"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handler untuk error 500"""
    return render_template('500.html'), 500


@app.errorhandler(413)
def file_too_large(e):
    """Handler untuk file yang terlalu besar"""
    flash('File terlalu besar! Maksimal 16MB', 'danger')
    return redirect(request.url)


# =====================================
# UTILITY FUNCTIONS (untuk maintenance)
# =====================================

def migrate_nama_field():
    """
    Fungsi untuk migrasi field 'nama_makanan' ke 'nama makanan'
    Jalankan sekali jika ada inkonsistensi nama field
    """
    items = collection.find({"nama_makanan": {"$exists": True}})
    count = 0
    for item in items:
        collection.update_one(
            {"_id": item["_id"]},
            {
                "$set": {"nama makanan": item["nama_makanan"]},
                "$unset": {"nama_makanan": ""}
            }
        )
        count += 1
    print(f"Migrasi selesai! {count} dokumen diupdate.")
    return count


def create_indexes():
    """Buat index untuk performa yang lebih baik"""
    collection.create_index('kode', unique=True)
    collection.create_index('nama makanan')
    collection.create_index('kategori')
    collection.create_index('tersedia')
    print("✓ Indexes berhasil dibuat!")


def seed_data():
    """Isi database dengan data contoh"""
    sample_data = [
        {
            "kode": "MKN001",
            "nama makanan": "Nasi Goreng Spesial",
            "kategori": "Makanan Utama",
            "harga": "Rp 25.000",
            "jumlah": 50,
            "deskripsi": "Nasi goreng dengan telur, ayam, dan sayuran segar. Dilengkapi dengan kerupuk dan acar.",
            "bahan": ["Nasi", "Telur", "Ayam", "Bawang merah", "Bawang putih", "Kecap manis", "Sayuran"],
            "tersedia": True,
            "foto": None
        },
        {
            "kode": "MNM001",
            "nama makanan": "Es Teh Manis",
            "kategori": "Minuman",
            "harga": "Rp 5.000",
            "jumlah": 100,
            "deskripsi": "Es teh manis segar, cocok untuk menemani makanan.",
            "bahan": ["Teh", "Gula", "Es batu"],
            "tersedia": True,
            "foto": None
        }
    ]
    
    try:
        collection.insert_many(sample_data)
        print(f"✓ {len(sample_data)} data contoh berhasil ditambahkan!")
    except Exception as e:
        print(f"✗ Error: {e}")


# =====================================
# MAIN
# =====================================

if __name__ == '__main__':
    # Uncomment untuk membuat indexes (jalankan sekali)
    # create_indexes()
    
    # Uncomment untuk mengisi data contoh (jalankan sekali)
    # seed_data()
    
    print("="*50)
    print("🍽️  KULINERKU - Aplikasi CRUD Menu Makanan")
    print("="*50)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🗄️  Database: {db.name}")
    print(f"📊 Collection: {collection.name}")
    print(f"📦 Total menu: {collection.count_documents({})}")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)