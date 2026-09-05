import unicodedata


def normalizar_texto(valor):
    if valor is None:
        return ""

    texto = str(valor).strip().lower()

    texto = "".join(
        caracter for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )

    texto = texto.replace("¿", "")
    texto = texto.replace("?", "")
    texto = texto.replace("¡", "")
    texto = texto.replace("!", "")
    texto = texto.replace(".", "")
    texto = texto.replace(":", "")
    texto = texto.replace(";", "")
    texto = " ".join(texto.split())

    return texto


def obtener_respuesta_por_codigo(respuestas_con_preguntas):
    respuestas = {}

    for item in respuestas_con_preguntas:
        pregunta = item["pregunta"]
        respuesta = item["respuesta"]

        respuestas[pregunta.codigo] = respuesta

    return respuestas


def calcular_puntaje_hemoglobina(respuesta):
    respuesta_normalizada = normalizar_texto(respuesta)

    if respuesta_normalizada in [
        "no se sabe",
        "no recuerda",
        "no se sabe / no recuerda",
        "no sabe",
        ""
    ]:
        return 2

    try:
        valor = float(str(respuesta).replace(",", ".").strip())
    except ValueError:
        return 0

    if valor >= 11:
        return 0

    if valor >= 10:
        return 4

    return 8


def calcular_puntaje_por_codigo(codigo, respuesta):
    codigo = normalizar_texto(codigo)
    respuesta_normalizada = normalizar_texto(respuesta)

    if codigo == "valor_hemoglobina":
        return calcular_puntaje_hemoglobina(respuesta)

    reglas = {
        # Datos generales: no suman riesgo directo
        "nombre_paciente": {
            "texto libre": 0,
        },
        "fecha_nacimiento": {
            "fecha": 0,
        },
        "sexo_paciente": {
            "masculino": 0,
            "femenino": 0,
            "hombre": 0,
            "mujer": 0,
        },
        "ubicacion": {},
        "zona_rural_alejada": {
            "si": 0,
            "no": 0,
            "no se sabe": 0,
            "no sabe": 0,
        },

        # Antecedentes al nacer
        "prematuro": {
            "si": 2,
            "no": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },
        "bajo_peso_nacer": {
            "si": 3,
            "no": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },
        "anemia_materna_embarazo": {
            "si": 3,
            "no": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },

        # Alimentación
        "frecuencia_consumo_hierro": {
            "todos los dias": 0,
            "3 a 5 veces por semana": 1,
            "3 a 5 veces/semana": 1,
            "1 a 2 veces por semana": 2,
            "1 a 2 veces/semana": 2,
            "casi nunca o nunca": 4,
            "casi nunca/nunca": 4,
        },
        # Código antiguo de tu BD
        "consume_hierro": {
            "todos los dias": 0,
            "3 a 5 veces por semana": 1,
            "3 a 5 veces/semana": 1,
            "1 a 2 veces por semana": 2,
            "1 a 2 veces/semana": 2,
            "casi nunca o nunca": 4,
            "casi nunca/nunca": 4,
            "si": 0,
            "no": 4,
            "no se sabe": 1,
            "no sabe": 1,
        },

        "frecuencia_consumo_menestras": {
            "3 o mas veces por semana": 0,
            "3 o mas veces/semana": 0,
            "1 a 2 veces por semana": 1,
            "1 a 2 veces/semana": 1,
            "casi nunca o nunca": 2,
            "casi nunca/nunca": 2,
        },
        # Código antiguo de tu BD
        "consume_menestras": {
            "3 o mas veces por semana": 0,
            "3 o mas veces/semana": 0,
            "1 a 2 veces por semana": 1,
            "1 a 2 veces/semana": 1,
            "casi nunca o nunca": 2,
            "casi nunca/nunca": 2,
            "si": 0,
            "no": 2,
            "no se sabe": 1,
            "no sabe": 1,
        },

        "dieta_baja_hierro": {
            "si": 3,
            "no": 0,
        },
        # Código antiguo de tu BD
        "dieta_carbohidratos": {
            "si": 3,
            "no": 0,
        },

        "alimentacion_complementaria_6m": {
            "si": 0,
            "no": 3,
            "no aplica menor de 6 meses": 0,
            "no aplica, menor de 6 meses": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },
        # Código antiguo de tu BD
        "alimentacion_complementaria": {
            "si": 0,
            "no": 3,
            "no aplica menor de 6 meses": 0,
            "no aplica, menor de 6 meses": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },

        "buen_apetito": {
            "si": 0,
            "no": 2,
            "no se sabe": 1,
            "no sabe": 1,
        },

        # Suplementación y controles
        "recibe_suplemento_hierro": {
            "si": 0,
            "no": 5,
            "no se sabe": 2,
            "no sabe": 2,
        },
        # Código antiguo de tu BD
        "recibe_hierro_micronutrientes": {
            "si": 0,
            "no": 5,
            "no se sabe": 2,
            "no sabe": 2,
        },

        "adherencia_suplemento_hierro": {
            "siempre": 0,
            "a veces": 3,
            "casi nunca": 6,
            "casi nunca o nunca": 6,
            "no se sabe": 2,
            "no sabe": 2,
        },
        # Código antiguo de tu BD
        "toma_suplemento_diario": {
            "siempre": 0,
            "a veces": 3,
            "casi nunca": 6,
            "casi nunca o nunca": 6,
            "si": 0,
            "no": 6,
            "no se sabe": 2,
            "no sabe": 2,
        },

        "asiste_cred": {
            "si": 0,
            "no": 3,
            "no se sabe": 1,
            "no sabe": 1,
        },
        # Código antiguo de tu BD
        "asiste_controles_cred": {
            "si": 0,
            "no": 3,
            "no se sabe": 1,
            "no sabe": 1,
        },

        "ultimo_control_salud": {
            "menos de 1 mes": 0,
            "1 a 2 meses": 1,
            "3 a 5 meses": 2,
            "6 meses o mas": 3,
            "nunca": 4,
            "no se sabe": 2,
            "no sabe": 2,
        },
        # Código antiguo de tu BD
        "tiempo_ultimo_control": {
            "menos de 1 mes": 0,
            "1 a 2 meses": 1,
            "3 a 5 meses": 2,
            "6 meses o mas": 3,
            "nunca": 4,
            "no se sabe": 2,
            "no sabe": 2,
        },

        # Síntomas
        "palidez": {
            "si": 5,
            "no": 0,
        },
        "cansancio_decaimiento": {
            "si": 3,
            "no": 0,
        },
        "perdida_apetito": {
            "si": 2,
            "no": 0,
        },

        # Enfermedades recientes
        "diarrea_reciente": {
            "si": 3,
            "no": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },
        "infecciones_recientes": {
            "si": 2,
            "no": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },
        # Código antiguo de tu BD
        "infecciones_frecuentes": {
            "si": 2,
            "no": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },

        "parasitosis": {
            "si": 3,
            "no": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },
        # Código antiguo de tu BD
        "parasitos": {
            "si": 3,
            "no": 0,
            "no se sabe": 1,
            "no sabe": 1,
        },

        "desparasitacion": {
            "si": 0,
            "no": 3,
            "no se sabe": 1,
            "no sabe": 1,
        },
        # Código antiguo de tu BD
        "desparasitado": {
            "si": 0,
            "no": 3,
            "no se sabe": 1,
            "no sabe": 1,
        },

        # Condiciones del hogar y estado nutricional
        "agua_segura": {
            "si": 0,
            "no": 4,
            "no se sabe": 2,
            "no sabe": 2,
        },

        "bajo_peso_edad": {
            "si": 4,
            "no": 0,
        },
        # Código antiguo de tu BD
        "bajo_peso_observado": {
            "si": 4,
            "no": 0,
        },

        "talla_baja_edad": {
            "si": 4,
            "no": 0,
        },
        # Código antiguo de tu BD
        "baja_talla_observado": {
            "si": 4,
            "no": 0,
        },

        "delgadez_edad": {
            "si": 4,
            "no": 0,
        },
        # Código antiguo de tu BD
        "delgadez_observado": {
            "si": 4,
            "no": 0,
        },

        "frecuencia_inseguridad_alimentaria": {
            "siempre": 5,
            "casi siempre": 4,
            "a veces": 2,
            "rara vez": 1,
            "nunca": 0,
        },
        # Código antiguo de tu BD
        "inseguridad_alimentaria": {
            "siempre": 5,
            "casi siempre": 4,
            "a veces": 2,
            "rara vez": 1,
            "nunca": 0,
            "si": 4,
            "no": 0,
            "no se sabe": 2,
            "no sabe": 2,
        },

        # Pruebas médicas
        "hemoglobina_medida": {
            "si": 0,
            "no": 2,
            "no se sabe": 2,
            "no sabe": 2,
        },

        "fecha_hemoglobina": {
            "menos de 1 mes": 0,
            "1 a 3 meses": 1,
            "4 a 6 meses": 2,
            "mas de 6 meses": 3,
            "no se sabe": 2,
            "no sabe": 2,
        },
        # Código antiguo de tu BD
        "fecha_prueba_hemoglobina": {
            "menos de 1 mes": 0,
            "1 a 3 meses": 1,
            "4 a 6 meses": 2,
            "mas de 6 meses": 3,
            "no se sabe": 2,
            "no sabe": 2,
        },

        "lugar_prueba_hemoglobina": {
            "centro de salud": 0,
            "hospital": 0,
            "campana de salud": 1,
            "campana": 1,
            "institucion educativa": 1,
            "colegio": 1,
            "otro": 1,
            "no se sabe": 1,
            "no sabe": 1,
        },
    }

    return reglas.get(codigo, {}).get(respuesta_normalizada, 0)


