import requests

API_URL = "https://nucleobitacora.onrender.com/login"

def login_externo(username, password):
    payload = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(API_URL, json=payload)

        print("--- DEBUG API EXTERNA ---")
        print("Status:", response.status_code)
        print("Headers:", response.headers)
        print("Respuesta cruda:", response.text)
        print("-------------------------")

        # Intentar parsear JSON
        try:
            data = response.json()
        except Exception:
            return {"success": False, "error": f"Respuesta no es JSON: {response.text}"}

        # ✅ Login OK
        if response.status_code == 200 and data.get("success") == True:
            return {
                "success": True,
                "usuario": data.get("usuario"),
                "token": data.get("access_token"),
                "msg": data.get("msg")
            }

        # ❌ Login fallido
        return {
            "success": False,
            "error": data.get("error", "Error desconocido"),
            "detail": data
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
