from app.database.database import SessionLocal
from app.models.pregunta_model import Pregunta


preguntas = [
    {
        "codigo": "nombre_paciente",
        "texto_pregunta": "Nombre del paciente",
        "categoria": "Datos Generales",
        "peso_base": 0
    },
    {
        "codigo": "fecha_nacimiento",
        "texto_pregunta": "¿Fecha de nacimiento?",
        "categoria": "Datos Generales",
        "peso_base": 0
    },
    {
        "codigo": "sexo_paciente",
        "texto_pregunta": "¿Cuál es el sexo del niño?",
        "categoria": "Datos Generales",
        "peso_base": 0
    },
    {
        "codigo": "ubicacion",
        "texto_pregunta": "¿Dónde vive el niño?",
        "categoria": "Datos Generales",
        "peso_base": 0
    },
    {
        "codigo": "zona_rural_alejada",
        "texto_pregunta": "¿Vive en una zona rural o alejada del centro de salud?",
        "categoria": "Datos Generales",
        "peso_base": 3
    },
    {
        "codigo": "prematuro",
        "texto_pregunta": "¿El niño nació antes de tiempo (prematuro)?",
        "categoria": "Antecedentes al nacer",
        "peso_base": 4
    },
    {
        "codigo": "bajo_peso_nacer",
        "texto_pregunta": "¿El niño nació con bajo peso (menos de 2.5 kg)?",
        "categoria": "Antecedentes al nacer",
        "peso_base": 4
    },
    {
        "codigo": "anemia_materna_embarazo",
        "texto_pregunta": "¿La madre tuvo anemia durante el embarazo?",
        "categoria": "Antecedentes al nacer",
        "peso_base": 3
    },
    {
        "codigo": "consume_hierro",
        "texto_pregunta": "¿El niño consume alimentos como sangrecita, hígado, bazo o carne?",
        "categoria": "Alimentación",
        "peso_base": 5
    },
    {
        "codigo": "consume_menestras",
        "texto_pregunta": "¿El niño come menestras (lentejas, frejoles)?",
        "categoria": "Alimentación",
        "peso_base": 2
    },
    {
        "codigo": "dieta_carbohidratos",
        "texto_pregunta": "¿El niño come principalmente arroz, papa o fideos?",
        "categoria": "Alimentación",
        "peso_base": 3
    },
    {
        "codigo": "alimentacion_complementaria",
        "texto_pregunta": "¿Desde los 6 meses empezó a comer alimentos además de la leche?",
        "categoria": "Alimentación",
        "peso_base": 4
    },
    {
        "codigo": "buen_apetito",
        "texto_pregunta": "¿El niño tiene buen apetito actualmente?",
        "categoria": "Alimentación",
        "peso_base": 2
    },
    {
        "codigo": "recibe_hierro_micronutrientes",
        "texto_pregunta": "¿El niño recibe hierro o micronutrientes?",
        "categoria": "Suplementación y controles",
        "peso_base": 5
    },
    {
        "codigo": "toma_suplemento_diario",
        "texto_pregunta": "Si recibe: ¿los toma todos los días?",
        "categoria": "Suplementación y controles",
        "peso_base": 4
    },
    {
        "codigo": "asiste_controles_cred",
        "texto_pregunta": "¿El niño asiste a sus controles de crecimiento y desarrollo?",
        "categoria": "Suplementación y controles",
        "peso_base": 3
    },
    {
        "codigo": "tiempo_ultimo_control",
        "texto_pregunta": "¿Hace cuánto fue su último control de salud?",
        "categoria": "Suplementación y controles",
        "peso_base": 2
    },
    {
        "codigo": "palidez",
        "texto_pregunta": "¿El niño se ve pálido (cara, labios o manos)?",
        "categoria": "Síntomas",
        "peso_base": 5
    },
    {
        "codigo": "cansancio_decaimiento",
        "texto_pregunta": "¿El niño se cansa rápido o está decaído?",
        "categoria": "Síntomas",
        "peso_base": 4
    },
    {
        "codigo": "perdida_apetito",
        "texto_pregunta": "¿El niño ha perdido el apetito?",
        "categoria": "Síntomas",
        "peso_base": 3
    },
    {
        "codigo": "diarrea_reciente",
        "texto_pregunta": "¿El niño ha tenido diarrea en las últimas semanas?",
        "categoria": "Enfermedades recientes",
        "peso_base": 3
    },
    {
        "codigo": "infecciones_frecuentes",
        "texto_pregunta": "¿Ha tenido tos o infecciones frecuentes?",
        "categoria": "Enfermedades recientes",
        "peso_base": 3
    },
    {
        "codigo": "parasitos",
        "texto_pregunta": "¿Ha tenido parásitos?",
        "categoria": "Enfermedades recientes",
        "peso_base": 4
    },
    {
        "codigo": "desparasitado",
        "texto_pregunta": "¿El niño ha sido desparasitado?",
        "categoria": "Enfermedades recientes",
        "peso_base": 3
    },
    {
        "codigo": "agua_segura",
        "texto_pregunta": "¿El agua que consumen es segura (hervida o tratada)?",
        "categoria": "Condiciones del hogar",
        "peso_base": 3
    },
    {
        "codigo": "bajo_peso_observado",
        "texto_pregunta": "¿El personal de salud observa bajo peso para su edad?",
        "categoria": "Condiciones del hogar",
        "peso_base": 4
    },
    {
        "codigo": "baja_talla_observado",
        "texto_pregunta": "¿El personal de salud observa talla baja para su edad?",
        "categoria": "Condiciones del hogar",
        "peso_base": 3
    },
    {
        "codigo": "delgadez_observado",
        "texto_pregunta": "¿El personal de salud observa delgadez para su edad?",
        "categoria": "Condiciones del hogar",
        "peso_base": 4
    },
    {
        "codigo": "inseguridad_alimentaria",
        "texto_pregunta": "¿En casa a veces falta comida?",
        "categoria": "Condiciones del hogar",
        "peso_base": 4
    },
    {
        "codigo": "hemoglobina_medida",
        "texto_pregunta": "¿Al niño le han medido la hemoglobina alguna vez?",
        "categoria": "Pruebas médicas",
        "peso_base": 5
    },
    {
        "codigo": "valor_hemoglobina",
        "texto_pregunta": "¿Cuál fue el valor de hemoglobina (si lo conoce)?",
        "categoria": "Pruebas médicas",
        "peso_base": 5
    },
    {
        "codigo": "fecha_prueba_hemoglobina",
        "texto_pregunta": "¿Cuándo se realizó la prueba?",
        "categoria": "Pruebas médicas",
        "peso_base": 0
    },
    {
        "codigo": "lugar_prueba_hemoglobina",
        "texto_pregunta": "¿Dónde se realizó la prueba?",
        "categoria": "Pruebas médicas",
        "peso_base": 0
    }
]


def cargar_preguntas():
    db = SessionLocal()

    try:
        for item in preguntas:
            pregunta_existente = db.query(Pregunta).filter(
                Pregunta.codigo == item["codigo"]
            ).first()

            if not pregunta_existente:
                nueva_pregunta = Pregunta(
                    codigo=item["codigo"],
                    texto_pregunta=item["texto_pregunta"],
                    categoria=item["categoria"],
                    peso_base=item["peso_base"]
                )
                db.add(nueva_pregunta)

        db.commit()
        print("Preguntas cargadas correctamente.")

    except Exception as e:
        db.rollback()
        print("Error al cargar preguntas:", e)

    finally:
        db.close()


if __name__ == "__main__":
    cargar_preguntas()