import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
db_name = os.getenv("DB_NAME", "antojitos_mexicanos.db")

try:
    #This connect with the databse and create a cursor
    sqliteConection = sqlite3.connect(db_name)
    cursor = sqliteConection.cursor()
    print('DataBase Init')

    #Drop the table if it already exist
    cursor.executescript("""
        DROP TABLE IF EXISTS PLATILLO;
        DROP TABLE IF EXISTS MODIFICADOR;
        DROP TABLE IF EXISTS ORDEN;
        DROP TABLE IF EXISTS ORDEN_DETALLADO;
        DROP TABLE IF EXISTS ORDEN_DETALLE_MODIFICADOR;
        """)

    #SQL query to create a table
    table_creation_query = """
        CREATE TABLE PLATILLO(
            PlatilloID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            PrecioActual REAL NOT NULL,
            Activo INTEGER NOT NULL
        );

        CREATE TABLE MODIFICADOR(
            ModificadorID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            PrecioExtra REAL NOT NULL
            );

        CREATE TABLE ORDEN(
            OrdenID INTEGER PRIMARY KEY,
            FechaHora TEXT,
            NombreCliente TEXT NOT NULL,
            Total REAL NOT NULL,
            Estado TEXT NOT NULL
        );

        CREATE TABLE ORDEN_DETALLADO(
            DetalleID INTEGER PRIMARY KEY,
            OrdenID INTEGER NOT NULL REFERENCES ORDEN(OrdenID),
            PlatilloID INTEGER NOT NULL REFERENCES PLATILLO(PlatilloID),
            DetallePadreID INTEGER REFERENCES ORDEN_DETALLADO(DetalleID),
            Cantidad INTEGER NOT NULL,
            PrecioBaseHistorico REAL NOT NULL,
            Notas TEXT
        );

        CREATE TABLE ORDEN_DETALLE_MODIFICADOR(
            DetalleModificadorID INTEGER PRIMARY KEY,
            DetalleID  NOT NULL REFERENCES ORDEN_DETALLADO(DetalleID),
            ModificadorID INTEGER NOT NULL REFERENCES MODIFICADOR(ModificadorID),
            Cantidad INTEGER NOT NULL,
            PrecioExtraHistorico REAL NOT NULL
        );
    """

    cursor.executescript(table_creation_query)

    print('Table is created succesfully')


    #Remember close the cursor after use
    cursor.close()

except sqlite3.Error as error:
    print("Error ocurred -",error)

finally:
    #Ensure the database is close after use
    if sqliteConection:
        sqliteConection.close()
        print('SQLite conection was close')


