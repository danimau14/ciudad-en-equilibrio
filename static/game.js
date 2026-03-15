// ============================================================
// game.js - Ciudad en Equilibrio
// ============================================================

let decisionSeleccionada = null;
let preguntaActual       = null;
let preguntaIdx          = null;
let esperandoRespuesta   = false;

// ============================================================
// PASO 1: Seleccionar decisión
// ============================================================
function seleccionarDecision(idx) {
    const clave = String(idx);
    if (window._cooldowns && window._cooldowns[clave] !== undefined) {
        const rondaUsada = window._cooldowns[clave];
        const restantes  = 3 - (window._rondaActual - rondaUsada);
        if (restantes > 0) return;
    }

    document.querySelectorAll(".decision-card").forEach(c => c.classList.remove("seleccionada"));
    const card = document.querySelector(`.decision-card[data-idx="${idx}"]`);
    if (card) card.classList.add("seleccionada");

    decisionSeleccionada = idx;   // ✅ variable local, no window._

    fetch("/api/pregunta")
        .then(r => r.json())
        .then(datos => {
            preguntaActual = datos;
            preguntaIdx    = datos.idx;   // ✅ guardar idx aquí
            mostrarModalPregunta(datos);
        })
        .catch(err => console.error("Error al obtener pregunta:", err));
}

// ============================================================
// PASO 2: Mostrar modal con pregunta
// ============================================================
let _timerPregunta = null;

function mostrarModalPregunta(pregunta) {
    esperandoRespuesta = true;

    document.getElementById("modalTema").textContent          = "Tema: " + pregunta.tema;
    document.getElementById("modalPreguntaTexto").textContent = pregunta.pregunta;
    document.getElementById("msgPregunta").textContent        = "";

    const contenedor = document.getElementById("opcionesPregunta");
    contenedor.innerHTML = "";

    pregunta.opciones.forEach(function(opcion, i) {
        const btn       = document.createElement("button");
        btn.className   = "opcion-btn";
        btn.textContent = opcion;
        btn.onclick     = function() {
            clearInterval(_timerPregunta);
            quitarTimer();
            responder(i);
        };
        contenedor.appendChild(btn);
    });

    document.getElementById("modalPregunta").classList.remove("oculto");

    // ── Temporizador 20 segundos ─────────────────────────────
    let segundos = 20;
    let timerEl  = document.getElementById("timerPregunta");
    if (!timerEl) {
        timerEl           = document.createElement("div");
        timerEl.id        = "timerPregunta";
        timerEl.style.cssText = "text-align:center;font-size:.85rem;color:#94a3b8;margin-bottom:.5rem";
        document.getElementById("modalPreguntaTexto").insertAdjacentElement("beforebegin", timerEl);
    }
    timerEl.textContent = `⏱️ Tiempo: ${segundos}s`;
    timerEl.style.color = "#94a3b8";

    clearInterval(_timerPregunta);
    _timerPregunta = setInterval(() => {
        segundos--;
        timerEl.textContent = `⏱️ Tiempo: ${segundos}s`;
        if (segundos <= 5) timerEl.style.color = "#f87171";
        if (segundos <= 0) {
            clearInterval(_timerPregunta);
            if (esperandoRespuesta) {
                timerEl.textContent = "⏱️ ¡Tiempo agotado!";
                responder(-1);   // -1 = respuesta inválida = siempre incorrecto
            }
        }
    }, 1000);
}

function quitarTimer() {
    const t = document.getElementById("timerPregunta");
    if (t) t.textContent = "";
}


