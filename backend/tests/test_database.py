import pytest
import sqlite3
from database import inicializar_db

@pytest.fixture
def db_conexion(tmp_path):
    ruta_temp = tmp_path / "test_antojitos.db"
    inicializar_db(ruta_temp)

    conexion = sqlite3.connect(ruta_temp)
    conexion.execute("PRAGMA foreign_keys = ON;")

    yield conexion

    conexion.close()

def test_inicializar_db_crear_todas_las_tablas(db_conexion):
    cursor = db_conexion.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = ?;", ('table',)
    )
    nombre_tablas = cursor.fetchall()
    tablas_creadas = {fila[0] for fila in nombre_tablas}

    tablas_esperadas = {
        "PLATILLO",
        "MODIFICADOR",
        "ORDEN",
        "ORDEN_DETALLADO",
        "ORDEN_DETALLE_MODIFICADOR",
    }
    assert tablas_creadas == tablas_esperadas

@pytest.mark.parametrize("cantidad_invalida",[0, 2, -1])
def test_modificador_rechaza_cantidad_distinta_de_uno(db_conexion,cantidad_invalida):
    cursor = db_conexion.cursor()
    cursor.execute(
        "INSERT INTO PLATILLO (PlatilloID,Name,PrecioActual,Activo) VALUES (?,?,?,?)",
        (1, 'Taco', 2500, 1))
    cursor.execute(
        "INSERT INTO MODIFICADOR (ModificadorID, Name, PrecioExtra) VALUES (?,?,?);",
        (1, 'Sabor: Queso',500))
    cursor.execute(
        "INSERT INTO ORDEN (OrdenID,FechaHora,NombreCliente,Total,Estado) VALUES(?,?,?,?,?);",
        (1,'2026-11-15 15:00:00', 'Bob', 2500, 'ABIERTA'))
    cursor.execute(
        "INSERT INTO ORDEN_DETALLADO (DetalleID,OrdenID,PlatilloID,Cantidad,PrecioBaseHistorico) VALUES(?,?,?,?,?);",
        (1,1,1,1,2500))

    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        cursor.execute(
            "INSERT INTO ORDEN_DETALLE_MODIFICADOR (DetalleID,ModificadorID,Cantidad,PrecioExtraHistorico) VALUES(?,?,?,?);",
            (1,1,cantidad_invalida,500)
        )

    assert "CHECK constraint failed" in str(excinfo.value)