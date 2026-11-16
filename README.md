# 🌮 Antojitos Mexicanos - Sistema POS

Sistema de Punto de Venta (POS) desarrollado a medida para optimizar la gestión de pedidos, menús y pagos en un negocio familiar de comida tradicional mexicana. Este proyecto forma parte de una iniciativa de desarrollo de software con enfoque en arquitectura limpia, rendimiento y separación de responsabilidades.

##  Características principales

* **Arquitectura Modular:** Rutas organizadas por dominios de negocio (`/menu`, `/ordenes`, `/pago`) utilizando **FastAPI**.
* **Base de Datos Relacional Blindada:** **SQLite** con activación estricta de llaves foráneas (`PRAGMA foreign_keys`), control de transacciones y `dict_factory` para serialización eficiente.
* **Seguridad y Configuración:** Manejo seguro de variables de entorno mediante `python-dotenv` y protección de datos sensibles en archivos ocultos.
* **Validación de Datos:** Uso de esquemas robustos con **Pydantic** para asegurar la integridad de los datos entrantes en los endpoints.
* **Modelo de Árbol Recursivo (Platillo Base + Modificadores):** Estructura recursiva de *Platillo Base + Modificadores* para gestionar combinaciones complejas sin duplicar productos en el catálogo.
* **Integridad Financiera (Snapshots):** Cálculos monetarios en enteros (centavos) y almacenamiento de precios históricos por detalle para garantizar que los tickets cerrados sean inmutables.
* **Pruebas Automatizadas:** Cobertura de lógica de negocio, integridad de esquema y flujos *End-to-End* (E2E) con **pytest**.

##  Tecnologías utilizadas

* **Python 3.12+**
* **FastAPI** (Framework web asíncrono de alto rendimiento)
* **Pydantic** (Validación de datos y tipado)
* **SQLite3** (Base de datos ligera y embebida)
* **python-dotenv** (Gestión segura de variables de entorno)
* **pytest** & **HTTPX / TestClient** (Pruebas unitarias y E2E)

## Estructura del proyecto

```text
POS-antojitos-mexicanos/
│
├── backend/
│   ├── routers/      # Endpoints de la API (/ordenes)     
│   ├── schemas/      # Modelos de validación Pydantic
│   ├── servicios/    # Lógica de negocio y cálculo de árbol
│   ├── tests/        # Pruebas unitarias y E2E (pytest)
│   ├── config.py     # Configuración y rutas       
│   ├── databse.py    # Inicialización de esquema y constraints     
│   ├── db.py         # Gestión de conexiones y dict_factory
│   ├── errores.py.   # Excepciones de dominio personalizadas
│   ├── main.py       # Punto de entrada de FastAPI
│   └── pytest.ini    # Configuración de pruebas
│
├── .gitignore
├── README.md
└── requirements.txt
```
## Instrucciones de instalación y ejecución local
### Clonar el repositorio
git clone [https://github.com/Sunshine1917/POS-antojitos-mexicanos.git](https://github.com/Sunshine1917/POS-antojitos-mexicanos)
<br>
cd POS-antojitos-mexicanos

### Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate 
<br>*En Windows usa: venv\Scripts\activate*

### Instalar dependencias
pip install -r requirements.txt

### Ejecutar pruebas y levantar el servidor
cd backend <br>
pytest <br>
uvicorn main:app --reload

Una vez iniciado, la documentación interactiva estará disponible en http://127.0.0.1:8000/docs
