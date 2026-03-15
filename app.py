from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import sqlite3, re, random

app = Flask(__name__)
app.secret_key = "ciudad2024"
DATABASE = os.path.join(os.path.dirname(__file__), "database.db")

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS grupos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_grupo TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grupo_id INTEGER NOT NULL,
        nombre_estudiante TEXT NOT NULL,
        FOREIGN KEY (grupo_id) REFERENCES grupos(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS progreso_juego (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grupo_id INTEGER UNIQUE NOT NULL,
        economia INTEGER DEFAULT 50,
        medio_ambiente INTEGER DEFAULT 50,
        energia INTEGER DEFAULT 50,
        bienestar_social INTEGER DEFAULT 50,
        ronda_actual INTEGER DEFAULT 1,
        FOREIGN KEY (grupo_id) REFERENCES grupos(id))""")
    conn.commit(); conn.close()

if __name__ == "__main__" or os.environ.get("RENDER"):
    init_db()

PREGUNTAS = [
    # ── PYTHON ──────────────────────────────────────────────────────────────
    {"pregunta": "En Python, cual es la funcion para mostrar texto en pantalla?",
     "opciones": ["write()", "print()", "show()", "display()"], "correcta": 1, "tema": "Python"},
    {"pregunta": "Que tipo de dato retorna len('Hola') en Python?",
     "opciones": ["float", "string", "int", "bool"], "correcta": 2, "tema": "Python"},
    {"pregunta": "En Python, como se define una lista vacia?",
     "opciones": ["lista = {}", "lista = ()", "lista = []", "lista = <>"], "correcta": 2, "tema": "Python"},
    {"pregunta": "Cual es el operador de modulo (residuo) en Python?",
     "opciones": ["/", "//", "%", "**"], "correcta": 2, "tema": "Python"},
    {"pregunta": "Que hace el metodo .append() en una lista de Python?",
     "opciones": ["Elimina el ultimo elemento", "Agrega un elemento al final", "Ordena la lista", "Cuenta elementos"], "correcta": 1, "tema": "Python"},
    {"pregunta": "Cual es la forma correcta de un comentario en Python?",
     "opciones": ["// comentario", "/* comentario */", "# comentario", "-- comentario"], "correcta": 2, "tema": "Python"},
    {"pregunta": "Que devuelve type(3.14) en Python?",
     "opciones": ["int", "float", "str", "double"], "correcta": 1, "tema": "Python"},
    {"pregunta": "Como se convierte el string '10' a entero en Python?",
     "opciones": ["int('10')", "integer('10')", "str(10)", "float('10')"], "correcta": 0, "tema": "Python"},
    {"pregunta": "Cual es el rango correcto para recorrer del 0 al 4 en Python?",
     "opciones": ["range(1,4)", "range(0,5)", "range(4)", "range(0,4)"], "correcta": 1, "tema": "Python"},
    {"pregunta": "Que estructura se usa para manejar errores en Python?",
     "opciones": ["if/else", "try/except", "for/while", "def/return"], "correcta": 1, "tema": "Python"},
    {"pregunta": "Que operador se usa para potencia en Python?",
     "opciones": ["^", "pow", "**", "^^"], "correcta": 2, "tema": "Python"},
    {"pregunta": "Como se declara una funcion en Python?",
     "opciones": ["function miFuncion():", "def miFuncion():", "func miFuncion():", "void miFuncion():"], "correcta": 1, "tema": "Python"},

    # ── PSEINT ──────────────────────────────────────────────────────────────
    {"pregunta": "En PSeInt, que palabra se usa para iniciar un algoritmo?",
     "opciones": ["BEGIN", "START", "Algoritmo", "Inicio"], "correcta": 2, "tema": "PSeInt"},
    {"pregunta": "En PSeInt, que instruccion se usa para pedir un dato al usuario?",
     "opciones": ["Escribir", "Leer", "Input", "Mostrar"], "correcta": 1, "tema": "PSeInt"},
    {"pregunta": "En PSeInt, que estructura se usa para repetir mientras se cumpla una condicion?",
     "opciones": ["Para...FinPara", "Si...FinSi", "Mientras...FinMientras", "Repetir...Hasta"], "correcta": 2, "tema": "PSeInt"},
    {"pregunta": "En PSeInt, como se escribe la asignacion de un valor a una variable?",
     "opciones": ["variable == valor", "variable = valor", "variable <- valor", "variable := valor"], "correcta": 2, "tema": "PSeInt"},
    {"pregunta": "En PSeInt, que estructura repite un numero FIJO de veces?",
     "opciones": ["Mientras", "Repetir...Hasta", "Para...FinPara", "Si...SiNo"], "correcta": 2, "tema": "PSeInt"},
    {"pregunta": "En PSeInt, como se muestra texto en pantalla?",
     "opciones": ["Leer", "Print", "Escribir", "Mostrar"], "correcta": 2, "tema": "PSeInt"},
    {"pregunta": "En PSeInt, que palabra finaliza un algoritmo?",
     "opciones": ["END", "FinAlgoritmo", "Stop", "Return"], "correcta": 1, "tema": "PSeInt"},
    {"pregunta": "En PSeInt, cual es el operador logico para Y (AND)?",
     "opciones": ["&&", "AND", "Y", "y"], "correcta": 2, "tema": "PSeInt"},
    {"pregunta": "En PSeInt, la estructura Repetir...Hasta ejecuta el bloque...",
     "opciones": ["Antes de evaluar la condicion", "Solo si la condicion es verdadera", "Infinitamente", "Nunca"], "correcta": 0, "tema": "PSeInt"},
    {"pregunta": "En PSeInt, como se declara un arreglo de 5 elementos?",
     "opciones": ["Definir arr Como Entero[5]", "Array arr[5]", "Dim arr(5)", "arr = new int[5]"], "correcta": 0, "tema": "PSeInt"},

    # ── CALCULO INTEGRAL ────────────────────────────────────────────────────
    {"pregunta": "Cual es la integral de x dx?",
     "opciones": ["x^2/2 + C", "x^2 + C", "2x + C", "x/2 + C"], "correcta": 0, "tema": "Calculo Integral"},
    {"pregunta": "Cual es la integral de 2x dx?",
     "opciones": ["2 + C", "x^2 + C", "2x^2 + C", "x + C"], "correcta": 1, "tema": "Calculo Integral"},
    {"pregunta": "Cual es la integral de una constante k dx?",
     "opciones": ["0 + C", "k + C", "kx + C", "k^2 + C"], "correcta": 2, "tema": "Calculo Integral"},
    {"pregunta": "Cual es la integral de e^x dx?",
     "opciones": ["e^x + C", "x*e^x + C", "e^(x+1) + C", "e^x / x + C"], "correcta": 0, "tema": "Calculo Integral"},
    {"pregunta": "Cual es la integral de 1/x dx?",
     "opciones": ["x + C", "ln|x| + C", "1/x^2 + C", "-1/x^2 + C"], "correcta": 1, "tema": "Calculo Integral"},
    {"pregunta": "Cual es la integral de cos(x) dx?",
     "opciones": ["-sin(x) + C", "cos(x) + C", "sin(x) + C", "tan(x) + C"], "correcta": 2, "tema": "Calculo Integral"},
    {"pregunta": "Cual es la integral de sin(x) dx?",
     "opciones": ["cos(x) + C", "-cos(x) + C", "sin(x) + C", "-sin(x) + C"], "correcta": 1, "tema": "Calculo Integral"},
    {"pregunta": "Segun la regla de la potencia, la integral de x^n dx es...",
     "opciones": ["n*x^(n-1) + C", "x^(n+1)/(n+1) + C", "x^n/n + C", "x^(n-1)/(n-1) + C"], "correcta": 1, "tema": "Calculo Integral"},
    {"pregunta": "Cuanto vale la integral definida de 0 a 1 de x dx?",
     "opciones": ["1", "2", "0.5", "0"], "correcta": 2, "tema": "Calculo Integral"},

    # ── CALCULO DERIVADAS ───────────────────────────────────────────────────
    {"pregunta": "Cual es la derivada de x^2?",
     "opciones": ["x", "2x", "x^2", "2"], "correcta": 1, "tema": "Calculo Derivadas"},
    {"pregunta": "Cual es la derivada de una constante?",
     "opciones": ["La misma constante", "1", "0", "La constante al cuadrado"], "correcta": 2, "tema": "Calculo Derivadas"},
    {"pregunta": "Cual es la derivada de sin(x)?",
     "opciones": ["-sin(x)", "-cos(x)", "cos(x)", "tan(x)"], "correcta": 2, "tema": "Calculo Derivadas"},
    {"pregunta": "Cual es la derivada de cos(x)?",
     "opciones": ["sin(x)", "-sin(x)", "cos(x)", "-cos(x)"], "correcta": 1, "tema": "Calculo Derivadas"},
    {"pregunta": "Cual es la derivada de e^x?",
     "opciones": ["x*e^(x-1)", "e^x", "e^(x-1)", "x + e^x"], "correcta": 1, "tema": "Calculo Derivadas"},
    {"pregunta": "Cual es la derivada de ln(x)?",
     "opciones": ["ln(x)/x", "1/x", "x*ln(x)", "e^x"], "correcta": 1, "tema": "Calculo Derivadas"},
    {"pregunta": "Segun la regla de la potencia, la derivada de x^n es...",
     "opciones": ["x^(n+1)", "n*x^(n+1)", "n*x^(n-1)", "(n-1)*x^n"], "correcta": 2, "tema": "Calculo Derivadas"},
    {"pregunta": "Cual es la derivada de 3x^3?",
     "opciones": ["3x^2", "9x^2", "x^3", "9x^3"], "correcta": 1, "tema": "Calculo Derivadas"},

    # ── FISICA MRU ──────────────────────────────────────────────────────────
    {"pregunta": "En MRU, cual es la formula de la distancia?",
     "opciones": ["d = a*t^2", "d = v*t", "d = v/t", "d = v + t"], "correcta": 1, "tema": "Fisica MRU"},
    {"pregunta": "Un objeto viaja a 60 km/h durante 2 horas. Cuantos km recorre?",
     "opciones": ["90 km", "120 km", "30 km", "60 km"], "correcta": 1, "tema": "Fisica MRU"},
    {"pregunta": "Un tren viaja a 20 m/s durante 5 s. Cuantos metros recorre?",
     "opciones": ["200 m", "100 m", "25 m", "4 m"], "correcta": 1, "tema": "Fisica MRU"},
    {"pregunta": "En MRU, la aceleracion es...",
     "opciones": ["Variable", "Negativa", "Cero", "Igual a la velocidad"], "correcta": 2, "tema": "Fisica MRU"},
    {"pregunta": "Si d=150 m y t=5 s en MRU, cual es la velocidad?",
     "opciones": ["750 m/s", "145 m/s", "30 m/s", "15 m/s"], "correcta": 2, "tema": "Fisica MRU"},
    {"pregunta": "En MRU, la grafica de posicion vs tiempo es...",
     "opciones": ["Una parabola", "Una linea recta", "Una curva exponencial", "Un circulo"], "correcta": 1, "tema": "Fisica MRU"},
    {"pregunta": "Un ciclista recorre 200 m en 10 s. Cual es su velocidad en MRU?",
     "opciones": ["2000 m/s", "20 m/s", "10 m/s", "0.05 m/s"], "correcta": 1, "tema": "Fisica MRU"},

    # ── FISICA MRUA/MRUV ────────────────────────────────────────────────────
    {"pregunta": "En MRUA, cual es la formula de velocidad final?",
     "opciones": ["vf = v0 * a * t", "vf = v0 + a*t", "vf = v0 - t", "vf = a / t"], "correcta": 1, "tema": "Fisica MRUA"},
    {"pregunta": "En MRUA, cual es la formula de posicion?",
     "opciones": ["x = v0*t", "x = v0*t + (1/2)*a*t^2", "x = a*t^2", "x = v0 + a*t"], "correcta": 1, "tema": "Fisica MRUA"},
    {"pregunta": "Un auto parte del reposo con a=3 m/s^2. Cual es su velocidad a los 4 s?",
     "opciones": ["7 m/s", "12 m/s", "16 m/s", "3 m/s"], "correcta": 1, "tema": "Fisica MRUA"},
    {"pregunta": "En MRUA, la grafica de velocidad vs tiempo es...",
     "opciones": ["Una linea recta", "Una parabola", "Una constante", "Una sinusoide"], "correcta": 0, "tema": "Fisica MRUA"},
    {"pregunta": "Un objeto cae con a=10 m/s^2 desde el reposo. Cuanto cae en 3 s?",
     "opciones": ["30 m", "90 m", "45 m", "15 m"], "correcta": 2, "tema": "Fisica MRUA"},
    {"pregunta": "En MRUA, si la aceleracion es negativa el objeto...",
     "opciones": ["Acelera", "Se detiene instantaneamente", "Desacelera", "Mantiene velocidad"], "correcta": 2, "tema": "Fisica MRUA"},
    {"pregunta": "Cual es la diferencia entre MRU y MRUA?",
     "opciones": ["La masa del objeto", "La aceleracion: 0 en MRU, constante en MRUA", "La distancia recorrida", "El tiempo transcurrido"], "correcta": 1, "tema": "Fisica MRUA"},

    # ── MATRICES ────────────────────────────────────────────────────────────
    {"pregunta": "Cuantos elementos tiene una matriz 3x3?",
     "opciones": ["6", "9", "12", "3"], "correcta": 1, "tema": "Matrices"},
    {"pregunta": "La traza de una matriz es la suma de los elementos de su...",
     "opciones": ["Primera fila", "Diagonal principal", "Ultima columna", "Diagonal secundaria"], "correcta": 1, "tema": "Matrices"},
    {"pregunta": "Cuantas filas y columnas tiene una matriz cuadrada de orden 3?",
     "opciones": ["2 filas 3 col", "3 filas 3 col", "3 filas 2 col", "1 fila 9 col"], "correcta": 1, "tema": "Matrices"},
    {"pregunta": "Una matriz identidad tiene unos en...",
     "opciones": ["Toda la matriz", "La primera fila", "La diagonal principal", "La ultima columna"], "correcta": 2, "tema": "Matrices"},
    {"pregunta": "Si A es de 2x3 y B es de 3x2, el producto A*B resulta en una matriz de...",
     "opciones": ["3x3", "2x2", "2x3", "3x2"], "correcta": 1, "tema": "Matrices"},
    {"pregunta": "Una matriz transpuesta se obtiene...",
     "opciones": ["Sumando filas", "Intercambiando filas por columnas", "Multiplicando por -1", "Sumando la diagonal"], "correcta": 1, "tema": "Matrices"},
    {"pregunta": "El determinante de la matriz [[1,2],[3,4]] es...",
     "opciones": ["10", "-2", "2", "-10"], "correcta": 1, "tema": "Matrices"},
    {"pregunta": "Una matriz nula es aquella donde...",
     "opciones": ["Solo la diagonal es cero", "El determinante es 1", "Todos sus elementos son cero", "No tiene inversa"], "correcta": 2, "tema": "Matrices"},
    {"pregunta": "Para que dos matrices se puedan sumar deben tener...",
     "opciones": ["Mismo determinante", "Las mismas dimensiones", "Misma diagonal", "Ser cuadradas"], "correcta": 1, "tema": "Matrices"},
]


DECISIONES = [
    {"nombre": "🏭 Construir fabrica",        "efectos": {"economia": 15,  "energia": -5,  "medio_ambiente": -10, "bienestar_social": 0}},
    {"nombre": "🌳 Crear parque natural",      "efectos": {"economia": -5,  "energia": 0,   "medio_ambiente": 15,  "bienestar_social": 10}},
    {"nombre": "☀️ Instalar paneles solares",  "efectos": {"economia": -10, "energia": 20,  "medio_ambiente": 10,  "bienestar_social": 5}},
    {"nombre": "🏫 Construir escuelas",        "efectos": {"economia": -10, "energia": -5,  "medio_ambiente": 0,   "bienestar_social": 20}},
    {"nombre": "🛣️ Ampliar autopistas",       "efectos": {"economia": 10,  "energia": -10, "medio_ambiente": -15, "bienestar_social": 5}},
    {"nombre": "🌾 Agricultura urbana",        "efectos": {"economia": 5,   "energia": 5,   "medio_ambiente": 10,  "bienestar_social": 10}},
    {"nombre": "🏥 Mejorar hospitales",        "efectos": {"economia": -15, "energia": -5,  "medio_ambiente": 0,   "bienestar_social": 25}},
    {"nombre": "⚡ Planta de carbon",          "efectos": {"economia": 20,  "energia": 25,  "medio_ambiente": -20, "bienestar_social": -5}},
]

# ════════════════════════════════════════════════════════
#  RUTAS PRINCIPALES
# ════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/instrucciones")
def instrucciones():
    return render_template("instrucciones.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ════════════════════════════════════════════════════════
#  REGISTRO Y LOGIN
# ════════════════════════════════════════════════════════

@app.route("/registro", methods=["GET", "POST"])
def registro():
    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre_grupo", "").strip()
        pwd    = request.form.get("password", "").strip()
        if not nombre or not pwd:
            error = "Completa todos los campos."
        else:
            conn = get_db(); c = conn.cursor()
            c.execute("SELECT id FROM grupos WHERE nombre_grupo=?", (nombre,))
            if c.fetchone():
                error = "Ese nombre ya existe. Elige otro."
                conn.close()
            else:
                c.execute("INSERT INTO grupos (nombre_grupo, password) VALUES (?,?)", (nombre, pwd))
                conn.commit()
                nid = c.lastrowid; conn.close()
                session["grupo_id"]     = nid
                session["nombre_grupo"] = nombre
                return redirect(url_for("agregar_estudiantes"))
    return render_template("registro.html", error=error)

@app.route("/cancelar_registro", methods=["POST"])
def cancelar_registro():
    if "grupo_id" in session:
        gid = session["grupo_id"]
        conn = get_db(); c = conn.cursor()
        c.execute("DELETE FROM estudiantes    WHERE grupo_id=?", (gid,))
        c.execute("DELETE FROM progreso_juego WHERE grupo_id=?", (gid,))
        c.execute("DELETE FROM grupos         WHERE id=?",       (gid,))
        conn.commit(); conn.close()
    session.clear()
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre_grupo", "").strip()
        pwd    = request.form.get("password", "").strip()
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT id, nombre_grupo FROM grupos WHERE nombre_grupo=? AND password=?", (nombre, pwd))
        g = c.fetchone(); conn.close()
        if g:
            session["grupo_id"]     = g["id"]
            session["nombre_grupo"] = g["nombre_grupo"]
            return redirect(url_for("juego"))
        else:
            error = "Nombre o contrasena incorrectos."
    return render_template("login.html", error=error)

# ════════════════════════════════════════════════════════
#  AGREGAR ESTUDIANTES
# ════════════════════════════════════════════════════════

@app.route("/agregar_estudiantes", methods=["GET", "POST"])
def agregar_estudiantes():
    if "grupo_id" not in session:
        return redirect(url_for("index"))
    gid = session["grupo_id"]
    nombre_grupo = session["nombre_grupo"]
    error = mensaje = None
    if request.method == "POST":
        accion = request.form.get("accion")
        if accion == "agregar":
            nombre = request.form.get("nombre_estudiante", "").strip()
            if not nombre:
                error = "El nombre no puede estar vacio."
            elif not re.match(r"^[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1 ]+$", nombre):
                error = "Solo letras y espacios."
            else:
                conn = get_db(); c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM estudiantes WHERE grupo_id=?", (gid,))
                if c.fetchone()[0] >= 5:
                    error = "Maximo 5 estudiantes."
                    conn.close()
                else:
                    c.execute("SELECT id FROM estudiantes WHERE LOWER(nombre_estudiante)=LOWER(?)", (nombre,))
                    if c.fetchone():
                        error = "Ese estudiante ya existe en algun grupo."
                        conn.close()
                    else:
                        c.execute("INSERT INTO estudiantes (grupo_id, nombre_estudiante) VALUES (?,?)", (gid, nombre))
                        conn.commit(); conn.close()
                        mensaje = nombre + " agregado correctamente."
        elif accion == "finalizar":
            conn = get_db(); c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM estudiantes WHERE grupo_id=?", (gid,))
            cant = c.fetchone()[0]; conn.close()
            if cant < 3:
                error = "Necesitas al menos 3 estudiantes. Tienes " + str(cant) + "."
            else:
                conn = get_db(); c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO progreso_juego (grupo_id,economia,medio_ambiente,energia,bienestar_social,ronda_actual) VALUES (?,50,50,50,50,1)", (gid,))
                conn.commit(); conn.close()
                return redirect(url_for("juego"))
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT id, nombre_estudiante FROM estudiantes WHERE grupo_id=?", (gid,))
    estudiantes = [{"id": r["id"], "nombre": r["nombre_estudiante"]} for r in c.fetchall()]
    conn.close()
    return render_template("agregar_estudiantes.html",
                           nombre_grupo=nombre_grupo, estudiantes=estudiantes,
                           error=error, mensaje=mensaje)

@app.route("/eliminar_estudiante/<int:est_id>", methods=["POST"])
def eliminar_estudiante(est_id):
    if "grupo_id" not in session:
        return redirect(url_for("index"))
    gid = session["grupo_id"]
    conn = get_db(); c = conn.cursor()
    c.execute("DELETE FROM estudiantes WHERE id=? AND grupo_id=?", (est_id, gid))
    conn.commit(); conn.close()
    return redirect(url_for("agregar_estudiantes"))

# ════════════════════════════════════════════════════════
#  JUEGO
# ════════════════════════════════════════════════════════

@app.route("/juego")
def juego():
    if "grupo_id" not in session:
        return redirect(url_for("index"))
    gid = session["grupo_id"]
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT id, nombre_estudiante FROM estudiantes WHERE grupo_id=?", (gid,))
    filas = c.fetchall()
    estudiantes = [{"id": r["id"], "nombre": r["nombre_estudiante"]} for r in filas]
    if not estudiantes:
        conn.close()
        return redirect(url_for("agregar_estudiantes"))
    c.execute("SELECT * FROM progreso_juego WHERE grupo_id=?", (gid,))
    prog = c.fetchone()
    if not prog:
        c.execute("INSERT INTO progreso_juego (grupo_id,economia,medio_ambiente,energia,bienestar_social,ronda_actual) VALUES (?,50,50,50,50,1)", (gid,))
        conn.commit()
        c.execute("SELECT * FROM progreso_juego WHERE grupo_id=?", (gid,))
        prog = c.fetchone()
    conn.close()
    p = dict(prog)
    terminado = False; razon = ""; victoria = False
    nombres_s = {"economia":"Economia","medio_ambiente":"Medio Ambiente",
                 "energia":"Energia","bienestar_social":"Bienestar Social"}
    for s in ["economia","medio_ambiente","energia","bienestar_social"]:
        if p[s] <= 30:
            terminado = True; razon = nombres_s[s] + " llego a nivel critico."; break
    if not terminado and p["ronda_actual"] > 10:
        terminado = True; razon = "Se completaron las 10 rondas exitosamente."; victoria = True
    decisiones_idx = []
    for i, d in enumerate(DECISIONES):
        dd = dict(d); dd["idx"] = i; decisiones_idx.append(dd)
    nombres_display = [e["nombre"] for e in estudiantes]

    # Cooldowns: dict {str(idx): ronda_en_que_se_uso}
    cooldowns = session.get("cooldowns", {})

    # Limpiar cooldowns de sesiones anteriores si es ronda 1
    if p["ronda_actual"] == 1:
        session.pop("cooldowns", None)
        session.modified = True
    cooldowns = session.get("cooldowns", {})

    return render_template("juego.html",
        nombre_grupo=session["nombre_grupo"], estudiantes=nombres_display,
        progreso=p, decisiones=decisiones_idx,
        juego_terminado=terminado, razon_fin=razon, victoria=victoria,
        cooldowns=cooldowns)


@app.route("/api/pregunta")
def api_pregunta():
    idx = random.randint(0, len(PREGUNTAS) - 1)
    p   = PREGUNTAS[idx]
    return jsonify({"idx": idx, "pregunta": p["pregunta"],
                    "opciones": p["opciones"], "tema": p["tema"]})

@app.route("/api/aplicar_decision", methods=["POST"])
def api_aplicar_decision():
    if "grupo_id" not in session:
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Sin datos JSON"}), 400
    try:
        di = int(data.get("decision_idx", -1))
        ri = int(data.get("respuesta_idx", -1))
        pi = int(data.get("pregunta_idx",  -1))
    except (TypeError, ValueError) as e:
        return jsonify({"error": "Datos invalidos: " + str(e)}), 400
    if not (0 <= di < len(DECISIONES)): return jsonify({"error": "decision_idx fuera de rango"}), 400
    if not (0 <= pi < len(PREGUNTAS)):  return jsonify({"error": "pregunta_idx fuera de rango"}), 400

    gid = session["grupo_id"]
    decision = DECISIONES[di]; pregunta = PREGUNTAS[pi]

    conn = get_db(); c = conn.cursor()
    c.execute("SELECT * FROM progreso_juego WHERE grupo_id=?", (gid,))
    fila = c.fetchone()
    if not fila:
        conn.close(); return jsonify({"error": "Sin progreso"}), 400
    p = dict(fila)
    ronda_actual = p["ronda_actual"]

    # ── Cooldown ────────────────────────────────────────────
    cooldowns = session.get("cooldowns", {})
    clave = str(di)
    if clave in cooldowns:
        if ronda_actual - cooldowns[clave] < 3:
            restantes = 3 - (ronda_actual - cooldowns[clave])
            conn.close()
            return jsonify({"error": f"Esa decision estara disponible en {restantes} ronda(s) mas."}), 400

    correcto = (pregunta["correcta"] == ri)

    # ── Penalización doble en rondas pares si falla ─────────
    penalizacion = 10 if (ronda_actual % 2 == 0) else 5

    if correcto:
        ef = decision["efectos"]
        p["economia"]         = max(0, min(100, p["economia"]         + ef["economia"]))
        p["medio_ambiente"]   = max(0, min(100, p["medio_ambiente"]   + ef["medio_ambiente"]))
        p["energia"]          = max(0, min(100, p["energia"]          + ef["energia"]))
        p["bienestar_social"] = max(0, min(100, p["bienestar_social"] + ef["bienestar_social"]))
        mensaje = "¡Correcto! Se aplico: " + decision["nombre"]
        efectos = dict(ef)
        cooldowns[clave] = ronda_actual
        session["cooldowns"] = cooldowns
        session.modified = True
    else:
        p["economia"]         = max(0, p["economia"]         - penalizacion)
        p["medio_ambiente"]   = max(0, p["medio_ambiente"]   - penalizacion)
        p["energia"]          = max(0, p["energia"]          - penalizacion)
        p["bienestar_social"] = max(0, p["bienestar_social"] - penalizacion)
        pen_txt = f"({penalizacion} pts — ronda {'par, doble penalizacion' if penalizacion==10 else 'normal'})"
        mensaje = f"Incorrecto. Todos los sistemas pierden {penalizacion} puntos {pen_txt}"
        efectos = {"economia":-penalizacion,"medio_ambiente":-penalizacion,
                   "energia":-penalizacion,"bienestar_social":-penalizacion}

    # ── Evento aleatorio de la ronda ────────────────────────
    EVENTOS = [
        {"texto": "🌪️ Tormenta inesperada",       "sistema": "medio_ambiente",   "valor": -8},
        {"texto": "📈 Boom economico",             "sistema": "economia",         "valor": +10},
        {"texto": "💡 Ahorro energetico nacional", "sistema": "energia",          "valor": +8},
        {"texto": "😷 Brote de enfermedad",        "sistema": "bienestar_social", "valor": -10},
        {"texto": "🌞 Año de gran cosecha",        "sistema": "medio_ambiente",   "valor": +7},
        {"texto": "⚡ Fallo en la red electrica",  "sistema": "energia",          "valor": -9},
        {"texto": "💸 Crisis financiera leve",     "sistema": "economia",         "valor": -8},
        {"texto": "🎉 Festival cultural",          "sistema": "bienestar_social", "valor": +9},
        {"texto": "🔥 Incendio forestal",          "sistema": "medio_ambiente",   "valor": -12},
        {"texto": "🏗️ Inversion extranjera",      "sistema": "economia",         "valor": +12},
    ]
    evento = random.choice(EVENTOS)
    s = evento["sistema"]; v = evento["valor"]
    p[s] = max(0, min(100, p[s] + v))
    evento_resultado = {"texto": evento["texto"], "sistema": s, "valor": v}

    p["ronda_actual"] += 1
    c.execute("""UPDATE progreso_juego
                 SET economia=?,medio_ambiente=?,energia=?,bienestar_social=?,ronda_actual=?
                 WHERE grupo_id=?""",
              (p["economia"],p["medio_ambiente"],p["energia"],p["bienestar_social"],p["ronda_actual"],gid))
    conn.commit(); conn.close()

    return jsonify({
        "correcto": correcto, "mensaje": mensaje,
        "progreso": p, "efectos": efectos,
        "correcta_idx": pregunta["correcta"],
        "respuesta_correcta_texto": pregunta["opciones"][pregunta["correcta"]],
        "cooldowns": session.get("cooldowns", {}),
        "evento": evento_resultado
    })

@app.route("/api/reiniciar", methods=["POST"])
def api_reiniciar():
    if "grupo_id" not in session:
        return jsonify({"error": "No autorizado"}), 401
    gid = session["grupo_id"]
    conn = get_db(); c = conn.cursor()
    c.execute("DELETE FROM estudiantes WHERE grupo_id=?", (gid,))
    c.execute("UPDATE progreso_juego SET economia=50,medio_ambiente=50,energia=50,bienestar_social=50,ronda_actual=1 WHERE grupo_id=?", (gid,))
    conn.commit(); conn.close()
    # Limpiar cooldowns al reiniciar
    session.pop("cooldowns", None)
    session.modified = True
    return jsonify({"ok": True})

# ════════════════════════════════════════════════════════
#  ADMIN – BASE DE DATOS
# ════════════════════════════════════════════════════════

@app.route("/ver_db")
def ver_db():
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT * FROM grupos ORDER BY id")
    grupos = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM estudiantes ORDER BY grupo_id")
    estudiantes = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM progreso_juego ORDER BY grupo_id")
    progresos = [dict(r) for r in c.fetchall()]
    conn.close()
    return render_template("ver_db.html",
                           grupos=grupos, estudiantes=estudiantes, progresos=progresos)

@app.route("/db/nuevo_grupo", methods=["GET", "POST"])
def db_nuevo_grupo():
    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre_grupo", "").strip()
        pwd    = request.form.get("password", "").strip()
        if not nombre or not pwd:
            error = "Completa todos los campos."
        else:
            conn = get_db(); c = conn.cursor()
            c.execute("SELECT id FROM grupos WHERE nombre_grupo=?", (nombre,))
            if c.fetchone():
                error = "Ese nombre ya existe."; conn.close()
            else:
                c.execute("INSERT INTO grupos (nombre_grupo, password) VALUES (?,?)", (nombre, pwd))
                conn.commit(); conn.close()
                return redirect(url_for("ver_db"))
    return render_template("db_nuevo_grupo.html", error=error)

@app.route("/db/editar_grupo/<int:gid>", methods=["GET", "POST"])
def db_editar_grupo(gid):
    conn = get_db(); c = conn.cursor()
    error = None
    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre_grupo", "").strip()
        nueva_pwd    = request.form.get("password", "").strip()
        if not nuevo_nombre or not nueva_pwd:
            error = "Todos los campos son obligatorios."
        else:
            c.execute("SELECT id FROM grupos WHERE nombre_grupo=? AND id!=?", (nuevo_nombre, gid))
            if c.fetchone():
                error = "Ese nombre ya lo usa otro grupo."
            else:
                c.execute("UPDATE grupos SET nombre_grupo=?, password=? WHERE id=?",
                          (nuevo_nombre, nueva_pwd, gid))
                conn.commit(); conn.close()
                return redirect(url_for("ver_db"))
    c.execute("SELECT * FROM grupos WHERE id=?", (gid,))
    grupo = dict(c.fetchone())
    conn.close()
    return render_template("db_editar_grupo.html", grupo=grupo, error=error)

@app.route("/db/eliminar_grupo/<int:gid>", methods=["POST"])
def db_eliminar_grupo(gid):
    conn = get_db(); c = conn.cursor()
    c.execute("DELETE FROM estudiantes    WHERE grupo_id=?", (gid,))
    c.execute("DELETE FROM progreso_juego WHERE grupo_id=?", (gid,))
    c.execute("DELETE FROM grupos         WHERE id=?",       (gid,))
    conn.commit(); conn.close()
    return redirect(url_for("ver_db"))

@app.route("/db/editar_estudiante/<int:eid>", methods=["GET", "POST"])
def db_editar_estudiante(eid):
    conn = get_db(); c = conn.cursor()
    error = None
    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre_estudiante", "").strip()
        nuevo_gid    = request.form.get("grupo_id", type=int)
        if not nuevo_nombre:
            error = "El nombre no puede estar vacio."
        elif not re.match(r"^[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1 ]+$", nuevo_nombre):
            error = "Solo letras y espacios."
        else:
            c.execute("SELECT id FROM estudiantes WHERE LOWER(nombre_estudiante)=LOWER(?) AND id!=?",
                      (nuevo_nombre, eid))
            if c.fetchone():
                error = "Ese nombre ya existe en otro grupo."
            else:
                c.execute("UPDATE estudiantes SET nombre_estudiante=?, grupo_id=? WHERE id=?",
                          (nuevo_nombre, nuevo_gid, eid))
                conn.commit(); conn.close()
                return redirect(url_for("ver_db"))
    c.execute("SELECT * FROM estudiantes WHERE id=?", (eid,))
    est = dict(c.fetchone())
    c.execute("SELECT * FROM grupos ORDER BY id")
    grupos = [dict(r) for r in c.fetchall()]
    conn.close()
    return render_template("db_editar_estudiante.html", est=est, grupos=grupos, error=error)

@app.route("/db/eliminar_estudiante/<int:eid>", methods=["POST"])
def db_eliminar_estudiante(eid):
    conn = get_db(); c = conn.cursor()
    c.execute("DELETE FROM estudiantes WHERE id=?", (eid,))
    conn.commit(); conn.close()
    return redirect(url_for("ver_db"))

@app.route("/db/agregar_estudiante", methods=["GET", "POST"])
def db_agregar_estudiante():
    grupo_id_default = request.args.get("grupo_id", type=int, default=None)
    conn = get_db(); c = conn.cursor()
    error = None
    if request.method == "POST":
        nombre  = request.form.get("nombre_estudiante", "").strip()
        gid_new = request.form.get("grupo_id", type=int)
        if not nombre:
            error = "El nombre no puede estar vacio."
        elif not re.match(r"^[A-Za-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1 ]+$", nombre):
            error = "Solo letras y espacios."
        elif gid_new is None:
            error = "Selecciona un grupo."
        else:
            c.execute("SELECT COUNT(*) FROM estudiantes WHERE grupo_id=?", (gid_new,))
            if c.fetchone()[0] >= 5:
                error = "Ese grupo ya tiene 5 estudiantes (maximo)."
            else:
                c.execute("SELECT id FROM estudiantes WHERE LOWER(nombre_estudiante)=LOWER(?)", (nombre,))
                if c.fetchone():
                    error = "Ese estudiante ya existe en algun grupo."
                else:
                    c.execute("INSERT INTO estudiantes (grupo_id, nombre_estudiante) VALUES (?,?)",
                              (gid_new, nombre))
                    conn.commit(); conn.close()
                    return redirect(url_for("ver_db"))
    c.execute("SELECT * FROM grupos ORDER BY id")
    grupos = [dict(r) for r in c.fetchall()]
    conn.close()
    return render_template("db_agregar_estudiante.html",
                           grupos=grupos, error=error,
                           grupo_id_default=grupo_id_default)

# ════════════════════════════════════════════════════════

    # Inicializar DB al arrancar con gunicorn
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

