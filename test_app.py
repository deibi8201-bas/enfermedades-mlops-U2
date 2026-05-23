import os
import json
import pytest
from app import app, DATA_FILE

@pytest.fixture(autouse=True)
def limpiar_datos():
    """Filtro de limpieza: Elimina el archivo JSON antes y después de cada prueba."""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    yield
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)


# PRUEBA 1: Antes de correr cualquier predicción, esperar que no haya estadísticas
def test_estadisticas_iniciales_vacias():
    client = app.test_client()
    client.get("/estadisticas")
    assert os.path.exists(DATA_FILE) is False


# PRUEBA 2: Evaluar distintos grupos de parámetros individuales y esperar las 5 categorías
@pytest.mark.parametrize(
    "spo2, dolor, hemoglobina, fiebre, frecuencia_respiratoria, crisis_previas_6m, categoria_esperada",
    [
        (98, 1, 11.0, 36.0, 12, 0, "NO ENFERMO"),
        (96, 4, 8.0, 37.0, 18, 1, "ENFERMEDAD LEVE"),
        (92, 5, 7.5, 38.0, 22, 2, "ENFERMEDAD AGUDA"),
        (88, 7, 5.0, 39.0, 32, 3, "ENFERMEDAD CRÓNICA"),
        (80, 10, 2.0, 40.0, 45, 4, "ENFERMEDAD TERMINAL")
    ]
)
def test_obtener_todas_las_categorias(spo2, dolor, hemoglobina, fiebre, frecuencia_respiratoria, crisis_previas_6m, categoria_esperada):
    client = app.test_client()
    payload = {
        "spo2": spo2, "dolor": dolor, "hemoglobina": hemoglobina,
        "fiebre": fiebre, "frecuencia_respiratoria": frecuencia_respiratoria,
        "crisis_previas_6m": crisis_previas_6m
    }
    response = client.post("/predecir", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["resultado"] == categoria_esperada


# PRUEBA 3: Realizar las 5 predicciones seguidas y verificar el conteo preciso en el reporte
def test_conteo_exacto_por_categoria_en_reporte():
    client = app.test_client()
    
    # Definimos un set con los 5 escenarios clínicos diferentes
    casos_clinicos = [
        {"spo2": 98, "dolor": 1, "hemoglobina": 11.0, "fiebre": 36.0, "frecuencia_respiratoria": 12, "crisis_previas_6m": 0}, # NO ENFERMO
        {"spo2": 96, "dolor": 4, "hemoglobina": 8.0, "fiebre": 37.0, "frecuencia_respiratoria": 18, "crisis_previas_6m": 1}, # ENFERMEDAD LEVE
        {"spo2": 92, "dolor": 5, "hemoglobina": 7.5, "fiebre": 38.0, "frecuencia_respiratoria": 22, "crisis_previas_6m": 2}, # ENFERMEDAD AGUDA
        {"spo2": 88, "dolor": 7, "hemoglobina": 5.0, "fiebre": 39.0, "frecuencia_respiratoria": 32, "crisis_previas_6m": 3}, # ENFERMEDAD CRÓNICA
        {"spo2": 80, "dolor": 10, "hemoglobina": 2.0, "fiebre": 40.0, "frecuencia_respiratoria": 45, "crisis_previas_6m": 4} # ENFERMEDAD TERMINAL
    ]
    
    # 1. Ejecutar las 5 peticiones de forma consecutiva
    for caso in casos_clinicos:
        response = client.post("/predecir", json=caso)
        assert response.status_code == 200

    # 2. Verificar que el archivo persistente exista y contenga los 5 registros de auditoría
    assert os.path.exists(DATA_FILE) is True
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        historial = json.load(f)
        
    assert len(historial) == 5

    # 3. Inicializar un diccionario para simular el conteo que hace tu vista `/estadisticas`
    conteo_categorias = {
        "NO ENFERMO": 0,
        "ENFERMEDAD LEVE": 0,
        "ENFERMEDAD AGUDA": 0,
        "ENFERMEDAD CRÓNICA": 0,
        "ENFERMEDAD TERMINAL": 0
    }
    
    # Contabilizar lo que realmente quedó escrito en la persistencia de datos
    for registro in historial:
        cat = registro["categoria"]
        if cat in conteo_categorias:
            conteo_categorias[cat] += 1

    # 4. LA PRUEBA DE ORO: Validar que cada categoría sume exactamente 1 en las estadísticas
    assert conteo_categorias["NO ENFERMO"] == 1
    assert conteo_categorias["ENFERMEDAD LEVE"] == 1
    assert conteo_categorias["ENFERMEDAD AGUDA"] == 1
    assert conteo_categorias["ENFERMEDAD CRÓNICA"] == 1
    assert conteo_categorias["ENFERMEDAD TERMINAL"] == 1