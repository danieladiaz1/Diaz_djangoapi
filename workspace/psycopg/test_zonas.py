import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from zonas.zonas import Zonas

# EPSG 25830 - UTM Zona 30N (España)
ZONA_VALIDA = "POLYGON((400000 4500000, 400100 4500000, 400100 4500100, 400000 4500100, 400000 4500000))"
ZONA_INTERSECTA = "POLYGON((400050 4500050, 400150 4500050, 400150 4500150, 400050 4500150, 400050 4500050))"
ZONA_ALEJADA = "POLYGON((410000 4510000, 410100 4510000, 410100 4510100, 410000 4510100, 410000 4510000))"
GEOM_INVALIDA = "POLYGON((0 0, 1 1, 0 1, 1 0, 0 0))"


class TestZonasInsert(unittest.TestCase):

    def setUp(self):
        self.zonas = Zonas()
        self.ids_creados = []

    def tearDown(self):
        for rid in self.ids_creados:
            self.zonas.delete({"id": rid})
        self.zonas.disconnect()

    def _data_valida(self, geom=ZONA_VALIDA):
        return {
            "nombre": "Zona Test",
            "descripcion": "Descripción de prueba",
            "capacidad": 100,
            "abierto": True,
            "area": 10000.0,
            "geom": geom,
        }

    def test_insert_ok(self):
        result = self.zonas.insert(self._data_valida())
        self.assertTrue(result["ok"])
        self.assertIsNotNone(result["data"])
        self.ids_creados.append(result["data"][0]["id"])

    def test_insert_campos_faltantes(self):
        data = {"nombre": "Sin campos"}
        result = self.zonas.insert(data)
        self.assertFalse(result["ok"])
        self.assertIn("Faltan campos obligatorios", result["message"])

    def test_insert_geom_invalida(self):
        data = self._data_valida(geom=GEOM_INVALIDA)
        result = self.zonas.insert(data)
        self.assertFalse(result["ok"])
        self.assertIn("ST_IsValid", result["message"])

    def test_insert_intersecta_zona_existente(self):
        r1 = self.zonas.insert(self._data_valida(geom=ZONA_VALIDA))
        self.assertTrue(r1["ok"])
        self.ids_creados.append(r1["data"][0]["id"])

        r2 = self.zonas.insert(self._data_valida(geom=ZONA_INTERSECTA))
        self.assertFalse(r2["ok"])
        self.assertIn("intersecta", r2["message"])

    def test_insert_zona_alejada_ok(self):
        r1 = self.zonas.insert(self._data_valida(geom=ZONA_VALIDA))
        self.assertTrue(r1["ok"])
        self.ids_creados.append(r1["data"][0]["id"])

        r2 = self.zonas.insert(self._data_valida(geom=ZONA_ALEJADA))
        self.assertTrue(r2["ok"])
        self.ids_creados.append(r2["data"][0]["id"])


class TestZonasUpdate(unittest.TestCase):

    def setUp(self):
        self.zonas = Zonas()
        result = self.zonas.insert({
            "nombre": "Zona Update",
            "descripcion": "Para update",
            "capacidad": 50,
            "abierto": False,
            "area": 5000.0,
            "geom": ZONA_VALIDA,
        })
        self.zona_id = result["data"][0]["id"] if result["ok"] else None

    def tearDown(self):
        if self.zona_id:
            self.zonas.delete({"id": self.zona_id})
        self.zonas.disconnect()

    def test_update_sin_id(self):
        result = self.zonas.update({"nombre": "Sin ID"})
        self.assertFalse(result["ok"])
        self.assertIn("id", result["message"])

    def test_update_id_inexistente(self):
        result = self.zonas.update({"id": 999999, "nombre": "No existe"})
        self.assertFalse(result["ok"])
        self.assertIn("No existe zona", result["message"])

    def test_update_sin_campos(self):
        result = self.zonas.update({"id": self.zona_id})
        self.assertFalse(result["ok"])
        self.assertIn("No se proporcionaron campos", result["message"])

    def test_update_nombre_ok(self):
        result = self.zonas.update({"id": self.zona_id, "nombre": "Zona Actualizada"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"][0]["id"], self.zona_id)

    def test_update_geom_ok(self):
        result = self.zonas.update({"id": self.zona_id, "geom": ZONA_VALIDA})
        self.assertTrue(result["ok"])

    def test_update_geom_invalida(self):
        result = self.zonas.update({"id": self.zona_id, "geom": GEOM_INVALIDA})
        self.assertFalse(result["ok"])
        self.assertIn("ST_IsValid", result["message"])

    def test_update_geom_intersecta(self):
        r2 = self.zonas.insert({
            "nombre": "Segunda Zona",
            "descripcion": "Para interseccion",
            "capacidad": 30,
            "abierto": True,
            "area": 2000.0,
            "geom": ZONA_ALEJADA,
        })
        self.assertTrue(r2["ok"])
        id2 = r2["data"][0]["id"]

        result = self.zonas.update({"id": id2, "geom": ZONA_INTERSECTA})
        self.assertFalse(result["ok"])
        self.assertIn("intersecta", result["message"])
        self.zonas.delete({"id": id2})


class TestZonasDelete(unittest.TestCase):

    def setUp(self):
        self.zonas = Zonas()

    def tearDown(self):
        self.zonas.disconnect()

    def test_delete_sin_id(self):
        result = self.zonas.delete({})
        self.assertFalse(result["ok"])
        self.assertIn("id", result["message"])

    def test_delete_id_inexistente(self):
        result = self.zonas.delete({"id": 999999})
        self.assertFalse(result["ok"])
        self.assertIn("No existe zona", result["message"])

    def test_delete_ok(self):
        r = self.zonas.insert({
            "nombre": "Zona Para Borrar",
            "descripcion": "Temporal",
            "capacidad": 10,
            "abierto": True,
            "area": 1000.0,
            "geom": ZONA_VALIDA,
        })
        self.assertTrue(r["ok"])
        rid = r["data"][0]["id"]
        result = self.zonas.delete({"id": rid})
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"][0]["id"], rid)


class TestZonasSelect(unittest.TestCase):

    def setUp(self):
        self.zonas = Zonas()
        r = self.zonas.insert({
            "nombre": "Zona Select",
            "descripcion": "Para consulta",
            "capacidad": 200,
            "abierto": True,
            "area": 10000.0,
            "geom": ZONA_VALIDA,
        })
        self.zona_id = r["data"][0]["id"] if r["ok"] else None

    def tearDown(self):
        if self.zona_id:
            self.zonas.delete({"id": self.zona_id})
        self.zonas.disconnect()

    def test_select_as_tuples_todos(self):
        result = self.zonas.selectAsTuples({})
        self.assertTrue(result["ok"])
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)

    def test_select_as_tuples_por_id(self):
        result = self.zonas.selectAsTuples({"id": self.zona_id})
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0][0], self.zona_id)

    def test_select_as_dicts_todos(self):
        result = self.zonas.selectAsDicts({})
        self.assertTrue(result["ok"])
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)
        self.assertIn("nombre", result["data"][0])

    def test_select_as_dicts_por_id(self):
        result = self.zonas.selectAsDicts({"id": self.zona_id})
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["id"], self.zona_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
