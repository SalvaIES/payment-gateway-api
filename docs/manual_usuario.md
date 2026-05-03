# Manual de usuario — Payment Gateway API

## 1. Requisitos previos

- Python 3.12 o superior
- Git
- Postman (opcional, para pruebas visuales)

---

## 2. Instalación

### 2.1 Clonar el repositorio

```bash
git clone https://github.com/SalvaIES/payment-gateway-api.git
cd payment-gateway-api
```

### 2.2 Crear y activar el entorno virtual

```bash
python3 -m venv venv --without-pip
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
```

### 2.3 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2.4 Aplicar migraciones

```bash
python manage.py migrate
```

### 2.5 Crear un superusuario

```bash
python manage.py createsuperuser
```

### 2.6 Arrancar el servidor

```bash
python manage.py runserver
```

La API estará disponible en: http://127.0.0.1:8000/

---

## 3. Autenticación

Todos los endpoints requieren autenticación por token excepto el login.

### Obtener el token

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "tu_contraseña"}'
```

Respuesta:
```json
{"token": "a7879add4e69b2310b699f48a37ee90e11e5dc27"}
```

### Usar el token en cada petición

Añade esta cabecera en todas las peticiones:
```
Authorization: Token a7879add4e69b2310b699f48a37ee90e11e5dc27
```

---

## 4. Gestión de proveedores

### Listar proveedores

```bash
curl http://127.0.0.1:8000/api/providers/ \
  -H "Authorization: Token TU_TOKEN"
```

### Crear un proveedor

```bash
curl -X POST http://127.0.0.1:8000/api/providers/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Stripe",
    "api_key": "sk_test_123456",
    "environment": "sandbox"
  }'
```

Campos disponibles:

| Campo       | Obligatorio | Valores posibles          |
|-------------|-------------|---------------------------|
| name        | Sí          | Texto libre               |
| api_key     | Sí          | Texto libre               |
| environment | Sí          | sandbox / production      |
| is_active   | No          | true / false (default: true) |

### Editar un proveedor

```bash
curl -X PUT http://127.0.0.1:8000/api/providers/1/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Stripe",
    "api_key": "sk_live_999999",
    "environment": "production"
  }'
```

### Eliminar un proveedor

```bash
curl -X DELETE http://127.0.0.1:8000/api/providers/1/ \
  -H "Authorization: Token TU_TOKEN"
```

Nota: no es posible eliminar un proveedor que tenga transacciones asociadas.

---

## 5. Gestión de transacciones

### Crear una transacción

```bash
curl -X POST http://127.0.0.1:8000/api/transactions/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": 1,
    "amount": "150.00",
    "currency": "EUR",
    "status": "pending"
  }'
```

Campos disponibles:

| Campo         | Obligatorio | Valores posibles                        |
|---------------|-------------|-----------------------------------------|
| provider      | Sí          | ID de un proveedor existente            |
| amount        | Sí          | Número decimal mayor que cero           |
| currency      | Sí          | Código ISO 4217 (ej. EUR, USD)          |
| status        | Sí          | pending / completed / failed            |
| incident_type | No*         | impago / error_conexion / devolucion    |

*Obligatorio si el estado es `failed`.

### Marcar una incidencia

```bash
curl -X PUT http://127.0.0.1:8000/api/transactions/1/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": 1,
    "amount": "150.00",
    "currency": "EUR",
    "status": "failed",
    "incident_type": "impago"
  }'
```

Tipos de incidencia disponibles:

| Valor          | Descripción                          |
|----------------|--------------------------------------|
| impago         | El pago no ha sido realizado         |
| error_conexion | Fallo de comunicación con el proveedor|
| devolucion     | El cargo ha sido revertido           |

---

## 6. Consulta del historial

### Filtrar por estado

```bash
curl "http://127.0.0.1:8000/api/transactions/?status=pending" \
  -H "Authorization: Token TU_TOKEN"
```

### Filtrar por proveedor

```bash
curl "http://127.0.0.1:8000/api/transactions/?provider=1" \
  -H "Authorization: Token TU_TOKEN"
```

### Filtrar por fecha

```bash
curl "http://127.0.0.1:8000/api/transactions/?date=2026-05-03" \
  -H "Authorization: Token TU_TOKEN"
```

### Combinar filtros

```bash
curl "http://127.0.0.1:8000/api/transactions/?provider=1&status=failed" \
  -H "Authorization: Token TU_TOKEN"
```

---

## 7. Códigos de respuesta

| Código | Significado                                      |
|--------|--------------------------------------------------|
| 200    | Petición correcta                                |
| 201    | Recurso creado correctamente                     |
| 400    | Error de validación en los datos enviados        |
| 401    | Token no proporcionado o inválido                |
| 404    | Recurso no encontrado                            |
| 405    | Método HTTP no permitido                         |

---

## 8. Panel de administración

Django incluye un panel de administración web en:

http://127.0.0.1:8000/admin/

Accede con las credenciales del superusuario para gestionar proveedores,
transacciones y usuarios directamente desde el navegador.