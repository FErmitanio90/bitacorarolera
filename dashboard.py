import requests
import json # Importar para mejor manejo de errores de JSON

API_URL = "https://nucleobitacora.onrender.com/dashboard"

# Variable global para guardar el token una vez hecho el login
JWT_TOKEN = None

def set_token(token):
    """Permite guardar el JWT después del login."""
    global JWT_TOKEN
    JWT_TOKEN = token

def get_headers():
    """Devuelve los headers con el JWT y Content-Type."""
    headers = {
        # CLAVE: Asegura que el backend sepa que le estamos enviando JSON
        "Content-Type": "application/json" 
    }
    if JWT_TOKEN:
        # Formato estándar para enviar el token
        headers["Authorization"] = f"Bearer {JWT_TOKEN}"
    return headers

def agregar_sesiones(cronica, numero_de_sesion, fecha, resumen):
    payload = {
        "cronica": cronica,
        "numero_de_sesion": numero_de_sesion,
        "fecha": fecha,
        "resumen": resumen
    }
    
    headers = get_headers()
    print(f"\n[DEBUG] Petición a POST {API_URL}")
    print(f"[DEBUG] Headers: {headers}")

    try:
        # No es necesario pasar 'headers' si se usa 'json=payload', 
        # pero es más explícito y mejor si se modifican los headers en get_headers()
        response = requests.post(API_URL, json=payload, headers=headers)
        
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta cruda: {response.text}")

        # Intenta parsear la respuesta JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            # Captura si la respuesta no es un JSON válido (ej. HTML de error)
            return {"success": False, "error": f"Respuesta inválida del servidor: {response.status_code}", "detail": response.text}

        if response.status_code == 201:
            return {"success": True, "message": data.get("msg", "Sesión creada.")}
        elif response.status_code == 401:
             # Manejo específico si el token falla
            return {"success": False, "error": "Fallo de autenticación (Token inválido o expirado).", "detail": data.get("msg")}
        elif response.status_code == 400:
            # Manejo de errores de validación de datos
            return {"success": False, "error": "Datos de sesión incorrectos.", "detail": data.get("error", data.get("msg"))}
        else:
            return {"success": False, "error": f"Error del servidor ({response.status_code})", "detail": data.get("msg", data.get("error"))}
            
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Error de conexión. Asegúrate de que Flask esté corriendo en 5001."}
    except Exception as e:
        return {"success": False, "error": f"Error inesperado: {str(e)}"}

# --- Las otras funciones (listar, editar, eliminar) también se benefician de la función get_headers() ---

def listar_sesiones():
    try:
        response = requests.get(API_URL, headers=get_headers())
        print(f"\n[DEBUG] Petición a GET {API_URL}")
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta cruda: {response.text}")

        data = response.json()
        
        if response.status_code == 200:
            return {"success": True, "tareas": data}
        elif response.status_code == 401:
             return {"success": False, "error": "Fallo de autenticación (Token inválido o expirado)."}
        else:
            return {"success": False, "error": f"Error al listar sesiones ({response.status_code})", "detail": data.get("msg")}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def editar_sesiones(idsesion, cronica=None, numero_de_sesion=None, fecha=None, resumen=None):
    payload = {}
    # ... (construcción del payload) ...
    
    try:
        response = requests.put(f"{API_URL}/{idsesion}", json=payload, headers=get_headers())
        print(f"\n[DEBUG] Petición a PUT {API_URL}/{idsesion}")
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta cruda: {response.text}")

        data = response.json()
        if response.status_code == 200:
            return {"success": True, "message": data.get("msg", "Sesión actualizada exitosamente.")}
        else:
            return {"success": False, "error": data.get("msg", "Error al editar la sesión."), "detail": data.get("error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def eliminar_sesiones(idsesion):
    try:
        response = requests.delete(f"{API_URL}/{idsesion}", headers=get_headers())
        print(f"\n[DEBUG] Petición a DELETE {API_URL}/{idsesion}")
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta cruda: {response.text}")

        if response.status_code == 200:
            return {"success": True, "message": "Sesión eliminada exitosamente"}
        else:
            data = response.json()
            return {"success": False, "error": data.get("msg", "Error al eliminar la sesión"), "detail": data.get("error")}
    except Exception as e:
        return {"success": False, "error": str(e)}
