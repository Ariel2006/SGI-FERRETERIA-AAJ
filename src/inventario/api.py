"""API REST del incremento 1 (FastAPI). Ejecutar: uvicorn inventario.api:app"""
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from .errores import (
    DatoInvalidoError,
    ProductoDuplicadoError,
    ProductoNoEncontradoError,
    StockInsuficienteError,
)
from .servicio import ServicioInventario


class ProductoIn(BaseModel):
    codigo: str
    nombre: str
    categoria: str = ""
    precio_unitario: Decimal
    stock_minimo: int = 0


class MovimientoIn(BaseModel):
    cantidad: int = Field(gt=0)
    usuario: str
    observacion: str = ""


_ESTADOS = {
    DatoInvalidoError: 422,
    ProductoDuplicadoError: 409,
    ProductoNoEncontradoError: 404,
    StockInsuficienteError: 409,
}


def _a_http(exc: Exception) -> HTTPException:
    return HTTPException(status_code=_ESTADOS.get(type(exc), 400), detail=str(exc))


def _dto(p):
    return {"codigo": p.codigo, "nombre": p.nombre, "categoria": p.categoria,
            "precio_unitario": str(p.precio_unitario), "stock": p.stock,
            "stock_minimo": p.stock_minimo, "bajo_stock": p.bajo_stock}


def crear_app(servicio: ServicioInventario | None = None) -> FastAPI:
    srv = servicio or ServicioInventario()
    app = FastAPI(title="SGI-Ferretería", version="0.1.0")

    @app.post("/productos", status_code=201)
    def registrar_producto(datos: ProductoIn):
        try:
            return _dto(srv.registrar_producto(**datos.model_dump()))
        except Exception as exc:  # noqa: BLE001 - se traduce a HTTP
            raise _a_http(exc) from exc

    @app.get("/productos")
    def buscar(q: str = ""):
        return [_dto(p) for p in srv.buscar(q)]

    @app.post("/productos/{codigo}/entradas", status_code=201)
    def entrada(codigo: str, mov: MovimientoIn):
        try:
            srv.registrar_entrada(codigo, mov.cantidad, mov.usuario, mov.observacion)
            return _dto(srv.obtener(codigo))
        except Exception as exc:  # noqa: BLE001
            raise _a_http(exc) from exc

    @app.post("/productos/{codigo}/salidas", status_code=201)
    def salida(codigo: str, mov: MovimientoIn):
        try:
            srv.registrar_salida(codigo, mov.cantidad, mov.usuario, mov.observacion)
            return _dto(srv.obtener(codigo))
        except Exception as exc:  # noqa: BLE001
            raise _a_http(exc) from exc

    @app.get("/alertas/stock-bajo")
    def alertas():
        return [_dto(p) for p in srv.productos_bajo_stock()]

    @app.get("/reportes/stock-bajo.csv")
    def reporte_csv():
        return Response(content=srv.exportar_bajo_stock_csv(),
                        media_type="text/csv; charset=utf-8",
                        headers={"Content-Disposition":
                                 'attachment; filename="stock_bajo.csv"'})

    return app


app = crear_app()
