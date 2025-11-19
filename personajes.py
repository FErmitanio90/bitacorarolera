# personajes.py (FRONTEND)

import requests
import json

# Token JWT compartido, igual que en dashboard.py
JWT_TOKEN = None

# ============================
#     CONFIGURACIÓN API
# ============================
API_URL = "https://nucleobitacora.onrender.com/api/personajes"


def set_token(token):
    """Guarda el JWT luego del login (misma lógica que dashboard.py)."""
    global JWT_TOKEN
    JWT_TOKEN = token


def get_headers():
    """Headers estándar con JSON + Bearer Token (igual que dashboard.py)."""
    headers = {"Content-Type": "application/json"}
    if JWT_TOKEN:
        headers["Authorization"] = f"Bearer {JWT_TOKEN}"
    return headers


# ============================
#      FUNCIÓN UTIL
# ============================
def safe_json(response):
    """
    Evita errores si el backend no puede parsear JSON.
    Devuelve diccionario con info útil en caso de error.
    """
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"msg": "Respuesta inválida del servidor", "raw": response.text}


# ============================
#      AGREGAR PERSONAJE
# ============================
def agregar_personaje(cronica, juego, nombre, apellido, edad, genero, ocupacion, etnia, descripcion, historia, inventario, notas):
    payload = {
        "cronica": cronica,
        "juego": juego,
        "nombre": nombre,
        "apellido": apellido,
        "edad": edad,
        "genero": genero,
        "ocupacion": ocupacion,
        "etnia": etnia,
        "descripcion": descripcion,
        "historia": historia,
        "inventario": inventario,
        "notas": notas
    }

    try:
        response = requests.post(API_URL, json=payload, headers=get_headers())
        data = safe_json(response)

        if response.status_code == 201:
            return {"success": True, "message": data.get("msg", "Personaje creado")}

        return {"success": False, "error": data.get("msg", "Error al agregar personaje")}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================
#      LISTAR PERSONAJES
# ============================
def listar_personajes():
    print(f"\n[DEBUG] GET {API_URL}")
    try:
        response = requests.get(API_URL, headers=get_headers())
        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Respuesta: {response.text}")

        try:
            data = response.json()
        except:
            return {"success": False, "error": "Respuesta no JSON", "detail": response.text}

        if response.status_code == 200:
            return {"success": True, "personajes": data}

        if response.status_code == 401:
            return {"success": False, "error": "Token inválido o expirado"}

        return {"success": False, "error": f"Error {response.status_code}", "detail": data}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================
#      EDITAR PERSONAJE
# ============================
def editar_personajes(idpersonaje, **kwargs):
    payload = {k: v for k, v in kwargs.items() if v is not None}

    try:
        response = requests.put(f"{API_URL}/{idpersonaje}", json=payload, headers=get_headers())
        data = safe_json(response)

        if response.status_code == 200:
            return {"success": True, "message": data.get("msg", "Personaje actualizado")}

        return {"success": False, "error": data.get("msg", "Error al actualizar personaje")}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================
#      ELIMINAR PERSONAJE
# ============================
def eliminar_personaje(idpersonaje):
    try:
        response = requests.delete(f"{API_URL}/{idpersonaje}", headers=get_headers())
        data = safe_json(response)

        if response.status_code == 200:
            return {"success": True, "message": data.get("msg", "Personaje eliminado")}

        return {"success": False, "error": data.get("msg", "Error al eliminar personaje")}

    except Exception as e:
        return {"success": False, "error": str(e)}


