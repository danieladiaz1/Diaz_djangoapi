from django.db import connection, transaction
from django.forms.models import model_to_dict
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

from app_proyecto_parques.models import Ruta

SRID = 25830
PRECISION = getattr(settings, 'ST_SNAP_PRECISION', 0.0001)


def _instance_to_dict(instance):
    d = model_to_dict(instance)
    d['id'] = instance.pk
    if d.get('geom') is not None and hasattr(d['geom'], 'wkt'):
        d['geom'] = d['geom'].wkt
    return d


class CRUDRutas:
    """
    Clase CRUD para el modelo Ruta (d.rutas).
    Geometría: LINESTRING, SRID 25830.

    Restricciones espaciales aplicadas antes de insert/update:
      - ST_SnapToGrid: redondea coordenadas a PRECISION decimales.
      - ST_IsValid: rechaza geometrías inválidas.
      - ST_Intersects: rechaza si la línea intersecta con rutas existentes.
    """

    def _apply_spatial_constraints(self, geom_wkt: str, exclude_id=None):
        """
        Aplica ST_SnapToGrid, ST_IsValid y ST_Intersects sobre la línea entrante.
        Retorna (GEOSGeometry, None) si pasa todas las validaciones,
        o (None, mensaje_error) si alguna falla.
        """
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO public")
            # 1. Redondeo con ST_SnapToGrid
            cursor.execute(
                "SELECT ST_AsText(ST_SnapToGrid(ST_GeomFromText(%s, %s), %s))",
                [geom_wkt, SRID, PRECISION]
            )
            snapped_wkt = cursor.fetchone()[0]

            # 2. Validación con ST_IsValid
            cursor.execute(
                "SELECT ST_IsValid(ST_GeomFromText(%s, %s))",
                [snapped_wkt, SRID]
            )
            is_valid = cursor.fetchone()[0]
            if not is_valid:
                return None, "Geometría inválida tras ST_SnapToGrid (ST_IsValid = False)"

            # 3. Rechazo si intersecta con líneas existentes
            if exclude_id is not None:
                cursor.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM rutas
                        WHERE id != %s
                          AND ST_Intersects(geom, ST_GeomFromText(%s, %s))
                    )
                    """,
                    [exclude_id, snapped_wkt, SRID]
                )
            else:
                cursor.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM rutas
                        WHERE ST_Intersects(geom, ST_GeomFromText(%s, %s))
                    )
                    """,
                    [snapped_wkt, SRID]
                )
            intersects = cursor.fetchone()[0]
            if intersects:
                return None, "La geometría intersecta con una ruta ya existente (ST_Intersects = True)"

        return GEOSGeometry(snapped_wkt, srid=SRID), None

    # ------------------------------------------------------------------
    # INSERT
    # ------------------------------------------------------------------
    def insert(self, data: dict) -> dict:
        """
        Inserta una nueva Ruta.
        data: {
            'nombre': str, 'dificultad': str, 'desnivel': int,
            'abierta': bool, 'longitud': float, 'geom': str (WKT LINESTRING 25830)
        }
        """
        try:
            geom_wkt = data.get('geom')
            if not geom_wkt:
                return {"ok": False, "message": "El campo 'geom' (WKT) es obligatorio", "data": None}

            geom, error = self._apply_spatial_constraints(geom_wkt)
            if error:
                return {"ok": False, "message": error, "data": None}

with transaction.atomic():
                instance = Ruta.objects.create(
                    nombre=data.get('nombre'),
                    dificultad=data.get('dificultad'),
                    desnivel=data.get('desnivel'),
                   abierta=data.get('abierta'),
                    longitud=geom.length,
                    geom=geom,
                )
            return {
                "ok": True,
                "message": f"Ruta insertada correctamente con id={instance.pk}",
                "data": [_instance_to_dict(instance)],
            }
        except Exception as e:
            return {"ok": False, "message": f"Error en insert: {e}", "data": None}

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------
    def delete(self, data: dict) -> dict:
        """
        Elimina una Ruta por su id.
        data: {'id': int}
        """
        try:
            pk = data.get('id')
            if pk is None:
                return {"ok": False, "message": "El campo 'id' es obligatorio", "data": None}
            instance = Ruta.objects.get(pk=pk)
            d = _instance_to_dict(instance)
            instance.delete()
            return {"ok": True, "message": f"Ruta con id={pk} eliminada correctamente", "data": [d]}
        except Ruta.DoesNotExist:
            return {"ok": False, "message": f"Ruta con id={data.get('id')} no encontrada", "data": None}
        except Exception as e:
            return {"ok": False, "message": f"Error en delete: {e}", "data": None}

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update(self, data: dict) -> dict:
        """
        Actualiza una Ruta existente.
        data: {'id': int, [campos opcionales a modificar], 'geom': str WKT (opcional)}
        """
        try:
            pk = data.get('id')
            if pk is None:
                return {"ok": False, "message": "El campo 'id' es obligatorio", "data": None}
            instance = Ruta.objects.get(pk=pk)

            if 'geom' in data and data['geom']:
                geom, error = self._apply_spatial_constraints(data['geom'], exclude_id=pk)
                if error:
                    return {"ok": False, "message": error, "data": None}
                instance.geom = geom
                instance.longitud = geom.length

            for field in ('nombre', 'dificultad', 'desnivel', 'abierta'):
                if field in data:
                    setattr(instance, field, data[field])

            with transaction.atomic():
                instance.save()

            return {
                "ok": True,
                "message": f"Ruta con id={pk} actualizada correctamente",
                "data": [_instance_to_dict(instance)],
            }
        except Ruta.DoesNotExist:
            return {"ok": False, "message": f"Ruta con id={data.get('id')} no encontrada", "data": None}
        except Exception as e:
            return {"ok": False, "message": f"Error en update: {e}", "data": None}

    # ------------------------------------------------------------------
    # SELECT AS DICTS
    # ------------------------------------------------------------------
    def selectAsDicts(self, data: dict = None) -> dict:
        """
        Retorna registros como lista de diccionarios (model_to_dict).
        data: {'id': int} (opcional, filtra por id)
        """
        try:
            qs = Ruta.objects.all()
            if data and data.get('id') is not None:
                qs = qs.filter(pk=data['id'])
            result = [_instance_to_dict(i) for i in qs]
            return {"ok": True, "message": f"{len(result)} ruta(s) encontrada(s)", "data": result}
        except Exception as e:
            return {"ok": False, "message": f"Error en selectAsDicts: {e}", "data": None}

    # ------------------------------------------------------------------
    # SELECT AS TUPLES
    # ------------------------------------------------------------------
    def selectAsTuples(self, data: dict = None) -> dict:
        """
        Retorna registros como lista de tuplas usando values_list().
        data: {'id': int} (opcional, filtra por id)
        """
        try:
            qs = Ruta.objects.all()
            if data and data.get('id') is not None:
                qs = qs.filter(pk=data['id'])
            tuples = list(qs.values_list('id', 'nombre', 'dificultad', 'desnivel', 'abierta', 'longitud', 'geom'))
            return {"ok": True, "message": f"{len(tuples)} ruta(s) encontrada(s)", "data": tuples}
        except Exception as e:
            return {"ok": False, "message": f"Error en selectAsTuples: {e}", "data": None}
