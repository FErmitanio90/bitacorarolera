from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, Response
import requests

from login import login_externo
from dashboard import agregar_sesiones, listar_sesiones, editar_sesiones, eliminar_sesiones
from users import registrar_usuario

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# URL del backend externo
BACKEND_URL = "https://nucleobitacora.onrender.com"

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

@app.route('/', methods=['POST'])
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
            juego = request.form.get("juego")
            director = request.form.get("director")
            jugadores = request.form.get("jugadores")
            numero_de_sesion = request.form.get("numero_de_sesion")
            fecha = request.form.get("fecha")
            resumen = request.form.get("resumen")

            print(f"cronica={cronica}, numero={numero_de_sesion}, fecha={fecha}, resumen={resumen}")

            try:
                payload = {
                    "cronica": cronica,
                    "juego": juego,
                    "director": request.form.get("director"),
                    "jugadores": request.form.get("jugadores"),
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

        if response.status_code != 200:
            flash("No se pudo obtener la lista de sesiones.", "danger")
            return redirect(url_for("dashboard_view"))

        sesiones = response.json()

        # Buscar la sesión
        sesion = next((s for s in sesiones if int(s.get("idsesion")) == id_sesion), None)

        if not sesion:
            flash(f"No se encontró la sesión #{id_sesion}.", "warning")
            return redirect(url_for("dashboard_view"))

        return render_template("editar_sesion_form.html", sesion=sesion)

    except Exception as e:
        print("❌ Excepción:", e)
        flash("Error al cargar la sesión.", "danger")
        return redirect(url_for("dashboard_view"))

@app.route("/editar_sesion_submit", methods=["POST"])
def editar_sesion_submit():
    token = session.get("access_token")
    if not token:
        flash("Debe iniciar sesión.", "warning")
        return redirect(url_for("login_view"))

    id_sesion = request.form.get("idsesion")

    data = {
        "cronica": request.form.get("cronica"),
        "juego": request.form.get("juego"),
        "director": request.form.get("director"),
        "jugadores": request.form.get("jugadores"),
        "numero_de_sesion": request.form.get("numero_de_sesion"),
        "fecha": request.form.get("fecha"),
        "resumen": request.form.get("resumen")
    }

    url = f"{BACKEND_URL}/dashboard/{id_sesion}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(url, json=data, headers=headers)

        if response.status_code == 200:
            flash("Sesión actualizada correctamente.", "success")
        else:
            print("❌ Error PUT:", response.text)
            flash("No se pudo actualizar la sesión.", "danger")

    except Exception as e:
        print("❌ Excepción:", e)
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
        "juego": request.form.get("juego"),
        "director": request.form.get("director"),
        "jugadores": request.form.get("jugadores"),
        "numero_de_sesion": request.form.get("numero_de_sesion"),
        "fecha": request.form.get("fecha"),
        "resumen": request.form.get("resumen")
    }

    url = f"{BACKEND_URL}/dashboard/{id_sesion}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(url, json=data, headers=headers)

        if response.status_code == 200:
            flash("Sesión actualizada correctamente.", "success")
        else:
            print("❌ Error PUT:", response.text)
            flash("No se pudo actualizar la sesión.", "danger")

    except Exception as e:
        print("❌ Error PUT:", e)
        flash("Error al intentar actualizar la sesión.", "danger")

    return redirect(url_for("dashboard_view"))

@app.route("/download_session/<int:idsesion>", methods=["GET"])
def download_session_proxy(idsesion):
    # 1) recuperar token del session del usuario
    token = session.get("access_token")
    if not token:
        flash("Debe iniciar sesión para descargar.", "warning")
        return redirect(url_for("login_view"))

    # 2) construir URL objetivo en el backend (txt endpoint que creaste)
    backend_endpoint = f"{BACKEND_URL}/dashboard/{idsesion}/pdf"

    try:
        # 3) llamar al backend con Authorization y stream=True
        resp = requests.get(
            backend_endpoint,
            headers={"Authorization": f"Bearer {token}"},
            stream=True,
            timeout=30
        )
    except requests.exceptions.RequestException as e:
        flash("No se pudo conectar al backend para descargar el archivo.", "danger")
        return redirect(url_for("dashboard_view"))

    # 4) si backend responde con error (404,401,405...), reencolar mensaje
    if resp.status_code != 200:
        try:
            data = resp.json()
            msg = data.get("msg", data.get("error", resp.text))
        except Exception:
            msg = resp.text or f"Error {resp.status_code}"
        flash(f"No se pudo descargar: {msg}", "warning")
        return redirect(url_for("dashboard_view"))

    # 5) stream del contenido al navegador, preservando headers (Content-Disposition)
    headers_to_forward = {}
    if "content-disposition" in resp.headers:
        headers_to_forward["Content-Disposition"] = resp.headers["content-disposition"]
    if "content-type" in resp.headers:
        headers_to_forward["Content-Type"] = resp.headers["content-type"]

    def generate():
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return Response(generate(), headers=headers_to_forward)

