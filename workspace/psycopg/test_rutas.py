import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from rutas.rutas import Rutas

# EPSG 25830 - UTM Zona 30N (España)
RUTA_VALIDA = "LINESTRING(400000 4500000, 400100 4500100)"
RUTA_INTERSECTA = "LINESTRING(400050 4500050, 400200 4500200)"
RUTA_ALEJADA = "LINESTRING(410000 4510000, 410100 4510100)"
GEOM_INVALIDA = "POLYGON((0 0, 1 1, 0 1, 1 0, 0 0))"


class TestRutasInsert(unittest.TestCase):

    def setUp(self):
        self.rutas = Rutas()
        self.ids_creados = []

    def tearDown(self):
        for rid in self.ids_creados:
            self.rutas.delete({"id": rid})
        self.rutas.disconnect()

    def _data_valida(self, geom=RUTA_VALIDA):
        return {
            "nombre": "Ruta Test",
            "dificultad": "media",
            "desnivel": 150.0,
            "abierta": True,
            "longitud": 2500.0,
            "geom": geom,
        }

    def test_insert_ok(self):
        result = self.rutas.insert(self._data_valida())
        self.assertTrue(result["ok"])
        self.assertIsNotNone(result["data"])
        self.ids_creados.append(result["data"][0]["id"])

    def test_insert_campos_faltantes(self):
        result = self.rutas.insert({"nombre": "Sin campos"})
        self.assertFalse(result["ok"])
        self.assertIn("Faltan campos obligatorios", result["message"])

    def test_insert_geom_invalida(self):
        data = self._data_valida(geom=GEOM_INVALIDA)
        result = self.rutas.insert(data)
        self.assertFalse(result["ok"])
        self.assertIn("ST_IsValid", result["message"])

    def test_insert_intersecta_ruta_existente(self):
        r1 = self.rutas.insert(self._data_valida(geom=RUTA_VALIDA))
        self.assertTrue(r1["ok"])
        self.ids_creados.append(r1["data"][0]["id"])

        r2 = self.rutas.insert(self._data_valida(geom=RUTA_INTERSECTA))
        self.assertFalse(r2["ok"])
        self.assertIn("intersecta", r2["message"])

    def test_insert_ruta_alejada_ok(self):
        r1 = self.rutas.insert(self._data_valida(geom=RUTA_VALIDA))
        self.assertTrue(r1["ok"])
        self.ids_creados.append(r1["data"][0]["id"])

        r2 = self.rutas.insert(self._data_valida(geom=RUTA_ALEJADA))
        self.assertTrue(r2["ok"])
        self.ids_creados.append(r2["data"][0]["id"])


class TestRutasUpdate(unittest.TestCase):

    def setUp(self):
        self.rutas = Rutas()
        result = self.rutas.insert({
            "nombre": "Ruta Update",
            "dificultad": "baja",
            "desnivel": 50.0,
            "abierta": True,
            "longitud": 1000.0,
            "geom": RUTA_VALIDA,
        })
        self.ruta_id = result["data"][0]["id"] if result["ok"] else None

    def tearDown(self):
        if self.ruta_id:
            self.rutas.delete({"id": self.ruta_id})
        self.rutas.disconnect()

    def test_update_sin_id(self):
        result = self.rutas.update({"nombre": "Sin ID"})
        self.assertFalse(result["ok"])
        self.assertIn("id", result["message"])

    def test_update_id_inexistente(self):
        result = self.rutas.update({"id": 999999, "nombre": "No existe"})
        self.assertFalse(result["ok"])
        self.assertIn("No existe ruta", result["message"])

    def test_update_sin_campos(self):
        result = self.rutas.update({"id": self.ruta_id})
        self.assertFalse(result["ok"])
        self.assertIn("No se proporcionaron campos", result["message"])

    def test_update_nombre_ok(self):
        result = self.rutas.update({"id": self.ruta_id, "nombre": "Ruta Actualizada"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"][0]["id"], self.ruta_id)

    def test_update_geom_ok(self):
        result = self.rutas.update({"id": self.ruta_id, "geom": RUTA_VALIDA})
        self.assertTrue(result["ok"])

    def test_update_geom_invalida(self):
        result = self.rutas.update({"id": self.ruta_id, "geom": GEOM_INVALIDA})
        self.assertFalse(result["ok"])
        self.assertIn("ST_IsValid", result["message"])

    def test_update_geom_intersecta_otra_ruta(self):
        r2 = self.rutas.insert({
            "nombre": "Segunda Ruta",
            "dificultad": "alta",
            "desnivel": 300.0,
            "abierta": False,
            "longitud": 5000.0,
            "geom": RUTA_ALEJADA,
        })
        self.assertTrue(r2["ok"])
        id2 = r2["data"][0]["id"]

        result = self.rutas.update({"id": id2, "geom": RUTA_INTERSECTA})
        self.assertFalse(result["ok"])
        self.assertIn("intersecta", result["message"])
        self.rutas.delete({"id": id2})

    def test_update_geom_propia_no_intersecta(self):
        result = self.rutas.update({"id": self.ruta_id, "geom": RUTA_VALIDA})
        self.assertTrue(result["ok"])


class TestRutasDelete(unittest.TestCase):

    def setUp(self):
        self.rutas = Rutas()

    def tearDown(self):
        self.rutas.disconnect()

    def test_delete_sin_id(self):
        result = self.rutas.delete({})
        self.assertFalse(result["ok"])
        self.assertIn("id", result["message"])

    def test_delete_id_inexistente(self):
        result = self.rutas.delete({"id": 999999})
        self.assertFalse(result["ok"])
        self.assertIn("No existe ruta", result["message"])

    def test_delete_ok(self):
        r = self.rutas.insert({
            "nombre": "Ruta Para Borrar",
            "dificultad": "baja",
            "desnivel": 10.0,
            "abierta": True,
            "longitud": 500.0,
            "geom": RUTA_VALIDA,
        })
        self.assertTrue(r["ok"])
        rid = r["data"][0]["id"]
        result = self.rutas.delete({"id": rid})
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"][0]["id"], rid)


class TestRutasSelect(unittest.TestCase):

    def setUp(self):
        self.rutas = Rutas()
        r = self.rutas.insert({
            "nombre": "Ruta Select",
            "dificultad": "media",
            "desnivel": 100.0,
            "abierta": True,
            "longitud": 2000.0,
            "geom": RUTA_VALIDA,
        })
        self.ruta_id = r["data"][0]["id"] if r["ok"] else None

    def tearDown(self):
        if self.ruta_id:
            self.rutas.delete({"id": self.ruta_id})
        self.rutas.disconnect()

    def test_select_as_tuples_todos(self):
        result = self.rutas.selectAsTuples({})
        self.assertTrue(result["ok"])
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)

    def test_select_as_tuples_por_id(self):
        result = self.rutas.selectAsTuples({"id": self.ruta_id})
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0][0], self.ruta_id)

    def test_select_as_dicts_todos(self):
        result = self.rutas.selectAsDicts({})
        self.assertTrue(result["ok"])
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)
        self.assertIn("nombre", result["data"][0])

    def test_select_as_dicts_por_id(self):
        result = self.rutas.selectAsDicts({"id": self.ruta_id})
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["id"], self.ruta_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
