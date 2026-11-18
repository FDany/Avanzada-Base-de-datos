"""Módulo de conexión y consultas sobre la vista vw_productos."""

import psycopg2
from configuracion.config import DB_CONFIG


def obtener_conexion():
    """Abre y devuelve una conexión directa a PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def buscar_productos(filtro_producto="", filtro_categoria=""):
    """Consulta vw_productos aplicando filtros dinámicos por parámetro."""
    conn = obtener_conexion()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT productid, productname, categoryname, suppliername, unitprice, unitsinstock
                FROM vw_productos
                WHERE productname ILIKE %s
                  AND categoryname ILIKE %s
                ORDER BY productid ASC;
            """
            parametros = (
                f"%{filtro_producto.strip()}%",
                f"%{filtro_categoria.strip()}%",
            )
            cur.execute(sql, parametros)
            return cur.fetchall()
    finally:
        conn.close()
