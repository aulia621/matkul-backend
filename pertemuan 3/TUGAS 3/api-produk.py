from flask import Flask, jsonify

app = Flask(__name__)

snack_data = [
    {
        "id": 1,
        "nama": "Kentang Goreng",
        "harga": 10000
    },
    {
        "id": 2,
        "nama": "Pisang Goreng",
        "harga": 5000
    }
]

drink_data = [
    {
        "id": 1,
        "nama": "Es Teh",
        "harga": 3000
    },
    {
        "id": 2,
        "nama": "Es Milo",
        "harga": 5000
    }
]

@app.route('/')
def home():
    return jsonify({"message": "Selamat Datang di Produk UMKM"})

@app.route('/produk/snack')
def semua_snack():
    return jsonify({
        "message": "Halaman produk semua snack",
        "data": snack_data
    })

@app.route('/produk/drink')
def semua_drink():
    return jsonify({
        "message": "Halaman produk semua minuman",
        "data": drink_data
    })

@app.route('/produk/snack/<int:id>')
def snack_by_id(id):
    produk = next((item for item in snack_data if item["id"] == id), None)
    if produk:
        return jsonify({
            "message": f"Halaman produk snack dengan id = {id}",
            "data": produk
        })
    return jsonify({"error": "Snack tidak ditemukan"}), 404

@app.route('/produk/drink/<int:id>')
def drink_by_id(id):
    produk = next((item for item in drink_data if item["id"] == id), None)
    if produk:
        return jsonify({
            "message": f"Halaman produk minuman dengan id = {id}",
            "data": produk
        })
    return jsonify({"error": "Minuman tidak ditemukan"}), 404

if __name__ == '__main__':
    app.run(debug=True)