# Personajes
@app.route("/personajes/crear", methods=["POST"])
def crear_personaje_view():
    token = session.get("jwt") or session.get("access_token")

    if not token:
        flash("Debes iniciar sesión.", "warning")
        return redirect(url_for("login_view"))

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {
        "cronica": request.form.get("cronica"),
        "juego": request.form.get("juego"),
        "nombre": request.form.get("nombre"),
        "apellido": request.form.get("apellido"),
        "edad": request.form.get("edad"),
        "genero": request.form.get("genero"),
        "ocupacion": request.form.get("ocupacion"),
        "etnia": request.form.get("etnia"),
        "descripcion": request.form.get("descripcion"),
        "historia": request.form.get("historia"),
        "inventario": request.form.get("inventario"),
        "notas": request.form.get("notas"),
    }

    try:
        response = requests.post(f"{BACKEND_URL}/personajes", json=data, headers=headers)

        if response.status_code == 201:
            flash("¡Personaje creado con éxito!", "success")
        else:
            flash("Error creando personaje", "danger")

    except Exception as e:
        flash(f"Error conectando al backend: {e}", "danger")

    return redirect(url_for("personajes_view"))


@app.route("/personajes", methods=["GET"])
def personajes_view():
    username = session.get("username")
    token = session.get("jwt") or session.get("access_token")

    if not token:
        flash("Debes iniciar sesión", "warning")
        return redirect(url_for("login_view"))

    API_URL = "https://nucleobitacora.onrender.com/api/personajes"

    try:
        response = requests.get(API_URL, headers={"Authorization": f"Bearer {token}"})
        personajes = response.json() if response.status_code == 200 else []
        if response.status_code != 200:
            flash("Error obteniendo personajes", "danger")
    except Exception:
        personajes = []
        flash("No se pudo conectar al backend", "danger")

    return render_template("personajes.html", personajes=personajes, username=username)

@app.route("/personajes/eliminar/<int:id_personaje>", methods=["POST"])
def eliminar_personaje_view(id_personaje):
    token = session.get("jwt") or session.get("access_token")

    if not token:
        flash("Debes iniciar sesión.", "warning")
        return redirect(url_for("login_view"))

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        url = f"{BACKEND_URL}/personajes/{id_personaje}"
        response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            flash("Personaje eliminado correctamente.", "success")
        else:
            flash(f"Error eliminando personaje ({response.status_code})", "danger")

    except Exception as e:
        flash(f"Error conectando al backend: {e}", "danger")

    return redirect(url_for("personajes_view"))


@app.route('/personajes/editar/<int:id_personaje>', methods=['GET'])
def editar_personaje_view(id_personaje):
    token = session.get("access_token")
    if not token:
        flash("Debe iniciar sesión.", "warning")
        return redirect(url_for("index"))

    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BACKEND_URL}/personajes/{id_personaje}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            flash("No se pudo obtener el personaje solicitado.", "danger")
            return redirect(url_for("personajes_view"))

        personaje = response.json()

        return render_template("editar_personaje_form.html", personaje=personaje)

    except Exception as e:
        print("❌ Excepción:", e)
        flash("Error al cargar el personaje.", "danger")
        return redirect(url_for("personajes_view"))
@app.route('/personajes/editar_submit', methods=['POST'])
def editar_personaje_submit():
    token = session.get("access_token")
    if not token:
        flash("Debe iniciar sesión.", "warning")
        return redirect(url_for("index"))

    id_personaje = request.form.get("id")

    data = {
        "cronica": request.form.get("cronica"),
        "juego": request.form.get("juego"),
        "nombre": request.form.get("nombre"),
        "apellido": request.form.get("apellido"),
        "edad": request.form.get("edad"),
        "genero": request.form.get("genero"),
        "ocupacion": request.form.get("ocupacion"),
        "etnia": request.form.get("etnia"),
        "descripcion": request.form.get("descripcion"),
        "historia": request.form.get("historia"),
        "inventario": request.form.get("inventario"),
        "notas": request.form.get("notas")
    }

    url = f"{BACKEND_URL}/personajes/{id_personaje}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(url, json=data, headers=headers)

        if response.status_code == 200:
            flash("Personaje actualizado correctamente.", "success")
        else:
            print("❌ Error PUT:", response.text)
            flash("No se pudo actualizar el personaje.", "danger")

    except Exception as e:
        print("❌ Excepción:", e)
        flash("Error interno al actualizar personaje.", "danger")

    return redirect(url_for("personajes_view"))
#Descargar personaje PDF
@app.route('/personajes/<int:id_personaje>/download_pdf', methods=['GET'])
def download_personaje_pdf(id_personaje):
    token = session.get("access_token")
    if not token:
        flash("Debe iniciar sesión para descargar.", "warning")
        return redirect(url_for("index"))

    backend_endpoint = f"{BACKEND_URL}/personajes/{id_personaje}/pdf"

    try:
        resp = requests.get(
            backend_endpoint,
            headers={"Authorization": f"Bearer {token}"},
            stream=True,
            timeout=30
        )
    except requests.exceptions.RequestException as e:
        flash("No se pudo conectar al backend para descargar el archivo.", "danger")
        return redirect(url_for("personajes_view"))

    if resp.status_code != 200:
        try:
            data = resp.json()
            msg = data.get("msg", data.get("error", resp.text))
        except Exception:
            msg = resp.text or f"Error {resp.status_code}"
        flash(f"No se pudo descargar: {msg}", "warning")
        return redirect(url_for("personajes_view"))

    headers_to_forward = {}
    if "content-disposition" in resp.headers:
        headers_to_forward["Content-Disposition"] = resp.headers["content-disposition"]
    if "content-type" in resp.headers:
        headers_to_forward["Content-Type"] = resp.headers["content-type"]

    def generate():
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return Response(generate(), headers=headers_to_forward)

# Logout
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for('index'))

# Inicio del servidor
if __name__ == "__main__":
    app.run(debug=True, port=5000)