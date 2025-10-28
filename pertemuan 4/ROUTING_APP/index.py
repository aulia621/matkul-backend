from flask import Flask, render_template, request 
app= Flask(__name__) 
@app.route('/') 
def index(): return render_template('index.html') 
@app.route('/about') 
def about(): return render_template('about.html') @app.route('/form',
methods=['GET','POST']) 
def form(): 
    if request.method == 'POST': nama = request.form['nama'] 
    alamat = request.form['alamat'] 
    return f"halo,{nama} dan {alamat} Fore berhasil dikirim." 
    return render_template('form.html') 
if __name__=='__main__': app.run(debug=True)
