from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.paciente_model import Paciente
from app.schemas.paciente_schema import PacienteCreate, PacienteUpdate
from app.models.evaluacion_model import Evaluacion


def _obtener_paciente_modelo(db: Session, paciente_id: int):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()

    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )

    return paciente


def construir_paciente_response(db: Session, paciente: Paciente):
    consulta_evaluaciones = db.query(Evaluacion).filter(
        Evaluacion.paciente_id == paciente.id,
        Evaluacion.estado_evaluacion.ilike("culminada")
    )

    total_evaluaciones = consulta_evaluaciones.count()

    ultima_evaluacion = consulta_evaluaciones.order_by(
        Evaluacion.fecha_evaluacion.desc(),
        Evaluacion.id.desc()
    ).first()

    return {
        "id": paciente.id,
        "nombres": paciente.nombres,
        "apellidos": paciente.apellidos,
        "fecha_nacimiento": paciente.fecha_nacimiento,
        "dni": paciente.dni,
        "sexo": paciente.sexo,
        "peso": paciente.peso,
        "talla": paciente.talla,
        "fecha_registro": paciente.fecha_registro,
        "departamento": paciente.departamento,
        "evaluaciones": total_evaluaciones,
        "ultimo_riesgo": ultima_evaluacion.nivel_riesgo if ultima_evaluacion else None,
        "ultimo_puntaje": ultima_evaluacion.puntaje_total if ultima_evaluacion else None,
    }


def crear_paciente(db: Session, paciente_data: PacienteCreate):
    if paciente_data.dni:
        paciente_existente = db.query(Paciente).filter(
            Paciente.dni == paciente_data.dni
        ).first()

        if paciente_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un paciente registrado con ese DNI"
            )

    nuevo_paciente = Paciente(
        nombres=paciente_data.nombres,
        apellidos=paciente_data.apellidos,
        fecha_nacimiento=paciente_data.fecha_nacimiento,
        dni=paciente_data.dni,
        sexo=paciente_data.sexo,
        peso=paciente_data.peso,
        talla=paciente_data.talla,
        departamento=paciente_data.departamento,
        fecha_registro=date.today()
    )

    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)

    return construir_paciente_response(db, nuevo_paciente)


def listar_pacientes(db: Session):
    pacientes = db.query(Paciente).order_by(Paciente.id.desc()).all()

    return [
        construir_paciente_response(db, paciente)
        for paciente in pacientes
    ]


def obtener_paciente_por_id(db: Session, paciente_id: int):
    paciente = _obtener_paciente_modelo(db, paciente_id)

    return construir_paciente_response(db, paciente)


def actualizar_paciente(
    db: Session,
    paciente_id: int,
    paciente_data: PacienteUpdate
):
    paciente = _obtener_paciente_modelo(db, paciente_id)

    datos_actualizados = paciente_data.model_dump(exclude_unset=True)

    if "dni" in datos_actualizados and datos_actualizados["dni"]:
        paciente_existente = db.query(Paciente).filter(
            Paciente.dni == datos_actualizados["dni"],
            Paciente.id != paciente_id
        ).first()

        if paciente_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro paciente registrado con ese DNI"
            )

    for campo, valor in datos_actualizados.items():
        setattr(paciente, campo, valor)

    db.commit()
    db.refresh(paciente)

    return construir_paciente_response(db, paciente)