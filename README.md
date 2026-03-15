# Ciudad en Equilibrio – Ingeniería Edition

## ¿Cómo ejecutar la aplicación?

### 1. Instalar dependencias
```bash
pip install flask
```

### 2. Ejecutar el servidor
```bash
python app.py
```

### 3. Abrir en el navegador
```
http://127.0.0.1:5000
```

---

## Estructura del proyecto
```
ciudad_equilibrio/
├── app.py                  ← Servidor Flask (backend)
├── database.db             ← Base de datos SQLite (se crea automáticamente)
├── requirements.txt        ← Dependencias
├── templates/
│   ├── index.html          ← Pantalla de inicio
│   ├── login.html          ← Inicio de sesión
│   ├── registro.html       ← Registro de grupo
│   ├── agregar_estudiantes.html ← Agregar miembros
│   ├── juego.html          ← Pantalla del juego
│   └── instrucciones.html  ← Reglas del juego
└── static/
    ├── style.css           ← Estilos visuales
    └── game.js             ← Lógica del juego (JavaScript)
```

## Tablas de la base de datos

| Tabla | Descripción |
|-------|-------------|
| `grupos` | Almacena nombre y contraseña de cada grupo |
| `estudiantes` | Almacena los miembros de cada grupo |
| `progreso_juego` | Guarda el estado actual de los 4 sistemas y la ronda |
