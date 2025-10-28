from flask import Flask,render_template,request,redirect,url_for
from flask_mysqldb import MySQL

app= Flask(__name__)
app.secret_key = 'secret123'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'aulia'
app.config['MYSQL_DB'] = 'crud_db'

mysql= MySQL(app)

@app.route('/')
def index():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM stok")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', dtstok=data)

@app.route('/add',methods=['GET','POST'])
def add():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO stok (kode,nama,harga) VALUES (%s,%s,%s)", (kode,nama,harga))
        mysql.connection.commit()

        return redirect(url_for('index'))
    
    return render_template('add.html')

@app.route('/edit/<id>', methods=['GET','POST'])
def edit(id):
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']

        cur.execute("UPDATE stok SET kode=%s, nama=%s, harga=%s WHERE kode=%s",(kode,nama,harga, id))
        mysql.connection.commit()
        return redirect(url_for('index'))
    else:
        cur.execute("SELECT * FROM stok WHERE kode=%s",[id])
        data = cur.fetchone()
        return render_template('edit.html',dtstok=data)


@app.route('/delete/<id>',methods=['GET'])
def delete(id):
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM stok WHERE kode=%s",[id])
    mysql.connection.commit()
    return redirect(url_for('index'))

if __name__=='__main__':
    app.run(debug=True)