// ============================================================
// PASO 3: Responder y enviar al servidor
// ============================================================
async function responder(respuestaIdx) {
    if (!esperandoRespuesta) return;
    esperandoRespuesta = false;

    const botones = document.querySelectorAll(".opcion-btn");
    botones.forEach(btn => btn.disabled = true);

    // Tiempo agotado: forzar respuesta incorrecta sin verificar null
    const esTiempoAgotado = (respuestaIdx === -1);
    if (esTiempoAgotado) respuestaIdx = 99;  // índice inválido → siempre incorrecto

    if (decisionSeleccionada === null || preguntaIdx === null) {
        console.error("Faltan datos:", decisionSeleccionada, preguntaIdx);
        document.getElementById("msgPregunta").textContent = "Error interno. Cierra y vuelve a elegir.";
        botones.forEach(btn => btn.disabled = false);
        esperandoRespuesta = true;
        return;
    }

    try {
        const res = await fetch("/api/aplicar_decision", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                decision_idx:  decisionSeleccionada,
                respuesta_idx: respuestaIdx,
                pregunta_idx:  preguntaIdx
            })
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.error || "Error " + res.status);
        }
        const data = await res.json();

        if (data.correcto) {
            botones[respuestaIdx].classList.add("correcta");
            document.getElementById("msgPregunta").textContent = "¡Correcto!";
        } else {
            botones[respuestaIdx].classList.add("incorrecta");
            if (data.correcta_idx !== undefined && botones[data.correcta_idx]) {
                botones[data.correcta_idx].classList.add("correcta");
            }
            document.getElementById("msgPregunta").textContent =
                "Incorrecto. La respuesta correcta era: " + data.respuesta_correcta_texto;
        }

        setTimeout(function() {
            document.getElementById("modalPregunta").classList.add("oculto");
            if (data.cooldowns !== undefined) {
                actualizarCooldowns(data.cooldowns, data.progreso.ronda_actual);
            }
            mostrarResultadoRonda(data);
        }, 2000);

    } catch (error) {
        console.error("Error al responder:", error);
        document.getElementById("msgPregunta").textContent =
            "Error: " + error.message + ". Intenta de nuevo.";
        botones.forEach(btn => btn.disabled = false);
        esperandoRespuesta = true;
    }
}

// ============================================================
// PASO 4: Mostrar resultado de la ronda
// ============================================================
function mostrarResultadoRonda(data) {
    document.getElementById("resultadoTitulo").textContent = data.correcto
        ? "¡Decisión aplicada!" : "Respuesta incorrecta";
    document.getElementById("resultadoMensaje").textContent = data.mensaje;

    const contenedor = document.getElementById("resultadoEfectos");
    contenedor.innerHTML = "";

    const nombres = {
        economia: "Economía", medio_ambiente: "Ambiente",
        energia: "Energía",   bienestar_social: "Bienestar"
    };

    // Efectos de la decisión
    Object.entries(data.efectos).forEach(function([key, val]) {
        const span            = document.createElement("span");
        span.className        = "efecto-resultado-item";
        span.style.background = val >= 0 ? "rgba(34,197,94,0.2)" : "rgba(239,68,68,0.2)";
        span.style.color      = val >= 0 ? "#4ade80" : "#f87171";
        span.textContent      = (val > 0 ? "+" : "") + val + " " + nombres[key];
        contenedor.appendChild(span);
    });

    // Evento aleatorio de la ronda
    if (data.evento) {
        const ev  = data.evento;
        const div = document.createElement("div");
        div.style.cssText = "margin-top:.8rem;padding:.5rem .8rem;background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.3);border-radius:.45rem;font-size:.85rem;color:#fbbf24";
        div.innerHTML = `<strong>Evento:</strong> ${ev.texto} &nbsp;<span style="color:${ev.valor>=0?'#4ade80':'#f87171'}">${ev.valor>0?'+':''}${ev.valor} ${nombres[ev.sistema]}</span>`;
        contenedor.appendChild(div);
    }

    actualizarBarras(data.progreso);
    document.getElementById("modalResultado").classList.remove("oculto");
}

// ============================================================
// Actualizar barras de progreso
// ============================================================
function actualizarBarras(progreso) {
    const mapa = {
        economia:         { barra: "bar-economia",  valor: "val-economia"  },
        medio_ambiente:   { barra: "bar-ambiente",  valor: "val-ambiente"  },
        energia:          { barra: "bar-energia",   valor: "val-energia"   },
        bienestar_social: { barra: "bar-bienestar", valor: "val-bienestar" }
    };
    Object.entries(mapa).forEach(function([key, ids]) {
        const barra   = document.getElementById(ids.barra);
        const valorEl = document.getElementById(ids.valor);
        if (!barra || !valorEl) return;
        const pct = Math.max(0, Math.min(100, progreso[key]));
        barra.style.width   = pct + "%";
        valorEl.textContent = progreso[key];
        if (progreso[key] <= 30) {
            barra.style.background = "linear-gradient(90deg, #dc2626, #ef4444)";
            valorEl.style.color    = "#ef4444";
        }
    });
}

