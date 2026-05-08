from psycopg.rows import dict_row
from db.connect import connect
from db.p1Settings import EPSG_CODE


class Fuentes:
    def __init__(self):
        self.conn = connect()

    def disconnect(self):
        self.conn.close()

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------
    def _build_geom_expr(self, wkt: str) -> str:
        return f"ST_SnapToGrid(ST_GeomFromText('{wkt}', {EPSG_CODE}), 0.0001)"

    def _validate_geom(self, cur, wkt: str) -> tuple[bool, str]:
        cur.execute(
            "SELECT ST_IsValid(ST_GeomFromText(%s, %s));",
            [wkt, EPSG_CODE]
        )
        is_valid = cur.fetchone()[0]
        if not is_valid:
            return False, "La geometría proporcionada no es válida (ST_IsValid = false)."
        return True, ""

    def _check_within_zona(self, cur, wkt: str) -> tuple[bool, str]:
        geom_expr = self._build_geom_expr(wkt)
        cur.execute(
            f"""
            SELECT COUNT(*) FROM d.zonas
            WHERE ST_Within({geom_expr}, geom);
            """
        )
        count = cur.fetchone()[0]
        if count == 0:
            return False, "El punto no está dentro de ninguna zona de conservación (d.zonas). Operación rechazada."
        return True, ""

    # ------------------------------------------------------------------
    # insert
    # ------------------------------------------------------------------
    def insert(self, data: dict) -> dict:
        required = {"nombre", "potable", "caudal", "ultima_revision", "activa", "geom"}
        missing = required - data.keys()
        if missing:
            return {"ok": False, "message": f"Faltan campos obligatorios: {missing}", "data": None}

        try:
            with self.conn.cursor() as cur:
                valid, msg = self._validate_geom(cur, data["geom"])
                if not valid:
                    return {"ok": False, "message": msg, "data": None}

                within, msg = self._check_within_zona(cur, data["geom"])
                if not within:
                    return {"ok": False, "message": msg, "data": None}

                geom_expr = self._build_geom_expr(data["geom"])
                cur.execute(
                    f"""
                    INSERT INTO d.fuentes (nombre, potable, caudal, ultima_revision, activa, geom)
                    VALUES (%s, %s, %s, %s, %s, {geom_expr})
                    RETURNING id;
                    """,
                    [data["nombre"], data["potable"], data["caudal"],
                     data["ultima_revision"], data["activa"]]
                )
                new_id = cur.fetchone()[0]
                self.conn.commit()
                return {"ok": True, "message": "Fuente insertada correctamente.", "data": [{"id": new_id}]}
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error al insertar fuente: {e}", "data": None}

    # ------------------------------------------------------------------
    # update
    # ------------------------------------------------------------------
    def update(self, data: dict) -> dict:
        if "id" not in data:
            return {"ok": False, "message": "El campo 'id' es obligatorio para actualizar.", "data": None}

        try:
            with self.conn.cursor() as cur:
                if "geom" in data:
                    valid, msg = self._validate_geom(cur, data["geom"])
                    if not valid:
                        return {"ok": False, "message": msg, "data": None}

                    within, msg = self._check_within_zona(cur, data["geom"])
                    if not within:
                        return {"ok": False, "message": msg, "data": None}

                fields = {k: v for k, v in data.items() if k not in ("id", "geom")}
                set_parts = [f"{col} = %s" for col in fields]
                values = list(fields.values())

                if "geom" in data:
                    geom_expr = self._build_geom_expr(data["geom"])
                    set_parts.append(f"geom = {geom_expr}")

                if not set_parts:
                    return {"ok": False, "message": "No se proporcionaron campos a actualizar.", "data": None}

                values.append(data["id"])
                sql = f"UPDATE d.fuentes SET {', '.join(set_parts)} WHERE id = %s RETURNING id;"
                cur.execute(sql, values)
                row = cur.fetchone()
                if row is None:
                    self.conn.rollback()
                    return {"ok": False, "message": f"No existe fuente con id={data['id']}.", "data": None}
                self.conn.commit()
                return {"ok": True, "message": f"Fuente id={row[0]} actualizada correctamente.", "data": [{"id": row[0]}]}
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error al actualizar fuente: {e}", "data": None}

    # ------------------------------------------------------------------
    # delete
    # ------------------------------------------------------------------
    def delete(self, data: dict) -> dict:
        if "id" not in data:
            return {"ok": False, "message": "El campo 'id' es obligatorio para eliminar.", "data": None}
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM d.fuentes WHERE id = %s RETURNING id;", [data["id"]])
                row = cur.fetchone()
                if row is None:
                    self.conn.rollback()
                    return {"ok": False, "message": f"No existe fuente con id={data['id']}.", "data": None}
                self.conn.commit()
                return {"ok": True, "message": f"Fuente id={row[0]} eliminada correctamente.", "data": [{"id": row[0]}]}
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error al eliminar fuente: {e}", "data": None}

    # ------------------------------------------------------------------
    # selectAsTuples
    # ------------------------------------------------------------------
    def selectAsTuples(self, data: dict) -> dict:
        try:
            with self.conn.cursor() as cur:
                if "id" in data:
                    cur.execute(
                        "SELECT id, nombre, potable, caudal, ultima_revision, activa, ST_AsText(geom) FROM d.fuentes WHERE id = %s;",
                        [data["id"]]
                    )
                else:
                    cur.execute(
                        "SELECT id, nombre, potable, caudal, ultima_revision, activa, ST_AsText(geom) FROM d.fuentes;"
                    )
                rows = cur.fetchall()
                return {"ok": True, "message": f"{len(rows)} registro(s) encontrado(s).", "data": rows}
        except Exception as e:
            return {"ok": False, "message": f"Error al consultar fuentes (tuples): {e}", "data": None}

    # ------------------------------------------------------------------
    # selectAsDicts
    # ------------------------------------------------------------------
    def selectAsDicts(self, data: dict) -> dict:
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                if "id" in data:
                    cur.execute(
                        "SELECT id, nombre, potable, caudal, ultima_revision, activa, ST_AsText(geom) AS wkt FROM d.fuentes WHERE id = %s;",
                        [data["id"]]
                    )
                else:
                    cur.execute(
                        "SELECT id, nombre, potable, caudal, ultima_revision, activa, ST_AsText(geom) AS wkt FROM d.fuentes;"
                    )
                rows = cur.fetchall()
                return {"ok": True, "message": f"{len(rows)} registro(s) encontrado(s).", "data": rows}
        except Exception as e:
            return {"ok": False, "message": f"Error al consultar fuentes (dicts): {e}", "data": None}
