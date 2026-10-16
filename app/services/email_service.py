import requests

from app.core.config import settings


BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def enviar_correo_invitacion_doctor(
    email_destino: str,
    token: str
):
    enlace_registro = f"{settings.FRONTEND_URL}/registro-doctor/{token}"

    asunto = "Invitación para registrarse en el Sistema de Riesgo de Anemia"

    html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.5;">
        <h2>Invitación al Sistema de Riesgo de Anemia</h2>

        <p>Has sido invitado para registrarte como doctor en el sistema.</p>

        <p>Para completar tu registro, haz clic en el siguiente enlace:</p>

        <p>
            <a href="{enlace_registro}" 
               style="background-color:#2563eb;color:white;padding:10px 16px;
                      text-decoration:none;border-radius:6px;display:inline-block;">
                Completar registro
            </a>
        </p>

        <p>Este enlace tiene una duración limitada. Si no solicitaste esta invitación, puedes ignorar este correo.</p>

        <p>Enlace directo:</p>
        <p>{enlace_registro}</p>
    </div>
    """

    remitente_nombre, remitente_correo = _parsear_remitente(settings.EMAIL_FROM)

    payload = {
        "sender": {"name": remitente_nombre, "email": remitente_correo},
        "to": [{"email": email_destino}],
        "subject": asunto,
        "htmlContent": html
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }

    respuesta = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=10)
    respuesta.raise_for_status()

    return respuesta.json()


def _parsear_remitente(email_from: str):
    """
    Acepta formatos "Nombre <correo@dominio.com>" o solo "correo@dominio.com".
    """
    if "<" in email_from and ">" in email_from:
        nombre = email_from.split("<")[0].strip()
        correo = email_from.split("<")[1].split(">")[0].strip()
        return nombre or correo, correo

    return email_from.strip(), email_from.strip()


from html import escape


def enviar_correo_recuperacion_password(
    email_destino: str,
    token: str
):
    enlace = (
        f"{settings.FRONTEND_URL.rstrip('/')}"
        f"/restablecer-password/{token}"
    )

    asunto = "Restablecimiento de contraseña - SERAN"

    enlace_seguro = escape(enlace, quote=True)

    html = f"""
    <div style="font-family:Arial,sans-serif;line-height:1.6;">
        <h2>Recuperación de contraseña - SERAN</h2>

        <p>Recibimos una solicitud para restablecer
        la contraseña de tu cuenta.</p>

        <p>Haz clic en el siguiente botón:</p>

        <p>
            <a href="{enlace_seguro}"
               style="background:#1e293b;color:#fff;
                      padding:12px 20px;text-decoration:none;
                      border-radius:6px;display:inline-block;">
                Restablecer contraseña
            </a>
        </p>

        <p>Este enlace estará disponible durante
        <strong>15 minutos</strong> y solo podrá
        utilizarse una vez.</p>

        <p>Si no solicitaste este cambio,
        puedes ignorar este correo.</p>
    </div>
    """

    nombre_remitente, correo_remitente = _parsear_remitente(
        settings.EMAIL_FROM
    )

    payload = {
        "sender": {
            "name": nombre_remitente,
            "email": correo_remitente
        },
        "to": [{"email": email_destino}],
        "subject": asunto,
        "htmlContent": html
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }

    respuesta = requests.post(
        BREVO_API_URL,
        json=payload,
        headers=headers,
        timeout=15
    )

    respuesta.raise_for_status()

    return respuesta.json()
