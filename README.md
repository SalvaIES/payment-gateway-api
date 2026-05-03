# Payment Gateway API

API REST para la gestión centralizada de pasarelas de pago (Stripe, PayPal, Redsys).
Desarrollada con Django REST Framework como proyecto final del CE en Desarrollo
de aplicaciones en lenguaje Python.

## Descripción

Este backend permite a una plataforma de comercio electrónico alternar entre
diferentes proveedores de pago de forma centralizada, registrando cada intento
de transacción y gestionando incidencias técnicas o financieras.

## Tecnologías

- Python 3.12
- Django 5.x
- Django REST Framework
- SQLite
- Token Authentication

## Instalación

```bash
git clone https://github.com/TU_USUARIO/payment-gateway-api.git
cd payment-gateway-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Endpoints principales

| Método   | Ruta                        | Descripción                        |
|----------|-----------------------------|------------------------------------|
| GET/POST | /api/providers/             | Listar y crear proveedores         |
| GET/PUT  | /api/providers/{id}/        | Detalle, editar y eliminar         |
| GET/POST | /api/transactions/          | Listar y crear transacciones       |
| GET/PUT  | /api/transactions/{id}/     | Detalle y actualizar estado        |
| GET      | /api/transactions/?provider=&status=&date= | Historial filtrado  |
| POST     | /api/auth/login/            | Obtener token de autenticación     |

## Estados de transacción

- `pending` — pago iniciado
- `completed` — pago completado con éxito
- `failed` — pago fallido

## Tipos de incidencia

- `impago` — pago no realizado
- `error_conexion` — fallo de comunicación con el proveedor
- `devolucion` — cargo revertido

## Estructura del proyecto

```
payment-gateway-api/
├── core/                  # App principal Django
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── docs/
│   └── erd.md
├── backlog/
│   └── product_backlog.md
├── requirements.txt
└── manage.py
```

## Autores

- Salvador Martínez Bolinches
- IES Font de Sant Lluís — Curso 2025-2026