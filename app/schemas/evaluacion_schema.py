from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class RespuestaEvaluacionCreate(BaseModel):
    pregunta_id: int
    respuesta: str


class EvaluacionCreate(BaseModel):
    paciente_id: int
    respuestas: List[RespuestaEvaluacionCreate]

class EvaluacionFinalizarCreate(BaseModel):
    respuestas: List[RespuestaEvaluacionCreate]
    
class EvaluacionIniciarCreate(BaseModel):
    paciente_id: int


class RespuestaEvaluadaResponse(BaseModel):
    pregunta_id: int
    codigo: str
    texto_pregunta: str
    respuesta: str
    puntaje_obtenido: int


class ExplicacionResponse(BaseModel):
    tipo: str
    descripcion: str
    puntaje: int


class RecomendacionEvaluacionResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    tipo_recomendacion: str
    categoria: str


class EvaluacionResponse(BaseModel):
    evaluacion_id: int
    paciente_id: int
    usuario_id: int
    fecha_evaluacion: date
    estado_evaluacion: str
    puntaje_total: Optional[int] = None
    nivel_riesgo: Optional[str] = None
    respuestas_evaluadas: List[RespuestaEvaluadaResponse]
    explicaciones: List[ExplicacionResponse]
    recomendaciones: List[RecomendacionEvaluacionResponse] = []


class EvaluacionResumenResponse(BaseModel):
    id: int
    paciente_id: int
    usuario_id: int
    fecha_evaluacion: date
    estado_evaluacion: str
    puntaje_total: Optional[int] = None
    nivel_riesgo: Optional[str] = None

    class Config:
        from_attributes = True