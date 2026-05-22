# Servicio Docker para evaluación de crisis drepanocítica

## Finalidad

Este proyecto corresponde a una actividad académica de MLOps. Su objetivo es mostrar cómo se puede empaquetar en Docker un servicio que recibe parámetros clínicos básicos de un paciente con drepanocitosis (anemia falciforme) y retorna una categoría simulada de severidad de crisis.

La drepanocitosis es una enfermedad huérfana con prevalencia real en Colombia, especialmente en comunidades afrodescendientes del Pacífico y el Caribe. El modelo simula la evaluación de una posible crisis vaso-oclusiva o síndrome torácico agudo.

La función no representa un modelo clínico validado. Solo simula el comportamiento esperado para fines de despliegue en MLOps.

## Estados posibles

| Estado | Interpretación clínica |
|--------|------------------------|
| `NO ENFERMO` | Sin crisis drepanocítica activa. Control ambulatorio de rutina. |
| `ENFERMEDAD LEVE` | Crisis leve. Manejo ambulatorio con analgesia e hidratación oral. |
| `ENFERMEDAD AGUDA` | Crisis moderada. Observación hospitalaria, analgesia IV e hidratación. |
| `ENFERMEDAD CRÓNICA` | Crisis grave / Síndrome Torácico Agudo. Hospitalización urgente. |
| `ENFERMEDAD TERMINAL` | Crisis muy grave. Evaluación inmediata en unidad de cuidados intensivos. |

## Variables de entrada

| Variable | Descripción | Tipo |
|----------|-------------|------|
| `spo2` | Saturación de oxígeno (%) | float, obligatorio |
| `dolor` | Escala de dolor 0–10 | int, obligatorio |
| `hemoglobina` | Hemoglobina en g/dL | float, obligatorio |
| `fiebre` | Temperatura en °C | float, obligatorio |
| `frecuencia_respiratoria` | Respiraciones por minuto | int, obligatorio |
| `crisis_previas_6m` | Número de crisis en los últimos 6 meses | int, opcional (default 0) |

## Reglas simuladas de predicción

1. **`ENFERMEDAD TERMINAL`**: `SpO₂ < 85` **y** `dolor ≥ 9` **y** `Hb < 5` **y** `fiebre ≥ 39.5` **y** `FR > 40`
2. **`ENFERMEDAD CRÓNICA`**: `SpO₂ < 90` **y** `FR > 30` **y** `Hb < 5`
3. **`ENFERMEDAD AGUDA`**: `SpO₂ < 94` **y** `dolor ≥ 8` **y** `Hb < 7`
4. **`ENFERMEDAD LEVE`**: `dolor ≥ 4` **y** `fiebre ≥ 38.5` **y** `crisis_previas_6m ≥ 3`
5. **`NO ENFERMO`**: Ninguna de las condiciones anteriores se cumple.

## Estructura del proyecto

```text
mlops_enfermedades_app/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── templates/
    ├── index.html
    └── reporte.html
```

## Despliegue y Automatización con Docker Compose

El proyecto utiliza Docker Compose para automatizar el ciclo de vida del contenedor, configurar el almacenamiento persistente nativo y sincronizar de manera automática el huso horario de Colombia (America/Bogota).

Desde la carpeta del proyecto, ejecutar:

```bash
docker compose up -d --build
```

Después de ejecutar el comando, abrir en el navegador:

```text
http://localhost:5000
```

## Cómo obtener respuestas desde la página web

En la página web se ingresan los valores clínicos del paciente:

- SpO₂ (saturación de oxígeno)
- Dolor (0–10)
- Hemoglobina (g/dL)
- Temperatura (°C)
- Frecuencia respiratoria (rpm)
- Número de crisis previas en 6 meses

Luego se presiona el botón `Evaluar` y el sistema muestra el estado y la interpretación clínica.

## Cómo consultar las estadisticas 

```text
http://localhost:5000/estadisticas
```

## Ejemplos para probar los cinco estados

### NO ENFERMO — sin crisis activa

```json
{"spo2":98,"dolor":1,"hemoglobina":9.0,"fiebre":36.8,"frecuencia_respiratoria":16,"crisis_previas_6m":0}
```

### ENFERMEDAD LEVE — crisis leve

```json
{"spo2":96,"dolor":5,"hemoglobina":7.8,"fiebre":38.6,"frecuencia_respiratoria":20,"crisis_previas_6m":1}
```

### ENFERMEDAD AGUDA — crisis moderada

```json
{"spo2":92,"dolor":8,"hemoglobina":6.5,"fiebre":38.0,"frecuencia_respiratoria":22,"crisis_previas_6m":2}
```

### ENFERMEDAD CRÓNICA — crisis grave / síndrome torácico agudo

```json
{"spo2":87,"dolor":9,"hemoglobina":4.5,"fiebre":39.2,"frecuencia_respiratoria":34,"crisis_previas_6m":5}
```
### ENFERMEDAD TERMINAL — crisis grave / síndrome torácico agudo

```json
{"spo2":84,"dolor":10,"hemoglobina":3,"fiebre":41,"frecuencia_respiratoria":45,"crisis_previas_6m":5}
```

## Nota ética y clínica

Esta solución es únicamente académica. En un escenario real se requeriría validación clínica, revisión de sesgos, protección de datos personales conforme a la normativa colombiana (Ley 1581), seguridad, trazabilidad y monitoreo continuo del desempeño del modelo.
    "fiebre": 38.2,
    "dolor": 5,
    "duracion_dias": 4,
    "perdida_peso": false
  },
  "resultado": "ENFERMEDAD LEVE"
}
```

## Nota ética y clínica

Esta solución es únicamente académica. En un escenario real se requeriría validación clínica, revisión de sesgos, protección de datos personales, seguridad, trazabilidad y monitoreo continuo del desempeño del modelo.
