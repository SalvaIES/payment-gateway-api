# Memoria técnica — Payment Gateway API

## 1. Descripción del proyecto

Payment Gateway API es un backend desarrollado con Django REST Framework que permite
gestionar de forma centralizada múltiples pasarelas de pago (Stripe, PayPal, Redsys).
El sistema registra cada intento de transacción, gestiona incidencias y protege el
acceso mediante autenticación por token.

---

## 2. Tecnologías utilizadas

| Tecnología              | Versión  | Uso                                 |
|-------------------------|----------|-------------------------------------|
| Python                  | 3.12     | Lenguaje principal                  |
| Django                  | 6.0.4    | Framework web                       |
| Django REST Framework   | 3.17.1   | Construcción de la API REST         |
| SQLite                  | —        | Base de datos relacional            |
| Token Authentication    | —        | Autenticación de usuarios           |

---

## 3. Arquitectura del sistema

El proyecto sigue una arquitectura RESTful organizada en capas:

- **Modelos** (`core/models.py`): definen la estructura de datos y las relaciones.
- **Serializers** (`core/serializers.py`): validan y transforman los datos entre JSON y objetos Python.
- **Vistas** (`core/views.py`): gestionan la lógica de negocio mediante ViewSets de DRF.
- **URLs** (`core/urls.py` y `config/urls.py`): enrutan las peticiones a las vistas correspondientes.

### Estructura del proyecto

