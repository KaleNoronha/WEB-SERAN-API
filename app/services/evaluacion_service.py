
from datetime import date

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.paciente_model import Paciente
from app.models.usuario_model import Usuario
from app.models.pregunta_model import Pregunta
from app.models.evaluacion_model import Evaluacion, EvaluacionPregunta

from app.schemas.evaluacion_schema import (
    EvaluacionCreate,
    EvaluacionFinalizarCreate
)

from app.services.rule_engine_service import evaluar_motor_reglas

from app.models.recomendacion_model import (
    Recomendacion,
    RecomendacionEvaluacion
)

from app.models.config_recomendacion_model import ConfigRecomendacionUsuario

from app.services.config_recomendacion_service import (
    obtener_categorias_efectivas
)

# ==========================================================
# VALIDACIÓN DE ACCESO A PACIENTES
# ==========================================================

def verificar_acceso_paciente(
    db: Session,
    paciente_id: int,
    usuario_actual: Usuario
):
    if usuario_actual is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )

    if usuario_actual.rol_id not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a pacientes"
        )

    consulta = db.query(Paciente).filter(
        Paciente.id == paciente_id
    )

    # El doctor únicamente puede acceder a sus pacientes.
    # El administrador puede acceder a todos.
    if usuario_actual.rol_id == 2:
        consulta = consulta.filter(
            Paciente.usuario_id == usuario_actual.id
        )

    paciente = consulta.first()

    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )

    return paciente


def verificar_acceso_evaluacion(
    db: Session,
    evaluacion: Evaluacion,
    usuario_actual: Usuario
):
    verificar_acceso_paciente(
        db,
        evaluacion.paciente_id,
        usuario_actual
    )


def obtener_doctor_por_id(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.rol_id == 2,
        Usuario.estado == True
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor no autorizado"
        )

    return usuario


# ==========================================================
# INICIAR EVALUACIÓN
# ==========================================================

def iniciar_evaluacion(
    db: Session,
    paciente_id: int,
    usuario_id: int
):
    usuario_actual = obtener_doctor_por_id(db, usuario_id)

    verificar_acceso_paciente(
        db,
        paciente_id,
        usuario_actual
    )

    nueva_evaluacion = Evaluacion(
        usuario_id=usuario_id,
        paciente_id=paciente_id,
        fecha_evaluacion=date.today(),
        estado_evaluacion="En progreso",
        puntaje_total=None,
        nivel_riesgo=None
    )

    db.add(nueva_evaluacion)
    db.commit()
    db.refresh(nueva_evaluacion)

    return nueva_evaluacion


# ==========================================================
# CREAR EVALUACIÓN COMPLETA
# ==========================================================

