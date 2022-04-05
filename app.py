from flask import Flask 
from flask import render_template,request,redirect,url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory 

from datetime import datetime
import os


app= Flask(__name__)
app.secret_key="Develoteca"

mysql= MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistema'
mysql.init_app(app)

CARPETA= os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/')
def index():

    sql ="SELECT * FROM `estudiantes`;"
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)

    estudiantes=cursor.fetchall()
    print(estudiantes)

    conn.commit()
    return render_template('estudiantes/index.html', estudiantes=estudiantes)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn= mysql.connect()
    cursor=conn.cursor()

    cursor.execute("SELECT foto FROM estudiantes WHERE id=%s", id)
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    cursor.execute("DELETE FROM estudiantes WHERE id=%s",(id))
    conn.commit()
    return redirect('/')
      
@app.route('/edit/<int:id>')
def edit(id):

    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM estudiantes WHERE id=%s", (id))
    estudiantes=cursor.fetchall()
    conn.commit()
    print(estudiantes)
    return render_template('estudiantes/edit.html',estudiantes=estudiantes)

@app.route('/update', methods=['POST'])
def update():
    
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    _faltas=request.form['txtFaltas']
    id=request.form['txtID']

    sql ="UPDATE estudiantes SET nombre=%s, correo=%s, faltas=%s WHERE id=%s ;"

    datos=(_nombre,_correo,_faltas,id,)

    conn= mysql.connect()
    cursor=conn.cursor()

    now= datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if _foto.filename!='':

        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
        
        cursor.execute("SELECT foto FROM estudiantes WHERE id=%s", id)
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE estudiantes SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()

    
    return redirect('/')


@app.route('/create')
def create():
    return render_template('estudiantes/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']

    if _nombre=='' or _correo =='' or _foto=='':
        flash('Todos los campos deben estar llenos')
        return redirect(url_for('create'))

    now= datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    _faltas=request.form['txtFaltas']



    sql ="INSERT INTO `estudiantes` (`id`, `Nombre`, `Correo`, `Foto`, `Faltas`) VALUES (NULL,%s,%s,%s,%s);"
    
    datos=(_nombre,_correo,nuevoNombreFoto,_faltas)

    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')

    
if __name__== '__main__':
    app.run(debug=True)
    