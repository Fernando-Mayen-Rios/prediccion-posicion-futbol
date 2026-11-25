# Predicción de la posición habitual de un jugador de fútbol

Proyecto final de **Sistemas Inteligentes** · UNAM · Noviembre de 2026

**Integrantes:** 
- Chávez Ramírez Iker David 
- Mayen Rios Fernando 
- Rangel Sosa Oscar Yardel 
- Sanchez Lopez Miguel Angel 
- Torres Montes Sharon Danae

## Enlaces
| Qué | Enlace |
|---|---|
| **Tablero analítico** (web pública) | https://fernando-mayen-rios.github.io/prediccion-posicion-futbol/ |
| **Aplicación web de predicción** (pública, sin registro) | https://fernando-mayen-rios.github.io/prediccion-posicion-futbol/aplicacion.html |
| Repositorio | https://github.com/fernando-mayen-rios/prediccion-posicion-futbol |

## 1. Resumen para negocio
**Problema.** Quien empieza a jugar fútbol, o juega por diversión, no sabe en qué posición aprovecharía mejor sus habilidades, y los entrenadores de equipos escolares y amateur arman alineaciones por intuición.

**Solución.** Una aplicación web gratuita y sin registro: la persona se califica de 1 a 5 en 12 habilidades y recibe las **3 posiciones que mejor le encajan**, con la explicación de qué habilidades pesaron. Todo se calcula en el navegador: no se envía ni guarda nada.

**Qué tan confiable es.** Con 272 personas reales: acierta la posición habitual en **68.4 %** de los casos y en **82.7 %** está entre sus dos primeras sugerencias. Adivinar al azar acertaría 14.3 %; decir siempre la posición más común, 19.5 %.

**Hallazgos.** El regate es la habilidad que más separa a las posiciones. Pesan más el juego aéreo, la definición, la defensa y los reflejos. Se reconocen mejor portero (F1 0.84), delantero (0.79) y extremo (0.77). Se confunden lateral y mediocampista defensivo (0.61 y 0.57), que en la cancha hacen tareas parecidas. La experiencia (nivel, años, horas por semana) no mejora la predicción.

**Límites.** Pocas personas (de 27 a 53 por posición), autoevaluaciones subjetivas y una muestra con mucho juego recreativo. Es una orientación, no un dictamen. No sirve para decidir fichajes profesionales.

**Siguientes pasos.** Más respuestas (sobre todo de laterales y mediocampistas defensivos), evaluaciones hechas por entrenadores y variables como altura o pie dominante. Más detalle en `Documento_Negocio.docx`.

## 2. Resumen técnico
- **Tipo de problema:** clasificación supervisada multiclase, 7 clases (Portero, Defensa central, Lateral, Mediocampista defensivo, Mediocampista ofensivo, Extremo, Delantero).
- **Datos:** formulario propio de Google de 18 preguntas. 290 respuestas; 18 excluidas por no jugar; **272 válidas**. 12 habilidades autoevaluadas de 1 a 5 (con opción "No sé").
- **Limpieza:** solo reglas y expresiones regulares, con bitácora. No se borran casos dudosos: se marcan con banderas (duplicado posible, menor de 18, edad atípica, línea recta, incoherencia de experiencia) y se mide su efecto. Los 17 "No sé" (0.52 % de las celdas) se imputan con la mediana dentro de cada pliegue.
- **Evaluación:** validación cruzada anidada (externa 5 pliegues × 2 repeticiones, interna 3 pliegues con GridSearchCV), semillas fijas, preprocesamiento dentro del pipeline (sin fuga de información). Métrica principal: **F1 macro**; también aciertos, top-2, calibración (ECE).
- **Modelos comparados:** base, k vecinos, regresión logística, SVM calibrada, árbol y bosque (con y sin PCA donde aplica).
- **Selección:** regla de parsimonia fijada de antemano (entre modelos a menos de 0.01 de F1 del mejor, el más simple). Elegido: **regresión logística (C = 0.1)**.

| Modelo | F1 macro | Aciertos | Top-2 |
|---|---|---|---|
| Bosque aleatorio | 0.693 | 68.6 % | 80.0 % |
| Regresión logística + PCA | 0.692 | 68.8 % | 82.9 % |
| **Regresión logística (elegido)** | **0.688 ± 0.057** | **68.4 %** | **82.7 %** |
| SVM | 0.674 | 66.4 % | 80.4 % |
| SVM + PCA | 0.661 | 65.2 % | 82.2 % |
| k vecinos | 0.648 | 64.0 % | 74.8 % |
| k vecinos + PCA | 0.647 | 64.5 % | 77.8 % |
| Árbol de decisión | 0.608 | 60.7 % | 69.5 % |
| Base (siempre la más común) | 0.047 | 19.5 % | 35.3 % |

