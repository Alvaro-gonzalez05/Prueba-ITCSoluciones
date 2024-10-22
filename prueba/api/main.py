import pymysql
import base64
from tkinter import Tk, filedialog, messagebox,Label
from PIL import Image, ImageTk, UnidentifiedImageError
import io
import tkinter as tk
from typing import Union
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
import os


# Obtener una variable de entorno
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_database= os.getenv('DB_NAME')

#  Cargar las variables de entorno
app= FastAPI()




connection = pymysql.connect(
    host =db_host,  
    user=db_user,
    password=db_password, 
    database=db_database,

)

def conexion():
    try:
        # Primera conexión para crear la base de datos
        miconexion = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_database)
        micursor = miconexion.cursor()

        # Crear la base de datos si no existe
        micursor.execute("CREATE DATABASE IF NOT EXISTS prueba")
        print("DB CONECTED.......")

        micursor.close()  # Cerrar el cursor antes de cerrar la conexión
        miconexion.close()

        # Segunda conexión para crear la tabla en la base de datos "prueba"
        miconexion = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_database)
        micursor = miconexion.cursor()

        # Crear la tabla si no existe (corrigiendo el error en la sintaxis)
        micursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_product INT(11) AUTO_INCREMENT PRIMARY KEY, 
                imagen_64 LONGTEXT NOT NULL, 
                nombre_producto VARCHAR(30) NOT NULL
            )
        """)

        

        micursor.close()  # Cerrar el cursor antes de cerrar la conexión
        miconexion.close()

        miconexion = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_database)
        micursor = miconexion.cursor()

        # variable CREAR TABLA USUARIO = 
        micursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT(11) AUTO_INCREMENT PRIMARY KEY, 
                password VARCHAR(255) NOT NULL,
                username VARCHAR(30) NOT NULL,  
                role VARCHAR(30) NOT NULL
            )
        """)

        print("Tablas creadas con exito...")

        micursor.close()  # Cerrar el cursor antes de cerrar la conexión
        miconexion.close()

    except pymysql.MySQLError as e:
        # Capturar errores específicos de MySQL
        messagebox.showwarning("ERROR", f"Error de MySQL: {e}")
    except Exception as e:
        # Capturar cualquier otro error y mostrar el mensaje
        messagebox.showwarning("ERROR", f"Error inesperado: {e}")

conexion()


@app.post("/upload/", summary="Subir una Imagen", description="Subir una imagen desde el selector de medios y las convierte en base64")
async def upload_image(nombre_producto: str, file: UploadFile = File(...)):
    try:
        # Leer la imagen en binario
        imagen_bytes = await file.read()

        # Codificar la imagen en base64
        imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')

      

        # Verificar si la imagen ya existe en la base de datos
        with connection.cursor() as cursor:
            query_check = "SELECT COUNT(*) FROM productos WHERE imagen_64 = %s"
            cursor.execute(query_check, (imagen_base64,))
            resultado = cursor.fetchone()

        if resultado[0] > 0:
            # Si la imagen ya existe
            print("Esta imagen ya se encuentra en la base de datos.")
            
            return {"message": "Imagen ya existe en la base de datos."}
        else:
            # Si la imagen no existe, proceder a insertarla
            with connection.cursor() as cursor:
                query_insert = "INSERT INTO productos (nombre_producto, imagen_64) VALUES (%s, %s)"
                cursor.execute(query_insert, (nombre_producto, imagen_base64))
                connection.commit()

            

            print("La imagen fue insertada con éxito.")
            return {"message": f"Imagen '{nombre_producto}' insertada correctamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")


@app.get("/imagen/{id_producto}", summary="Obtener detalles del producto con ID", description="Obtiene el nombre y la imagen de un producto por su ID")
async def obtener_imagen(id_producto: int):
    try:
        with connection.cursor() as cursor:
            query = "SELECT id_product, nombre_producto, imagen_64 FROM productos WHERE id_product = %s"
            cursor.execute(query, (id_producto,))
            resultado = cursor.fetchone()

        if resultado:
            # Retornar los datos del producto: ID, nombre y imagen en base64
            return {
                "id_product": resultado[0],
                "nombre_producto": resultado[1],
                "imagen_64": resultado[2]
            }
        else:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el producto: {str(e)}")


    

