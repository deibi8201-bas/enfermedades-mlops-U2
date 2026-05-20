# Entrega actividad MLOps: predicción simulada de enfermedad

Este directorio contiene los dos componentes solicitados en la actividad:

1. Descripción general de un pipeline de MLOps para el problema de predicción de enfermedades comunes y huérfanas.
2. Servicio Docker funcional que permite simular una predicción clínica a partir de datos ingresados por un médico.

## Archivos incluidos

- `pipeline_mlops.md`: descripción del pipeline end-to-end con diagrama general en formato Mermaid.
- `app.py`: aplicación Flask con función simulada de predicción.
- `templates/index.html`: página web sencilla para ingresar datos clínicos.
- `requirements.txt`: dependencias de Python.
- `Dockerfile`: archivo para construir la imagen personalizada de Docker.
- `README.md`: instrucciones de construcción, ejecución y pruebas.

## Nota

La función implementada es simulada y no corresponde a un modelo clínico real. Su finalidad es demostrar el despliegue de una solución en Docker dentro del contexto de MLOps.