**Cómo leer el resultado.** Tres familias de modelos muy distintas empatan en torno a 0.69 y su diferencia es menor que la variación entre pliegues (± 0.057). Eso indica que el límite lo pone la información disponible (272 personas y autoevaluaciones subjetivas), no el algoritmo. No se juntaron posiciones para mejorar la cifra.

**Otras pruebas:** PCA (−0.003) y agregar experiencia (−0.004) no mejoran; sin casos marcados F1 0.682 (n = 260), sin menores de 18 F1 0.652 (n = 239); K-means exploratorio no recupera las posiciones (ARI 0.03 con k = 2, 0.12 con k = 7); ECE = 0.172 (> 0.08), por eso la aplicación no muestra porcentajes. Detalle completo en `Documento_Tecnico.docx`.

## 3. Contenido del repositorio
| Carpeta o archivo | Qué es |
|---|---|
| `01_Auditoria_y_Limpieza.ipynb` | Auditoría y limpieza de datos (reglas y regex, con bitácora) |
| `02_EDA_y_KPIs.ipynb` | Análisis exploratorio y KPIs |
| `03_Modelado.ipynb` | Modelado, validación anidada, calibración, K-means y sensibilidad |
| `04_Base_de_Datos.ipynb` | Base de datos SQLite (18 tablas, 6 vistas) y consultas |
| `Predicción de la posición habitual de un jugador de fútbol.csv` | Respuestas originales del formulario (sin nombre ni contacto) |
| `Datos_Limpios.csv`, `Bitacora_Limpieza.csv`, `Respuestas_Originales_Anonimas.csv` | Salidas del cuaderno 01 |
| `KPIs_EDA.csv`, `Perfil_Habilidades_por_Posicion.csv`, `Correlaciones_Habilidades.csv` | Salidas del cuaderno 02 |
| `resultados_modelado/` | Salidas del cuaderno 03 (CSV, `modelo_posicion.joblib`, `modelo_metadata.json`) y `modelo_app.json` |
| `docs/` | Tablero (`index.html`) y aplicación (`aplicacion.html`), publicados con GitHub Pages |
| `generador/` | Scripts que exportan el modelo y generan el tablero y la aplicación |
| `antecedente_sistema_experto/` | Antecedente conceptual: sistema experto previo basado en reglas y pesos definidos por personas. No se usa en el modelo de predicción |
| `requirements.txt` | Versiones exactas de las librerías |
| `Documento_Tecnico.docx`, `Documento_Negocio.docx` | Documentos del proyecto |

## 4. Cómo ejecutar todo (paso a paso)
### Por dónde empezar
Los cuadernos van en orden 01 → 02 → 03 → 04, pero **cada uno puede ejecutarse por separado** porque los archivos intermedios ya están en el repositorio.
- Para **comprobar cómo se limpiaron los datos**: empezar en el **01**.
- Para **ver análisis o resultados sin repetir la limpieza**: empezar en el **02** (análisis) o el **03** (modelo).

| Cuaderno | Necesita en la misma carpeta | Genera | Tiempo aproximado |
|---|---|---|---|
| 01 | `Predicción de la posición habitual de un jugador de fútbol.csv` | `Datos_Limpios.csv`, `Bitacora_Limpieza.csv`, `Respuestas_Originales_Anonimas.csv` | segundos |
| 02 | `Datos_Limpios.csv` (y opcionalmente `Bitacora_Limpieza.csv`) | `KPIs_EDA.csv`, `Perfil_Habilidades_por_Posicion.csv`, `Correlaciones_Habilidades.csv` | segundos |
| 03 | `Datos_Limpios.csv` | carpeta `resultados_modelado/` y `Resultados_Modelado.zip` | **varios minutos** |
| 04 | los 6 CSV anteriores y `Resultados_Modelado.zip` | `Base_Datos_Futbol.db`, `consultas_ejemplo.sql`, `exportes_csv.zip` | segundos |

