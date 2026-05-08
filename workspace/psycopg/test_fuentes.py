import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from fuentes.fuentes import Fuentes
from zonas.zonas import Zonas

# EPSG 25830 - UTM Zona 30N (España)
ZONA_WKT = "POLYGON((400000 4500000, 400100 4500000, 400100 4500100, 400000 4500100, 400000 4500000))"
PUNTO_DENTRO = "POINT(400050 4500050)"
PUNTO_FUERA = "POINT(500000 4600000)"
GEOM_INVALIDA = "POLYGON((0 0, 1 1, 0 1, 1 0, 0 0))"


class TestFuentesInsert(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.zonas = Zonas()
        r = cls.zonas.insert({
            "nombre": "Zona Fuentes Test",
            "descripcion": "Zona para pruebas de fuentes",
            "capacidad": 500,
            "abierto": True,
            "area": 10000.0,
            "geom": ZONA_WKT,
        })
        cls.zona_id = r["data"][0]["id"] if r["ok"] else None

    @classmethod
    def tearDownClass(cls):
        if cls.zona_id:
            cls.zonas.delete({"id": cls.zona_id})
        cls.zonas.disconnect()

    def setUp(self):
        self.fuentes = Fuentes()
        self.ids_creados = []

    def tearDown(self):
        for fid in self.ids_creados:
            self.fuentes.delete({"id": fid})
        self.fuentes.disconnect()

    def _data_valida(self, geom=PUNTO_DENTRO):
        return {
            "nombre": "Fuente Test",
            "potable": True,
            "caudal": 5.0,
            "ultima_revision": "2025-01-15",
            "activa": True,
            "geom": geom,
        }

    def test_insert_ok(self):
        result = self.fuentes.insert(self._data_valida())
        self.assertTrue(result["ok"])
        self.assertIsNotNone(result["data"])
        self.ids_creados.append(result["data"][0]["id"])

    def test_insert_campos_faltantes(self):
        result = self.fuentes.insert({"nombre": "Sin campos"})
        self.assertFalse(result["ok"])
        self.assertIn("Faltan campos obligatorios", result["message"])

    def test_insert_geom_invalida(self):
        data = self._data_valida(geom=GEOM_INVALIDA)
        result = self.fuentes.insert(data)
        self.assertFalse(result["ok"])
        self.assertIn("ST_IsValid", result["message"])

    def test_insert_punto_fuera_de_zona(self):
        data = self._data_valida(geom=PUNTO_FUERA)
        result = self.fuentes.insert(data)
        self.assertFalse(result["ok"])
        self.assertIn("zona de conservación", result["message"])

    def test_insert_punto_dentro_de_zona(self):
        result = self.fuentes.insert(self._data_valida(geom=PUNTO_DENTRO))
        self.assertTrue(result["ok"])
        self.ids_creados.append(result["data"][0]["id"])


class TestFuentesUpdate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.zonas = Zonas()
        r = cls.zonas.insert({
            "nombre": "Zona Fuentes Update",
            "descripcion": "Zona para pruebas update de fuentes",
            "capacidad": 500,
            "abierto": True,
            "area": 10000.0,
            "geom": ZONA_WKT,
        })
        cls.zona_id = r["data"][0]["id"] if r["ok"] else None

    @classmethod
    def tearDownClass(cls):
        if cls.zona_id:
            cls.zonas.delete({"id": cls.zona_id})
        cls.zonas.disconnect()

    def setUp(self):
        self.fuentes = Fuentes()
        r = self.fuentes.insert({
            "nombre": "Fuente Update",
            "potable": False,
            "caudal": 2.0,
            "ultima_revision": "2024-06-01",
            "activa": True,
            "geom": PUNTO_DENTRO,
        })
        self.fuente_id = r["data"][0]["id"] if r["ok"] else None

    def tearDown(self):
        if self.fuente_id:
            self.fuentes.delete({"id": self.fuente_id})
        self.fuentes.disconnect()

    def test_update_sin_id(self):
        result = self.fuentes.update({"nombre": "Sin ID"})
        self.assertFalse(result["ok"])
        self.assertIn("id", result["message"])

    def test_update_id_inexistente(self):
        result = self.fuentes.update({"id": 999999, "nombre": "No existe"})
        self.assertFalse(result["ok"])
        self.assertIn("No existe fuente", result["message"])

    def test_update_sin_campos(self):
        result = self.fuentes.update({"id": self.fuente_id})
        self.assertFalse(result["ok"])
        self.assertIn("No se proporcionaron campos", result["message"])

    def test_update_nombre_ok(self):
        result = self.fuentes.update({"id": self.fuente_id, "nombre": "Fuente Actualizada"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"][0]["id"], self.fuente_id)

    def test_update_geom_ok(self):
        result = self.fuentes.update({"id": self.fuente_id, "geom": PUNTO_DENTRO})
        self.assertTrue(result["ok"])

    def test_update_geom_invalida(self):
        result = self.fuentes.update({"id": self.fuente_id, "geom": GEOM_INVALIDA})
        self.assertFalse(result["ok"])
        self.assertIn("ST_IsValid", result["message"])

    def test_update_geom_fuera_de_zona(self):
        result = self.fuentes.update({"id": self.fuente_id, "geom": PUNTO_FUERA})
        self.assertFalse(result["ok"])
        self.assertIn("zona de conservación", result["message"])


class TestFuentesDelete(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.zonas = Zonas()
        r = cls.zonas.insert({
            "nombre": "Zona Fuentes Delete",
            "descripcion": "Zona para pruebas delete de fuentes",
            "capacidad": 500,
            "abierto": True,
            "area": 10000.0,
            "geom": ZONA_WKT,
        })
        cls.zona_id = r["data"][0]["id"] if r["ok"] else None

    @classmethod
    def tearDownClass(cls):
        if cls.zona_id:
            cls.zonas.delete({"id": cls.zona_id})
        cls.zonas.disconnect()

    def setUp(self):
        self.fuentes = Fuentes()

    def tearDown(self):
        self.fuentes.disconnect()

    def test_delete_sin_id(self):
        result = self.fuentes.delete({})
        self.assertFalse(result["ok"])
        self.assertIn("id", result["message"])

    def test_delete_id_inexistente(self):
        result = self.fuentes.delete({"id": 999999})
        self.assertFalse(result["ok"])
        self.assertIn("No existe fuente", result["message"])

    def test_delete_ok(self):
        r = self.fuentes.insert({
            "nombre": "Fuente Para Borrar",
            "potable": True,
            "caudal": 1.0,
            "ultima_revision": "2025-03-01",
            "activa": True,
            "geom": PUNTO_DENTRO,
        })
        self.assertTrue(r["ok"])
        fid = r["data"][0]["id"]
        result = self.fuentes.delete({"id": fid})
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"][0]["id"], fid)


class TestFuentesSelect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.zonas = Zonas()
        r = cls.zonas.insert({
            "nombre": "Zona Fuentes Select",
            "descripcion": "Zona para pruebas select de fuentes",
            "capacidad": 500,
            "abierto": True,
            "area": 10000.0,
            "geom": ZONA_WKT,
        })
        cls.zona_id = r["data"][0]["id"] if r["ok"] else None

    @classmethod
    def tearDownClass(cls):
        if cls.zona_id:
            cls.zonas.delete({"id": cls.zona_id})
        cls.zonas.disconnect()

    def setUp(self):
        self.fuentes = Fuentes()
        r = self.fuentes.insert({
            "nombre": "Fuente Select",
            "potable": True,
            "caudal": 3.5,
            "ultima_revision": "2025-02-10",
            "activa": True,
            "geom": PUNTO_DENTRO,
        })
        self.fuente_id = r["data"][0]["id"] if r["ok"] else None

    def tearDown(self):
        if self.fuente_id:
            self.fuentes.delete({"id": self.fuente_id})
        self.fuentes.disconnect()

    def test_select_as_tuples_todos(self):
        result = self.fuentes.selectAsTuples({})
        self.assertTrue(result["ok"])
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)

    def test_select_as_tuples_por_id(self):
        result = self.fuentes.selectAsTuples({"id": self.fuente_id})
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0][0], self.fuente_id)

    def test_select_as_dicts_todos(self):
        result = self.fuentes.selectAsDicts({})
        self.assertTrue(result["ok"])
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)
        self.assertIn("nombre", result["data"][0])

    def test_select_as_dicts_por_id(self):
        result = self.fuentes.selectAsDicts({"id": self.fuente_id})
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["id"], self.fuente_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
