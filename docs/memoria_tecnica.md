# Memoria técnica — Payment Gateway API

## 1. Descripción del proyecto

Payment Gateway API es un backend desarrollado con Django REST Framework que permite
gestionar de forma centralizada múltiples pasarelas de pago: Stripe, PayPal y Redsys.
El sistema registra cada intento de transacción, gestiona incidencias, procesa pagos
reales a través de cada pasarela y actualiza automáticamente el estado mediante webhooks.
Incluye además un frontend completo desarrollado con Django Templates.

---

## 2. Tecnologías utilizadas

| Tecnología              | Versión   | Uso                                        |
|-------------------------|-----------|--------------------------------------------|
| Python                  | 3.12      | Lenguaje principal                         |
| Django                  | 6.0.4     | Framework web                              |
| Django REST Framework   | 3.17.1    | Construcción de la API REST                |
| SQLite                  | —         | Base de datos relacional                   |
| stripe                  | 15.1.0    | SDK oficial de Stripe                      |
| paypalrestsdk           | 1.13.3    | SDK oficial de PayPal                      |
| pyredsys                | 0.1.6     | Librería para integración con Redsys       |
| python-dotenv           | 1.2.2     | Gestión de variables de entorno            |
| requests                | 2.33.1    | Peticiones HTTP desde el frontend          |
| ngrok                   | —         | Túnel HTTPS para webhooks en desarrollo    |
| Stripe CLI              | 1.40.9    | Reenvío de webhooks de Stripe en local     |

---

## 3. Arquitectura del sistema

El proyecto sigue una arquitectura RESTful organizada en capas:

- **Modelos** (`core/models.py`): definen la estructura de datos y las relaciones.
- **Serializers** (`core/serializers.py`): validan y transforman los datos entre JSON y objetos Python.
- **Vistas API** (`core/views.py`): gestionan la lógica de negocio, los pagos y los webhooks.
- **Vistas Frontend** (`frontend/views.py`): sirven las páginas HTML del panel de gestión.
- **URLs** (`config/urls.py`, `core/urls.py`, `frontend/urls.py`): enrutan las peticiones.

### Estructura del proyecto

```
payment-gateway-api/
├── config/
│   ├── settings.py
│   └── urls.py
├── core/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── templates/core/
│       ├── stripe_payment.html
│       └── redsys_payment.html
├── frontend/
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── templates/frontend/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── providers.html
│       └── transactions.html
├── docs/
│   ├── memoria_tecnica.md
│   └── manual_usuario.md
├── backlog/
│   └── product_backlog.md
├── .env
├── manage.py
└── requirements.txt
```

---

## 4. Modelo de datos

### Provider (Proveedor)

Representa una pasarela de pago con sus parámetros de configuración.

| Campo        | Tipo         | Descripción                              |
|--------------|--------------|------------------------------------------|
| id           | Integer (PK) | Identificador único                      |
| name         | CharField    | Nombre del proveedor (Stripe/PayPal/Redsys) |
| api_key      | CharField    | Clave de API del proveedor               |
| environment  | CharField    | Entorno: sandbox o production            |
| is_active    | BooleanField | Indica si el proveedor está activo       |
| created_at   | DateTime     | Fecha de registro (auto)                 |

### Transaction (Transacción)

Registra cada intento de pago vinculado a un proveedor.

| Campo                    | Tipo         | Descripción                                          |
|--------------------------|--------------|------------------------------------------------------|
| id                       | Integer (PK) | Identificador único                                  |
| provider                 | FK → Provider| Proveedor asociado                                   |
| amount                   | Decimal      | Importe del pago                                     |
| currency                 | CharField    | Código de moneda (ej. EUR)                           |
| status                   | CharField    | Estado: pending, completed o failed                  |
| incident_type            | CharField    | Tipo de incidencia: impago, error_conexion, devolucion|
| stripe_payment_intent_id | CharField    | ID del PaymentIntent de Stripe                       |
| stripe_client_secret     | CharField    | Client secret para confirmar el pago en Stripe       |
| created_at               | DateTime     | Fecha de creación (auto)                             |
| updated_at               | DateTime     | Fecha de última modificación (auto)                  |

**Relación:** Un Provider puede tener muchas Transactions (1:N).

---

## 5. Endpoints de la API REST

### Autenticación