### Opción A. Google Colab (la que usamos; no hay que instalar nada)
1. Descarga o clona este repositorio (https://github.com/fernando-mayen-rios/prediccion-posicion-futbol; botón verde **Code → Download ZIP**) y descomprímelo.
2. Entra a https://colab.research.google.com con una cuenta de Google y elige **Archivo → Subir cuaderno**; sube `01_Auditoria_y_Limpieza.ipynb`.
3. Abre el panel de archivos de la izquierda (icono de carpeta) y arrastra el CSV original `Predicción de la posición habitual de un jugador de fútbol.csv`. Si no lo subes, el cuaderno abrirá una ventana para elegirlo.
4. Ejecuta **Entorno de ejecución → Ejecutar todo**. La primera línea imprime las versiones de las librerías; no debe haber errores ni advertencias.
5. Repite el proceso con 02, 03 y 04, subiendo cada vez los archivos que la tabla anterior indica (los cuadernos también abren una ventana para subirlos).
6. Los archivos generados se descargan solos o se ven en el panel de archivos.

### Opción B. En tu computadora (Windows, macOS o Linux)
1. Instala Python 3.11 o superior desde https://www.python.org/downloads/ y Git (opcional).
2. Descarga el repositorio y entra a la carpeta desde una terminal:
```
git clone https://github.com/fernando-mayen-rios/prediccion-posicion-futbol.git
cd prediccion-posicion-futbol
```
3. Crea un entorno e instala las librerías:
```
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -r requirements.txt
pip install notebook
```
4. Abre Jupyter y ejecuta los cuadernos en orden (Kernel → Restart & Run All):
```
jupyter notebook
```
Mantén los cuadernos y los CSV en la **misma carpeta**. Los resultados exactos del proyecto se obtuvieron con las versiones de `requirements.txt` (Python 3.13.18, scikit-learn 1.6.1); con otras versiones pueden aparecer diferencias mínimas.

### Regenerar el tablero y la aplicación web
Desde la carpeta del repositorio, con las librerías instaladas:
```
python generador/exportar_modelo.py --modelo resultados_modelado/modelo_posicion.joblib --metadata resultados_modelado/modelo_metadata.json --salida resultados_modelado/modelo_app.json
python generador/generar_aplicacion.py
python generador/generar_tablero.py --url-app aplicacion.html
```
- El primer paso necesita **scikit-learn 1.6.1** (la versión que guardó el modelo). Si usas otra versión, omítelo: `modelo_app.json` ya está en el repositorio.
- Los otros dos escriben `docs/aplicacion.html` y `docs/index.html`. Para verlos, abre esos archivos en el navegador.

### Solución de problemas
| Problema | Qué hacer |
|---|---|
| "No se encontró el archivo..." | El CSV debe estar en la misma carpeta que el cuaderno y con el nombre exacto indicado; en Colab, súbelo al panel de archivos |
| El cuaderno 03 parece detenido | Es normal: tarda varios minutos; espera a que termine la celda |
| Error al abrir `modelo_posicion.joblib` | Se guardó con scikit-learn 1.6.1; instala esa versión o usa `modelo_app.json` |
| Diferencias de decimales | Usa las versiones de `requirements.txt` |
| El CSV se ve mal en Excel | No lo guardes desde Excel (cambia la codificación); ábrelo solo para leer |

## 5. Privacidad
El formulario no pidió nombre, correo ni teléfono, y la marca de tiempo no se usa en el análisis. La aplicación web calcula todo en el navegador y no envía ni guarda lo que se escribe.

## 6. Uso de inteligencia artificial (declaración)
Se utilizó Claude (Anthropic), un asistente de inteligencia artificial, como herramienta de apoyo. Lo usamos sobre todo para (1) construir la aplicación web, (2) escribir el código que genera el tablero, (3) documentar y comentar los cuadernos, y (4) apoyarnos en la revisión del código. El equipo definió el problema, diseñó y aplicó el formulario, tomó las decisiones del proyecto, ejecutó los cuadernos en Google Colab y revisó los resultados. Las cifras reportadas son las que obtuvimos en Colab. La limpieza de datos se hizo con reglas y expresiones regulares, sin IA ni NLP.

## 7. Sistema experto
Se consideró solo como antecedente conceptual y está en la carpeta `antecedente_sistema_experto/`. Funciona con reglas y pesos definidos por personas; no se integró con el modelo de aprendizaje automático, que aprende sus pesos a partir de los datos.