def determinar_nivel_riesgo(puntaje_total: int):
    if puntaje_total <= 11:
        return "Bajo"

    if puntaje_total <= 23:
        return "Moderado"

    return "Alto"


def subir_minimo_riesgo(nivel_actual, nivel_minimo):
    orden = {
        "Bajo": 1,
        "Moderado": 2,
        "Alto": 3,
    }

    if orden[nivel_actual] < orden[nivel_minimo]:
        return nivel_minimo

    return nivel_actual


def actualizar_nivel_minimo(nivel_actual, nuevo_nivel):
    if nivel_actual is None:
        return nuevo_nivel

    orden = {
        "Moderado": 2,
        "Alto": 3,
    }

    if orden[nuevo_nivel] > orden[nivel_actual]:
        return nuevo_nivel

    return nivel_actual


def evaluar_motor_reglas(respuestas_con_preguntas):
    puntaje_total = 0
    respuestas_evaluadas = []
    explicaciones = []

    respuestas_por_codigo = obtener_respuesta_por_codigo(respuestas_con_preguntas)

    for item in respuestas_con_preguntas:
        pregunta = item["pregunta"]
        respuesta = item["respuesta"]

        puntaje = calcular_puntaje_por_codigo(
            codigo=pregunta.codigo,
            respuesta=respuesta
        )

        puntaje_total += puntaje

        respuestas_evaluadas.append({
            "pregunta_id": pregunta.id,
            "codigo": pregunta.codigo,
            "texto_pregunta": pregunta.texto_pregunta,
            "respuesta": respuesta,
            "puntaje_obtenido": puntaje
        })

        if puntaje > 0:
            explicaciones.append({
                "tipo": "Regla individual",
                "codigo": pregunta.codigo,
                "descripcion": (
                    f"La respuesta '{respuesta}' en la pregunta "
                    f"'{pregunta.texto_pregunta}' activó un factor de riesgo "
                    f"y aportó {puntaje} punto(s)."
                ),
                "puntaje": puntaje
            })

    puntaje_adicional, explicaciones_combinadas, nivel_minimo = aplicar_reglas_combinadas(
        respuestas_por_codigo
    )

    puntaje_total += puntaje_adicional
    explicaciones.extend(explicaciones_combinadas)

    nivel_riesgo = determinar_nivel_riesgo(puntaje_total)

    if nivel_minimo:
        nivel_riesgo = subir_minimo_riesgo(nivel_riesgo, nivel_minimo)

    return {
        "puntaje_total": puntaje_total,
        "nivel_riesgo": nivel_riesgo,
        "respuestas_evaluadas": respuestas_evaluadas,
        "explicaciones": explicaciones
    }


