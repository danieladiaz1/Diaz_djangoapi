"""
Script de pruebas para las clases CRUD de Zonas, Rutas y Fuentes.

Ejecución:
    python manage.py runscript test_parques

Descripción:
    Prueba el ciclo completo INSERT → SELECT → UPDATE → DELETE para cada
    uno de los tres modelos espaciales. También valida el rechazo de
    operaciones que violan las restricciones espaciales de PostGIS.

Geometrías de prueba en EPSG:25830 (ETRS89 / UTM zone 30N):
    - Zona (polígono 1000 x 1000 m centrado en ~Castellón de la Plana)
    - Ruta (línea dentro de la zona)
    - Fuente (punto dentro de la zona)
"""

import pprint

from scripts.crud_zonas import CRUDZonas
from scripts.crud_rutas import CRUDRutas
from scripts.crud_fuentes import CRUDFuentes

pp = pprint.PrettyPrinter(indent=2, width=100)

# ---------------------------------------------------------------------------
# Geometrías de prueba  (EPSG:25830 — coordenadas en metros)
# Zona: cuadrado de 1000 x 1000 m
# ---------------------------------------------------------------------------
ZONA_WKT = (
    "POLYGON(("
    "730000 4395000,"
    "731000 4395000,"
    "731000 4396000,"
    "730000 4396000,"
    "730000 4395000"
    "))"
)

# Polígono que intersecta con el anterior (comparte borde/área) → debe rechazarse
ZONA_WKT_INTERSECTA = (
    "POLYGON(("
    "730500 4395500,"
    "731500 4395500,"
    "731500 4396500,"
    "730500 4396500,"
    "730500 4395500"
    "))"
)

# Ruta: línea dentro de la zona
RUTA_WKT = (
    "LINESTRING("
    "730100 4395100,"
    "730500 4395500,"
    "730900 4395900"
    ")"
)

# Línea que intersecta con la anterior → debe rechazarse
RUTA_WKT_INTERSECTA = (
    "LINESTRING("
    "730200 4395800,"
    "730800 4395200"
    ")"
)

# Punto dentro de la zona
FUENTE_WKT = "POINT(730500 4395500)"

# Punto fuera de cualquier zona → debe rechazarse
FUENTE_WKT_FUERA = "POINT(100000 100000)"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _header(title: str):
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  {title}")
    print(sep)


def _print_result(label: str, result: dict):
    status = "OK" if result.get("ok") else "FAIL"
    print(f"\n  [{status}] {label}")
    print(f"  message : {result.get('message')}")
    if result.get("data"):
        print("  data    :")
        pp.pprint(result["data"])
    else:
        print("  data    : None")


# ---------------------------------------------------------------------------
# Pruebas Zona (polígono)
# ---------------------------------------------------------------------------

def test_zonas():
    _header("PRUEBAS ZONAS (Polígonos)")
    crud = CRUDZonas()

    # --- INSERT válido ---
    data_insert = {
        "nombre": "Zona de Prueba A",
        "descripcion": "Zona creada desde script de test",
        "capacidad": 200,
        "abierto": True,
        "area": 1000000.0,
        "geom": ZONA_WKT,
    }
    res_insert = crud.insert(data_insert)
    _print_result("INSERT zona válida", res_insert)

    zona_id = res_insert["data"][0]["id"] if res_insert["ok"] else None

    # --- INSERT que debe fallar (intersección) ---
    data_intersecta = {**data_insert, "nombre": "Zona Solapada", "geom": ZONA_WKT_INTERSECTA}
    res_intersecta = crud.insert(data_intersecta)
    _print_result("INSERT zona intersectante (debe fallar)", res_intersecta)
    assert not res_intersecta["ok"], "ERROR: debió rechazarse la zona intersectante"

    # --- SELECT AS DICTS ---
    res_sel = crud.selectAsDicts()
    _print_result("SELECT AS DICTS (todas las zonas)", res_sel)

    # --- SELECT AS TUPLES ---
    res_tup = crud.selectAsTuples({'id': zona_id})
    _print_result("SELECT AS TUPLES (por id)", res_tup)

    # --- UPDATE válido ---
    if zona_id:
        res_upd = crud.update({'id': zona_id, 'nombre': 'Zona Actualizada A', 'capacidad': 350})
        _print_result("UPDATE zona válido", res_upd)

    # --- DELETE ---
    if zona_id:
        res_del = crud.delete({'id': zona_id})
        _print_result("DELETE zona", res_del)

    # --- DELETE de registro inexistente ---
    res_del_404 = crud.delete({'id': 999999})
    _print_result("DELETE zona inexistente (debe fallar)", res_del_404)
    assert not res_del_404["ok"], "ERROR: debió indicar que el registro no existe"


