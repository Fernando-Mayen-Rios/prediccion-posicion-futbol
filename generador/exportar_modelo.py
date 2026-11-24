"""Exporta el modelo entrenado (modelo_posicion.joblib) a un JSON que no depende de la versión de scikit-learn.

Por qué existe: un archivo .joblib solo se puede abrir con la MISMA versión de scikit-learn con la que se
guardó (Colab guardó este con la 1.6.1). Para que la aplicación web funcione siempre, se guardan solo los
números del modelo: medianas (para rellenar "No sé"), media y escala (estandarización) y los pesos de la
regresión logística. La aplicación aplica exactamente esas mismas operaciones.

Seguridad: los .joblib son "pickles", que pueden ejecutar código al abrirse. Aquí se lee con un lector
restringido: solo permite arreglos de numpy y estructuras simples, y rechaza cualquier otra cosa.

Uso:
    python exportar_modelo.py --modelo resultados_modelado/modelo_posicion.joblib \
                              --metadata resultados_modelado/modelo_metadata.json \
                              --salida resultados_modelado/modelo_app.json
"""
import argparse
import json
import pickle

import numpy as np
from joblib.numpy_pickle import NumpyUnpickler
from joblib.numpy_pickle_utils import _validate_fileobject_and_memmap

PERMITIDOS = {
    "numpy": {"ndarray", "dtype", "float64", "int64", "bool_", "str_", "object_", "float32", "int32"},
    "numpy._core.multiarray": {"_reconstruct", "scalar"},
    "numpy.core.multiarray": {"_reconstruct", "scalar"},
    "numpy.dtypes": None,  # clases de tipos de numpy (Float64DType, etc.)
    "collections": {"OrderedDict"},
    "builtins": {"list", "dict", "tuple", "set", "frozenset", "object", "slice", "int", "float", "str", "bool", "complex"},
    "copyreg": {"_reconstructor"},
    "joblib.numpy_pickle": {"NumpyArrayWrapper"},
}


class Objeto:
    """Sustituye a las clases de scikit-learn: solo guarda sus atributos, sin ejecutar nada."""

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        self._items, self._map = [], {}

    def __setstate__(self, estado):
        if isinstance(estado, tuple) and len(estado) == 2:
            estado = {**(estado[0] or {}), **(estado[1] or {})}
        if isinstance(estado, dict):
            self.__dict__.update(estado)
        else:
            self.estado = estado

    def append(self, valor):
        self._items.append(valor)

    def extend(self, valores):
        self._items.extend(valores)

    def __setitem__(self, clave, valor):
        self._map[clave] = valor


class LectorSeguro(NumpyUnpickler):
    def find_class(self, modulo, nombre):
        if modulo.startswith("sklearn"):
            return type(nombre, (Objeto,), {})
        if modulo in PERMITIDOS:
            permitidos = PERMITIDOS[modulo]
            if permitidos is None or nombre in permitidos:
                return super().find_class(modulo, nombre)
        raise pickle.UnpicklingError(f"Clase no permitida: {modulo}.{nombre}")


def leer(ruta):
    with open(ruta, "rb") as f:
        with _validate_fileobject_and_memmap(f, ruta, None) as (fobj, _):
            lector = LectorSeguro(ruta, fobj, True, mmap_mode=None)
            return lector.load()


def paso(modelo, nombre):
    for n, p in modelo.steps:
        if n == nombre:
            return p
    raise KeyError(nombre)


def buscar(obj, atributo):
    """Busca un atributo en el objeto y, si hace falta, dentro de sus pasos y transformadores."""
    if hasattr(obj, atributo):
        return getattr(obj, atributo)
    for valor in obj.__dict__.values():
        candidatos = valor if isinstance(valor, (list, tuple)) else [valor]
        for c in candidatos:
            sub = c[1] if isinstance(c, tuple) and len(c) > 1 else c
            if isinstance(sub, Objeto):
                try:
                    return buscar(sub, atributo)
                except KeyError:
                    pass
    raise KeyError(atributo)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modelo", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--salida", required=True)
    args = parser.parse_args()

    pipeline = leer(args.modelo)
    with open(args.metadata, encoding="utf-8") as f:
        meta = json.load(f)

    medianas = np.asarray(buscar(pipeline, "statistics_"), dtype=float)
    media = np.asarray(buscar(pipeline, "mean_"), dtype=float)
    escala = np.asarray(buscar(pipeline, "scale_"), dtype=float)
    coef = np.asarray(buscar(pipeline, "coef_"), dtype=float)
    intercepto = np.asarray(buscar(pipeline, "intercept_"), dtype=float)
    clases = [str(c) for c in np.asarray(buscar(pipeline, "classes_"))]

    columnas = meta["columnas_entrada"]
    assert meta["conjunto_variables"] == "Solo habilidades" and not meta["columnas_categoricas"], \
        "Este exportador solo admite el modelo que usa únicamente las 12 habilidades."
    assert len(columnas) == len(medianas) == len(media) == len(escala) == coef.shape[1]
    assert coef.shape[0] == len(clases) == intercepto.shape[0] == len(meta["clases"])
    assert clases == meta["clases"], "El orden de las clases no coincide con el de los metadatos."
    assert meta["modelo"] == "Regresión logística"

    salida = {
        "modelo": meta["modelo"],
        "scikit_learn_entrenamiento": meta["versiones"]["scikit_learn"],
        "clases": clases,
        "columnas": columnas,
        "mediana": medianas.tolist(),
        "media": media.tolist(),
        "escala": escala.tolist(),
        "coef": coef.tolist(),
        "intercepto": intercepto.tolist(),
        "mostrar_probabilidades": bool(meta["mostrar_probabilidades"]),
        "ece": meta["ece"],
        "metricas_validacion": meta["metricas_validacion"],
        "personas_entrenamiento": meta["personas_entrenamiento"],
    }
    with open(args.salida, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)
    print(f"Modelo exportado: {args.salida} | {len(clases)} clases x {len(columnas)} variables")


if __name__ == "__main__":
    main()
