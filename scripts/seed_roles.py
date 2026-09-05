from app.database.database import SessionLocal
from app.models.usuario_model import Rol


roles = [
    {
        "id": 1,
        "rol": "Administrador"
    },
    {
        "id": 2,
        "rol": "Doctor"
    }
]


def cargar_roles():
    db = SessionLocal()

    try:
        for item in roles:
            rol_existente = db.query(Rol).filter(
                Rol.id == item["id"]
            ).first()

            if not rol_existente:
                nuevo_rol = Rol(
                    id=item["id"],
                    rol=item["rol"]
                )
                db.add(nuevo_rol)

        db.commit()
        print("Roles cargados correctamente.")

    except Exception as e:
        db.rollback()
        print("Error al cargar roles:", e)

    finally:
        db.close()


if __name__ == "__main__":
    cargar_roles()