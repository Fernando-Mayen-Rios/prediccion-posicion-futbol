# Predicción de la posición habitual de un jugador de fútbol

Proyecto final de **Sistemas Inteligentes** (UNAM).

**Integrantes:** [NOMBRE COMPLETO 1], [NOMBRE COMPLETO 2], [NOMBRE COMPLETO 3], [NOMBRE COMPLETO 4], [NOMBRE COMPLETO 5]

## Enlaces
- **Tablero analítico (web pública):** [PEGAR ENLACE DEL TABLERO]
- **Aplicación web de predicción (pública):** [PEGAR ENLACE DE LA APLICACIÓN]

## ¿De qué trata?
Clasificación supervisada de 7 posiciones (portero, defensa central, lateral, mediocampista defensivo, mediocampista ofensivo, extremo y delantero) a partir de 12 habilidades que cada persona se califica de 1 a 5 en un formulario de Google propio (290 respuestas, 272 válidas).

**Resultado del modelo elegido (regresión logística):** F1 macro 0.688 ± 0.057, 68.4 % de aciertos y 82.7 % en top-2. Referencias: azar 14.3 %, modelo base 19.5 %. Resultados medidos con validación cruzada anidada; no se juntaron posiciones para mejorar la cifra. Con 272 personas el techo es bajo: tres familias de modelos distintas empatan en ~0.69. Detalles y limitaciones en el documento técnico.

## Por dónde empezar
Los cuadernos se ejecutan en orden, pero **cada uno puede correrse por separado** porque los archivos intermedios ya están en el repositorio.

| Cuaderno | Qué hace | Entrada |
|---|---|---|
| `01_Auditoria_y_Limpieza.ipynb` | Auditoría y **limpieza de datos** con reglas y regex, con bitácora de cada cambio | `Predicción de la posición habitual de un jugador de fútbol.csv` (original, sin modificar) |
| `02_EDA_y_KPIs.ipynb` | Análisis exploratorio y KPIs | `Datos_Limpios.csv` |
| `03_Modelado.ipynb` | Modelos, validación anidada, calibración, K-means, sensibilidad (tarda varios minutos) | `Datos_Limpios.csv` |
| `04_Base_de_Datos.ipynb` | Base SQLite (18 tablas, 6 vistas) y consultas de ejemplo | CSV de resultados y `Resultados_Modelado.zip` |

- Para **ver cómo se limpiaron los datos**, empezar en el **01**.
- Para **ver resultados y modelo directamente**, empezar en el **02** o el **03**.

## Estructura
- `docs/` — tablero (`index.html`) y aplicación (`aplicacion.html`), publicados con GitHub Pages.
- `generador/` — scripts que exportan el modelo a JSON y generan el tablero y la aplicación a partir de los CSV.
- `resultados_modelado/` — resultados del modelado (CSV), modelo (`.joblib`, `modelo_metadata.json`) y `modelo_app.json`.
- `requirements.txt` — versiones exactas.
- Documentos: `Documento_Tecnico.docx`, `Documento_Negocio.docx`.

## Cómo reproducirlo
```
pip install -r requirements.txt
```
Ejecutar los cuadernos 01 a 04 (se usaron en Google Colab, Python 3.13.18). Semillas fijas.
Para regenerar la web: `python generador/exportar_modelo.py --modelo resultados_modelado/modelo_posicion.joblib --metadata resultados_modelado/modelo_metadata.json --salida resultados_modelado/modelo_app.json`, luego `python generador/generar_aplicacion.py` y `python generador/generar_tablero.py --url-app aplicacion.html`.
(El `.joblib` solo abre con scikit-learn 1.6.1; por eso la app usa `modelo_app.json`.)

## Privacidad
El formulario no pidió nombre, correo ni teléfono. La marca de tiempo no se usa en el análisis. La aplicación web corre en el navegador y no envía ni guarda datos.

## Uso de inteligencia artificial (transparencia)
Se usó un asistente de IA (Claude, de Anthropic) para escribir y probar el código, generar el tablero y la aplicación, y redactar documentos y guion de exposición. El equipo definió el planteamiento, creó el formulario, ejecutó los cuadernos en Google Colab y revisó los resultados; las cifras reportadas son las obtenidas en Colab. La limpieza de datos se hizo con reglas y expresiones regulares, sin IA ni NLP.

## Sistema experto
Se considera solo como antecedente conceptual; no se integró con el modelo.
