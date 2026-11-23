"""Excepciones de negocio del módulo de inventario."""


class ErrorInventario(Exception):
    """Error base del módulo."""


class DatoInvalidoError(ErrorInventario):
    """Un dato de entrada no cumple las reglas del requisito."""


class ProductoDuplicadoError(ErrorInventario):
    """Ya existe un producto con el mismo código."""


class ProductoNoEncontradoError(ErrorInventario):
    """No existe un producto con el código indicado."""


class StockInsuficienteError(ErrorInventario):
    """La salida solicitada dejaría el stock en negativo."""