def crear_evaluacion(
    db: Session,
    evaluacion_data: EvaluacionCreate,
    usuario_id: int
):
    usuario_actual = obtener_doctor_por_id(db, usuario_id)

    verificar_acceso_paciente(
        db,
        evaluacion_data.paciente_id,
        usuario_actual
    )

    if not evaluacion_data.respuestas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe registrar al menos una respuesta"
        )

    respuestas_con_preguntas = []

    for respuesta_item in evaluacion_data.respuestas:
        pregunta = db.query(Pregunta).filter(
            Pregunta.id == respuesta_item.pregunta_id
        ).first()

        if not pregunta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Pregunta con ID "
                    f"{respuesta_item.pregunta_id} no encontrada"
                )
            )

        respuestas_con_preguntas.append({
            "pregunta": pregunta,
            "respuesta": respuesta_item.respuesta
        })

    resultado = evaluar_motor_reglas(respuestas_con_preguntas)

    nueva_evaluacion = Evaluacion(
        usuario_id=usuario_id,
        paciente_id=evaluacion_data.paciente_id,
        fecha_evaluacion=date.today(),
        estado_evaluacion="Culminada",
        puntaje_total=resultado["puntaje_total"],
        nivel_riesgo=resultado["nivel_riesgo"]
    )

    db.add(nueva_evaluacion)
    db.commit()
    db.refresh(nueva_evaluacion)

    for respuesta in resultado["respuestas_evaluadas"]:
        evaluacion_pregunta = EvaluacionPregunta(
            evaluacion_id=nueva_evaluacion.id,
            pregunta_id=respuesta["pregunta_id"],
            respuesta=respuesta["respuesta"],
            puntaje_obtenido=respuesta["puntaje_obtenido"]
        )

        db.add(evaluacion_pregunta)

    db.commit()

    tipo_recomendacion = (
        f"Riesgo {resultado['nivel_riesgo'].lower()}"
    )

    categorias_config = db.query(
        ConfigRecomendacionUsuario
    ).filter(
        ConfigRecomendacionUsuario.usuario_id == nueva_evaluacion.usuario_id,
        ConfigRecomendacionUsuario.activo == True
    ).all()

    categorias_activas = obtener_categorias_efectivas(
        db,
        nueva_evaluacion.usuario_id
    )

    recomendaciones = db.query(Recomendacion).filter(
        Recomendacion.estado == True,
        Recomendacion.tipo_recomendacion == tipo_recomendacion,
        Recomendacion.categoria.in_(categorias_activas)
    ).all()

    recomendaciones_response = []

    for recomendacion in recomendaciones:
        recomendacion_evaluacion = RecomendacionEvaluacion(
            evaluacion_id=nueva_evaluacion.id,
            recomendacion_id=recomendacion.id
        )

        db.add(recomendacion_evaluacion)

        recomendaciones_response.append({
            "id": recomendacion.id,
            "titulo": recomendacion.titulo,
            "descripcion": recomendacion.descripcion,
            "tipo_recomendacion": recomendacion.tipo_recomendacion,
            "categoria": recomendacion.categoria
        })

    db.commit()

    return {
        "evaluacion_id": nueva_evaluacion.id,
        "paciente_id": nueva_evaluacion.paciente_id,
        "usuario_id": nueva_evaluacion.usuario_id,
        "fecha_evaluacion": nueva_evaluacion.fecha_evaluacion,
        "estado_evaluacion": nueva_evaluacion.estado_evaluacion,
        "puntaje_total": nueva_evaluacion.puntaje_total,
        "nivel_riesgo": nueva_evaluacion.nivel_riesgo,
        "respuestas_evaluadas": resultado["respuestas_evaluadas"],
        "explicaciones": resultado["explicaciones"],
        "recomendaciones": recomendaciones_response
    }


# ==========================================================
# LISTAR EVALUACIONES
# ==========================================================

def listar_evaluaciones(
    db: Session,
    usuario_actual: Usuario
):
    if usuario_actual.rol_id not in (1, 2):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar evaluaciones"
        )

    consulta = db.query(Evaluacion)

    if usuario_actual.rol_id == 2:
        consulta = consulta.join(
            Paciente,
            Evaluacion.paciente_id == Paciente.id
        ).filter(
            Paciente.usuario_id == usuario_actual.id
        )

    return consulta.order_by(
        Evaluacion.id.desc()
    ).all()


# ==========================================================
# OBTENER EVALUACIÓN POR ID
# ==========================================================

