import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from fuentes.fuentes import Fuentes
from rutas.rutas import Rutas
from zonas.zonas import Zonas


def print_result(label: str, result: dict):
    print(f"\n  [{label}]")
    print(f"    ok      : {result['ok']}")
    print(f"    message : {result['message']}")
    if result["data"] is not None:
        print(f"    data    : {result['data']}")
    else:
        print(f"    data    : None")


def main():

    # =========================================================
    # TABLA 1: Zonas (POLYGON) — debe insertarse PRIMERO
    # porque Fuentes (POINT) depende de ST_Within(zona)
    # =========================================================
    print("\n" + "=" * 60)
    print("TABLA: d.zonas  (POLYGON, EPSG:25830)")
    print("=" * 60)

    zonas = Zonas()

    # --- INSERT válido ---
    res = zonas.insert({
        "nombre": "Zona Recreativa Sur",
        "descripcion": "Area de uso publico con merenderos",
        "capacidad": 200,
        "abierto": True,
        "area": 1000000.00,
        "geom": "POLYGON((400000 4500000, 402000 4500000, 402000 4502000, 400000 4502000, 400000 4500000))"
    })
    print_result("INSERT zona válida", res)
    id_zona = res["data"][0]["id"] if res["ok"] else None

    # --- INSERT inválido: intersecta con la zona recién creada ---
    res_intersect = zonas.insert({
        "nombre": "Zona Solapada",
        "descripcion": "Debería ser rechazada por intersección",
        "capacidad": 50,
        "abierto": False,
        "area": 500000.00,
        "geom": "POLYGON((401000 4501000, 403000 4501000, 403000 4503000, 401000 4503000, 401000 4501000))"
    })
    print_result("INSERT zona inválida (intersecta)", res_intersect)

    # --- UPDATE atributo no espacial ---
    if id_zona:
        res = zonas.update({"id": id_zona, "abierto": False, "capacidad": 150})
        print_result("UPDATE zona (atributos)", res)

    # --- SELECT AS TUPLES ---
    res = zonas.selectAsTuples({})
    print_result("SELECT zonas AS tuples", res)

    # --- SELECT AS DICTS (filtrado por id) ---
    if id_zona:
        res = zonas.selectAsDicts({"id": id_zona})
        print_result("SELECT zona AS dicts (por id)", res)

    # =========================================================
    # TABLA 2: Rutas (LINESTRING)
    # =========================================================
    print("\n" + "=" * 60)
    print("TABLA: d.rutas  (LINESTRING, EPSG:25830)")
    print("=" * 60)

    rutas = Rutas()

    # --- INSERT válido ---
    res = rutas.insert({
        "nombre": "Ruta del Bosque",
        "dificultad": "Media",
        "desnivel": 320,
        "abierta": True,
        "longitud": 5.80,
        "geom": "LINESTRING(410000 4510000, 411000 4511000, 412000 4512000)"
    })
    print_result("INSERT ruta válida", res)
    id_ruta = res["data"][0]["id"] if res["ok"] else None

    # --- INSERT inválido: intersecta con la ruta anterior ---
    res_intersect = rutas.insert({
        "nombre": "Ruta Solapada",
        "dificultad": "Baja",
        "desnivel": 100,
        "abierta": True,
        "longitud": 2.00,
        "geom": "LINESTRING(410500 4510500, 411500 4511500)"
    })
    print_result("INSERT ruta inválida (intersecta)", res_intersect)

    # --- UPDATE con campo espacial ---
    if id_ruta:
        res = rutas.update({"id": id_ruta, "desnivel": 450, "abierta": False})
        print_result("UPDATE ruta (atributos)", res)

    # --- SELECT AS TUPLES ---
    res = rutas.selectAsTuples({})
    print_result("SELECT rutas AS tuples", res)

    # --- SELECT AS DICTS (filtrado por id) ---
    if id_ruta:
        res = rutas.selectAsDicts({"id": id_ruta})
        print_result("SELECT ruta AS dicts (por id)", res)

    # =========================================================
    # TABLA 3: Fuentes (POINT) — el punto DEBE estar dentro
    # de algún polígono de d.zonas (ST_Within)
    # =========================================================
    print("\n" + "=" * 60)
    print("TABLA: d.fuentes  (POINT, EPSG:25830)")
    print("=" * 60)

    fuentes = Fuentes()

    # --- INSERT inválido: punto fuera de toda zona ---
    res_out = fuentes.insert({
        "nombre": "Fuente Exterior",
        "potable": True,
        "caudal": 1.5,
        "ultima_revision": "2024-06-01",
        "activa": True,
        "geom": "POINT(420000 4520000)"
    })
    print_result("INSERT fuente fuera de zona (rechazada)", res_out)

    # --- INSERT válido: punto dentro de la zona creada ---
    if id_zona:
        res = fuentes.insert({
            "nombre": "Fuente Norte",
            "potable": True,
            "caudal": 3.50,
            "ultima_revision": "2024-01-15",
            "activa": True,
            "geom": "POINT(401000 4501000)"
        })
        print_result("INSERT fuente dentro de zona", res)
        id_fuente = res["data"][0]["id"] if res["ok"] else None
    else:
        id_fuente = None

    # --- UPDATE atributo no espacial ---
    if id_fuente:
        res = fuentes.update({"id": id_fuente, "activa": False, "caudal": 2.75})
        print_result("UPDATE fuente (atributos)", res)

    # --- SELECT AS TUPLES ---
    res = fuentes.selectAsTuples({})
    print_result("SELECT fuentes AS tuples", res)

    # --- SELECT AS DICTS ---
    if id_fuente:
        res = fuentes.selectAsDicts({"id": id_fuente})
        print_result("SELECT fuente AS dicts (por id)", res)

    # =========================================================
    # LIMPIEZA: DELETE en orden inverso de dependencia
    # =========================================================
    print("\n" + "=" * 60)
    print("LIMPIEZA — DELETE")
    print("=" * 60)

    if id_fuente:
        print_result("DELETE fuente", fuentes.delete({"id": id_fuente}))
    if id_ruta:
        print_result("DELETE ruta", rutas.delete({"id": id_ruta}))
    if id_zona:
        print_result("DELETE zona", zonas.delete({"id": id_zona}))

    # --- DELETE con id inexistente ---
    print_result("DELETE zona inexistente", zonas.delete({"id": 99999}))

    fuentes.disconnect()
    rutas.disconnect()
    zonas.disconnect()


if __name__ == "__main__":
    main()