| Método | Ruta               | Descripción                        | Auth |
|--------|--------------------|------------------------------------|------|
| POST   | /api/auth/login/   | Obtener token de autenticación     | No   |

### Proveedores

| Método        | Ruta                  | Descripción                  | Auth |
|---------------|-----------------------|------------------------------|------|
| GET/POST      | /api/providers/       | Listar y crear proveedores   | Sí   |
| GET/PUT/DELETE| /api/providers/{id}/  | Detalle, editar y eliminar   | Sí   |

### Transacciones

| Método        | Ruta                      | Descripción                        | Auth |
|---------------|---------------------------|------------------------------------|------|
| GET/POST      | /api/transactions/        | Listar y crear transacciones       | Sí   |
| GET/PUT/DELETE| /api/transactions/{id}/   | Detalle, actualizar y eliminar     | Sí   |

**Filtros disponibles:** `?status=`, `?provider=`, `?date=`, `?ordering=`

### Pasarelas de pago

| Método | Ruta                              | Descripción                        | Auth |
|--------|-----------------------------------|------------------------------------|------|
| GET    | /api/pay/stripe/{id}/             | Formulario de pago con Stripe      | No   |
| GET    | /api/pay/redsys/{id}/             | Redirección al TPV de Redsys       | No   |
| GET    | /api/pay/paypal/{id}/             | Redirección a PayPal               | No   |
| GET    | /api/pay/paypal/execute/          | Callback de confirmación de PayPal | No   |

### Webhooks

| Método | Ruta                        | Descripción                        | Auth |
|--------|-----------------------------|------------------------------------|------|
| POST   | /api/webhooks/stripe/       | Notificaciones de Stripe           | No   |
| POST   | /api/webhooks/redsys/       | Notificaciones de Redsys           | No   |

---

## 6. Integración con pasarelas de pago

### 6.1 Stripe

**Flujo:**
1. Al crear una transacción con proveedor Stripe, se crea automáticamente un `PaymentIntent`.
2. El usuario accede al formulario de pago (`/api/pay/stripe/{id}/`) e introduce los datos de tarjeta.
3. Stripe confirma el pago y envía un evento `payment_intent.succeeded` al webhook.
4. El webhook actualiza el estado de la transacción a `completed`.

**Configuración requerida en `.env`:**
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Tarjeta de prueba:** `4242 4242 4242 4242` / Caducidad: `12/34` / CVC: `123`

**Herramienta de desarrollo:** Stripe CLI para reenvío de webhooks en local:
```bash
stripe listen --forward-to http://127.0.0.1:8000/api/webhooks/stripe/
```

---

### 6.2 Redsys

**Flujo:**
1. El usuario hace click en "Pagar" en una transacción con proveedor Redsys.
2. El backend genera un formulario firmado con HMAC-SHA256 y redirige al TPV virtual.
3. El usuario introduce los datos de tarjeta en la web del banco.
4. Redsys envía una notificación POST al webhook con el resultado.
5. El webhook verifica la firma y actualiza el estado de la transacción.

**Configuración requerida en `.env`:**
```
REDSYS_SECRET_KEY=sq7HjrUOBfKmC576ILgskD5srU870gJ7
REDSYS_MERCHANT_CODE=999008881
REDSYS_TERMINAL=1
REDSYS_URL=https://sis-t.redsys.es:25443/sis/realizarPago
```

**Tarjeta de prueba:** `4548 8120 4940 0004` / Caducidad: `12/34` / CVV: `123`

**Nota:** En desarrollo se usa ngrok para exponer el webhook al exterior:
```bash
ngrok http 8000
```
La URL del webhook en `core/views.py` debe actualizarse con el dominio de ngrok.

---

### 6.3 PayPal

**Flujo:**
1. El usuario hace click en "Pagar" en una transacción con proveedor PayPal.
2. El backend crea un pago en PayPal mediante la API REST y redirige al usuario.
3. El usuario aprueba el pago en la web de PayPal.
4. PayPal redirige al callback `/api/pay/paypal/execute/` con el `paymentId` y `PayerID`.
5. El backend ejecuta el pago y actualiza el estado de la transacción a `completed`.

**Configuración requerida en `.env`:**
```
PAYPAL_CLIENT_ID=AcXYVuNGqe...
PAYPAL_CLIENT_SECRET=EHwRMP03...
PAYPAL_URL=https://api-m.sandbox.paypal.com
```

