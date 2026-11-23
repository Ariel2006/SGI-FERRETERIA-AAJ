"""Pruebas de integración de la API REST (IS.5.4)."""
import pytest
from fastapi.testclient import TestClient

from inventario.api import crear_app


@pytest.fixture
def cliente():
    c = TestClient(crear_app())
    c.post("/productos", json={"codigo": "LLV-008", "nombre": "Llave inglesa 8\"",
                               "categoria": "Herramientas",
                               "precio_unitario": "12.40", "stock_minimo": 3})
    return c


def test_pi01_flujo_entrada_salida_y_alerta(cliente):
    r = cliente.post("/productos/LLV-008/entradas",
                     json={"cantidad": 5, "usuario": "bodega1"})
    assert r.status_code == 201 and r.json()["stock"] == 5
    r = cliente.post("/productos/llv-008/salidas",
                     json={"cantidad": 2, "usuario": "caja1"})
    assert r.json()["stock"] == 3 and r.json()["bajo_stock"] is True
    assert [p["codigo"] for p in cliente.get("/alertas/stock-bajo").json()] == ["LLV-008"]


def test_pi02_salida_sin_stock_responde_409(cliente):
    r = cliente.post("/productos/LLV-008/salidas",
                     json={"cantidad": 1, "usuario": "caja1"})
    assert r.status_code == 409


def test_pi03_producto_duplicado_responde_409(cliente):
    r = cliente.post("/productos", json={"codigo": "llv-008", "nombre": "Otra",
                                         "precio_unitario": "1"})
    assert r.status_code == 409


def test_pi04_producto_inexistente_responde_404(cliente):
    r = cliente.post("/productos/NADA/entradas",
                     json={"cantidad": 1, "usuario": "bodega1"})
    assert r.status_code == 404


def test_pi05_datos_invalidos_responden_422(cliente):
    assert cliente.post("/productos", json={"codigo": "X", "nombre": "X",
                                            "precio_unitario": "0"}).status_code == 422
    assert cliente.post("/productos/LLV-008/entradas",
                        json={"cantidad": 0, "usuario": "b"}).status_code == 422


def test_pi06_busqueda_y_reporte_csv(cliente):
    assert cliente.get("/productos", params={"q": "INGLESA"}).json()[0]["codigo"] == "LLV-008"
    r = cliente.get("/reportes/stock-bajo.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "LLV-008;" in r.text