def aplicar_reglas_combinadas(respuestas):
    puntaje_adicional = 0
    explicaciones = []
    nivel_minimo = None

    def existe(*codigos):
        for codigo in codigos:
            if codigo in respuestas:
                return codigo
        return None

    def valor(codigo):
        if not codigo:
            return ""
        return normalizar_texto(respuestas.get(codigo))

    def es_si(codigo):
        return valor(codigo) == "si"

    cod_prematuro = existe("prematuro")
    cod_bajo_peso_nacer = existe("bajo_peso_nacer")
    cod_hierro = existe("frecuencia_consumo_hierro", "consume_hierro")
    cod_suplemento = existe("recibe_suplemento_hierro", "recibe_hierro_micronutrientes")
    cod_palidez = existe("palidez")
    cod_cansancio = existe("cansancio_decaimiento")
    cod_perdida_apetito = existe("perdida_apetito")
    cod_diarrea = existe("diarrea_reciente")
    cod_agua = existe("agua_segura")
    cod_parasitosis = existe("parasitosis", "parasitos")
    cod_desparasitacion = existe("desparasitacion", "desparasitado")
    cod_bajo_peso_edad = existe("bajo_peso_edad", "bajo_peso_observado")
    cod_delgadez = existe("delgadez_edad", "delgadez_observado")
    cod_hb_medida = existe("hemoglobina_medida")
    cod_hb_valor = existe("valor_hemoglobina")
    cod_hb_fecha = existe("fecha_hemoglobina", "fecha_prueba_hemoglobina")

    # R1: prematuridad + bajo peso al nacer
    if cod_prematuro and cod_bajo_peso_nacer:
        if es_si(cod_prematuro) and es_si(cod_bajo_peso_nacer):
            puntaje_adicional += 2
            explicaciones.append({
                "tipo": "Regla combinada",
                "codigo": "R1",
                "descripcion": (
                    "La combinación de prematuridad y bajo peso al nacer "
                    "activa un riesgo perinatal acumulado."
                ),
                "puntaje": 2
            })

    # R2: bajo consumo de hierro + ausencia de suplemento
    if cod_hierro and cod_suplemento:
        bajo_consumo_hierro = valor(cod_hierro) in [
            "casi nunca o nunca",
            "casi nunca/nunca",
            "no"
        ]

        if bajo_consumo_hierro and valor(cod_suplemento) == "no":
            puntaje_adicional += 3
            explicaciones.append({
                "tipo": "Regla combinada",
                "codigo": "R2",
                "descripcion": (
                    "El bajo consumo de alimentos ricos en hierro junto con "
                    "la ausencia de suplementación aumenta el riesgo nutricional."
                ),
                "puntaje": 3
            })

    # R3: palidez + cansancio + pérdida de apetito
    if cod_palidez and cod_cansancio and cod_perdida_apetito:
        if es_si(cod_palidez) and es_si(cod_cansancio) and es_si(cod_perdida_apetito):
            nivel_minimo = actualizar_nivel_minimo(nivel_minimo, "Moderado")
            explicaciones.append({
                "tipo": "Regla de seguridad",
                "codigo": "R3",
                "descripcion": (
                    "La presencia conjunta de palidez, cansancio y pérdida de apetito "
                    "eleva el caso como mínimo a riesgo moderado."
                ),
                "puntaje": 0
            })

    # R4: diarrea reciente + agua no segura
    if cod_diarrea and cod_agua:
        if es_si(cod_diarrea) and valor(cod_agua) == "no":
            puntaje_adicional += 2
            explicaciones.append({
                "tipo": "Regla combinada",
                "codigo": "R4",
                "descripcion": (
                    "La diarrea reciente junto con consumo de agua no segura "
                    "activa un riesgo sanitario acumulado."
                ),
                "puntaje": 2
            })

    # R5: parasitosis + no desparasitación
    if cod_parasitosis and cod_desparasitacion:
        if es_si(cod_parasitosis) and valor(cod_desparasitacion) == "no":
            explicaciones.append({
                "tipo": "Regla combinada",
                "codigo": "R5",
                "descripcion": (
                    "La presencia de parasitosis junto con ausencia de desparasitación "
                    "activa un riesgo parasitológico. No se agregan puntos extra porque "
                    "ambos factores ya puntúan individualmente."
                ),
                "puntaje": 0
            })

    # R6: bajo peso + delgadez
    if cod_bajo_peso_edad and cod_delgadez:
        if es_si(cod_bajo_peso_edad) and es_si(cod_delgadez):
            nivel_minimo = actualizar_nivel_minimo(nivel_minimo, "Moderado")
            explicaciones.append({
                "tipo": "Regla de seguridad",
                "codigo": "R6",
                "descripcion": (
                    "La combinación de bajo peso y delgadez eleva el caso "
                    "como mínimo a riesgo moderado por compromiso nutricional."
                ),
                "puntaje": 0
            })

    # R7 y R8: hemoglobina baja
    if cod_hb_medida and cod_hb_valor:
        if valor(cod_hb_medida) == "si":
            try:
                hb = float(str(respuestas.get(cod_hb_valor)).replace(",", ".").strip())
            except ValueError:
                hb = None

            if hb is not None and hb < 11:
                nivel_minimo = actualizar_nivel_minimo(nivel_minimo, "Moderado")
                explicaciones.append({
                    "tipo": "Regla de seguridad",
                    "codigo": "R7",
                    "descripcion": (
                        "El valor de hemoglobina reportado es menor a 11 g/dL. "
                        "Esto activa una alerta clínica y eleva el caso como mínimo "
                        "a riesgo moderado."
                    ),
                    "puntaje": 0
                })

                if cod_hb_fecha and valor(cod_hb_fecha) == "menos de 1 mes":
                    nivel_minimo = actualizar_nivel_minimo(nivel_minimo, "Alto")
                    explicaciones.append({
                        "tipo": "Regla de seguridad",
                        "codigo": "R8",
                        "descripcion": (
                            "La hemoglobina baja corresponde a una prueba reciente. "
                            "El caso se eleva como mínimo a riesgo alto."
                        ),
                        "puntaje": 0
                    })

    return puntaje_adicional, explicaciones, nivel_minimo