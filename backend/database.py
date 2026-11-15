import sqlite3
from pathlib import Path
from config import DB_PATH

def inicializar_db(ruta_db: Path = DB_PATH) -> None:
    conexion = sqlite3.connect(ruta_db)
    try:
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.executescript("""
                DROP TABLE IF EXISTS ORDEN_DETALLE_MODIFICADOR;
                DROP TABLE IF EXISTS ORDEN_DETALLADO;
                DROP TABLE IF EXISTS ORDEN;
                DROP TABLE IF EXISTS MODIFICADOR;
                DROP TABLE IF EXISTS PLATILLO;

                CREATE TABLE PLATILLO(
                    PlatilloID INTEGER PRIMARY KEY,
                    Name TEXT NOT NULL,
                    PrecioActual INTEGER NOT NULL,
                    Activo INTEGER NOT NULL
                );
        
                CREATE TABLE MODIFICADOR(
                    ModificadorID INTEGER PRIMARY KEY,
                    Name TEXT NOT NULL,
                    PrecioExtra INTEGER NOT NULL
                    );
        
                CREATE TABLE ORDEN(
                    OrdenID INTEGER PRIMARY KEY,
                    FechaHora DATETIME NOT NULL,
                    NombreCliente TEXT NOT NULL,
                    Total INTEGER NOT NULL,
                    Estado TEXT NOT NULL
                );
        
                CREATE TABLE ORDEN_DETALLADO(
                    DetalleID INTEGER PRIMARY KEY,
                    OrdenID INTEGER NOT NULL REFERENCES ORDEN(OrdenID),
                    PlatilloID INTEGER NOT NULL REFERENCES PLATILLO(PlatilloID),
                    DetallePadreID INTEGER REFERENCES ORDEN_DETALLADO(DetalleID),
                    Cantidad INTEGER NOT NULL,
                    PrecioBaseHistorico INTEGER NOT NULL,
                    Notas TEXT
                );
        
                CREATE TABLE ORDEN_DETALLE_MODIFICADOR(
                    DetalleModificadorID INTEGER PRIMARY KEY,
                    DetalleID  INTEGER NOT NULL REFERENCES ORDEN_DETALLADO(DetalleID),
                    ModificadorID INTEGER NOT NULL REFERENCES MODIFICADOR(ModificadorID),
                    Cantidad INTEGER NOT NULL CHECK (Cantidad = 1),
                    PrecioExtraHistorico INTEGER NOT NULL
                );
                """)
        print('Table is created succesfully')
    except sqlite3.Error as error:
        print("Ocurrio un error:", error)
        raise 

    finally:
        conexion.close()

if __name__ == "__main__":
    inicializar_db()


