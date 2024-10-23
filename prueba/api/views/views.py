from fastapi import APIRouter
from controllers.controllers import handle_image_upload, get_product_details, delete_image, get_all_images, update_product,register_user,login_user,get_all_users,get_user_by_id, update_user,delete_user

from typing import Union



from fastapi import  UploadFile, File, Form


router = APIRouter()

#Permite subir una imagen desde el selector de medios y convertirla en base64
@router.post("/upload/", summary="Subir una Imagen", description="Subir una imagen desde el selector de medios y convertirla en base64")
async def upload_image(nombre_producto: str, file: UploadFile = File(...)):
    return await handle_image_upload(nombre_producto, file)

#Permite Obtener detalles del producto con ID
@router.get("/imagen/{id_producto}", summary="Obtener detalles del producto con ID", description="Obtiene el nombre y la imagen de un producto por su ID")
async def obtener_imagen(id_producto: int):
    return await get_product_details(id_producto)

#Permite Borrar una Imagen con ID
@router.delete("/imagen/delete/{id_producto}", summary="Borrar una Imagen con ID", description="Elimina elementos de la base de datos con el ID correspondiente y si la tabla queda vacía, restablece el AUTOINCREMENT")
async def eliminar_imagen(id_producto: int):
    return await delete_image(id_producto)

#Permite Obtener todas las imágenes
@router.get("/imagenes/", summary="Obtener todas las imágenes", description="Obtiene todas las imágenes almacenadas en la base de datos")
async def obtener_imagenes():
    return await get_all_images()

#Permite editar un producto
@router.put("/productos/{id_producto}/editar", summary="Editar un producto")
async def editar_producto(id_producto: int, nombre_producto: str = Form(...), file: Union[UploadFile, None] = None):
    return await update_product(id_producto, nombre_producto, file)

#Permite Registrar un nuevo usuario y validarlo
@router.post("/register", summary="Registrar un nuevo usuario")
async def register(username: str, password: str, role: str):
    return await register_user(username, password, role)

#Permite Validar los usuarios de la base de datos y iniciar sesion
@router.post("/login", summary="Iniciar sesión")
async def login(username: str, password: str):
    return await login_user(username, password)

#Permite tener todos los usuarios
@router.get("/usuarios", summary="Obtener todos los usuarios")
async def obtener_usuarios():
    return await get_all_users()

#Permite obetener usuarios por id
@router.get("/usuarios/{id}", summary="Obtener un usuario por ID")
async def obtener_usuario(id: int):
    return await get_user_by_id(id)

#Permite editar usuarios en base al id
@router.put("/usuarios/{id}/editar", summary="Editar un usuario")
async def editar_usuario(id: int, username: str, password: str, role: str):
    return await update_user(id, username, password, role)

#Permite eliminar usuarios en base al id
@router.delete("/usuarios/{id}/eliminar", summary="Eliminar un usuario")
async def eliminar_usuario(id: int):
    return await delete_user(id)
