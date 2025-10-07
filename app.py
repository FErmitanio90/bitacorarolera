from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
import requests

from login import login_externo
from dashboard import agregar_sesiones, listar_sesiones, editar_sesiones, eliminar_sesiones
from users import registrar_usuario

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# URL del backend externo
BACKEND_URL = "https://apiroleraback.onrender.com"

# Registro de usuario
@app.route("/registro", methods=["GET"])
def mostrar_registro():
    return render_template("registro.html")

@app.route("/registro", methods=["POST"])
def registrar():
    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    usuario = request.form.get("usuario")
    password = request.form.get("password")

    if not nombre or not apellido or not usuario or not password:
        flash("Todos los campos son obligatorios", "danger")
        return redirect(url_for("mostrar_registro"))

    resultado = registrar_usuario(nombre, apellido, usuario, password)

    if resultado["success"]:
        flash("Registro exitoso. Ahora podés iniciar sesión.", "success")
        return redirect(url_for("index"))
    else:
        flash("Error en el registro: " + resultado["error"], "danger")
        return redirect(url_for("mostrar_registro"))

# Login
@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get("usuario")
    password = request.form.get("password")

    if not usuario or not password:
        flash("Usuario y contraseña son requeridos", "danger")
        return redirect(url_for("index"))

    resultado = login_externo(usuario, password)

    if resultado["success"]:
        # Guardamos usuario y token externo en la sesión
        session["usuario"] = resultado["usuario"]
        session["access_token"] = resultado["token"]

        flash("Login exitoso", "success")
        return redirect(url_for("dashboard_view"))
    else:
        flash("Error de login: " + resultado["error"], "danger")
        return redirect(url_for("index"))

# Dashboard protegido (con token del backend externo)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard_view():
    usuario = session.get("usuario")
    token = session.get("access_token")

    if not usuario or not token:
        flash("No hay sesión activa. Por favor, inicia sesión.", "danger")
        return redirect(url_for("index"))

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # --- POST (Manejo de Formularios: Agregar y Eliminar) ---
    if request.method == "POST":
        accion = request.form.get("accion")
        print(f"\n[DEBUG FRONT] Acción recibida en POST: {accion}")

        # Lógica para AGREGAR Sesión
        if accion == "agregar":
            cronica = request.form.get("cronica")
            numero_de_sesion = request.form.get("numero_de_sesion")
            fecha = request.form.get("fecha")
            resumen = request.form.get("resumen")

            print(f"cronica={cronica}, numero={numero_de_sesion}, fecha={fecha}, resumen={resumen}")

            try:
                payload = {
                    "cronica": cronica,
                    "numero_de_sesion": int(numero_de_sesion) if numero_de_sesion else None,
                    "fecha": fecha,
                    "resumen": resumen
                }
                print(f"[DEBUG FRONT] Payload enviado al backend: {payload}")
                response = requests.post(f"{BACKEND_URL}/dashboard", json=payload, headers=headers)
                
                if response.status_code == 201:
                    flash("¡Sesión creada exitosamente!", "success")
                else:
                    data = response.json() if response.content else {}
                    flash(f"Error ({response.status_code}): {data.get('msg', 'Fallo en la API')}", "warning")

            except ValueError:
                flash("Número de sesión inválido.", "danger")
            except requests.exceptions.ConnectionError:
                flash("Backend no disponible (Error de conexión).", "danger")
            except Exception as e:
                flash(f"Error inesperado al agregar: {e}", "danger")
        
        # 🎯 Lógica para ELIMINAR Sesión (CORRECCIÓN APLICADA)
        elif accion == "eliminar":
            id_sesion = request.form.get("id")
            print(f"[DEBUG FRONT] Intentando eliminar sesión con ID: {id_sesion}")
            
            try:
                # Usa requests.delete, apuntando a un endpoint que acepte el ID (ej: /dashboard/123)
                response = requests.delete(f"{BACKEND_URL}/dashboard/{id_sesion}", headers=headers)
                
                print(f"[DEBUG FRONT] Status DELETE backend: {response.status_code}")

                if response.status_code == 200:
                    flash("Sesión eliminada correctamente.", "success")
                elif response.status_code == 404:
                    flash("Error: Sesión no encontrada.", "danger")
                else:
                    data = response.json() if response.content else {}
                    flash(f"Error al eliminar ({response.status_code}): {data.get('msg', 'Fallo en la API')}", "warning")
            except requests.exceptions.ConnectionError:
                flash("Backend no disponible (Error de conexión).", "danger")
            except Exception as e:
                flash(f"Error inesperado al eliminar: {e}", "danger")
                
        return redirect(url_for("dashboard_view"))

    # --- GET (Listado de Sesiones) ---
    username_a_mostrar = usuario.get('nombre') if isinstance(usuario, dict) else usuario

    try:
        response = requests.get(f"{BACKEND_URL}/dashboard", headers=headers)
        print(f"[DEBUG FRONT] GET backend status: {response.status_code}")
        print(f"[DEBUG FRONT] GET respuesta: {response.text}")

        if response.status_code == 200:
            sesiones = response.json()
            return render_template("dashboard.html", tareas=sesiones, username=username_a_mostrar)
        else:
            flash(f"Error ({response.status_code}): {response.json().get('msg', 'Error al obtener sesiones')}", "warning")
            return render_template("dashboard.html", tareas=[], username=username_a_mostrar)

    except Exception as e:
        flash(f"Error conectando al backend: {e}", "danger")
        return render_template("dashboard.html", tareas=[], username=username_a_mostrar)

