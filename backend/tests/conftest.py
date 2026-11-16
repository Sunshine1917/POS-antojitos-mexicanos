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