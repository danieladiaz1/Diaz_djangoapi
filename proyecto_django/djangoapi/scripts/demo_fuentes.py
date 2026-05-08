"""
Demo de presentación: Restricción espacial ST_Within en Fuentes.

Ejecución:
    python manage.py runscript demo_fuentes

Muestra:
    1. Crear una zona de conservación (polígono).
    2. INSERT fuente VÁLIDA  → punto dentro de la zona  (debe aceptarse).
    3. INSERT fuente INVÁLIDA → punto fuera de la zona  (debe rechazarse).
    4. Limpieza de los registros creados.
"""

from scripts.crud_zonas import CRUDZonas
from scripts.crud_fuentes import CRUDFuentes

# ---------------------------------------------------------------------------
# Geometrías  (EPSG:25830 — metros, zona UTM 30N sobre Castellón)
# ---------------------------------------------------------------------------

# Cuadrado 1000 x 1000 m que actúa como zona de conservación
ZONA_WKT = (
    "POLYGON(("
    "730000 4395000,"
    "731000 4395000,"
    "731000 4396000,"
    "730000 4396000,"
    "730000 4395000"
    "))"
)

# Punto en el centro exacto de la zona  → ST_Within = True
FUENTE_DENTRO_WKT = "POINT(730500 4395500)"

# Punto muy alejado de cualquier zona  → ST_Within = False
FUENTE_FUERA_WKT = "POINT(100000 100000)"

# ---------------------------------------------------------------------------
# Helpers de presentación
# ---------------------------------------------------------------------------

def _sep(char="─", n=60):
    print(char * n)

def _titulo(texto):
    _sep("═")
    print(f"  {texto}")
    _sep("═")

def _paso(numero, texto):
    _sep()
    print(f"  PASO {numero}: {texto}")
    _sep()

def _resultado(ok, mensaje, datos=None):
    icono = "✔ ACEPTADO" if ok else "✘ RECHAZADO"
    print(f"  {icono}")
    print(f"  Mensaje : {mensaje}")
    if datos:
        for k, v in datos[0].items():
            print(f"    {k}: {v}")


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def run():
    _titulo("DEMO — Restricción ST_Within en Fuentes (Django + PostGIS)")

    crud_zonas   = CRUDZonas()
    crud_fuentes = CRUDFuentes()

    # ------------------------------------------------------------------
    # PASO 1 — Crear la zona de conservación
    # ------------------------------------------------------------------
    _paso(1, "Crear zona de conservación (polígono 1 km²)")

    res_zona = crud_zonas.insert({
        "nombre"     : "Zona Demo Presentación",
        "descripcion": "Zona creada para la demo de restricción espacial",
        "capacidad"  : 100,
        "abierto"    : True,
        "area"       : 1_000_000.0,
        "geom"       : ZONA_WKT,
    })

    _resultado(res_zona["ok"], res_zona["message"], res_zona.get("data"))
    zona_id = res_zona["data"][0]["id"] if res_zona["ok"] else None

    if not res_zona["ok"]:
        print("\n  No se pudo crear la zona. Abortando demo.")
        return

    # ------------------------------------------------------------------
    # PASO 2 — INSERT fuente VÁLIDA (dentro de la zona)
    # ------------------------------------------------------------------
    _paso(2, f"INSERT fuente VÁLIDA  →  geom = {FUENTE_DENTRO_WKT}")
    print(f"  La zona abarca X:[730000-731000]  Y:[4395000-4396000]")
    print(f"  El punto  X=730500  Y=4395500  está en el centro exacto.\n")

    res_ok = crud_fuentes.insert({
        "nombre"         : "Fuente del Pinar",
        "potable"        : True,
        "caudal"         : 3.5,
        "ultima_revision": "2026-03-01",
        "activa"         : True,
        "geom"           : FUENTE_DENTRO_WKT,
    })

    _resultado(res_ok["ok"], res_ok["message"], res_ok.get("data"))
    fuente_id = res_ok["data"][0]["id"] if res_ok["ok"] else None

    # ------------------------------------------------------------------
    # PASO 3 — INSERT fuente INVÁLIDA (fuera de la zona)
    # ------------------------------------------------------------------
    _paso(3, f"INSERT fuente INVÁLIDA →  geom = {FUENTE_FUERA_WKT}")
    print(f"  El punto  X=100000  Y=100000  está fuera de toda zona.\n")

    res_fail = crud_fuentes.insert({
        "nombre"         : "Fuente Exterior",
        "potable"        : False,
        "caudal"         : 0.5,
        "ultima_revision": "2026-03-01",
        "activa"         : True,
        "geom"           : FUENTE_FUERA_WKT,
    })

    _resultado(res_fail["ok"], res_fail["message"])

    # ------------------------------------------------------------------
    # PASO 4 — Limpieza
    # ------------------------------------------------------------------
    _paso(4, "Limpieza — eliminar registros creados en la demo")

    if fuente_id:
        r = crud_fuentes.delete({"id": fuente_id})
        print(f"  Fuente id={fuente_id}: {r['message']}")

    if zona_id:
        r = crud_zonas.delete({"id": zona_id})
        print(f"  Zona   id={zona_id}: {r['message']}")

    _sep("═")
    print("  FIN DE LA DEMO")
    _sep("═")
    print()
