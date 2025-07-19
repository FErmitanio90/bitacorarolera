# tareas.py
import requests

API_URL = "http://api-todo.mteam.com.ar/api/v1/tareas"

def agregar_tareas(nombre, usuario, descripcion, fecha_limite, activa, token=None):
    payload = {
        "nombre": nombre,
        "usuario": usuario,
        "descripcion": descripcion,
        "fecha_limite": fecha_limite,
        "activa": activa
    }

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        print("Código de estado:", response.status_code)
        print("Respuesta cruda:", response.text)

        data = response.json()
        if response.status_code == 201:
            return {"success": True, "message": data.get("message")}
        else:
            return {"success": False, "error": data.get("message", "Error al agregar la tarea")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def listar_tareas(token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        response = requests.get(API_URL, headers=headers)
        print("Código de estado:", response.status_code)
        print("Respuesta cruda:", response.text)

        data = response.json()
        print("Respuesta como JSON:", data)

        if response.status_code == 200 and data.get("status") is True:
            tareas = data.get("data", [])
            return {"success": True, "tareas": tareas}
        else:
            return {
                "success": False,
                "error": data.get("message", "Error al listar tareas")
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def editar_tareas(id_tarea, nombre=None, descripcion=None, fecha_limite=None, activa=None, token=None):

    if token is None:
        return {"success": False, "error": "El token de autorización es requerido."}

    payload = {}

    if nombre is not None:
        payload["nombre"] = nombre
    if descripcion is not None:
        payload["descripcion"] = descripcion
    if fecha_limite is not None:
        payload["fecha_limite"] = fecha_limite
    if activa is not None:
        payload["activa"] = activa  # Usar "activa" según la documentación

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(f"{API_URL}/{id_tarea}", json=payload, headers=headers)
        print("Código de estado:", response.status_code)
        print("Respuesta cruda:", response.text)

        data = response.json()

        if response.status_code == 200:
            if data.get("status") is True:
                return {"success": True, "message": data.get("message", "Tarea editada exitosamente.")}
            else:
                return {"success": False, "error": data.get("message", "Error lógico al editar la tarea.")}
        else:
            return {"success": False, "error": data.get("message", f"Error del servidor: {response.status_code}")}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Error de conexión: {e}"}
    except ValueError as e:
        return {"success": False, "error": f"Error al decodificar la respuesta JSON: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Ocurrió un error inesperado: {e}"}

def eliminar_tareas(id, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        response = requests.delete(f"{API_URL}/{id}", headers=headers)
        print("Código de estado:", response.status_code)
        print("Respuesta cruda:", response.text)

        if response.status_code == 204:
            return {"success": True, "message": "Tarea eliminada exitosamente"}
        else:
            try:
                data = response.json()
                return {"success": False, "error": data.get("message", "Error al eliminar la tarea")}
            except Exception:
                return {"success": False, "error": "Respuesta no válida del servidor"}
    except Exception as e:
        return {"success": False, "error": str(e)}
