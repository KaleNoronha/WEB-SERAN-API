from sqlalchemy.orm import Session
from app.models.config_recomendacion_model import ConfigRecomendacionUsuario

CATEGORIAS_DEFAULT = [
    "alimentacion",
    "suplementacion",
    "controles",
    "higiene",
    "estimulacion",
    "derivacion",
]


def obtener_config_recomendaciones(db: Session, usuario_id: int):
    existentes = db.query(ConfigRecomendacionUsuario).filter(
        ConfigRecomendacionUsuario.usuario_id == usuario_id
    ).all()

    existentes_por_categoria = {c.categoria: c for c in existentes}

    for categoria in CATEGORIAS_DEFAULT:
        if categoria not in existentes_por_categoria:
            nueva = ConfigRecomendacionUsuario(
                usuario_id=usuario_id,
                categoria=categoria,
                activo=True
            )
            db.add(nueva)

    db.commit()

    return db.query(ConfigRecomendacionUsuario).filter(
        ConfigRecomendacionUsuario.usuario_id == usuario_id
    ).order_by(ConfigRecomendacionUsuario.categoria.asc()).all()


def actualizar_config_recomendaciones(db: Session, usuario_id: int, configuraciones):
    for item in configuraciones:
        config = db.query(ConfigRecomendacionUsuario).filter(
            ConfigRecomendacionUsuario.usuario_id == usuario_id,
            ConfigRecomendacionUsuario.categoria == item.categoria
        ).first()

        if config:
            config.activo = item.activo
        else:
            config = ConfigRecomendacionUsuario(
                usuario_id=usuario_id,
                categoria=item.categoria,
                activo=item.activo
            )
            db.add(config)

    db.commit()

    return obtener_config_recomendaciones(db, usuario_id)