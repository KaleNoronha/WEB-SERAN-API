from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.database import get_db, engine, Base
from app.models import usuario_model, paciente_model, pregunta_model, evaluacion_model, recomendacion_model, invitacion_model
from app.routes import auth_routes, paciente_routes, pregunta_routes, evaluacion_routes, recomendacion_routes, invitacion_routes, usuario_routes
from app.routes import config_recomendacion_routes


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema Experto para Detección de Riesgo de Anemia",
    description="Backend con FastAPI, JWT y motor de reglas",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://web-seran-front-fix.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_routes.router,
    prefix="/api/auth",
    tags=["Autenticación"]
)

app.include_router(
    paciente_routes.router,
    prefix="/api/pacientes",
    tags=["Pacientes"]
)

app.include_router(
    pregunta_routes.router,
    prefix="/api/preguntas",
    tags=["Preguntas"]
)

app.include_router(
    evaluacion_routes.router,
    prefix="/api/evaluaciones",
    tags=["Evaluaciones"]
)

app.include_router(
    recomendacion_routes.router,
    prefix="/api/recomendaciones",
    tags=["Recomendaciones"]
)

app.include_router(
    invitacion_routes.router,
    prefix="/api/invitaciones",
    tags=["Invitaciones"]
)

app.include_router(
    config_recomendacion_routes.router)

@app.get("/")
def root():
    return {
        "mensaje": "Backend del sistema experto funcionando correctamente"
    }


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    resultado = db.execute(text("SELECT 1")).scalar()
    return {
        "conexion": "Correcta",
        "resultado": resultado
    }

app.include_router(
    usuario_routes.router,
    prefix="/api/usuarios",
    tags=["Usuarios"]
)