from fastapi import FastAPI
from app.config import settings
from app.database import connect_to_mongo
from app.routes import tipos_torneo
from app.routes import torneos  
from app.routes import equipos
from app.routes import jugadores
from app.routes import partidos
from app.routes import eventos
from app.routes import tipos_evento
from app.routes import pipelines
from app.routes import auth  

app = FastAPI(title="FutPlay API", version="1.0")

@app.on_event("startup")
async def startup_db():
    await connect_to_mongo()
    print("✅ Conexión establecida con MongoDB y servidor iniciado.")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Incluir rutas
app.include_router(tipos_torneo.router, prefix="/api/tipos-torneo", tags=["Tipos de Torneo"])
app.include_router(torneos.router, prefix="/api/torneos", tags=["Torneos"])  
app.include_router(equipos.router, prefix="/api/equipos", tags=["Equipos"])
app.include_router(jugadores.router, prefix="/api/jugadores", tags=["Jugadores"])
app.include_router(partidos.router, prefix="/api/partidos", tags=["Partidos"])
app.include_router(eventos.router, prefix="/api/eventos", tags=["Eventos"])
app.include_router(tipos_evento.router, prefix="/api/tipos-evento", tags=["Tipos de Evento"])
app.include_router(pipelines.router, prefix="/api", tags=["Pipelines"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de FutPlay"}
