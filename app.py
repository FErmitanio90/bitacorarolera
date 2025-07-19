from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from registro import registrar_usuario
from login import login_externo
from tareas import listar_tareas, agregar_tareas, editar_tareas, eliminar_tareas
from dateutil import parser  

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# Mostrar formulario de registro
@app.route("/registro", methods=["GET"])
def mostrar_registro():
    return render_template("registro.html")

# Procesar registro
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
@app.route("/", methods=["GET"])
def index():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get("usuario")
    password = request.form.get("password")

    if not usuario or not password:
        flash("Usuario y contraseña son requeridos", "danger")
        return redirect(url_for("index"))

    resultado = login_externo(usuario, password)

    if resultado["success"]:
        session["token"] = resultado["token"]
        session["usuario"] = resultado["usuario"]
        flash("Login exitoso", "success")
        return redirect(url_for("dashboard"))
    else:
        flash("Error de login: " + resultado["error"], "danger")
        return redirect(url_for("index"))

# Dashboard: listado + alta/baja/edición
@app.route("/tareas", methods=['GET', 'POST'])
def dashboard():
    if "token" not in session:
        return redirect(url_for("index"))

    token = session["token"]
    usuario_data = session["usuario"]
    usuario_nombre = usuario_data.get("usuario")

    if request.method == 'POST':
        accion = request.form.get("accion")

        if accion == 'agregar':
            nombre = request.form.get("nombre")
            descripcion = request.form.get("descripcion")
            fecha_limite = request.form.get("fecha_limite")
            activa = request.form.get("activa") == "on"

            resultado = agregar_tareas(nombre, usuario_nombre, descripcion, fecha_limite, activa, token=token)
            flash("Tarea agregada correctamente" if resultado["success"] else f"Error al agregar tarea: {resultado['error']}", "success" if resultado["success"] else "danger")
            return redirect(url_for("dashboard"))

        elif accion == 'editar':
            id_tarea = request.form.get("id")
            nombre = request.form.get("nombre")
            descripcion = request.form.get("descripcion")
            fecha_limite = request.form.get("fecha_limite")
            activa = request.form.get("activa") == "on"

            resultado = editar_tareas(id_tarea, nombre, descripcion, fecha_limite, activa, token)
            flash("Tarea editada correctamente" if resultado["success"] else f"Error al editar tarea: {resultado['error']}", "success" if resultado["success"] else "danger")
            return redirect(url_for("dashboard"))

        elif accion == 'eliminar':
            id_tarea = request.form.get("id")
            resultado = eliminar_tareas(id_tarea, token=token)
            flash("Tarea eliminada correctamente" if resultado["success"] else f"Error al eliminar tarea: {resultado['error']}", "success" if resultado["success"] else "danger")
            return redirect(url_for("dashboard"))

    # GET: listar tareas
    tareas_result = listar_tareas(token=token)
    tareas = []

    if tareas_result["success"]:
        tareas = tareas_result["tareas"]
        for tarea in tareas:
            if 'fecha_limite' in tarea and tarea['fecha_limite']:
                try:
                    tarea['fecha_limite'] = parser.parse(tarea['fecha_limite'])
                    print(f"✔️ Parseada fecha_limite: {tarea['fecha_limite']} ({type(tarea['fecha_limite'])})")
                except Exception as e:
                    print(f"❌ Error al parsear fecha_limite: {e}")
                    tarea['fecha_limite'] = None
            else:
                tarea['fecha_limite'] = None

    else:
        flash(f"Error al listar tareas: {tareas_result.get('error', 'Error desconocido')}", "danger")

    return render_template("tareas.html", usuario=usuario_data, tareas=tareas)

# Mostrar formulario de edición
@app.route("/editar_tarea/<int:id_tarea>", methods=['GET'])
def mostrar_editar_tarea(id_tarea):
    if "token" not in session:
        return redirect(url_for("index"))

    token = session["token"]
    tareas_result = listar_tareas(token=token)
    tarea_a_editar = None

    if tareas_result["success"]:
        for tarea in tareas_result["tareas"]:
            if str(tarea.get("id")) == str(id_tarea):
                tarea_a_editar = tarea
                if 'fecha_limite' in tarea_a_editar:
                    fecha_limite_raw = tarea_a_editar['fecha_limite']
                    if fecha_limite_raw:
                        try:
                            tarea_a_editar['fecha_limite'] = datetime.strptime(fecha_limite_raw, '%Y-%m-%dT%H:%M:%S')
                        except ValueError:
                            try:
                                tarea_a_editar['fecha_limite'] = datetime.strptime(fecha_limite_raw, '%Y-%m-%dT%H:%M')
                            except ValueError:
                                try:
                                    tarea_a_editar['fecha_limite'] = datetime.strptime(fecha_limite_raw, '%Y-%m-%d %H:%M')
                                except ValueError:
                                    try:
                                        tarea_a_editar['fecha_limite'] = datetime.strptime(fecha_limite_raw.split('.')[0], '%Y-%m-%d %H:%M:%S')
                                    except ValueError:
                                        try:
                                            tarea_a_editar['fecha_limite'] = datetime.strptime(fecha_limite_raw.split(' ')[0], '%Y-%m-%d')
                                        except ValueError:
                                            tarea_a_editar['fecha_limite'] = None
                    else:
                        tarea_a_editar['fecha_limite'] = None
                break

    if not tarea_a_editar:
        flash("Tarea no encontrada para editar.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("editar_tarea_form.html", tarea=tarea_a_editar, token=token)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
