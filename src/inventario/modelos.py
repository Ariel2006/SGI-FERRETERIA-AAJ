"""Entidades del dominio de inventario (SGI-Ferretería, incremento 1)."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TipoMovimiento(str, Enum):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"


@dataclass
class Producto:
    codigo: str
    nombre: str
    categoria: str
    precio_unitario: Decimal
    stock_minimo: int
    stock: int = 0

    @property
    def bajo_stock(self) -> bool:
        return self.stock <= self.stock_minimo


@dataclass(frozen=True)
class Movimiento:
    codigo_producto: str
    tipo: TipoMovimiento
    cantidad: int
    usuario: str
    fecha: datetime
    observacion: str = ""
