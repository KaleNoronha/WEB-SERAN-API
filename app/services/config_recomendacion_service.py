
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.config_recomendacion_model import (
    ConfigRecomendacionUsuario,
    ConfigRecomendacionGlobal
)


CATEGORIAS_DEFAULT = [
    "alimentacion",
    "suplementacion",
    "controles",
    "higiene",
    "estimulacion",
    "derivacion",
]


def obtener_config_global(db: Session):
    existentes = {
        config.categoria: config
        for config in db.query(ConfigRecomendacionGlobal).all()
    }

    nuevas = False

    for categoria in CATEGORIAS_DEFAULT:
        if categoria not in existentes:
            db.add(
                ConfigRecomendacionGlobal(
                    categoria=categoria,
                    activo=True
                )
            )
            nuevas = True

    if nuevas:
        db.commit()

    registros = db.query(ConfigRecomendacionGlobal).all()

    return [
        {
            "categoria": categoria,
            "activo": next(
                (r.activo for r in registros if r.categoria == categoria),
                True
            ),
            "disponible": True
        }
        for categoria in CATEGORIAS_DEFAULT
    ]


def actualizar_config_global(db: Session, configuraciones):
    categorias_validas = set(CATEGORIAS_DEFAULT)

    for item in configuraciones:
        if item.categoria not in categorias_validas:
            raise HTTPException(
                status_code=400,
                detail=f"Categoría no válida: {item.categoria}"
            )

    for item in configuraciones:
        config = db.query(ConfigRecomendacionGlobal).filter(
            ConfigRecomendacionGlobal.categoria == item.categoria
        ).first()

        if config:
            config.activo = item.activo
        else:
            db.add(
                ConfigRecomendacionGlobal(
                    categoria=item.categoria,
                    activo=item.activo
                )
            )

    db.commit()
    return obtener_config_global(db)


def obtener_config_recomendaciones(db: Session, usuario_id: int):
    globales = {
        c["categoria"]: c["activo"]
        for c in obtener_config_global(db)
    }

    existentes = db.query(ConfigRecomendacionUsuario).filter(
        ConfigRecomendacionUsuario.usuario_id == usuario_id
    ).all()

    por_categoria = {c.categoria: c for c in existentes}

    nuevos = False

    for categoria in CATEGORIAS_DEFAULT:
        if categoria not in por_categoria:
            nuevo = ConfigRecomendacionUsuario(
                usuario_id=usuario_id,
                categoria=categoria,
                activo=True
            )
            db.add(nuevo)
            por_categoria[categoria] = nuevo
            nuevos = True

    if nuevos:
        db.commit()

    return [
        {
            "categoria": categoria,
            "activo": (
                bool(por_categoria[categoria].activo)
                and globales.get(categoria, False)
            ),
            "disponible": globales.get(categoria, False)
        }
        for categoria in CATEGORIAS_DEFAULT
    ]


def actualizar_config_recomendaciones(
    db: Session,
    usuario_id: int,
    configuraciones
):
    globales = {
        c["categoria"]: c["activo"]
        for c in obtener_config_global(db)
    }

    for item in configuraciones:
        if item.categoria not in CATEGORIAS_DEFAULT:
            raise HTTPException(
                status_code=400,
                detail=f"Categoría no válida: {item.categoria}"
            )

        if item.activo and not globales.get(item.categoria, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"La categoría {item.categoria} "
                    "está deshabilitada por el administrador"
                )
            )

    for item in configuraciones:
        config = db.query(ConfigRecomendacionUsuario).filter(
            ConfigRecomendacionUsuario.usuario_id == usuario_id,
            ConfigRecomendacionUsuario.categoria == item.categoria
        ).first()

        if config:
            config.activo = item.activo
        else:
            db.add(
                ConfigRecomendacionUsuario(
                    usuario_id=usuario_id,
                    categoria=item.categoria,
                    activo=item.activo
                )
            )

    db.commit()

    return obtener_config_recomendaciones(db, usuario_id)


def obtener_categorias_efectivas(db: Session, usuario_id: int):
    configuraciones = obtener_config_recomendaciones(db, usuario_id)

    return [
        c["categoria"]
        for c in configuraciones
        if c["activo"] and c["disponible"]
    ]