# ---------------------------------------------------------------------------
# Pruebas Ruta (línea)
# ---------------------------------------------------------------------------

def test_rutas():
    _header("PRUEBAS RUTAS (Líneas)")
    crud_zonas = CRUDZonas()
    crud_rutas = CRUDRutas()

    # Necesitamos una zona para que los puntos/líneas tengan contexto
    # (las líneas no tienen restricción ST_Within, pero creamos la zona
    #  para que el test de fuentes funcione después)
    res_zona = crud_zonas.insert({
        "nombre": "Zona Auxiliar para Rutas",
        "descripcion": "Temporal",
        "capacidad": 100,
        "abierto": True,
        "area": 1000000.0,
        "geom": ZONA_WKT,
    })
    zona_id_aux = res_zona["data"][0]["id"] if res_zona["ok"] else None

    # --- INSERT válido ---
    data_insert = {
        "nombre": "Ruta del Bosque",
        "dificultad": "media",
        "desnivel": 150,
        "abierta": True,
        "longitud": 5200.0,
        "geom": RUTA_WKT,
    }
    res_insert = crud_rutas.insert(data_insert)
    _print_result("INSERT ruta válida", res_insert)
    ruta_id = res_insert["data"][0]["id"] if res_insert["ok"] else None

    # --- INSERT que debe fallar (intersección) ---
    data_intersecta = {**data_insert, "nombre": "Ruta Solapada", "geom": RUTA_WKT_INTERSECTA}
    res_intersecta = crud_rutas.insert(data_intersecta)
    _print_result("INSERT ruta intersectante (debe fallar)", res_intersecta)
    assert not res_intersecta["ok"], "ERROR: debió rechazarse la ruta intersectante"

    # --- SELECT AS DICTS ---
    res_sel = crud_rutas.selectAsDicts()
    _print_result("SELECT AS DICTS (todas las rutas)", res_sel)

    # --- SELECT AS TUPLES ---
    res_tup = crud_rutas.selectAsTuples({'id': ruta_id})
    _print_result("SELECT AS TUPLES (por id)", res_tup)

    # --- UPDATE válido ---
    if ruta_id:
        res_upd = crud_rutas.update({'id': ruta_id, 'dificultad': 'alta', 'desnivel': 300})
        _print_result("UPDATE ruta válido", res_upd)

    # --- DELETE ---
    if ruta_id:
        res_del = crud_rutas.delete({'id': ruta_id})
        _print_result("DELETE ruta", res_del)

    # --- DELETE de registro inexistente ---
    res_del_404 = crud_rutas.delete({'id': 999999})
    _print_result("DELETE ruta inexistente (debe fallar)", res_del_404)
    assert not res_del_404["ok"], "ERROR: debió indicar que el registro no existe"

    # Limpieza zona auxiliar
    if zona_id_aux:
        crud_zonas.delete({'id': zona_id_aux})


# ---------------------------------------------------------------------------
# Pruebas Fuente (punto)
# ---------------------------------------------------------------------------

