import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Definición de la ruta del archivo de persistencia dentro del contenedor
DATA_FILE = "data/historial_predicciones.json"

INTERPRETACIONES = {
    "NO ENFERMO": "Sin crisis drepanocítica activa. Control ambulatorio de rutina.",
    "ENFERMEDAD LEVE": "Crisis leve. Manejo ambulatorio con analgesia e hidratación oral.",
    "ENFERMEDAD AGUDA": "Crisis moderada. Observación hospitalaria, analgesia IV e hidratación.",
    "ENFERMEDAD CRÓNICA": "Crisis grave / Síndrome Torácico Agudo. Hospitalización urgente.",
    "ENFERMEDAD TERMINAL": "Crisis muy grave. Evaluación en unidad de cuidados intensivos."
}

# Asegurar que la carpeta 'data' exista para que Docker no falle
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

def guardar_prediccion(resultado):
    """Guarda la predicción actual en el archivo JSON con su respectiva marca de tiempo."""
    registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "categoria": resultado
    }
    
    historial = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                historial = json.load(f)
        except Exception:
            historial = []
            
    historial.append(registro)
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=4)

def predecir_crisis(spo2: float, dolor: int, hemoglobina: float,
                    fiebre: float, frecuencia_respiratoria: int,
                    crisis_previas_6m: int = 0) -> str:
    if spo2 < 85 and dolor >= 9 and hemoglobina < 5 and fiebre >= 39.5 and frecuencia_respiratoria > 40:
        return "ENFERMEDAD TERMINAL"    
    elif spo2 < 90 and frecuencia_respiratoria > 30 and hemoglobina < 5:
        return "ENFERMEDAD CRÓNICA"
    elif spo2 < 94 and dolor >= 8 and hemoglobina < 7:
        return "ENFERMEDAD AGUDA"
    elif dolor >= 4 and fiebre >= 38.5 and crisis_previas_6m >= 3:
        return "ENFERMEDAD LEVE"
    else:
        return "NO ENFERMO"

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/predecir", methods=["POST"])
def predecir():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        spo2 = float(data.get("spo2"))
        dolor = int(data.get("dolor"))
        hemoglobina = float(data.get("hemoglobina"))
        fiebre = float(data.get("fiebre"))
        frecuencia_respiratoria = int(data.get("frecuencia_respiratoria"))
        crisis_previas_6m = int(data.get("crisis_previas_6m", 0))

        resultado = predecir_crisis(spo2, dolor, hemoglobina, fiebre,
                                    frecuencia_respiratoria, crisis_previas_6m)
        interpretacion = INTERPRETACIONES[resultado]

        # NUEVO: Guardar de manera persistente la predicción realizada
        guardar_prediccion(resultado)

        if request.is_json:
            return jsonify({
                "entrada": {"spo2": spo2, "dolor": dolor, "hemoglobina": hemoglobina, "fiebre": fiebre, "frecuencia_respiratoria": frecuencia_respiratoria, "crisis_previas_6m": crisis_previas_6m},
                "resultado": resultado,
                "interpretacion_clinica": interpretacion,
            })

        return render_template("index.html", resultado=resultado, interpretacion=interpretacion)

    except Exception as error:
        mensaje = "Datos inválidos. Revise todos los campos obligatorios."
        if request.is_json:
            return jsonify({"error": mensaje, "detalle": str(error)}), 400
        return render_template("index.html", error=mensaje), 400

# ==============================================================================
# NUEVA RUTA: REPORTES Y ESTADÍSTICAS PARA LOS MÉDICOS
# ==============================================================================
@app.route("/estadisticas", methods=["GET"])
def obtener_estadisticas():
    historial = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                historial = json.load(f)
        except Exception:
            pass

    # 1. Inicializar el conteo de predicciones por cada categoría disponible
    conteo_categorias = {cat: 0 for cat in INTERPRETACIONES.keys()}
    for registro in historial:
        cat = registro.get("categoria")
        if cat in conteo_categorias:
            conteo_categorias[cat] += 1

    # 2. Obtener las últimas 5 predicciones (invirtiendo la lista)
    ultimas_5 = historial[-5:][::-1] if historial else []

    # 3. Obtener la fecha de la última predicción general
    fecha_ultima = historial[-1]["fecha"] if historial else "No hay predicciones registradas aún"

    reporte = {
        "total_predicciones_por_categoria": conteo_categorias,
        "ultimas_5_predicciones": ultimas_5,
        "fecha_ultima_prediccion": fecha_ultima,
        "gran_total_predicciones": len(historial)
    }

    # CAMBIO: En vez de JSON crudo, enviamos los datos maquetados a la plantilla HTML
    return render_template("reporte.html", datos=reporte)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)