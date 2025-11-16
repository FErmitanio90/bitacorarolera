# dashboard frontend
import requests
import json

# === IMPORTANTE: URL CORRECTA DEL BACKEND ===
API_URL = "https://nucleobitacora.onrender.com/api/dashboard"

JWT_TOKEN = None

def set_token(token):
    """Guarda el JWT luego del login."""
    global JWT_TOKEN
    JWT_TOKEN = token


def get_headers():
    """Headers estándar incluyendo JSON + Bearer Token."""
    headers = {
        "Content-Type": "application/json"
    }
    if JWT_TOKEN:
        headers["Authorization"] = f"Bearer {JWT_TOKEN}"
    return headers
# ============================
#      AGREGAR SESIONES
# ============================
def agregar_sesiones(cronica, numero_de_sesion, fecha, resumen):
    payload = {
        "cronica": cronica,
        "numero_de_sesion": numero_de_sesion,
        "fecha": fecha,
        "resumen": resumen
    }
    
    headers = get_headers()
    print(f"\n[DEBUG] POST {API_URL}")
    print(f"[DEBUG] Headers: {headers}")
    print(f"[DEBUG] Payload: {payload}")

    try:
        response = requests.post(API_URL, json=payload, headers=headers)

        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Respuesta cruda: {response.text}")

        # Intentar parsear JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Respuesta no válida del servidor ({response.status_code})",
                "detail": response.text
            }

        if response.status_code == 201:
            return {"success": True, "message": data.get("msg", "Sesión creada.")}
        elif response.status_code == 401:
            return {
                "success": False,
                "error": "Token inválido o expirado.",
                "detail": data.get("msg")
            }
        elif response.status_code == 400:
            return {
                "success": False,
                "error": "Datos inválidos.",
                "detail": data.get("error", data.get("msg"))
            }
        else:
            return {
                "success": False,
                "error": f"Error del servidor ({response.status_code})",
                "detail": data.get("msg", data.get("error"))
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "No se pudo conectar al servidor (Render está dormido?)."
        }
    except Exception as e:
        return {"success": False, "error": f"Error inesperado: {e}"}


# ============================
#      LISTAR SESIONES
# ============================
def listar_sesiones():
    print(f"\n[DEBUG] GET {API_URL}")

    try:
        response = requests.get(API_URL, headers=get_headers())
        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Respuesta: {response.text}")

        try:
            data = response.json()
        except:
            return {
                "success": False,
                "error": "El servidor devolvió algo que no es JSON.",
                "detail": response.text
            }

        if response.status_code == 200:
            return {"success": True, "tareas": data}
        elif response.status_code == 401:
            return {"success": False, "error": "Token inválido o expirado"}
        else:
            return {
                "success": False,
                "error": f"Error {response.status_code}",
                "detail": data.get("msg")
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================
#      EDITAR SESIONES
# ============================
def editar_sesiones(idsesion, cronica=None, juego=None, numero_de_sesion=None, fecha=None, resumen=None):
    payload = {}

    if cronica is not None:
        payload["cronica"] = cronica
    if juego is not None:
        payload["juego"] = juego
    if numero_de_sesion is not None:
        payload["numero_de_sesion"] = numero_de_sesion
    if fecha is not None:
        payload["fecha"] = fecha
    if resumen is not None:
        payload["resumen"] = resumen

    url = f"{API_URL}/{idsesion}"

    print(f"\n[DEBUG] PUT {url}")
    print(f"[DEBUG] Payload: {payload}")

    try:
        response = requests.put(url, json=payload, headers=get_headers())
        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Respuesta: {response.text}")

        data = response.json()

        if response.status_code == 200:
            return {"success": True, "message": data.get("msg", "Sesión actualizada.")}
        else:
            return {
                "success": False,
                "error": data.get("msg", "Error al editar."),
                "detail": data.get("error")
            }

    except Exception as e:
        return {"success": False, "error": str(e)}
# ============================
#      ELIMINAR SESIÓN
# ============================
def eliminar_sesiones(idsesion):
    url = f"{API_URL}/{idsesion}"
    print(f"\n[DEBUG] DELETE {url}")

    try:
        response = requests.delete(url, headers=get_headers())
        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Respuesta: {response.text}")

        if response.status_code == 200:
            return {"success": True, "message": "Sesión eliminada"}
        else:
            data = response.json()
            return {
                "success": False,
                "error": data.get("msg", "Error al eliminar"),
                "detail": data.get("error")
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