// ============================================================
// Cooldowns
// ============================================================
function actualizarCooldowns(cooldowns, rondaActual) {
    window._cooldowns   = cooldowns;
    window._rondaActual = rondaActual;

    document.querySelectorAll(".decision-card").forEach(card => {
        const idx = String(card.dataset.idx);
        card.classList.remove("bloqueada");
        const tagViejo = card.querySelector(".cooldown-tag");
        if (tagViejo) tagViejo.remove();

        if (cooldowns[idx] !== undefined) {
            const rondaUsada = cooldowns[idx];
            const restantes  = 3 - (rondaActual - rondaUsada);
            if (restantes > 0) {
                card.classList.add("bloqueada");
                const tag       = document.createElement("span");
                tag.className   = "cooldown-tag";
                tag.textContent = `🔒 disponible en ${restantes} ronda${restantes > 1 ? "s" : ""}`;
                card.appendChild(tag);
            }
        }
    });
}

// ============================================================
// Botón Continuar → siguiente ronda
// ============================================================
document.getElementById("btnSiguienteRonda").addEventListener("click", function() {
    document.getElementById("modalResultado").classList.add("oculto");
    decisionSeleccionada = null;
    preguntaIdx          = null;
    esperandoRespuesta   = false;
    document.querySelectorAll(".decision-card").forEach(c => c.classList.remove("seleccionada"));
    window.location.reload();
});

// ============================================================
// Configuración ⚙️
// ============================================================
document.getElementById("btnConfig").addEventListener("click", function() {
    document.getElementById("menuConfig").classList.remove("oculto");
});
document.getElementById("btnCerrarConfig").addEventListener("click", function() {
    document.getElementById("menuConfig").classList.add("oculto");
});
document.getElementById("btnVolverInicio").addEventListener("click", function() {
    document.getElementById("menuConfig").classList.add("oculto");
    document.getElementById("modalConfirmar").classList.remove("oculto");
});
document.getElementById("btnCancelarVolver").addEventListener("click", function() {
    document.getElementById("modalConfirmar").classList.add("oculto");
});

// ============================================================
// Botón Reiniciar (pantalla final)
// ============================================================
const btnReiniciar = document.getElementById("btnReiniciar");
if (btnReiniciar) {
    btnReiniciar.addEventListener("click", async function() {
        btnReiniciar.disabled    = true;
        btnReiniciar.textContent = "Reiniciando...";
        try {
            const res  = await fetch("/api/reiniciar", { method: "POST" });
            const data = await res.json();
            if (data.ok) window.location.href = "/agregar_estudiantes";
        } catch (e) {
            alert("Error al reiniciar.");
            btnReiniciar.disabled = false;
        }
    });
}

// ============================================================
// DOMContentLoaded: inicializar todo
// ============================================================
document.addEventListener("DOMContentLoaded", function() {

    // Colorear barras críticas
    document.querySelectorAll(".barra-progreso").forEach(function(barra) {
        const val = parseInt(barra.dataset.valor || "100");
        if (val <= 30) {
            barra.style.background = "linear-gradient(90deg, #dc2626, #ef4444)";
            const label = barra.closest(".barra-item");
            if (label) {
                const valorEl = label.querySelector(".barra-valor");
                if (valorEl) valorEl.style.color = "#ef4444";
            }
        }
    });

    // Botón ✕ Cambiar pregunta
    document.getElementById("btnCancelarPregunta")?.addEventListener("click", () => {
        esperandoRespuesta   = false;
        decisionSeleccionada = null;
        preguntaIdx          = null;
        document.getElementById("modalPregunta").classList.add("oculto");
        document.querySelectorAll(".decision-card").forEach(c => c.classList.remove("seleccionada"));
        document.getElementById("opcionesPregunta").innerHTML = "";
        const msg = document.getElementById("msgPregunta");
        if (msg) { msg.textContent = ""; msg.className = "msg-respuesta"; }
    });

    // Inicializar cooldowns al cargar
    if (typeof COOLDOWNS !== "undefined" && typeof RONDA_ACTUAL !== "undefined") {
        actualizarCooldowns(COOLDOWNS, RONDA_ACTUAL);
    }
});
