"""Genera el tablero analítico (una sola página HTML) a partir de los archivos del proyecto.

Uso (desde la carpeta del repositorio, donde están los CSV):

    python generador/generar_tablero.py --url-app aplicacion.html

Lee:    Datos_Limpios.csv, KPIs_EDA.csv, Perfil_Habilidades_por_Posicion.csv,
        Correlaciones_Habilidades.csv y la carpeta resultados_modelado/
Escribe: docs/index.html  (la carpeta que publica GitHub Pages)

Todas las cifras del tablero salen de esos archivos; no se escribe ninguna a mano.
"""
import argparse
import json
import os

import pandas as pd
from scipy import stats

HABILIDADES = [
    "velocidad", "resistencia", "fuerza", "control_balon", "regate", "pase",
    "definicion", "defensa", "juego_aereo", "vision_juego", "reflejos", "posicionamiento",
]
NOMBRES = {
    "velocidad": "Velocidad", "resistencia": "Resistencia", "fuerza": "Fuerza",
    "control_balon": "Control del balón", "regate": "Regate", "pase": "Pase",
    "definicion": "Definición", "defensa": "Defensa", "juego_aereo": "Juego aéreo",
    "vision_juego": "Visión de juego", "reflejos": "Reflejos", "posicionamiento": "Posicionamiento",
}
POSICIONES = [
    "Portero", "Defensa central", "Lateral", "Mediocampista defensivo",
    "Mediocampista ofensivo", "Extremo", "Delantero",
]


def leer(ruta):
    return pd.read_csv(ruta, encoding="utf-8-sig")


def limpio(df):
    """DataFrame -> lista de diccionarios con None en lugar de NaN (JSON válido)."""
    return json.loads(df.to_json(orient="records", force_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datos", default=".", help="carpeta con Datos_Limpios.csv y los CSV del EDA")
    parser.add_argument("--resultados", default="resultados_modelado", help="carpeta con los resultados del modelado")
    parser.add_argument("--salida", default=os.path.join("docs", "index.html"))
    parser.add_argument("--url-app", default="", help="enlace de la aplicación web (puede ser relativo)")
    parser.add_argument("--plantilla", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "plantilla_tablero.html"))
    args = parser.parse_args()

    d = args.datos
    r = args.resultados
    datos = leer(os.path.join(d, "Datos_Limpios.csv"))
    kpis = leer(os.path.join(d, "KPIs_EDA.csv"))
    perfil = leer(os.path.join(d, "Perfil_Habilidades_por_Posicion.csv"))
    correlaciones = leer(os.path.join(d, "Correlaciones_Habilidades.csv"))
    resumen = leer(os.path.join(r, "Resumen_Modelado.csv")).set_index("concepto")["valor"].to_dict()

    # --- Comprobaciones de consistencia entre archivos -------------------------------------------------
    assert len(datos) == int(resumen["personas"]), "Datos_Limpios.csv no coincide con el resumen del modelado."
    promedio = datos.groupby("posicion")[HABILIDADES].mean().reindex(POSICIONES)
    referencia = perfil.set_index("posicion").reindex(POSICIONES)
    referencia.columns = HABILIDADES
    assert (promedio - referencia).abs().max().max() < 0.001, "El perfil por posición no coincide con los datos."

    # Cuántas respuestas se recibieron (válidas + las que dijeron "No").
    recibidas = int(kpis.loc[kpis["kpi"] == "Respuestas recibidas", "valor"].iloc[0])

    # Separación de posiciones por habilidad (Kruskal-Wallis, tamaño del efecto ε²), igual que en el EDA.
    separacion = []
    for h in HABILIDADES:
        sub = datos[["posicion", h]].dropna()
        grupos = [sub.loc[sub["posicion"] == p, h].to_numpy(dtype=float) for p in POSICIONES]
        H, _ = stats.kruskal(*grupos)
        separacion.append({"habilidad": NOMBRES[h], "efecto": float(H / (len(sub) - 1))})
    separacion.sort(key=lambda x: -x["efecto"])

    banderas = {c: int(datos[c].sum()) for c in
                ["duplicado_posible", "duplicado_repetida", "menor_18", "edad_atipica", "linea_recta", "incoherencia_experiencia"]}

    columnas = ["posicion", "nivel", "edad", "tiempo_juego", "horas_semana"] + HABILIDADES
    corr = correlaciones.set_index("habilidad")

    paquete = {
        "personas": limpio(datos[columnas]),
        "habilidades": [{"id": h, "nombre": NOMBRES[h]} for h in HABILIDADES],
        "posiciones": POSICIONES,
        "recibidas": recibidas,
        "banderas": banderas,
        "no_se_celdas": int(datos["n_no_se"].sum()),
        "no_se_personas": int((datos["n_no_se"] > 0).sum()),
        "separacion": separacion,
        "correlaciones": {"nombres": list(corr.index), "valores": corr.round(3).values.tolist()},
        "modelos": limpio(leer(os.path.join(r, "Resultados_Modelos.csv"))),
        "pca": limpio(leer(os.path.join(r, "Comparacion_PCA.csv"))),
        "variables": limpio(leer(os.path.join(r, "Comparacion_Variables.csv"))),
        "por_posicion": limpio(leer(os.path.join(r, "Resultados_Por_Posicion.csv"))),
        "confusion": limpio(leer(os.path.join(r, "Matriz_Confusion.csv"))),
        "importancia": limpio(leer(os.path.join(r, "Importancia_Variables.csv"))),
        "calibracion": limpio(leer(os.path.join(r, "Calibracion.csv"))),
        "sensibilidad": limpio(leer(os.path.join(r, "Sensibilidad.csv"))),
        "kmeans": limpio(leer(os.path.join(r, "Resultados_KMeans.csv"))),
        "resumen": resumen,
        "url_app": args.url_app,
    }

    with open(args.plantilla, encoding="utf-8") as f:
        plantilla = f.read()
    marcador = "/*__DATOS__*/null"
    assert marcador in plantilla
    html = plantilla.replace(marcador, json.dumps(paquete, ensure_ascii=False, allow_nan=False))

    os.makedirs(os.path.dirname(args.salida) or ".", exist_ok=True)
    with open(args.salida, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Tablero generado: {args.salida} ({len(html) / 1024:.0f} KB) | personas: {len(datos)} | modelo elegido: {resumen['mejor_modelo']}")


if __name__ == "__main__":
    main()