```
payment-gateway-api/
├── config/
│   ├── settings.py       # Configuración global de Django
│   └── urls.py           # Rutas principales
├── core/
│   ├── models.py         # Modelos Provider y Transaction
│   ├── serializers.py    # Validación y serialización
│   ├── views.py          # ViewSets de la API
│   ├── urls.py           # Rutas de la app
│   └── tests.py          # Tests unitarios
├── docs/
│   └── memoria_tecnica.md
├── backlog/
│   └── product_backlog.md
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
| name         | CharField    | Nombre del proveedor (ej. Stripe)        |
| api_key      | CharField    | Clave de API del proveedor               |
| environment  | CharField    | Entorno: sandbox o production            |
| is_active    | BooleanField | Indica si el proveedor está activo       |
| created_at   | DateTime     | Fecha de registro (auto)                 |

### Transaction (Transacción)

Registra cada intento de pago vinculado a un proveedor.

| Campo         | Tipo         | Descripción                                          |
|---------------|--------------|------------------------------------------------------|
| id            | Integer (PK) | Identificador único                                  |
| provider      | FK → Provider| Proveedor asociado                                   |
| amount        | Decimal      | Importe del pago                                     |
| currency      | CharField    | Código de moneda (ej. EUR)                           |
| status        | CharField    | Estado: pending, completed o failed                  |
| incident_type | CharField    | Tipo de incidencia: impago, error_conexion, devolucion|
| created_at    | DateTime     | Fecha de creación (auto)                             |
| updated_at    | DateTime     | Fecha de última modificación (auto)                  |

**Relación:** Un Provider puede tener muchas Transactions (1:N).

---

## 5. Endpoints de la API

### Autenticación

| Método | Ruta               | Descripción                        | Auth |
|--------|--------------------|------------------------------------|------|
| POST   | /api/auth/login/   | Obtener token de autenticación     | No   |

**Ejemplo de petición:**
```json
POST /api/auth/login/
{
    "username": "admin",
    "password": "admin1234"
}
```

**Ejemplo de respuesta:**
```json
{
    "token": "a7879add4e69b2310b699f48a37ee90e11e5dc27"
}
```

---

### Proveedores

| Método | Ruta                  | Descripción                  | Auth |
|--------|-----------------------|------------------------------|------|
| GET    | /api/providers/       | Listar todos los proveedores | Sí   |
| POST   | /api/providers/       | Crear un proveedor           | Sí   |
| GET    | /api/providers/{id}/  | Detalle de un proveedor      | Sí   |
| PUT    | /api/providers/{id}/  | Actualizar un proveedor      | Sí   |
| DELETE | /api/providers/{id}/  | Eliminar un proveedor        | Sí   |

**Ejemplo de respuesta GET /api/providers/:**
```json
[
    {
        "id": 1,
        "name": "Stripe",
        "api_key": "sk_test_123456",
        "environment": "sandbox",
        "is_active": true,
        "created_at": "2026-05-03T17:47:17.367621Z"
    }
]
```

---

### Transacciones

| Método | Ruta                      | Descripción                        | Auth |
|--------|---------------------------|------------------------------------|------|
| GET    | /api/transactions/        | Listar transacciones               | Sí   |
| POST   | /api/transactions/        | Crear una transacción              | Sí   |
| GET    | /api/transactions/{id}/   | Detalle de una transacción         | Sí   |
| PUT    | /api/transactions/{id}/   | Actualizar estado e incidencia     | Sí   |
| DELETE | /api/transactions/{id}/   | Eliminar una transacción           | Sí   |

**Filtros disponibles:**

| Parámetro  | Ejemplo                                    | Descripción               |
|------------|--------------------------------------------|---------------------------|
| status     | /api/transactions/?status=pending          | Filtra por estado         |
| provider   | /api/transactions/?provider=1              | Filtra por proveedor      |
| date       | /api/transactions/?date=2026-05-03         | Filtra por fecha          |

**Ejemplo de petición POST /api/transactions/:**
```json
{
    "provider": 1,
    "amount": "150.00",
    "currency": "EUR",
    "status": "pending"
}
```

---

## 6. Validaciones implementadas

- El importe de una transacción debe ser mayor que cero.
- Si el estado de una transacción es `failed`, el campo `incident_type` es obligatorio.
- El campo `currency` acepta códigos de 3 caracteres (ISO 4217).
- El campo `environment` solo acepta los valores `sandbox` o `production`.

---

## 7. Seguridad

El acceso a todos los endpoints (excepto `/api/auth/login/`) requiere autenticación
mediante token. El token se obtiene enviando las credenciales al endpoint de login
y debe incluirse en la cabecera de cada petición:

```
Authorization: Token a7879add4e69b2310b699f48a37ee90e11e5dc27
```

---

## 8. Tests unitarios

Se han implementado 7 tests unitarios en `core/tests.py` que verifican:

| Test                        | Descripción                                          |
|-----------------------------|------------------------------------------------------|
| test_listar_proveedores      | GET /api/providers/ devuelve 200 y la lista          |
| test_crear_proveedor         | POST /api/providers/ crea el proveedor y devuelve 201|
| test_acceso_sin_token        | GET sin token devuelve 401                           |
| test_crear_transaccion       | POST /api/transactions/ devuelve 201                 |
| test_importe_negativo        | POST con importe negativo devuelve 400               |
| test_failed_sin_incidencia   | PUT con failed sin incident_type devuelve 400        |
| test_filtro_por_estado       | GET con ?status= filtra correctamente                |

Ejecución:
```bash
python manage.py test core
```

Resultado: **7 passed, 0 errors**

---

## 9. Decisiones arquitectónicas

**Uso de ViewSets:** Se han utilizado `ModelViewSet` de DRF porque proporcionan
automáticamente las operaciones CRUD completas, reduciendo código repetitivo y
siguiendo el principio DRY.

**Autenticación por token:** Se eligió `TokenAuthentication` por su simplicidad
y compatibilidad con clientes externos como Postman o aplicaciones móviles,
frente a la autenticación por sesión que está orientada a navegadores web.

**PROTECT en ForeignKey:** La transacción usa `on_delete=models.PROTECT` para
evitar eliminar un proveedor que tenga transacciones asociadas, garantizando
la integridad de los datos históricos.

**SQLite como base de datos:** Para el entorno de desarrollo se usa SQLite por
su simplicidad. En producción se reemplazaría por PostgreSQL.

---

## 10. Posibles mejoras futuras

- Paginación de resultados en los endpoints de listado.
- Integración real con las APIs de Stripe, PayPal y Redsys.
- Sistema de notificaciones ante incidencias.
- Migración a PostgreSQL para entornos de producción.
- Autenticación JWT como alternativa al token simple.