import pytest
import sqlite3
from db import dict_factory, get_db
from database import inicializar_db
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def db_e2e(tmp_path):
    ruta_temp = tmp_path / "test_antojitos.db"
    inicializar_db(ruta_temp)

    conexion = sqlite3.connect(ruta_temp, check_same_thread=False)
    conexion.row_factory = dict_factory
    conexion.execute("PRAGMA foreign_keys = ON;")

    platillos = [
        (1,"Chalupa Prueba", 800, 1),
        (2,"Torta de chalupa Prueba", 2500, 1),
        (3,"Taco dorado Prueba", 1500, 1),
    ]

    modificador = [
        (1,"Sabor: Queso Prueba", 0),
        (2,"Extra: Pollo", 800),
        (3,"Sin cebolla", 0),
    ]
    conexion.executemany(
        "INSERT INTO PLATILLO (PlatilloID,Name,PrecioActual, Activo) VALUES (?,?,?,?);", (platillos)
    )
    conexion.executemany(
        "INSERT INTO MODIFICADOR (ModificadorID,Name,PrecioExtra) VALUES (?,?,?);", (modificador)
    )

    conexion.commit()

    yield conexion

    conexion.close()


@pytest.fixture
def cliente_e2e(db_e2e):
    def override_get_db():
        cursor = db_e2e.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        yield client
    finally:
        client.close()
        app.dependency_overrides.pop(get_db,None)


def test_crear_y_leer_ticket(cliente_e2e):
    orden = {
        "NombreCliente": "Omar",
        "Platillos": [
            {
                "Platillo": 2,
                "Cantidad": 2,
                "Modificador": [2, 3],
                "Notas": None,
                "Contiene": [
                    {
                        "Platillo": 3,
                        "Cantidad": 3,
                        "Modificador": [1],
                        "Notas": None,
                        "Contiene": [],
                    }
                ],
            }
        ],
    }
    respuesta_post = cliente_e2e.post("/ordenes", json=orden)
    datos_post = respuesta_post.json()
    assert respuesta_post.status_code == 201
    assert datos_post["Total"] == "156.00"

    id_orden = datos_post["OrdenID"]
    respuesta_get = cliente_e2e.get(f"/ordenes/{id_orden}/ticket")
    datos_ticket = respuesta_get.json()
    assert respuesta_get.status_code == 200
    assert datos_ticket["OrdenID"] == id_orden
    assert datos_ticket["Total"] == datos_post["Total"]
    assert datos_ticket["Platillos"][0]["PrecioTotalPlatillo"] == "156.00"
