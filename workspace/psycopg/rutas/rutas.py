from psycopg.rows import dict_row
from db.connect import connect
from db.p1Settings import EPSG_CODE


class Rutas:
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

    def _check_intersection(self, cur, wkt: str, exclude_id: int | None = None) -> tuple[bool, str]:
        geom_expr = self._build_geom_expr(wkt)
        if exclude_id is not None:
            cur.execute(
                f"""
                SELECT id FROM d.rutas
                WHERE id != %s
                  AND ST_Intersects(geom, {geom_expr});
                """,
                [exclude_id]
            )
        else:
            cur.execute(
                f"""
                SELECT id FROM d.rutas
                WHERE ST_Intersects(geom, {geom_expr});
                """
            )
        rows = cur.fetchall()
        if rows:
            ids = [str(r[0]) for r in rows]
            return True, f"La geometría intersecta con registros existentes en d.rutas (IDs: {', '.join(ids)})."
        return False, ""

    # ------------------------------------------------------------------
    # insert
    # ------------------------------------------------------------------
    def insert(self, data: dict) -> dict:
        required = {"nombre", "dificultad", "desnivel", "abierta", "longitud", "geom"}
        missing = required - data.keys()
        if missing:
            return {"ok": False, "message": f"Faltan campos obligatorios: {missing}", "data": None}

        try:
            with self.conn.cursor() as cur:
                valid, msg = self._validate_geom(cur, data["geom"])
                if not valid:
                    return {"ok": False, "message": msg, "data": None}

                intersects, msg = self._check_intersection(cur, data["geom"])
                if intersects:
                    return {"ok": False, "message": msg, "data": None}

                geom_expr = self._build_geom_expr(data["geom"])
                cur.execute(
                    f"""
                    INSERT INTO d.rutas (nombre, dificultad, desnivel, abierta, longitud, geom)
                    VALUES (%s, %s, %s, %s, %s, {geom_expr})
                    RETURNING id;
                    """,
                    [data["nombre"], data["dificultad"], data["desnivel"],
                     data["abierta"], data["longitud"]]
                )
                new_id = cur.fetchone()[0]
                self.conn.commit()
                return {"ok": True, "message": "Ruta insertada correctamente.", "data": [{"id": new_id}]}
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error al insertar ruta: {e}", "data": None}

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

                    intersects, msg = self._check_intersection(cur, data["geom"], exclude_id=data["id"])
                    if intersects:
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
                sql = f"UPDATE d.rutas SET {', '.join(set_parts)} WHERE id = %s RETURNING id;"
                cur.execute(sql, values)
                row = cur.fetchone()
                if row is None:
                    self.conn.rollback()
                    return {"ok": False, "message": f"No existe ruta con id={data['id']}.", "data": None}
                self.conn.commit()
                return {"ok": True, "message": f"Ruta id={row[0]} actualizada correctamente.", "data": [{"id": row[0]}]}
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error al actualizar ruta: {e}", "data": None}

    # ------------------------------------------------------------------
    # delete
    # ------------------------------------------------------------------
    def delete(self, data: dict) -> dict:
        if "id" not in data:
            return {"ok": False, "message": "El campo 'id' es obligatorio para eliminar.", "data": None}
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM d.rutas WHERE id = %s RETURNING id;", [data["id"]])
                row = cur.fetchone()
                if row is None:
                    self.conn.rollback()
                    return {"ok": False, "message": f"No existe ruta con id={data['id']}.", "data": None}
                self.conn.commit()
                return {"ok": True, "message": f"Ruta id={row[0]} eliminada correctamente.", "data": [{"id": row[0]}]}
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error al eliminar ruta: {e}", "data": None}

    # ------------------------------------------------------------------
    # selectAsTuples
    # ------------------------------------------------------------------
    def selectAsTuples(self, data: dict) -> dict:
        try:
            with self.conn.cursor() as cur:
                if "id" in data:
                    cur.execute(
                        "SELECT id, nombre, dificultad, desnivel, abierta, longitud, ST_AsText(geom) FROM d.rutas WHERE id = %s;",
                        [data["id"]]
                    )
                else:
                    cur.execute(
                        "SELECT id, nombre, dificultad, desnivel, abierta, longitud, ST_AsText(geom) FROM d.rutas;"
                    )
                rows = cur.fetchall()
                return {"ok": True, "message": f"{len(rows)} registro(s) encontrado(s).", "data": rows}
        except Exception as e:
            return {"ok": False, "message": f"Error al consultar rutas (tuples): {e}", "data": None}

    # ------------------------------------------------------------------
    # selectAsDicts
    # ------------------------------------------------------------------
    def selectAsDicts(self, data: dict) -> dict:
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                if "id" in data:
                    cur.execute(
                        "SELECT id, nombre, dificultad, desnivel, abierta, longitud, ST_AsText(geom) AS wkt FROM d.rutas WHERE id = %s;",
                        [data["id"]]
                    )
                else:
                    cur.execute(
                        "SELECT id, nombre, dificultad, desnivel, abierta, longitud, ST_AsText(geom) AS wkt FROM d.rutas;"
                    )
                rows = cur.fetchall()
                return {"ok": True, "message": f"{len(rows)} registro(s) encontrado(s).", "data": rows}
        except Exception as e:
            return {"ok": False, "message": f"Error al consultar rutas (dicts): {e}", "data": None}
