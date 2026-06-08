<div align="center">

# PDF Toolkit API

[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.13+-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![uv](https://img.shields.io/badge/uv-managed-DE5FE9?logo=python&logoColor=white)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-D7FF64?logo=ruff&logoColor=black)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#license--licencia)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing--contribuir)

**A modern, asynchronous REST API for PDF manipulation built with FastAPI.**
**Una API REST moderna y asíncrona para manipulación de PDFs construida con FastAPI.**

[English](#-english) · [Español](#-español) · [API Reference](#-api-reference) · [Contributing](#-contributing--contribuir)

</div>

---

## Table of Contents · Tabla de Contenidos

- [English](#-english)
  - [Overview](#overview)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [WeasyPrint Setup on Windows](#weasyprint-setup-on-windows)
  - [Running the Server](#running-the-server)
  - [Project Structure](#project-structure)
- [Español](#-español)
  - [Descripción General](#descripción-general)
  - [Características](#características)
  - [Stack Tecnológico](#stack-tecnológico)
  - [Requisitos](#requisitos)
  - [Instalación](#instalación)
  - [Configuración de WeasyPrint en Windows](#configuración-de-weasyprint-en-windows)
  - [Ejecución del Servidor](#ejecución-del-servidor)
  - [Estructura del Proyecto](#estructura-del-proyecto)
- [API Reference](#-api-reference)
- [Error Handling · Manejo de Errores](#-error-handling--manejo-de-errores)
- [Testing](#-testing)
- [Contributing · Contribuir](#-contributing--contribuir)
- [License · Licencia](#-license--licencia)

---

## English

### Overview

**PDF Toolkit API** is a lightweight, production-ready REST service that exposes common PDF operations through a clean HTTP interface. It is built on top of [FastAPI](https://fastapi.tiangolo.com/), leveraging asynchronous I/O for high throughput, and uses battle-tested libraries such as `pypdf`, `pdf2docx`, and `WeasyPrint` under the hood.

### Features

- Merge multiple PDF documents into a single file.
- Extract plain text from a PDF.
- Split a PDF into individual pages (returned as a ZIP archive).
- Split a PDF by user-defined page ranges (returned as a ZIP archive).
- Convert a PDF document to a Microsoft Word (`.docx`) file.
- Convert an HTML document to a PDF.
- Built-in `/health` endpoint for liveness checks.
- Automatic interactive documentation via Swagger UI (`/docs`) and ReDoc (`/redoc`).

### Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.14+ |
| Framework | FastAPI |
| Validation | Pydantic v2 |
| PDF I/O | pypdf, pdf2docx |
| HTML → PDF | WeasyPrint |
| HTML parsing | BeautifulSoup 4 |
| Tooling | uv, Ruff |

### Requirements

- Python **3.14** or newer
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`
- System dependencies required by **WeasyPrint** (Pango, Cairo, GDK-PixBuf). See the [official guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation).

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/JeanPaulCardozo/pdf_toolkit_api.git
cd pdf_toolkit_api

# 2. Install dependencies (recommended: uv)
uv sync

# Or with pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### WeasyPrint Setup on Windows

The `POST /pdf/convert-html-to-pdf` endpoint relies on **WeasyPrint**, which depends on native libraries (Pango, Cairo, GDK-PixBuf) that are not bundled with Windows. Follow the steps below to enable HTML → PDF conversion on a Windows machine.

> Run the commands in a terminal with administrator privileges.

**1. Install MSYS2** (the package manager that provides the required native libraries):

```powershell
winget install MSYS2.MSYS2
```

**2. Update MSYS2 and install the required libraries** from the MSYS2 shell:

```bash
pacman -Syu
pacman -S mingw-w64-x86_64-pango mingw-w64-x86_64-gdk-pixbuf2 mingw-w64-x86_64-cairo
```

**3. Add the MSYS2 binaries to your Windows `PATH`**:

```
C:\msys64\mingw64\bin
```

> *System Properties → Environment Variables → Path → New*. Restart any open terminals after saving.

**4. Verify the installation** in a new terminal session:

```bash
uv run python -m weasyprint --info
```

If WeasyPrint prints its version and the discovered backend libraries, the setup is complete and the HTML → PDF endpoint is ready to use.

### Running the Server

```bash
# With uv
uv run fastapi dev app/main.py

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, open:

- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc
- Health check → http://localhost:8000/health

### Project Structure

```
pdf_toolkit_api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── pdf.py            # HTTP endpoints
│   ├── schemas/
│   │   └── pdf_schemas.py        # Pydantic models
│   ├── services/
│   │   └── pdf_service.py        # Business logic
│   └── main.py                   # FastAPI application factory
├── main.py                       # CLI entry point
├── pyproject.toml                # Project metadata & dependencies
└── README.md
```

---

## Español

### Descripción General

**PDF Toolkit API** es un servicio REST ligero y listo para producción que expone operaciones comunes sobre archivos PDF mediante una interfaz HTTP limpia. Está construido sobre [FastAPI](https://fastapi.tiangolo.com/), aprovechando E/S asíncrona para alto rendimiento, y utiliza librerías ampliamente probadas como `pypdf`, `pdf2docx` y `WeasyPrint`.

### Características

- Fusionar múltiples documentos PDF en un único archivo.
- Extraer texto plano de un PDF.
- Dividir un PDF en páginas individuales (entregado como archivo ZIP).
- Dividir un PDF según rangos de páginas definidos por el usuario (entregado como archivo ZIP).
- Convertir un documento PDF a un archivo de Microsoft Word (`.docx`).
- Convertir un documento HTML a PDF.
- Endpoint `/health` integrado para verificación de disponibilidad.
- Documentación interactiva automática mediante Swagger UI (`/docs`) y ReDoc (`/redoc`).

### Stack Tecnológico

| Capa | Tecnología |
| --- | --- |
| Lenguaje | Python 3.14+ |
| Framework | FastAPI |
| Validación | Pydantic v2 |
| E/S PDF | pypdf, pdf2docx |
| HTML → PDF | WeasyPrint |
| Parseo HTML | BeautifulSoup 4 |
| Herramientas | uv, Ruff |

### Requisitos

- Python **3.14** o superior
- [uv](https://docs.astral.sh/uv/) (recomendado) o `pip`
- Dependencias del sistema requeridas por **WeasyPrint** (Pango, Cairo, GDK-PixBuf). Consulta la [guía oficial](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation).

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/JeanPaulCardozo/pdf_toolkit_api.git
cd pdf_toolkit_api

# 2. Instalar dependencias (recomendado: uv)
uv sync

# O con pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Configuración de WeasyPrint en Windows

El endpoint `POST /pdf/convert-html-to-pdf` depende de **WeasyPrint**, el cual requiere librerías nativas (Pango, Cairo, GDK-PixBuf) que no vienen incluidas en Windows. Sigue los pasos siguientes para habilitar la conversión HTML → PDF en una máquina Windows.

> Ejecuta los comandos en una terminal con privilegios de administrador.

**1. Instala MSYS2** (el gestor de paquetes que proporciona las librerías nativas necesarias):

```powershell
winget install MSYS2.MSYS2
```

**2. Actualiza MSYS2 e instala las librerías requeridas** desde la shell de MSYS2:

```bash
pacman -Syu
pacman -S mingw-w64-x86_64-pango mingw-w64-x86_64-gdk-pixbuf2 mingw-w64-x86_64-cairo
```

**3. Agrega los binarios de MSYS2 a la variable `PATH` de Windows**:

```
C:\msys64\mingw64\bin
```

> *Propiedades del Sistema → Variables de entorno → Path → Nuevo*. Reinicia cualquier terminal abierta tras guardar.

**4. Verifica la instalación** en una nueva sesión de terminal:

```bash
uv run python -m weasyprint --info
```

Si WeasyPrint imprime su versión y las librerías de backend detectadas, la configuración está completa y el endpoint HTML → PDF está listo para usarse.

### Ejecución del Servidor

```bash
# Con uv
uv run fastapi dev app/main.py

# O directamente con uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Una vez iniciado, abre:

- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc
- Health check → http://localhost:8000/health

### Estructura del Proyecto

```
pdf_toolkit_api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── pdf.py            # Endpoints HTTP
│   ├── schemas/
│   │   └── pdf_schemas.py        # Modelos Pydantic
│   ├── services/
│   │   └── pdf_service.py        # Lógica de negocio
│   └── main.py                   # Fábrica de la aplicación FastAPI
├── main.py                       # Punto de entrada CLI
├── pyproject.toml                # Metadatos y dependencias
└── README.md
```

---

## API Reference

> Base URL · URL base: `http://localhost:8000`

### `GET /health`

Liveness probe. Returns service status.
Sondeo de disponibilidad. Devuelve el estado del servicio.

**Response · Respuesta** `200 OK`

```json
{ "status": "ok" }
```

---

### `POST /pdf/merge`

Merge two or more PDF files into a single document.
Fusiona dos o más archivos PDF en un solo documento.

**Request · Solicitud** — `multipart/form-data`

| Field · Campo | Type · Tipo | Required · Requerido | Description · Descripción |
| --- | --- | --- | --- |
| `files` | `File[]` | ✅ | List of PDF files to merge. · Lista de archivos PDF a fusionar. |

**Example · Ejemplo**

```bash
curl -X POST http://localhost:8000/pdf/merge \
  -F "files=@first.pdf" \
  -F "files=@second.pdf" \
  -o merged.pdf
```

**Response · Respuesta** `200 OK` — `application/pdf` (file download · descarga de archivo `merged.pdf`).

---

### `POST /pdf/extract-text`

Extract textual content from a PDF.
Extrae el contenido textual de un PDF.

**Request · Solicitud** — `multipart/form-data`

| Field · Campo | Type · Tipo | Required · Requerido | Description · Descripción |
| --- | --- | --- | --- |
| `file` | `File` | ✅ | PDF file to process. · Archivo PDF a procesar. |

**Example · Ejemplo**

```bash
curl -X POST http://localhost:8000/pdf/extract-text \
  -F "file=@document.pdf"
```

**Response · Respuesta** `200 OK`

```json
{
  "status": "success",
  "extracted_text": "Lorem ipsum dolor sit amet..."
}
```

---

### `POST /pdf/split`

Split a PDF into individual single-page PDF files, returned as a ZIP archive.
Divide un PDF en archivos PDF individuales de una sola página, entregado como archivo ZIP.

**Request · Solicitud** — `multipart/form-data`

| Field · Campo | Type · Tipo | Required · Requerido | Description · Descripción |
| --- | --- | --- | --- |
| `file` | `File` | ✅ | PDF file to split. · Archivo PDF a dividir. |

**Example · Ejemplo**

```bash
curl -X POST http://localhost:8000/pdf/split \
  -F "file=@document.pdf" \
  -o split_pdfs.zip
```

**Response · Respuesta** `200 OK` — `application/zip` (`split_pdfs.zip`).

---

### `POST /pdf/split_by_ranges`

Split a PDF by user-defined page ranges and return them grouped in a ZIP archive.
Divide un PDF en rangos de páginas definidos por el usuario y los devuelve agrupados en un archivo ZIP.

**Request · Solicitud** — `multipart/form-data`

| Field · Campo | Type · Tipo | Required · Requerido | Description · Descripción |
| --- | --- | --- | --- |
| `file` | `File` | ✅ | PDF file to split. · Archivo PDF a dividir. |
| `ranges` | `string` (JSON) | ✅ | Stringified JSON array of `{start, end}` objects (1-indexed, inclusive). · Cadena JSON con un arreglo de objetos `{start, end}` (base 1, inclusivo). |

**`ranges` schema · esquema**

```json
[
  { "start": 1, "end": 3 },
  { "start": 5, "end": 7 }
]
```

**Example · Ejemplo**

```bash
curl -X POST http://localhost:8000/pdf/split_by_ranges \
  -F "file=@document.pdf" \
  -F 'ranges=[{"start":1,"end":3},{"start":5,"end":7}]' \
  -o split_by_ranges_pdfs.zip
```

**Response · Respuesta** `200 OK` — `application/zip` (`split_by_ranges_pdfs.zip`).

---

### `POST /pdf/convert-to-word`

Convert a PDF document to a Word (`.docx`) document.
Convierte un documento PDF a un documento de Word (`.docx`).

**Request · Solicitud** — `multipart/form-data`

| Field · Campo | Type · Tipo | Required · Requerido | Description · Descripción |
| --- | --- | --- | --- |
| `file` | `File` | ✅ | PDF file to convert. · Archivo PDF a convertir. |

**Example · Ejemplo**

```bash
curl -X POST http://localhost:8000/pdf/convert-to-word \
  -F "file=@document.pdf" \
  -o converted.docx
```

**Response · Respuesta** `200 OK` — `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (`converted.docx`).

---

### `POST /pdf/convert-html-to-pdf`

Convert a well-formed HTML file (must contain `<html>` and `<body>` tags) into a PDF.
Convierte un archivo HTML bien formado (debe contener etiquetas `<html>` y `<body>`) a un PDF.

**Request · Solicitud** — `multipart/form-data`

| Field · Campo | Type · Tipo | Required · Requerido | Description · Descripción |
| --- | --- | --- | --- |
| `file` | `File` | ✅ | HTML file (`text/html`) to convert. · Archivo HTML (`text/html`) a convertir. |

**Example · Ejemplo**

```bash
curl -X POST http://localhost:8000/pdf/convert-html-to-pdf \
  -F "file=@page.html" \
  -o html_to_pdf_converted.pdf
```

**Response · Respuesta** `200 OK` — `application/pdf` (`html_to_pdf_converted.pdf`).

---

## Error Handling · Manejo de Errores

The API follows standard HTTP semantics. All errors return a JSON body matching FastAPI's default schema:
La API sigue la semántica HTTP estándar. Todos los errores devuelven un cuerpo JSON acorde al esquema por defecto de FastAPI:

```json
{ "detail": "Human-readable error message" }
```

| Status | Cause · Causa |
| --- | --- |
| `400 Bad Request` | Invalid file type, corrupted PDF, invalid HTML, malformed page ranges, or ranges exceeding the document length. · Tipo de archivo no válido, PDF corrupto, HTML inválido, rangos mal formados o que exceden el total de páginas. |
| `422 Unprocessable Entity` | Missing or schema-invalid form fields. · Campos del formulario ausentes o que no cumplen el esquema. |
| `500 Internal Server Error` | Unhandled server-side exception. · Excepción no controlada en el servidor. |

---

## Testing

Run the API locally and exercise the endpoints from the auto-generated Swagger UI at `/docs`, or use `curl`/HTTPie/Postman as shown above.
Ejecuta la API localmente y prueba los endpoints desde la Swagger UI auto-generada en `/docs`, o usa `curl`/HTTPie/Postman como se muestra arriba.

Lint the codebase with Ruff: · Analiza el código con Ruff:

```bash
uv run ruff check .
uv run ruff format .
```

---

## Contributing · Contribuir

Contributions are welcome! Please follow these steps:
¡Las contribuciones son bienvenidas! Por favor sigue estos pasos:

1. **Fork** the repository. · Haz un **fork** del repositorio.
2. Create a feature branch: `git checkout -b feat/my-feature`. · Crea una rama: `git checkout -b feat/mi-funcionalidad`.
3. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/). · Realiza commits siguiendo [Conventional Commits](https://www.conventionalcommits.org/).
4. Run linters and ensure the app boots. · Ejecuta los linters y verifica que la app arranque.
5. Open a Pull Request describing the motivation and changes. · Abre un Pull Request describiendo la motivación y los cambios.

### Commit message conventions · Convención de mensajes

| Prefix · Prefijo | Use case · Caso de uso |
| --- | --- |
| `feat:` | New feature · Nueva funcionalidad |
| `fix:` | Bug fix · Corrección de error |
| `docs:` | Documentation only · Solo documentación |
| `refactor:` | Code refactor · Refactorización |
| `test:` | Add or fix tests · Añadir/corregir tests |
| `chore:` | Tooling, build, deps · Tooling, build, dependencias |

### Code style · Estilo de código

- Follow **PEP 8** and project Ruff rules. · Sigue **PEP 8** y las reglas de Ruff del proyecto.
- Prefer type hints throughout the codebase. · Usa anotaciones de tipo en todo el código.
- Keep service logic out of route handlers. · Mantén la lógica de negocio fuera de los handlers de rutas.

---

## License · Licencia

This project is distributed under the **MIT License**. See the `LICENSE` file for details (add one to your repository if it does not yet exist).
Este proyecto se distribuye bajo la **Licencia MIT**. Consulta el archivo `LICENSE` para más detalles (agrégalo a tu repositorio si aún no existe).

---

## Author · Autor

**Jean Paul Cardozo** — [@JeanPaulCardozo](https://github.com/JeanPaulCardozo)

> If you find this project useful, please consider giving it a ⭐ on GitHub.
> Si este proyecto te resulta útil, considera darle una ⭐ en GitHub.
