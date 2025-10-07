import requests

API_URL = "https://apiroleraback.onrender.com/login"

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

        try:
            data = response.json()
        except Exception:
            return {"success": False, "error": f"Respuesta no es JSON: {response.text}"}

        if response.status_code == 200:
            # ✅ ahora coincide con tu backend
            if data.get("success"):
                return {
                    "success": True,
                    "usuario": data.get("usuario"),
                    "token": data.get("access_token"),
                    "msg": data.get("msg")
                }
            else:
                return {"success": False, "error": data.get("msg")}
        else:
            return {"success": False, "error": data.get("error", f"Código de estado: {response.status_code}")}

    except Exception as e:
        return {"success": False, "error": str(e)}
