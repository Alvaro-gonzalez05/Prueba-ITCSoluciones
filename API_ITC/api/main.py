from fastapi import FastAPI
from views.views import router as views_router
from models.models import conexion

app = FastAPI()

# INCLUYE LAS RUTAS DEFINIDAS EN VIEWS
app.include_router(views_router)


if __name__ == "__main__":
    conexion()  
