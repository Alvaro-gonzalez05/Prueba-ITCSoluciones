from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
import requests 
import os
import jwt  # Importación de la librería para manejar JWT




app = Flask(__name__)
app.secret_key = os.urandom(24)  # Genera una clave secreta aleatoria
@app.route('/')
def index():
    # Hacer la petición GET a tu API
    response = requests.get('http://api:8000/imagenes/')
    
    # Verificar si la respuesta es exitosa
    if response.status_code == 200:
        productos = response.json()  # Convertir la respuesta a JSON
    else:
        productos = []  # Si la API falla, enviar una lista vacía
    
    return render_template('index.html', productos=productos)

@app.route('/imagen/delete', methods=['POST'])
def eliminar_producto():
    id_producto = request.form.get('id_producto')
    
    if id_producto:
        url = f'http://api:8000/imagen/delete/{id_producto}'
        response = requests.delete(url)
        
        if response.status_code == 200:
            return redirect(url_for('index'))
        else:
            return "Error al eliminar el producto", response.status_code
    else:
        return "ID de producto no proporcionado", 400

@app.route('/upload', methods=['POST'])
def upload_imagen():
    nombre_producto = request.form.get('nombre_producto')
    if 'imagen' not in request.files or not nombre_producto:
        return "No se ha proporcionado un archivo o el nombre del producto", 400

    file = request.files['imagen']
    
    if file.filename == '':
        return "No se ha seleccionado ninguna imagen", 400

    files = {'file': (file.filename, file.stream, file.content_type)}  # Archivo en formato multipart

    url = f'http://api:8000/upload/?nombre_producto={nombre_producto}'

    response = requests.post(url, files=files)

    if response.status_code == 200:
        return redirect(url_for('index'))
    else:
        return f"Error al subir la imagen: {response.status_code} - {response.text}", response.status_code
    

@app.route('/editar/<int:id_producto>', methods=['GET'])
def mostrar_formulario_editar(id_producto):
    response = requests.get(f'http://api:8000/imagen/{id_producto}')
    
    if response.status_code == 200:
        producto = response.json()
    else:
        return f"Error al obtener el producto: {response.status_code}", response.status_code
    
    return render_template('editar_producto.html', producto=producto)

@app.route('/editar/<int:id_producto>', methods=['POST'])
def guardar_cambios_producto(id_producto):
    nombre_producto = request.form.get('nombre_producto')
    
    file = request.files.get('imagen')
    files = None
    if file and file.filename != '':
        files = {'file': (file.filename, file.stream, file.content_type)}
    
    url = f'http://api:8000/productos/{id_producto}/editar'
    data = {'nombre_producto': nombre_producto}

    if files:
        response = requests.put(url, files=files, data=data)
    else:
        response = requests.put(url, data=data)

    if response.status_code == 200:
        return redirect(url_for('index'))
    else:
        return f"Error al modificar el producto: {response.status_code} - {response.text}", response.status_code


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Debes ingresar usuario y contraseña.")
            return redirect(url_for('login'))

        # Enviar los datos como query parameters
        try:
            response = requests.post('http://api:8000/login', params={'username': username, 'password': password}) # LogimDto(username, password)
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión con el servidor: {e}")
            return redirect(url_for('login'))

        # Verificar la respuesta
        if response.status_code == 200:
            data = response.json()
            session['username'] = username
            session['role'] = data.get('role')  # Guardar el rol del usuario en la sesión
            print(f"Rol guardado: {session['role']}")  # Depuración
            flash("Inicio de sesión exitoso.")
            return redirect(url_for('index'))
        elif response.status_code == 400:
            flash("Credenciales incorrectas. Inténtalo de nuevo.")
        else:
            flash(f"Error inesperado: {response.status_code} - {response.text}")
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Eliminar los datos de la sesión
    session.pop('username', None)
    session.pop('role', None)
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for('index'))  


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not username or not password or not role:
            flash("Debes completar todos los campos.")
            return redirect(url_for('register'))

        # Enviar los datos como query parameters
        try:
            response = requests.post('http://api:8000/register', params={'username': username, 'password': password, 'role': role})
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión con el servidor: {e}")
            return redirect(url_for('register'))

        # Verificar la respuesta
        if response.status_code == 200:
            flash("Usuario registrado exitosamente. Ahora puedes iniciar sesión.")
            return redirect(url_for('login'))
        elif response.status_code == 400:
            flash("El usuario ya existe.")
        else:
            flash(f"Error inesperado: {response.status_code} - {response.text}")
        return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/usuarios', methods=['GET'])
def mostrar_usuarios():
    # Verificar si el usuario es un administrador
    if session.get('role') != 'admin':
        flash("No tienes permiso para acceder a esta página.")
        return redirect(url_for('index'))

    try:
        # Hacer la petición GET a la API para obtener todos los usuarios
        response = requests.get('http://api:8000/usuarios')

        if response.status_code == 200:
            usuarios = response.json()
        else:
            flash(f"Error al obtener los usuarios: {response.status_code}")
            usuarios = []
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión con el servidor: {e}")
        usuarios = []

    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    print(f"Accediendo a la edición del usuario con ID: {id}")  # Depuración
    print(f"Método de la solicitud: {request.method}")  # Verificar si la solicitud GET o POST se ejecuta

    # Verificar si el usuario es un administrador
    if session.get('role') != 'admin':
        flash("No tienes permiso para acceder a esta página.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Recoger los datos del formulario
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        # Enviar los datos al API como query parameters
        try:
            response = requests.put(f'http://api:8000/usuarios/{id}/editar', params={
                'username': username,
                'password': password,
                'role': role
            })

            if response.status_code == 200:
                flash("Usuario actualizado correctamente.")
                return redirect(url_for('mostrar_usuarios'))
            else:
                flash(f"Error al actualizar el usuario: {response.status_code}")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión con el servidor: {e}")
        
        return redirect(url_for('editar_usuario', id=id))

    # Obtener los datos actuales del usuario
    try:
        response = requests.get(f'http://api:8000/usuarios/{id}')
        if response.status_code == 200:
            usuario = response.json()
        else:
            flash(f"Error al obtener los datos del usuario: {response.status_code}")
            return redirect(url_for('mostrar_usuarios'))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión con el servidor: {e}")
        return redirect(url_for('mostrar_usuarios'))

    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuarios/eliminar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    # Verificar si el usuario es un administrador
    if session.get('role') != 'admin':
        flash("No tienes permiso para eliminar usuarios.")
        return redirect(url_for('index'))

    # Enviar solicitud para eliminar al usuario en la API
    try:
        response = requests.delete(f'http://api:8000/usuarios/{id}/eliminar')

        if response.status_code == 200:
            flash("Usuario eliminado correctamente.")
        else:
            flash(f"Error al eliminar el usuario: {response.status_code}")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión con el servidor: {e}")
    
    return redirect(url_for('mostrar_usuarios'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
