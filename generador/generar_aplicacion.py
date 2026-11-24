"""Genera la aplicación web (una sola página HTML) con el modelo ya exportado.

Uso (desde la carpeta del repositorio):

    python generador/generar_aplicacion.py

Lee:    resultados_modelado/modelo_app.json   (lo crea generador/exportar_modelo.py)
        resultados_modelado/Resumen_Modelado.csv
        Datos_Limpios.csv   (solo para los ejemplos: el perfil promedio de cada posición)
Escribe: docs/aplicacion.html

Las cifras de la página salen de esos archivos; no se escribe ninguna a mano.
"""
import argparse
import json
import os

import numpy as np
import pandas as pd

HABILIDADES = [
    "velocidad", "resistencia", "fuerza", "control_balon", "regate", "pase",
    "definicion", "defensa", "juego_aereo", "vision_juego", "reflejos", "posicionamiento",
]
NOMBRES = {
    "velocidad": "Velocidad", "resistencia": "Resistencia física", "fuerza": "Fuerza física",
    "control_balon": "Control del balón", "regate": "Capacidad de regate", "pase": "Precisión de pase",
    "definicion": "Definición o remate", "defensa": "Capacidad defensiva", "juego_aereo": "Juego aéreo",
    "vision_juego": "Visión de juego", "reflejos": "Reflejos", "posicionamiento": "Posicionamiento táctico",
}
ORDEN_POSICION = [
    "Portero", "Defensa central", "Lateral", "Mediocampista defensivo",
    "Mediocampista ofensivo", "Extremo", "Delantero",
]


def predecir(modelo, x):
    x = np.asarray(x, dtype=float)
    x = np.where(np.isnan(x), np.asarray(modelo["mediana"]), x)
    z = (x - np.asarray(modelo["media"])) / np.asarray(modelo["escala"])
    logits = z @ np.asarray(modelo["coef"]).T + np.asarray(modelo["intercepto"])
    logits -= logits.max(axis=-1, keepdims=True)
    e = np.exp(logits)
    return e / e.sum(axis=-1, keepdims=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datos", default=".")
    parser.add_argument("--resultados", default="resultados_modelado")
    parser.add_argument("--salida", default=os.path.join("docs", "aplicacion.html"))
    parser.add_argument("--plantilla", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "plantilla_aplicacion.html"))
    args = parser.parse_args()

    with open(os.path.join(args.resultados, "modelo_app.json"), encoding="utf-8") as f:
        modelo = json.load(f)
    resumen = pd.read_csv(os.path.join(args.resultados, "Resumen_Modelado.csv"), encoding="utf-8-sig") \
        .set_index("concepto")["valor"].to_dict()
    datos = pd.read_csv(os.path.join(args.datos, "Datos_Limpios.csv"), encoding="utf-8-sig")

    # --- Comprobaciones de consistencia -----------------------------------------------------------------
    assert modelo["columnas"] == HABILIDADES, "El orden de las variables del modelo no es el esperado."
    assert sorted(modelo["clases"]) == sorted(ORDEN_POSICION)
    assert modelo["modelo"] == resumen["mejor_modelo"], "El modelo exportado no es el elegido en el modelado."
    assert str(modelo["mostrar_probabilidades"]) == str(resumen["mostrar_probabilidades"])
    assert int(resumen["personas"]) == modelo["personas_entrenamiento"] == len(datos)

    # Ejemplos: perfil promedio redondeado de cada posición. Solo se incluyen los que el modelo
    # predice como esa misma posición (para que la demostración sea coherente y honesta).
    ejemplos, descartados = {}, []
    for pos in ORDEN_POSICION:
        perfil = datos.loc[datos["posicion"] == pos, HABILIDADES].mean().round(0).astype(int)
        pred = modelo["clases"][int(np.argmax(predecir(modelo, perfil.to_numpy())))]
        if pred == pos:
            ejemplos[pos] = perfil.tolist()
        else:
            descartados.append(pos)

    paquete = {
        "clases": modelo["clases"],
        "columnas": modelo["columnas"],
        "nombres": [NOMBRES[c] for c in modelo["columnas"]],
        "mediana": modelo["mediana"], "media": modelo["media"], "escala": modelo["escala"],
        "coef": modelo["coef"], "intercepto": modelo["intercepto"],
        "mostrar_probabilidades": bool(modelo["mostrar_probabilidades"]),
        "personas_entrenamiento": int(modelo["personas_entrenamiento"]),
        "metricas": {
            "aciertos_pct": float(resumen["mejor_aciertos_pct"]),
            "top2_pct": float(resumen["mejor_top2_pct"]),
            "azar_pct": float(resumen["azar_pct"]),
            "base_aciertos_pct": float(resumen["base_aciertos_pct"]),
        },
        "ejemplos": ejemplos,
    }

    with open(args.plantilla, encoding="utf-8") as f:
        plantilla = f.read()
    marcador = "/*__MODELO__*/null"
    assert plantilla.count(marcador) == 1
    texto = json.dumps(paquete, ensure_ascii=False, allow_nan=False).replace("</", "<\\/")
    html = plantilla.replace(marcador, texto)

    os.makedirs(os.path.dirname(args.salida) or ".", exist_ok=True)
    with open(args.salida, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Aplicación generada: {args.salida} ({len(html) / 1024:.0f} KB) | ejemplos: {len(ejemplos)}"
          + (f" | descartados: {descartados}" if descartados else ""))


if __name__ == "__main__":
    main()