@app.delete("/imagen/delete/{id_producto}", summary="Borrar una Imagen con ID", description="Elimina elementos de la base de datos con el ID correspondiente y en caso de que la tabla quede vacia reanuda el AUTOINCREMENT de los id empezando por 1")
async def eliminar_imagen(id_producto: int):
    try:

        with connection.cursor() as cursor:
            query_check = "SELECT COUNT(*) FROM productos WHERE id_product = %s"
            cursor.execute(query_check, (id_producto,))
            resultado = cursor.fetchone()

        if resultado[0] == 0:
           
            
            raise HTTPException(status_code=404, detail="Imagen no encontrada.")

 
        with connection.cursor() as cursor:
            query_delete = "DELETE FROM productos WHERE id_product = %s"
            cursor.execute(query_delete, (id_producto,))
            connection.commit()

       
        with connection.cursor() as cursor:
            query_count = "SELECT COUNT(*) FROM productos"
            cursor.execute(query_count)
            count_result = cursor.fetchone()

        if count_result[0] == 0:
            
            with connection.cursor() as cursor:
                query_reset = "ALTER TABLE productos AUTO_INCREMENT = 1"
                cursor.execute(query_reset)
                connection.commit()

            print("AUTO_INCREMENT restablecido a 1 porque la tabla está vacía.")

        print(f"La imagen con ID {id_producto} fue eliminada con éxito.")
        return {"message": f"Imagen con ID {id_producto} eliminada correctamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar la imagen: {str(e)}")

@app.get("/imagenes/")
async def obtener_imagenes():
    
    with connection.cursor() as cursor:
        query = "SELECT id_product, nombre_producto, imagen_64 FROM productos"
        cursor.execute(query)
        imagenes = cursor.fetchall()  
        
        return [{"id": img[0], "nombre_producto": img[1], "imagen_64": img[2]} for img in imagenes]


@app.put("/productos/{id_producto}/editar", summary="Editar un producto")
async def editar_producto(id_producto: int, nombre_producto: str = Form(...), file: Union[UploadFile, None] = None):
    try:
        with connection.cursor() as cursor:
            query_check = "SELECT COUNT(*) FROM productos WHERE id_product = %s"
            cursor.execute(query_check, (id_producto,))
            resultado = cursor.fetchone()

        if resultado[0] == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        if file:
            imagen_bytes = await file.read()
            imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
        else:
            imagen_base64 = None

     
        with connection.cursor() as cursor:
            if imagen_base64:
                query_update = "UPDATE productos SET nombre_producto = %s, imagen_64 = %s WHERE id_product = %s"
                cursor.execute(query_update, (nombre_producto, imagen_base64, id_producto))
            else:
                query_update = "UPDATE productos SET nombre_producto = %s WHERE id_product = %s"
                cursor.execute(query_update, (nombre_producto, id_producto))
            
            connection.commit()

        return {"message": f"Producto con ID {id_producto} actualizado correctamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al modificar el producto: {str(e)}")



@app.post("/register")
async def register(username: str, password: str, role:str):
    try:
        with connection.cursor() as cursor:
            # Verificar si el usuario ya existe
            cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result:
                raise HTTPException(status_code=400, detail="El usuario ya existe")

            # Registrar el nuevo usuario
            cursor.execute("INSERT INTO usuarios (username, password,role) VALUES (%s, %s, %s)", (username, password,role))
            connection.commit()
            return {"message": "Usuario registrado exitosamente"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(username: str, password: str):
    try:
        with connection.cursor() as cursor:
            # Verificar si el usuario y contraseña son correctos
            cursor.execute("SELECT username, role FROM usuarios WHERE username = %s AND password = %s", (username, password))
            result = cursor.fetchone()
            if result:
                # Devuelve el rol junto con el nombre de usuario
                return {"username": result[0], "role": result[1]}
            else:
                raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    

@app.get("/usuarios", summary="Obtener todos los usuarios")
async def obtener_usuarios():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, role, password FROM usuarios")
            usuarios = cursor.fetchall()
            return [{"id": u[0], "username": u[1], "role": u[2], "password": u[3]} for u in usuarios]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/usuarios/{id}", summary="Obtener un usuario por ID")
async def obtener_usuario(id: int):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, role, password FROM usuarios WHERE id = %s", (id,))
            usuario = cursor.fetchone()
            if usuario:
                return {
                    "id": usuario[0],
                    "username": usuario[1],
                    "role": usuario[2],
                    "password": usuario[3]
                }
            else:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.put("/usuarios/{id}/editar")
async def editar_usuario(id: int, username: str, password: str, role: str):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE usuarios SET username = %s, password = %s, role = %s WHERE id = %s
            """, (username, password, role, id))
            connection.commit()

        return {"message": "Usuario actualizado correctamente"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))