def test_fuentes():
    _header("PRUEBAS FUENTES (Puntos)")
    crud_zonas = CRUDZonas()
    crud_fuentes = CRUDFuentes()

    # Creamos la zona de contención
    res_zona = crud_zonas.insert({
        "nombre": "Zona de Conservación Test",
        "descripcion": "Zona para contener fuentes de test",
        "capacidad": 50,
        "abierto": True,
        "area": 1000000.0,
        "geom": ZONA_WKT,
    })
    zona_id = res_zona["data"][0]["id"] if res_zona["ok"] else None
    _print_result("INSERT zona de contencion para fuentes", res_zona)

    # --- INSERT válido (dentro de la zona) ---
    data_insert = {
        "nombre": "Fuente del Pinar",
        "potable": True,
        "caudal": 3.5,
        "ultima_revision": "2025-06-15",
        "activa": True,
        "geom": FUENTE_WKT,
    }
    res_insert = crud_fuentes.insert(data_insert)
    _print_result("INSERT fuente válida (dentro de zona)", res_insert)
    fuente_id = res_insert["data"][0]["id"] if res_insert["ok"] else None

    # --- INSERT que debe fallar (punto fuera de zona) ---
    data_fuera = {**data_insert, "nombre": "Fuente Exterior", "geom": FUENTE_WKT_FUERA}
    res_fuera = crud_fuentes.insert(data_fuera)
    _print_result("INSERT fuente fuera de zona (debe fallar)", res_fuera)
    assert not res_fuera["ok"], "ERROR: debió rechazarse la fuente fuera de la zona"

    # --- SELECT AS DICTS ---
    res_sel = crud_fuentes.selectAsDicts()
    _print_result("SELECT AS DICTS (todas las fuentes)", res_sel)

    # --- SELECT AS TUPLES ---
    res_tup = crud_fuentes.selectAsTuples({'id': fuente_id})
    _print_result("SELECT AS TUPLES (por id)", res_tup)

    # --- UPDATE válido ---
    if fuente_id:
        res_upd = crud_fuentes.update({
            'id': fuente_id,
            'potable': False,
            'caudal': 1.2,
            'ultima_revision': '2026-01-10',
        })
        _print_result("UPDATE fuente válido", res_upd)

    # --- UPDATE con geom fuera de zona (debe fallar) ---
    if fuente_id:
        res_upd_fuera = crud_fuentes.update({'id': fuente_id, 'geom': FUENTE_WKT_FUERA})
        _print_result("UPDATE fuente con geom fuera de zona (debe fallar)", res_upd_fuera)
        assert not res_upd_fuera["ok"], "ERROR: debió rechazarse la actualización fuera de zona"

    # --- DELETE ---
    if fuente_id:
        res_del = crud_fuentes.delete({'id': fuente_id})
        _print_result("DELETE fuente", res_del)

    # --- DELETE de registro inexistente ---
    res_del_404 = crud_fuentes.delete({'id': 999999})
    _print_result("DELETE fuente inexistente (debe fallar)", res_del_404)
    assert not res_del_404["ok"], "ERROR: debió indicar que el registro no existe"

    # Limpieza zona de contencion
    if zona_id:
        crud_zonas.delete({'id': zona_id})


# ---------------------------------------------------------------------------
# Punto de entrada para django-extensions runscript
# ---------------------------------------------------------------------------

def run():
    """
    Función principal invocada por:
        python manage.py runscript test_parques
    """
    print("\n" + "#" * 70)
    print("  INICIO DE PRUEBAS CRUD ESPACIALES — Proyecto Parques")
    print("#" * 70)

    try:
        test_zonas()
    except AssertionError as e:
        print(f"\n  [ASSERTION ERROR] {e}")
    except Exception as e:
        print(f"\n  [ERROR INESPERADO en test_zonas] {e}")

    try:
        test_rutas()
    except AssertionError as e:
        print(f"\n  [ASSERTION ERROR] {e}")
    except Exception as e:
        print(f"\n  [ERROR INESPERADO en test_rutas] {e}")

    try:
        test_fuentes()
    except AssertionError as e:
        print(f"\n  [ASSERTION ERROR] {e}")
    except Exception as e:
        print(f"\n  [ERROR INESPERADO en test_fuentes] {e}")

    print("\n" + "#" * 70)
    print("  FIN DE PRUEBAS")
    print("#" * 70 + "\n")
