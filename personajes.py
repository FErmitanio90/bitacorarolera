# personajes.py (FRONTEND)

import requests
import json
from login import login_externo
JWT_TOKEN = None

# IMPORTANTE: Cargar el token JWT
# Ajustá esto según donde lo guardes realmente
from session import JWT_TOKEN  

API_URL = "https://nucleobitacora.onrender.com/api/personajes"

def set_token(token):
    """Guarda el JWT luego del login."""
    global JWT_TOKEN
    JWT_TOKEN = token

def get_headers():
    """Headers estándar incluyendo JSON + Bearer Token."""
    headers = {"Content-Type": "application/json"}
    if JWT_TOKEN:
        headers["Authorization"] = f"Bearer {JWT_TOKEN}"
    return headers


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

        try:
            data = response.json()
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Respuesta no válida del servidor ({response.status_code})",
                "detail": response.text
            }

        if response.status_code == 201:
            return {"success": True, "message": data.get("msg", "Personaje creado")}

        if response.status_code == 400:
            return {"success": False, "error": data.get("msg", "Error al agregar el personaje")}

        if response.status_code == 401:
            return {"success": False, "error": "No autorizado. Por favor, inicie sesión."}

        return {
            "success": False,
            "error": data.get("msg", "Error al agregar el personaje"),
            "detail": data
        }

    except Exception as e:
        return {"success": False, "error": str(e)}



# ============================
#      LISTAR PERSONAJES
# ============================
def listar_personajes():
    try:
        response = requests.get(API_URL, headers=get_headers())

        try:
            data = response.json()
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Respuesta no válida del servidor ({response.status_code})",
                "detail": response.text
            }

        if response.status_code == 200:
            return {"success": True, "personajes": data}

        if response.status_code == 401:
            return {"success": False, "error": "No autorizado. Por favor, inicie sesión."}

        return {
            "success": False,
            "error": "Error al obtener los personajes",
            "detail": data
        }

    except Exception as e:
        return {"success": False, "error": str(e)}



# ============================
#      EDITAR PERSONAJE
# ============================
def editar_personajes(idpersonaje, cronica=None, juego=None, nombre=None, apellido=None, edad=None, genero=None, ocupacion=None, etnia=None, descripcion=None, historia=None, inventario=None, notas=None):
    payload = {}

    if cronica is not None: payload["cronica"] = cronica
    if juego is not None: payload["juego"] = juego
    if nombre is not None: payload["nombre"] = nombre
    if apellido is not None: payload["apellido"] = apellido
    if edad is not None: payload["edad"] = edad
    if genero is not None: payload["genero"] = genero
    if ocupacion is not None: payload["ocupacion"] = ocupacion
    if etnia is not None: payload["etnia"] = etnia
    if descripcion is not None: payload["descripcion"] = descripcion
    if historia is not None: payload["historia"] = historia
    if inventario is not None: payload["inventario"] = inventario
    if notas is not None: payload["notas"] = notas

    try:
        response = requests.put(f"{API_URL}/{idpersonaje}", json=payload, headers=get_headers())

        try:
            data = response.json()
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Respuesta no válida del servidor ({response.status_code})",
                "detail": response.text
            }

        if response.status_code == 200:
            return {"success": True, "message": data.get("msg", "Personaje actualizado")}

        if response.status_code == 400:
            return {"success": False, "error": data.get("msg", "Error al actualizar el personaje")}

        if response.status_code == 401:
            return {"success": False, "error": "No autorizado. Por favor, inicie sesión."}

        return {
            "success": False,
            "error": data.get("msg", "Error al actualizar el personaje"),
            "detail": data
        }

    except Exception as e:
        return {"success": False, "error": str(e)}



# ============================
#      ELIMINAR PERSONAJE
# ============================
def eliminar_personaje(idpersonaje):
    try:
        response = requests.delete(f"{API_URL}/{idpersonaje}", headers=get_headers())

        try:
            data = response.json()
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Respuesta no válida del servidor ({response.status_code})",
                "detail": response.text
            }

        if response.status_code == 200:
            return {"success": True, "message": data.get("msg", "Personaje eliminado")}

        if response.status_code == 400:
            return {"success": False, "error": data.get("msg", "Error al eliminar el personaje")}

        if response.status_code == 401:
            return {"success": False, "error": "No autorizado. Por favor, inicie sesión."}

        return {
            "success": False,
            "error": data.get("msg", "Error al eliminar el personaje"),
            "detail": data
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
