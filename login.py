# login.py
import requests

API_URL = "http://api-todo.mteam.com.ar/api/v1/login"

def login_externo(usuario, password):
    payload = {
        "usuario": usuario,
        "password": password
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") and data.get("data"):
                subdata = data["data"]
                return {
                    "success": True,
                    "token": subdata.get("JWT Token"),
                    "usuario": subdata.get("usuario")
                }

            else:
                return {"success": False, "error": data.get("message")}
        else:
            return {"success": False, "error": "Código de estado: " + str(response.status_code)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    