@app.route("/editar_sesion/<int:id_sesion>", methods=["GET"])
def editar_sesion_view(id_sesion):
    token = session.get("access_token")
    if not token:
        flash("Debe iniciar sesión.", "warning")
        return redirect(url_for("login_view"))

    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BACKEND_URL}/dashboard"
        response = requests.get(url, headers=headers)

        print("===== DEBUG EDITAR SESIÓN =====")
        print("ID buscado:", id_sesion)
        print("Status code backend:", response.status_code)
        print("Texto backend:", response.text)

        if response.status_code != 200:
            flash("No se pudo obtener la lista de sesiones.", "danger")
            return redirect(url_for("dashboard_view"))

        sesiones = response.json()
        print("Sesiones decodificadas JSON:", sesiones)

        # Buscar la sesión específica
        sesion = None
        for s in sesiones:
            print("Comparando con:", s.get("idsesion"))
            if int(s.get("idsesion")) == int(id_sesion):
                sesion = s
                break

        if not sesion:
            flash(f"No se encontró la sesión #{id_sesion}.", "warning")
            return redirect(url_for("dashboard_view"))

        print("Sesión encontrada:", sesion)
        print("===== FIN DEBUG =====")

        return render_template("editar_sesion_form.html", sesion=sesion)

    except Exception as e:
        print("❌ Excepción capturada:", e)
        flash("Error al cargar la sesión para editar.", "danger")
        return redirect(url_for("dashboard_view"))

@app.route("/editar_sesion_submit", methods=["POST"])
def editar_sesion_submit():
    token = session.get("access_token")
    if not token:
        flash("Debe iniciar sesión.", "warning")
        return redirect(url_for("login_view"))

    idsesion = request.form.get("idsesion")
    cronica = request.form.get("cronica")
    numero_de_sesion = request.form.get("numero_de_sesion")
    fecha = request.form.get("fecha")
    resumen = request.form.get("resumen")

    payload = {
        "idsesion": int(idsesion),
        "cronica": cronica,
        "numero_de_sesion": int(numero_de_sesion),
        "fecha": fecha,
        "resumen": resumen
    }

    print("[DEBUG FRONT] Enviando PUT con payload:", payload)

    try:
        response = requests.put(
            f"{BACKEND_URL}/dashboard",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        print("[DEBUG FRONT] Respuesta backend:", response.status_code, response.text)

        if response.status_code == 200:
            flash("✅ Sesión actualizada correctamente", "success")
        else:
            flash(f"❌ Error al actualizar: {response.text}", "danger")

    except Exception as e:
        print("❌ Error al conectar al backend:", e)
        flash("Error interno al actualizar sesión.", "danger")

    return redirect(url_for("dashboard_view"))


    
@app.route("/guardar_edicion_sesion/<int:id_sesion>", methods=["POST"])
def guardar_edicion_sesion(id_sesion):
    token = session.get("access_token")
    if not token:
        flash("Debe iniciar sesión.", "warning")
        return redirect(url_for("login_view"))

    data = {
        "cronica": request.form.get("cronica"),
        "numero_de_sesion": request.form.get("numero_de_sesion"),
        "fecha": request.form.get("fecha"),
        "resumen": request.form.get("resumen")
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        url = f"{BACKEND_URL}/dashboard/{id_sesion}"
        print(f"🔹 Enviando PUT a {url} con data:", data)  # ✅ log de debug

        response = requests.put(url, json=data, headers=headers)

        print(f"🔸 Status code: {response.status_code}")
        print(f"🔸 Respuesta backend: {response.text}")

        if response.status_code == 200:
            flash("Sesión actualizada correctamente.", "success")
        else:
            flash("No se pudo actualizar la sesión.", "danger")
            # Mostramos la respuesta en consola para depurar
            print("❌ PUT error:", response.text)

    except Exception as e:
        print(f"❌ Error en PUT /dashboard/{id_sesion}: {e}")
        flash("Error al intentar actualizar la sesión.", "danger")

    return redirect(url_for("dashboard_view"))



# Logout
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for('index'))

# Inicio del servidor
if __name__ == "__main__":
    app.run(debug=True, port=5000)



