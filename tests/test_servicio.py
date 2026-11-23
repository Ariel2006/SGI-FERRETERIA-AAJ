"""Pruebas unitarias del ServicioInventario (IS.4.4).

Cada prueba lleva el identificador del caso de prueba (PU-xx) y el
requisito que verifica, para mantener el Registro de trazabilidad.
"""
from datetime import datetime
from decimal import Decimal

import pytest

from inventario import (
    DatoInvalidoError,
    ProductoDuplicadoError,
    ProductoNoEncontradoError,
    ServicioInventario,
    StockInsuficienteError,
    TipoMovimiento,
)

FECHA = datetime(2026, 11, 20, 10, 30)


@pytest.fixture
def inv():
    s = ServicioInventario(reloj=lambda: FECHA)
    s.registrar_producto("MRT-001", "Martillo de uña 16 oz", "Herramientas",
                         "8.50", stock_minimo=5)
    s.registrar_producto("TUB-050", "Tubería PVC 1/2 pulgada", "Plomería",
                         "3.20", stock_minimo=20)
    return s


# RF-01 Registrar producto ---------------------------------------------
def test_pu01_registra_producto_valido(inv):
    p = inv.registrar_producto(" clv-010 ", "Clavo 2 pulgadas (lb)", "Fijación",
                               "1.10", stock_minimo=10)
    assert p.codigo == "CLV-010"
    assert p.stock == 0
    assert p.precio_unitario == Decimal("1.10")


def test_pu02_rechaza_codigo_duplicado(inv):
    with pytest.raises(ProductoDuplicadoError):
        inv.registrar_producto("mrt-001", "Otro martillo", "Herramientas", "9")


@pytest.mark.parametrize("codigo,nombre,precio,minimo", [
    ("", "Sin código", "1.00", 0),
    ("X-1", "   ", "1.00", 0),
    ("X-2", "Precio cero", "0", 0),
    ("X-3", "Precio negativo", "-2.5", 0),
    ("X-4", "Precio texto", "abc", 0),
    ("X-5", "Mínimo negativo", "1.00", -1),
    ("X-6", "Mínimo decimal", "1.00", 2.5),
])
def test_pu03_rechaza_datos_invalidos(inv, codigo, nombre, precio, minimo):
    with pytest.raises(DatoInvalidoError):
        inv.registrar_producto(codigo, nombre, "General", precio, minimo)


# RF-02 Registrar entrada ----------------------------------------------
def test_pu04_entrada_incrementa_stock_y_registra_movimiento(inv):
    mov = inv.registrar_entrada("MRT-001", 12, "bodega1", "Factura 0045")
    assert inv.obtener("MRT-001").stock == 12
    assert mov.tipo is TipoMovimiento.ENTRADA
    assert mov.fecha == FECHA
    assert mov.usuario == "bodega1"


@pytest.mark.parametrize("cantidad", [0, -3, 1.5, True, "4"])
def test_pu05_entrada_rechaza_cantidad_invalida(inv, cantidad):
    with pytest.raises(DatoInvalidoError):
        inv.registrar_entrada("MRT-001", cantidad, "bodega1")
    assert inv.obtener("MRT-001").stock == 0


def test_pu06_entrada_sin_usuario_no_altera_stock(inv):
    with pytest.raises(DatoInvalidoError):
        inv.registrar_entrada("MRT-001", 5, "  ")
    assert inv.obtener("MRT-001").stock == 0
    assert inv.kardex("MRT-001") == []


def test_pu07_producto_inexistente(inv):
    with pytest.raises(ProductoNoEncontradoError):
        inv.registrar_entrada("NO-EXISTE", 1, "bodega1")


# RF-03 Registrar salida -----------------------------------------------
def test_pu08_salida_descuenta_stock(inv):
    inv.registrar_entrada("TUB-050", 30, "bodega1")
    inv.registrar_salida("TUB-050", 12, "caja1", "Venta 1021")
    assert inv.obtener("TUB-050").stock == 18


def test_pu09_salida_no_permite_stock_negativo(inv):
    inv.registrar_entrada("TUB-050", 4, "bodega1")
    with pytest.raises(StockInsuficienteError):
        inv.registrar_salida("TUB-050", 5, "caja1")
    assert inv.obtener("TUB-050").stock == 4


def test_pu10_salida_exacta_deja_stock_en_cero(inv):
    inv.registrar_entrada("TUB-050", 4, "bodega1")
    inv.registrar_salida("TUB-050", 4, "caja1")
    assert inv.obtener("TUB-050").stock == 0


# RF-04 Alertas de stock bajo ------------------------------------------
def test_pu11_alerta_incluye_stock_igual_al_minimo(inv):
    inv.registrar_entrada("MRT-001", 5, "bodega1")      # 5 == mínimo 5
    inv.registrar_entrada("TUB-050", 50, "bodega1")     # 50 > mínimo 20
    codigos = [p.codigo for p in inv.productos_bajo_stock()]
    assert codigos == ["MRT-001"]


def test_pu12_alerta_vacia_cuando_todo_sobre_minimo(inv):
    inv.registrar_entrada("MRT-001", 6, "bodega1")
    inv.registrar_entrada("TUB-050", 21, "bodega1")
    assert inv.productos_bajo_stock() == []


# RF-05 Buscar productos -----------------------------------------------
@pytest.mark.parametrize("texto,esperado", [
    ("martillo", ["MRT-001"]),
    ("TUBERIA", ["TUB-050"]),          # sin tilde y en mayúsculas
    ("tub-0", ["TUB-050"]),            # código parcial
    ("pulgada", ["TUB-050"]),
    ("", ["MRT-001", "TUB-050"]),      # texto vacío lista todo
    ("serrucho", []),
])
def test_pu13_busqueda_insensible_a_mayusculas_y_tildes(inv, texto, esperado):
    assert [p.codigo for p in inv.buscar(texto)] == esperado


# RF-06 Valor del inventario -------------------------------------------
def test_pu14_valor_inventario_usa_decimal_exacto(inv):
    inv.registrar_entrada("MRT-001", 3, "bodega1")    # 3 x 8.50 = 25.50
    inv.registrar_entrada("TUB-050", 10, "bodega1")   # 10 x 3.20 = 32.00
    assert inv.valor_inventario() == Decimal("57.50")


def test_pu15_valor_inventario_vacio_es_cero():
    assert ServicioInventario().valor_inventario() == Decimal("0")


# RF-07 Kardex ---------------------------------------------------------
def test_pu16_kardex_en_orden_cronologico(inv):
    inv.registrar_entrada("MRT-001", 10, "bodega1")
    inv.registrar_salida("MRT-001", 2, "caja1")
    inv.registrar_entrada("TUB-050", 5, "bodega1")
    tipos = [(m.tipo, m.cantidad) for m in inv.kardex("mrt-001")]
    assert tipos == [(TipoMovimiento.ENTRADA, 10), (TipoMovimiento.SALIDA, 2)]
