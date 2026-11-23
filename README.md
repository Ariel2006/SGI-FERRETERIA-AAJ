# SGI-Ferretería (incremento 1)

Sistema web de gestión de inventario para una ferretería. Caso práctico del
taller de ISO/IEC 29110 (Perfil Básico), Aseguramiento de la Calidad de
Software, ESPE, NRC 36845.

## Alcance del incremento 1

| Requisito | Descripción | Estado |
|---|---|---|
| RF-01 | Registrar producto | Implementado |
| RF-02 | Registrar entrada de mercadería | Implementado |
| RF-03 | Registrar salida sin permitir stock negativo | Implementado |
| RF-04 | Alertas de stock bajo (stock <= mínimo) | Implementado |
| RF-05 | Búsqueda sin distinguir mayúsculas ni tildes | Implementado |
| RF-06 | Valor total del inventario | Implementado |
| RF-07 | Kardex por producto | Implementado |
| RF-08 | Exportar stock bajo a CSV (SC-01) | Implementado |

## Cómo ejecutar

```bash
pip install -e ".[dev]"
pytest -v --cov=inventario --cov-branch      # 39 pruebas
uvicorn inventario.api:app --reload --app-dir src
```

## Estructura

```
src/inventario/     modelos.py, errores.py, servicio.py, api.py
tests/              test_servicio.py (PU-01..PU-18), test_api.py (PI-01..PI-06)
docs/               evidencias de ejecución de pruebas y medición de rendimiento
docs/entregables/   informe y presentación del taller (LaTeX y PDF)
```

## Entregables del taller

| Archivo | Contenido |
|---|---|
| `docs/entregables/Informe_ISO29110_AAJ.pdf` | Informe: guía paso a paso de ISO/IEC 29110 con todas las evidencias |
| `docs/entregables/Informe_ISO29110_AAJ.tex` | Fuente LaTeX del informe (compila con pdfLaTeX) |
| `docs/entregables/Presentacion_ISO29110_AAJ.pdf` | Presentación de 15 minutos (Beamer) |
| `docs/entregables/Presentacion_ISO29110_AAJ.tex` | Fuente LaTeX de la presentación |
| `docs/entregables/Notas_Presentacion_AAJ.pdf` | Guion del expositor con tiempos por diapositiva |

Autor: Ariel Jara.

## Estrategia de control de versiones

Rama única `main` (equipo de una persona). Cada commit lleva el identificador
de la tarea ISO/IEC 29110 que lo origina (p. ej. `IS.4.5`, `GP.2.2`). Las
líneas base se marcan con etiquetas Git (`lb-IS4`, `v0.1.0`) y el repositorio
se respalda en un remoto al final de cada sesión (GP.2.5).