def obtener_evaluacion_por_id(
    db: Session,
    evaluacion_id: int,
    usuario_actual: Usuario
):
    evaluacion = db.query(Evaluacion).filter(
        Evaluacion.id == evaluacion_id
    ).first()

    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada"
        )

    verificar_acceso_evaluacion(
        db,
        evaluacion,
        usuario_actual
    )

    respuestas_bd = db.query(EvaluacionPregunta).filter(
        EvaluacionPregunta.evaluacion_id == evaluacion_id
    ).all()

    respuestas_evaluadas = []
    respuestas_con_preguntas = []

    for respuesta in respuestas_bd:
        pregunta = db.query(Pregunta).filter(
            Pregunta.id == respuesta.pregunta_id
        ).first()

        respuestas_evaluadas.append({
            "pregunta_id": respuesta.pregunta_id,
            "codigo": pregunta.codigo if pregunta else "",
            "texto_pregunta": (
                pregunta.texto_pregunta if pregunta else ""
            ),
            "respuesta": respuesta.respuesta,
            "puntaje_obtenido": respuesta.puntaje_obtenido
        })

        if pregunta:
            respuestas_con_preguntas.append({
                "pregunta": pregunta,
                "respuesta": respuesta.respuesta
            })

    resultado_recalculado = evaluar_motor_reglas(
        respuestas_con_preguntas
    )

    recomendaciones_bd = db.query(Recomendacion).join(
        RecomendacionEvaluacion,
        Recomendacion.id == RecomendacionEvaluacion.recomendacion_id
    ).filter(
        RecomendacionEvaluacion.evaluacion_id == evaluacion_id
    ).all()

    recomendaciones_response = []

    for recomendacion in recomendaciones_bd:
        recomendaciones_response.append({
            "id": recomendacion.id,
            "titulo": recomendacion.titulo,
            "descripcion": recomendacion.descripcion,
            "tipo_recomendacion": recomendacion.tipo_recomendacion,
            "categoria": recomendacion.categoria
        })

    return {
        "evaluacion_id": evaluacion.id,
        "paciente_id": evaluacion.paciente_id,
        "usuario_id": evaluacion.usuario_id,
        "fecha_evaluacion": evaluacion.fecha_evaluacion,
        "estado_evaluacion": evaluacion.estado_evaluacion,
        "puntaje_total": evaluacion.puntaje_total,
        "nivel_riesgo": evaluacion.nivel_riesgo,
        "respuestas_evaluadas": respuestas_evaluadas,
        "explicaciones": resultado_recalculado["explicaciones"],
        "recomendaciones": recomendaciones_response
    }


# ==========================================================
# FINALIZAR EVALUACIÓN EN PROGRESO
# ==========================================================

def finalizar_evaluacion(
    db: Session,
    evaluacion_id: int,
    evaluacion_data: EvaluacionFinalizarCreate,
    usuario_id: int
):
    usuario_actual = obtener_doctor_por_id(db, usuario_id)

    evaluacion = db.query(Evaluacion).filter(
        Evaluacion.id == evaluacion_id
    ).first()

    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada"
        )

    if evaluacion.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para finalizar esta evaluación"
        )

    verificar_acceso_evaluacion(
        db,
        evaluacion,
        usuario_actual
    )

    if evaluacion.estado_evaluacion != "En progreso":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La evaluación no se encuentra en progreso"
        )

    if not evaluacion_data.respuestas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe registrar al menos una respuesta"
        )

    respuestas_existentes = db.query(EvaluacionPregunta).filter(
        EvaluacionPregunta.evaluacion_id == evaluacion_id
    ).first()

    if respuestas_existentes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta evaluación ya tiene respuestas registradas"
        )

    respuestas_con_preguntas = []

    for respuesta_item in evaluacion_data.respuestas:
        pregunta = db.query(Pregunta).filter(
            Pregunta.id == respuesta_item.pregunta_id
        ).first()

        if not pregunta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Pregunta con ID "
                    f"{respuesta_item.pregunta_id} no encontrada"
                )
            )

        respuestas_con_preguntas.append({
            "pregunta": pregunta,
            "respuesta": respuesta_item.respuesta
        })

    resultado = evaluar_motor_reglas(respuestas_con_preguntas)

    evaluacion.puntaje_total = resultado["puntaje_total"]
    evaluacion.nivel_riesgo = resultado["nivel_riesgo"]
    evaluacion.estado_evaluacion = "Culminada"

    for respuesta in resultado["respuestas_evaluadas"]:
        evaluacion_pregunta = EvaluacionPregunta(
            evaluacion_id=evaluacion.id,
            pregunta_id=respuesta["pregunta_id"],
            respuesta=respuesta["respuesta"],
            puntaje_obtenido=respuesta["puntaje_obtenido"]
        )

        db.add(evaluacion_pregunta)

    db.commit()
    db.refresh(evaluacion)

    tipo_recomendacion = (
        f"Riesgo {resultado['nivel_riesgo'].lower()}"
    )

    categorias_config = db.query(
        ConfigRecomendacionUsuario
    ).filter(
        ConfigRecomendacionUsuario.usuario_id == evaluacion.usuario_id,
        ConfigRecomendacionUsuario.activo == True
    ).all()

    categorias_activas = obtener_categorias_efectivas(
        db,
        evaluacion.usuario_id
    )

    recomendaciones = db.query(Recomendacion).filter(
        Recomendacion.estado == True,
        Recomendacion.tipo_recomendacion == tipo_recomendacion,
        Recomendacion.categoria.in_(categorias_activas)
    ).all()


    recomendaciones_response = []

    for recomendacion in recomendaciones:
        recomendacion_evaluacion = RecomendacionEvaluacion(
            evaluacion_id=evaluacion.id,
            recomendacion_id=recomendacion.id
        )

        db.add(recomendacion_evaluacion)

        recomendaciones_response.append({
            "id": recomendacion.id,
            "titulo": recomendacion.titulo,
            "descripcion": recomendacion.descripcion,
            "tipo_recomendacion": recomendacion.tipo_recomendacion,
            "categoria": recomendacion.categoria
        })

    db.commit()

    return {
        "evaluacion_id": evaluacion.id,
        "paciente_id": evaluacion.paciente_id,
        "usuario_id": evaluacion.usuario_id,
        "fecha_evaluacion": evaluacion.fecha_evaluacion,
        "estado_evaluacion": evaluacion.estado_evaluacion,
        "puntaje_total": evaluacion.puntaje_total,
        "nivel_riesgo": evaluacion.nivel_riesgo,
        "respuestas_evaluadas": resultado["respuestas_evaluadas"],
        "explicaciones": resultado["explicaciones"],
        "recomendaciones": recomendaciones_response
    }


