# High-Performance Async FastAPI & Redis Notes Engine

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![MySQL 8.4](https://img.shields.io/badge/MySQL-8.4-4479A1.svg)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D.svg)](https://redis.io/)

Aplicación web asíncrona modular desarrollada con **FastAPI**, **SQLAlchemy 2.0 (Async)**, **MySQL**, **Redis Cache-Aside** y autenticación **Bcrypt + JWT**. Incluye panel de administración de usuarios y un bloc de notas personal aislado por sesión.

---

## Arquitectura del Sistema
[ Frontend (HTML5 / Vanilla JS) 

│ (HTTP / Bearer JWT)


▼


[ FastAPI Layered Architecture ]


├── Auth (Bcrypt + OAuth2 Bearer JWT)


├── Routers ➔ Services ➔ Repositories


├── Redis Cache-Aside Engine (TTL + Auto Invalidation)


└── Database Session (SQLAlchemy Async ORM)





[ MySQL 8.4 ]   [ Redis 7 ]


(Persistencia)    (Caché)


---

## 🛠 Características Técnicas

* **Arquitectura Limpia en Capas:** Desacoplamiento estricto entre controladores de ruta, lógica de dominio/servicios y repositorios de datos.
* **Persistencia Asíncrona:** Manejo no bloqueante de base de datos relacional mediante `SQLAlchemy 2.0` y driver `aiomysql`.
* **Caché en Memoria (Cache-Aside):** Almacenamiento temporal en Redis para lecturas de notas con invalidación inmediata ante escrituras o borrados.
* **Seguridad & Hashing:** Contraseñas protegidas mediante algoritmos de hashing seguro (`Bcrypt`), tokens de acceso firmados (`PyJWT`) y documentación interactiva protegida con `HTTP Basic Auth`.
* **Migraciones de Base de Datos:** Versionado declarativo de esquemas utilizando `Alembic`.
* **Calidad y Testing:** Suite de pruebas asíncronas con `Pytest`, `HTTPX` y mocks en memoria, verificado mediante **GitHub Actions CI**.

---

## 📁 Estructura del Proyecto

```text
.
├── .github/workflows/ci.yml  # Pipeline de Integración Continua
├── alembic/                  # Scripts y versiones de migración
├── src/
│   ├── core/                 # Configuración (pydantic-settings) y seguridad (Bcrypt, JWT)
│   ├── database/             # Configuración de conexiones (MySQL y Redis)
│   ├── models/               # Modelos ORM (User, Note)
│   ├── repositories/         # Capa de acceso a datos (I/O)
│   ├── schemas/              # Esquemas y validaciones Pydantic
│   ├── services/             # Lógica de negocio y autenticación
│   └── main.py               # Punto de entrada de la aplicación FastAPI
├── frontend/                 # Interfaz gráfica (HTML5 + CSS + JS)
├── tests/                    # Tests unitarios y de integración con Pytest
├── compose.yaml              # Orquestación multinodo de Docker
├── Dockerfile                # Configuración de imagen de la API
└── requirements.txt          # Dependencias del proyecto
```



## ⚡ Despliegue Rápido (Docker)
1. Clonar el repositorio

    git clone [https://github.com/Rabenn/fastapi-notes-engine.git](https://github.com/Rabenn/fastapi-notes-engine.git)
    cd fastapi-notes-engine

2. Configurar variables de entorno

    cp .env.example .env

3. Levantar los contenedores

    docker compose up --build

## 🌐 Acceso a los Servicios
Documentación Interactiva (Swagger UI): http://localhost:8000/docs

Usuario: admin | Contraseña: admin

Frontend Web: Abre el archivo frontend/index.html directamente en tu navegador.

Credenciales por defecto iniciales:

Admin: Usuario admin (o admin@admin.com) | Contraseña admin

## 🧪 Pruebas Automatizadas y Calidad
Para ejecutar las pruebas en un entorno local:

Bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Análisis estático de código (Linter)
ruff check .

# 3. Ejecutar suite de pruebas unitarias y de integración
pytest -v

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.