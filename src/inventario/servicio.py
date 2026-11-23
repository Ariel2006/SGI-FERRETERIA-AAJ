"""Servicio de inventario: reglas de negocio RF-01 a RF-07."""
import unicodedata
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Callable

from .errores import (
    DatoInvalidoError,
    ProductoDuplicadoError,
    ProductoNoEncontradoError,
    StockInsuficienteError,
)
from .modelos import Movimiento, Producto, TipoMovimiento


class ServicioInventario:
    def __init__(self, reloj: Callable[[], datetime] = datetime.now):
        self._productos: dict[str, Producto] = {}
        self._movimientos: list[Movimiento] = []
        self._reloj = reloj

    # RF-01 ---------------------------------------------------------------
    def registrar_producto(self, codigo, nombre, categoria, precio_unitario,
                           stock_minimo=0) -> Producto:
        codigo = (codigo or "").strip().upper()
        nombre = (nombre or "").strip()
        if not codigo:
            raise DatoInvalidoError("El código es obligatorio")
        if not nombre:
            raise DatoInvalidoError("El nombre es obligatorio")
        try:
            precio = Decimal(str(precio_unitario))
        except InvalidOperation as exc:
            raise DatoInvalidoError("Precio unitario no numérico") from exc
        if precio <= 0:
            raise DatoInvalidoError("El precio unitario debe ser mayor que cero")
        if isinstance(stock_minimo, bool) or not isinstance(stock_minimo, int) \
                or stock_minimo < 0:
            raise DatoInvalidoError("El stock mínimo debe ser un entero >= 0")
        if codigo in self._productos:
            raise ProductoDuplicadoError(f"Ya existe el producto {codigo}")
        producto = Producto(codigo, nombre, (categoria or "").strip(),
                            precio, stock_minimo)
        self._productos[codigo] = producto
        return producto

    def obtener(self, codigo) -> Producto:
        clave = (codigo or "").strip().upper()
        if clave not in self._productos:
            raise ProductoNoEncontradoError(f"No existe el producto {clave}")
        return self._productos[clave]

    # RF-02 / RF-03 -------------------------------------------------------
    def registrar_entrada(self, codigo, cantidad, usuario,
                          observacion="") -> Movimiento:
        producto = self.obtener(codigo)
        self._validar_cantidad(cantidad)
        self._validar_usuario(usuario)          # DEF-01: validar antes de mutar
        producto.stock += cantidad
        return self._anotar(producto, TipoMovimiento.ENTRADA, cantidad,
                            usuario, observacion)

    def registrar_salida(self, codigo, cantidad, usuario,
                         observacion="") -> Movimiento:
        producto = self.obtener(codigo)
        self._validar_cantidad(cantidad)
        self._validar_usuario(usuario)
        if cantidad > producto.stock:
            raise StockInsuficienteError(
                f"Stock insuficiente de {producto.codigo}: "
                f"disponible {producto.stock}, solicitado {cantidad}")
        producto.stock -= cantidad
        return self._anotar(producto, TipoMovimiento.SALIDA, cantidad,
                            usuario, observacion)

    # RF-04 ---------------------------------------------------------------
    def productos_bajo_stock(self) -> list[Producto]:
        # DEF-02: el requisito dice "stock <= mínimo"; se reutiliza la regla
        return sorted((p for p in self._productos.values() if p.bajo_stock),
                      key=lambda p: p.codigo)

    # RF-05 ---------------------------------------------------------------
    def buscar(self, texto) -> list[Producto]:
        # DEF-03: comparación sin distinguir mayúsculas ni tildes
        patron = _normalizar(texto)
        return sorted((p for p in self._productos.values()
                       if patron in _normalizar(p.codigo)
                       or patron in _normalizar(p.nombre)),
                      key=lambda p: p.codigo)

    # RF-06 ---------------------------------------------------------------
    def valor_inventario(self) -> Decimal:
        return sum((p.precio_unitario * p.stock
                    for p in self._productos.values()), Decimal("0"))

    # RF-07 ---------------------------------------------------------------
    def kardex(self, codigo) -> list[Movimiento]:
        producto = self.obtener(codigo)
        return [m for m in self._movimientos
                if m.codigo_producto == producto.codigo]

    # Auxiliares ----------------------------------------------------------
    @staticmethod
    def _validar_cantidad(cantidad) -> None:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) \
                or cantidad <= 0:
            raise DatoInvalidoError("La cantidad debe ser un entero mayor que cero")

    @staticmethod
    def _validar_usuario(usuario) -> None:
        if not (usuario or "").strip():
            raise DatoInvalidoError("El usuario responsable es obligatorio")

    def _anotar(self, producto, tipo, cantidad, usuario, observacion):
        mov = Movimiento(producto.codigo, tipo, cantidad, usuario.strip(),
                         self._reloj(), observacion)
        self._movimientos.append(mov)
        return mov


def _normalizar(texto) -> str:
    """Minúsculas y sin tildes: 'Tubería' -> 'tuberia'."""
    descompuesto = unicodedata.normalize("NFKD", (texto or "").strip())
    return "".join(c for c in descompuesto
                   if not unicodedata.combining(c)).casefold()