# ==========================================================
# EVALUACIONES POR PACIENTE
# ==========================================================

def listar_evaluaciones_por_paciente(
    db: Session,
    paciente_id: int,
    usuario_actual: Usuario
):
    verificar_acceso_paciente(
        db,
        paciente_id,
        usuario_actual
    )

    return db.query(Evaluacion).filter(
        Evaluacion.paciente_id == paciente_id
    ).order_by(
        Evaluacion.id.desc()
    ).all()


# ==========================================================
# EVALUACIONES EN PROGRESO POR USUARIO
# ==========================================================

def listar_evaluaciones_en_progreso_por_usuario(
    db: Session,
    usuario_id: int
):
    return db.query(Evaluacion).join(
        Paciente,
        Evaluacion.paciente_id == Paciente.id
    ).filter(
        Evaluacion.usuario_id == usuario_id,
        Paciente.usuario_id == usuario_id,
        Evaluacion.estado_evaluacion == "En progreso"
    ).order_by(
        Evaluacion.id.desc()
    ).all()


# ==========================================================
# EVALUACIONES CULMINADAS POR USUARIO
# ==========================================================

def listar_evaluaciones_culminadas_por_usuario(
    db: Session,
    usuario_id: int
):
    return db.query(Evaluacion).join(
        Paciente,
        Evaluacion.paciente_id == Paciente.id
    ).filter(
        Evaluacion.usuario_id == usuario_id,
        Paciente.usuario_id == usuario_id,
        Evaluacion.estado_evaluacion == "Culminada"
    ).order_by(
        Evaluacion.id.desc()
    ).all()


# ==========================================================
# CANCELAR EVALUACIÓN EN PROGRESO
# ==========================================================

def cancelar_evaluacion(
    db: Session,
    evaluacion_id: int,
    usuario_id: int
):
    usuario_actual = obtener_doctor_por_id(db, usuario_id)

    evaluacion = db.query(Evaluacion).filter(
        Evaluacion.id == evaluacion_id
    ).first()

    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación no encontrada"
        )

    if evaluacion.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para cancelar esta evaluación"
        )

    verificar_acceso_evaluacion(
        db,
        evaluacion,
        usuario_actual
    )

    if evaluacion.estado_evaluacion != "En progreso":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden cancelar evaluaciones en progreso"
        )

    evaluacion.estado_evaluacion = "Cancelada"

    db.commit()
    db.refresh(evaluacion)

    return evaluacion
