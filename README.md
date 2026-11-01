# 🌮 Antojitos Mexicanos - Sistema POS

Sistema de Punto de Venta (POS) desarrollado a medida para optimizar la gestión de pedidos, menús y pagos en un negocio familiar de comida tradicional mexicana. Este proyecto forma parte de una iniciativa de desarrollo de software con enfoque en arquitectura limpia, rendimiento y separación de responsabilidades.

##  Características principales

* **Arquitectura Modular:** Rutas organizadas por dominios de negocio (`/menu`, `/pedido`, `/pago`) utilizando **FastAPI**.
* **Gestión de Base de Datos Relacional:** Uso de **SQLite** con control estricto de transacciones, llaves foráneas e integridad referencial para platillos, modificadores y órdenes detalladas.
* **Mapeo Eficiente (Data Transfer):** Implementación de factorías personalizadas (`dict_factory`) para transformar registros crudos de SQL en diccionarios JSON nativos optimizados para la web.
* **Seguridad y Configuración:** Manejo seguro de variables de entorno mediante `python-dotenv` y protección de datos sensibles en archivos ocultos.
* **Validación de Datos:** Uso de esquemas robustos con **Pydantic** para asegurar la integridad de los datos entrantes en los endpoints.

##  Tecnologías utilizadas

* **Python 3.12+**
* **FastAPI** (Framework web asíncrono de alto rendimiento)
* **Pydantic** (Validación de datos y tipado)
* **SQLite3** (Base de datos ligera y embebida)
* **python-dotenv** (Gestión segura de variables de entorno)

## Estructura del proyecto

```text
POS-antojitos-mexicanos/
│
├── backend/
│   ├── routers/
│   │   ├── menu.py
│   │   ├── pago.py
│   │   └── pedido.py
│   ├── database.py
│   └── main.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```
## Instrucciones de instalación y ejecución local
### Clonar el repositorio
git clone [https://github.com/Sunshine_1917/POS-antojitos-mexicanos.git](https://github.com/Sunshine_1917/POS-antojitos-mexicanos.git)
<br>
cd POS-antojitos-mexicanos

### Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate 
<br>*En Windows usa: venv\Scripts\activate*

### Instalar dependencias
pip install -r requirements.txt
