import db
import pytest
import sqlite3


@pytest.fixture
def detalle_orden_base(db_conexion):
    cursor = db_conexion.cursor()
    cursor.execute(
        "INSERT INTO PLATILLO (PlatilloID,Name,PrecioActual,Activo) VALUES (?,?,?,?)",
        (1, "Taco", 2500, 1),
    )
    cursor.execute(
        "INSERT INTO MODIFICADOR (ModificadorID, Name, PrecioExtra) VALUES (?,?,?);",
        (1, "Sabor: Queso", 500),
    )
    cursor.execute(
        "INSERT INTO ORDEN (OrdenID,FechaHora,NombreCliente,Total,Estado) VALUES(?,?,?,?,?);",
        (1, "2026-11-15 15:00:00", "Bob", 2500, "ABIERTA"),
    )
    cursor.execute(
        "INSERT INTO ORDEN_DETALLADO (DetalleID,OrdenID,PlatilloID,Cantidad,PrecioBaseHistorico) VALUES(?,?,?,?,?);",
        (1, 1, 1, 1, 2500),
    )
    return {
        "conexion": db_conexion,
        "detalle_id": 1,
        "modificador_id": 1,
    }


def test_inicializar_db_crear_todas_las_tablas(db_conexion):
    cursor = db_conexion.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type = ?;", ("table",))
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


@pytest.mark.parametrize("cantidad_invalida", [0, 2, -1])
def test_modificador_rechaza_cantidad_distinta_de_uno(
    detalle_orden_base, cantidad_invalida
):
    cursor = detalle_orden_base["conexion"].cursor()

    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        cursor.execute(
            "INSERT INTO ORDEN_DETALLE_MODIFICADOR (DetalleID,ModificadorID,Cantidad,PrecioExtraHistorico) VALUES(?,?,?,?);",
            (
                detalle_orden_base["detalle_id"],
                detalle_orden_base["modificador_id"],
                cantidad_invalida,
                500,
            ),
        )

    assert "CHECK constraint failed" in str(excinfo.value)


def test_modificador_acepta_cantidad_uno(detalle_orden_base):
    cursor = detalle_orden_base["conexion"].cursor()
    cursor.execute(
        "INSERT INTO ORDEN_DETALLE_MODIFICADOR (DetalleID,ModificadorID,Cantidad,PrecioExtraHistorico) VALUES(?,?,?,?);",
        (
            detalle_orden_base["detalle_id"],
            detalle_orden_base["modificador_id"],
            1,
            500,
        ),
    )
    cursor.execute(
        "SELECT Cantidad FROM ORDEN_DETALLE_MODIFICADOR WHERE DetalleID = ?;", (detalle_orden_base["detalle_id"],)
    )
    assert cursor.fetchone() == (1,)


def test_get_db_activa_foreign_keys(tmp_path, monkeypatch):
    ruta_temp = tmp_path / "test_get_db.db"
    monkeypatch.setattr(db, "DB_PATH", ruta_temp)

    assert not ruta_temp.exists()

    generador = db.get_db()
    conexion = next(generador)

    try:
        assert ruta_temp.exists()
        resultado = conexion.execute("PRAGMA foreign_keys;").fetchone()
        assert resultado == {
            "foreign_keys": 1,
        }
    finally:
        generador.close()
