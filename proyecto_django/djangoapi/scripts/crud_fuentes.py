from django.db import connection, transaction
from django.forms.models import model_to_dict
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

from app_proyecto_parques.models import Fuente

SRID = 25830
PRECISION = getattr(settings, 'ST_SNAP_PRECISION', 0.0001)


def _instance_to_dict(instance):
    d = model_to_dict(instance)
    d['id'] = instance.pk
    if d.get('geom') is not None and hasattr(d['geom'], 'wkt'):
        d['geom'] = d['geom'].wkt
    return d


class CRUDFuentes:
    """
    Clase CRUD para el modelo Fuente (d.fuentes).
    Geometría: POINT, SRID 25830.

    Restricciones espaciales aplicadas antes de insert/update:
      - ST_SnapToGrid: redondea coordenadas a PRECISION decimales.
      - ST_IsValid: rechaza geometrías inválidas.
      - ST_Within: el punto debe estar dentro de alguna zona (d.zonas).
                   Si cae fuera de todos los polígonos, se rechaza.
    """

    def _apply_spatial_constraints(self, geom_wkt: str):
        """
        Aplica ST_SnapToGrid, ST_IsValid y ST_Within sobre el punto entrante.
        Retorna (GEOSGeometry, None) si pasa todas las validaciones,
        o (None, mensaje_error) si alguna falla.
        """
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO d, public")
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

            # 3. El punto debe estar dentro de alguna zona (ST_Within)
            cursor.execute(
                """
                SELECT EXISTS(
                    SELECT 1 FROM zonas
                    WHERE ST_Within(ST_GeomFromText(%s, %s), geom)
                )
                """,
                [snapped_wkt, SRID]
            )
            within = cursor.fetchone()[0]
            if not within:
                return None, (
                    "El punto no está dentro de ninguna zona de conservación "
                    "(ST_Within = False). Operación rechazada."
                )

        return GEOSGeometry(snapped_wkt, srid=SRID), None

    # ------------------------------------------------------------------
    # INSERT
    # ------------------------------------------------------------------
    def insert(self, data: dict) -> dict:
        """
        Inserta una nueva Fuente.
        data: {
            'nombre': str, 'potable': bool, 'caudal': float,
            'ultima_revision': str (YYYY-MM-DD), 'activa': bool,
            'geom': str (WKT POINT 25830)
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
                instance = Fuente.objects.create(
                    nombre=data.get('nombre'),
                    potable=data.get('potable'),
                    caudal=data.get('caudal'),
                    ultima_revision=data.get('ultima_revision'),
                    activa=data.get('activa'),
                    geom=geom,
                )
            return {
                "ok": True,
                "message": f"Fuente insertada correctamente con id={instance.pk}",
                "data": [_instance_to_dict(instance)],
            }
        except Exception as e:
            return {"ok": False, "message": f"Error en insert: {e}", "data": None}

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------
    def delete(self, data: dict) -> dict:
        """
        Elimina una Fuente por su id.
        data: {'id': int}
        """
        try:
            pk = data.get('id')
            if pk is None:
                return {"ok": False, "message": "El campo 'id' es obligatorio", "data": None}
            instance = Fuente.objects.get(pk=pk)
            d = _instance_to_dict(instance)
            instance.delete()
            return {"ok": True, "message": f"Fuente con id={pk} eliminada correctamente", "data": [d]}
        except Fuente.DoesNotExist:
            return {"ok": False, "message": f"Fuente con id={data.get('id')} no encontrada", "data": None}
        except Exception as e:
            return {"ok": False, "message": f"Error en delete: {e}", "data": None}

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update(self, data: dict) -> dict:
        """
        Actualiza una Fuente existente.
        data: {'id': int, [campos opcionales a modificar], 'geom': str WKT (opcional)}
        """
        try:
            pk = data.get('id')
            if pk is None:
                return {"ok": False, "message": "El campo 'id' es obligatorio", "data": None}
            instance = Fuente.objects.get(pk=pk)

            if 'geom' in data and data['geom']:
                geom, error = self._apply_spatial_constraints(data['geom'])
                if error:
                    return {"ok": False, "message": error, "data": None}
                instance.geom = geom

            for field in ('nombre', 'potable', 'caudal', 'ultima_revision', 'activa'):
                if field in data:
                    setattr(instance, field, data[field])

            with transaction.atomic():
                instance.save()

            return {
                "ok": True,
                "message": f"Fuente con id={pk} actualizada correctamente",
                "data": [_instance_to_dict(instance)],
            }
        except Fuente.DoesNotExist:
            return {"ok": False, "message": f"Fuente con id={data.get('id')} no encontrada", "data": None}
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
            qs = Fuente.objects.all()
            if data and data.get('id') is not None:
                qs = qs.filter(pk=data['id'])
            result = [_instance_to_dict(i) for i in qs]
            return {"ok": True, "message": f"{len(result)} fuente(s) encontrada(s)", "data": result}
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
            qs = Fuente.objects.all()
            if data and data.get('id') is not None:
                qs = qs.filter(pk=data['id'])
            tuples = list(qs.values_list(
                'id', 'nombre', 'potable', 'caudal', 'ultima_revision', 'activa', 'geom'
            ))
            return {"ok": True, "message": f"{len(tuples)} fuente(s) encontrada(s)", "data": tuples}
        except Exception as e:
            return {"ok": False, "message": f"Error en selectAsTuples: {e}", "data": None}