**Cuenta de prueba:** Usar las cuentas sandbox de PayPal Developer (Testing Tools → Sandbox Accounts).

---

## 7. Frontend

El frontend está desarrollado con Django Templates y Bootstrap 5. Incluye las siguientes páginas:

| Página         | URL              | Descripción                                      |
|----------------|------------------|--------------------------------------------------|
| Login          | /login/          | Autenticación de usuario                         |
| Dashboard      | /                | Estadísticas y gráfico de transacciones por estado|
| Proveedores    | /providers/      | Listar, crear y eliminar proveedores             |
| Transacciones  | /transactions/   | Listar, crear, filtrar, ordenar y pagar          |

### Funcionalidades del frontend

- Autenticación por sesión con token de la API
- Dashboard con tarjetas de estadísticas y gráfico doughnut (Chart.js)
- Tabla de transacciones con paginación (10 por página)
- Ordenación por importe y fecha
- Filtros por estado y proveedor
- Botones de pago según el proveedor (Stripe, Redsys, PayPal)
- Modal para actualizar estado e incidencia
- Confirmación antes de eliminar

---

## 8. Seguridad

- Todos los endpoints de la API requieren token de autenticación (`TokenAuthentication`).
- Las claves de API y secrets se almacenan en `.env` y nunca se suben a GitHub.
- Los webhooks de Stripe verifican la firma con `STRIPE_WEBHOOK_SECRET`.
- Los webhooks de Redsys verifican la firma HMAC-SHA256.
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` configurados para desarrollo.

---

## 9. Tests unitarios

Se han implementado 13 tests en `core/tests.py` y `frontend/tests.py`:

**core/tests.py (7 tests):**

| Test                        | Descripción                                          |
|-----------------------------|------------------------------------------------------|
| test_listar_proveedores      | GET /api/providers/ devuelve 200 y la lista          |
| test_crear_proveedor         | POST /api/providers/ devuelve 201                    |
| test_acceso_sin_token        | GET sin token devuelve 401                           |
| test_crear_transaccion       | POST /api/transactions/ devuelve 201                 |
| test_importe_negativo        | POST con importe negativo devuelve 400               |
| test_failed_sin_incidencia   | PUT con failed sin incident_type devuelve 400        |
| test_filtro_por_estado       | GET con ?status= filtra correctamente                |

**frontend/tests.py (6 tests):**

| Test                            | Descripción                                     |
|---------------------------------|-------------------------------------------------|
| test_login_page_carga           | GET /login/ devuelve 200                        |
| test_login_incorrecto           | Login incorrecto devuelve 200                   |
| test_dashboard_sin_sesion       | Dashboard sin sesión redirige al login          |
| test_providers_sin_sesion       | Providers sin sesión redirige al login          |
| test_transactions_sin_sesion    | Transactions sin sesión redirige al login       |
| test_logout_sin_sesion          | Logout sin sesión redirige al login             |

Ejecución: `python manage.py test`

---

## 10. Decisiones arquitectónicas

**ModelViewSet:** Proporciona automáticamente las operaciones CRUD completas, reduciendo código repetitivo y siguiendo el principio DRY.

**TokenAuthentication:** Elegida por su compatibilidad con clientes externos (Postman, frontend, apps móviles), frente a la autenticación por sesión orientada a navegadores.

**PROTECT en ForeignKey:** Evita eliminar un proveedor con transacciones asociadas, garantizando la integridad histórica de los datos.

**SQLite:** Usado en desarrollo por su simplicidad. En producción se reemplazaría por PostgreSQL.

**Django Templates para el frontend:** Integrado en el mismo proyecto Django para simplificar el despliegue y evitar la complejidad de gestionar dos servidores separados.

**python-dotenv:** Gestiona las variables de entorno sensibles fuera del código fuente, siguiendo las buenas prácticas de seguridad.

---

## 11. Posibles mejoras futuras

- Migración a PostgreSQL para entornos de producción.
- Autenticación JWT como alternativa al token simple.
- Paginación en la API REST.
- Integración con más pasarelas (Bizum, Apple Pay, Google Pay).
- Notificaciones por email ante incidencias.
- Panel de administración personalizado.
- Despliegue en servidor con Gunicorn + Nginx.