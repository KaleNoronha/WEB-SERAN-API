from scripts.seed_roles import cargar_roles
from scripts.seed_preguntas import cargar_preguntas


def cargar_datos_iniciales():
    print("Iniciando carga de datos iniciales...")

    cargar_roles()
    cargar_preguntas()

    print("Carga de datos iniciales finalizada correctamente.")


if __name__ == "__main__":
    cargar_datos_iniciales()