from flask import Flask, render_template,request,redirect,url_for,flash
from flask import send_from_directory
import mysql.connector
from datetime import datetime
import os


app = Flask(__name__)
app.secret_key='samuel'

# Configuración de la base de datos
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'control'
app.config['MYSQL_HOST'] = 'localhost'

# Inicializar la conexión a la base de datos
mysql = mysql.connector.connect(
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB'],
    host=app.config['MYSQL_HOST']
) 

CARPETA= os.path.join('uploads')
app.config['CARPETA']= CARPETA


@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)


@app.route("/")
def index():
    
        # Ejecutar la consulta SQL
        sql = "SELECT * FROM personal;"
        cursor = mysql.cursor()
        cursor.execute(sql)
       
        personal=cursor.fetchall()
        print(personal)
        
        mysql.commit()
        return render_template('empleados/index.html',personal=personal)



@app.route('/destroy/<int:id>')
def destroy(id):
      cursor = mysql.cursor()

      cursor.execute("SELECT foto FROM personal WHERE id=%s", (id,))
      fila = cursor.fetchall()
      os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) 

      cursor.execute('DELETE FROM personal WHERE id=%s',(id,))
      mysql.commit()
      return redirect('/')

        
@app.route('/edit/<int:id>')
def edit(id):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM personal WHERE id=%s",(id,))
    personal=cursor.fetchall()
    print(personal)
    mysql.commit()
    
    return render_template('empleados/edit.html',personal=personal)

@app.route('/update', methods=['POST'])
def update():
  
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtID']

    sql = "UPDATE personal SET nombre=%s, correo=%s WHERE id=%s;"

    datos=(_nombre,_correo,id)

    
    cursor = mysql.cursor()

    now = datetime.now()
    tiempo = now.strftime('%Y%H%M%S')
    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

        cursor.execute("SELECT foto FROM personal WHERE id=%s", (id,))
        fila = cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute('UPDATE personal SET foto=%s WHERE id=%s', (nuevoNombreFoto, id))
        mysql.commit()

    cursor.execute(sql, datos)
    mysql.commit()

    return redirect('/')



@app.route('/create')
def create():
    return render_template('empleados/create.html')


@app.route('/store', methods=['POST'])
def storage():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']

    if _nombre =='' or _correo ==''or _foto=='':
         flash('Recuerda llenar los datos de los campos')
         return redirect(url_for('create'))
     
    now= datetime.now()
    tiempo=now.strftime('%Y%H%M%S')

    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "INSERT INTO `personal` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s,%s,%s);"

    datos=(_nombre,_correo,nuevoNombreFoto)

    cursor = mysql.cursor()
    cursor.execute(sql,datos)
    mysql.commit()
    return redirect ('/')
 

    


if __name__ == '__main__':
    app.run(debug=True)
