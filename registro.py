# registro.py
import requests

API_URL = "http://api-todo.mteam.com.ar/api/v1/registro"

def registrar_usuario(nombre, apellido, usuario, password):
    payload = {
        "nombre": nombre,
        "apellido": apellido,
        "usuario": usuario,
        "password": password
    }

    try:
        response = requests.post(API_URL, json=payload)

        # Capturamos el contenido bruto de la respuesta
        print("Código de estado:", response.status_code)
        print("Respuesta cruda:", response.text)

        # Intentamos parsear como JSON
        data = response.json()
        print("Respuesta como JSON:", data)  # 🔍 Imprimimos el JSON real

        if response.status_code == 201:
            return {"success": True, "message": data.get("message")}
        else:
            return {"success": False, "error": data.get("message", "Error en el registro")}

    except Exception as e:
        return {"success": False, "error": str(e)}

