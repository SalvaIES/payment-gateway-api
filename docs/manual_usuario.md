# Manual de usuario — Payment Gateway API

## 1. Requisitos previos

- Python 3.10 o superior (3.12 recomendado)
- Git
- Cuenta en Stripe (https://stripe.com)
- Cuenta en PayPal Developer (https://developer.paypal.com)
- Stripe CLI (para webhooks en desarrollo)
- ngrok (para webhooks de Redsys en desarrollo)

---

## 2. Instalación

### 2.1 Clonar el repositorio

```bash
git clone https://github.com/SalvaIES/payment-gateway-api.git
cd payment-gateway-api
```

### 2.2 Crear el entorno virtual

**Linux:**
```bash
python3 -m venv venv --without-pip
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
```

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python -m venv venv
.\venv\Scripts\activate
```

### 2.3 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2.4 Crear el archivo .env

Crea un archivo `.env` en la raíz del proyecto con este contenido:

```
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Redsys (entorno de pruebas público)
REDSYS_SECRET_KEY=sq7HjrUOBfKmC576ILgskD5srU870gJ7
REDSYS_MERCHANT_CODE=999008881
REDSYS_TERMINAL=1
REDSYS_URL=https://sis-t.redsys.es:25443/sis/realizarPago

# PayPal
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_URL=https://api-m.sandbox.paypal.com
```

### 2.5 Aplicar migraciones

```bash
python manage.py migrate
```

### 2.6 Crear superusuario

```bash
python manage.py createsuperuser
```

### 2.7 Arrancar el servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en: http://127.0.0.1:8000/

---

## 3. Configuración de las pasarelas de pago

### 3.1 Stripe

**Obtener las claves:**
1. Crea una cuenta en https://stripe.com
2. Ve a Developers → API keys → modo Test
3. Copia la **Publishable key** (`pk_test_...`) y la **Secret key** (`sk_test_...`)
4. Añádelas al `.env`

**Configurar el webhook secret para desarrollo:**

Instala la Stripe CLI:

*Linux:*
```bash
curl -s https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public | gpg --dearmor | sudo tee /usr/share/keyrings/stripe.gpg
echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main" | sudo tee /etc/apt/sources.list.d/stripe.list
sudo apt update && sudo apt install stripe
```

*Windows:*
Descarga el instalador desde https://github.com/stripe/stripe-cli/releases/latest

Autentica y arranca el listener:
```bash
stripe login
stripe listen --forward-to http://127.0.0.1:8000/api/webhooks/stripe/
```

El comando mostrará el `whsec_...` — añádelo al `.env` como `STRIPE_WEBHOOK_SECRET`.

**Tarjeta de prueba:**
- Número: `4242 4242 4242 4242`
- Caducidad: `12/34`
- CVC: `123`

---

### 3.2 Redsys

Redsys usa credenciales públicas de prueba — no necesitas cuenta bancaria para desarrollo.

**Credenciales de prueba (ya incluidas en el .env de ejemplo):**
- Secret key: `sq7HjrUOBfKmC576ILgskD5srU870gJ7`
- Merchant code: `999008881`
- Terminal: `1`
- URL: `https://sis-t.redsys.es:25443/sis/realizarPago`

**Configurar ngrok para webhooks:**

Instala ngrok:
```bash
sudo snap install ngrok
```

Crea una cuenta en https://ngrok.com y configura el authtoken:
```bash
ngrok config add-authtoken TU_AUTHTOKEN
```

Arranca el túnel:
```bash
ngrok http 8000
```

Copia la URL pública (ej. `https://xxxx.ngrok-free.dev`) y actualiza estas líneas
en `core/views.py` dentro de la función `redsys_payment`:

```python
DS_MERCHANT_MERCHANTURL='https://xxxx.ngrok-free.dev/api/webhooks/redsys/',
DS_MERCHANT_URLOK='https://xxxx.ngrok-free.dev/transactions/',
DS_MERCHANT_URLKO='https://xxxx.ngrok-free.dev/transactions/',
```

También añade el dominio a `config/settings.py`:
```python
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.ngrok-free.dev']
CSRF_TRUSTED_ORIGINS = ['https://xxxx.ngrok-free.dev']
```

**Tarjeta de prueba:**
- Número: `4548 8120 4940 0004`
- Caducidad: `12/34`
- CVV: `123`
- En el simulador 3DS selecciona: **Autenticación con éxito**

---

### 3.3 PayPal

**Obtener las credenciales:**
1. Accede a https://developer.paypal.com con tu cuenta de PayPal
2. Ve a Apps & Credentials → modo Sandbox
3. Haz click en **Create App**
4. Nombre: cualquiera, Tipo: Merchant
5. Copia el **Client ID** y el **Client Secret**
6. Añádelos al `.env`

**Cuenta de prueba para pagos:**
1. Ve a Testing Tools → Sandbox Accounts
2. Usa la cuenta de tipo **Personal** (comprador) para iniciar sesión en PayPal sandbox

---

## 4. Arranque diario del sistema

Cada vez que arranques el proyecto necesitas tres terminales:

**Terminal 1 — Servidor Django:**
```bash
cd payment-gateway-api
source venv/bin/activate        # Linux
# o .\venv\Scripts\activate     # Windows
python manage.py runserver
```

**Terminal 2 — Stripe CLI (para webhooks de Stripe):**
```bash
stripe listen --forward-to http://127.0.0.1:8000/api/webhooks/stripe/
```

**Terminal 3 — ngrok (solo si vas a probar Redsys):**
```bash
ngrok http 8000
```

> Recuerda: la URL de ngrok cambia cada vez que reinicias. Actualiza `core/views.py`
> y `config/settings.py` con el nuevo dominio.

---

## 5. Uso del frontend

### 5.1 Login

Accede a http://127.0.0.1:8000/ e introduce tus credenciales de superusuario.

### 5.2 Dashboard

Muestra un resumen de:
- Número de proveedores activos
- Total de transacciones
- Transacciones pendientes, completadas y fallidas
- Gráfico doughnut con la distribución por estado

### 5.3 Gestión de proveedores

En http://127.0.0.1:8000/providers/ puedes:
- **Crear** un proveedor con nombre, clave API y entorno
- **Ver** la lista de proveedores con su estado
- **Eliminar** un proveedor (solo si no tiene transacciones asociadas)

Los proveedores reconocidos para pagos automáticos son: `Stripe`, `PayPal`, `Redsys`
(el nombre debe coincidir exactamente).

### 5.4 Gestión de transacciones

En http://127.0.0.1:8000/transactions/ puedes:
- **Crear** una transacción seleccionando proveedor, importe y moneda
- **Pagar** haciendo click en el botón de pago (aparece solo en transacciones pending)
- **Filtrar** por estado y proveedor
- **Ordenar** por importe o fecha haciendo click en la cabecera
- **Editar** el estado e incidencia con el botón del lápiz
- **Eliminar** con el botón de la papelera

### 5.5 Proceso de pago

**Con Stripe:**
1. Crea una transacción con proveedor Stripe
2. Haz click en el botón azul **Pagar**
3. Introduce los datos de tarjeta en el formulario
4. El estado se actualiza automáticamente a `completed` via webhook

**Con Redsys:**
1. Crea una transacción con proveedor Redsys
2. Haz click en el botón amarillo **Pagar**
3. Introduce los datos de tarjeta en el TPV virtual del banco
4. En el simulador 3DS selecciona **Autenticación con éxito**
5. El estado se actualiza automáticamente a `completed` via webhook

**Con PayPal:**
1. Crea una transacción con proveedor PayPal
2. Haz click en el botón azul claro **Pagar**
3. Inicia sesión en PayPal sandbox con la cuenta de comprador
4. Aprueba el pago
5. El estado se actualiza automáticamente a `completed`

---

## 6. Uso de la API REST

### Obtener token

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "tu_contraseña"}'
```

Respuesta: `{"token": "..."}`

### Usar el token

Incluye esta cabecera en todas las peticiones:
```
Authorization: Token TU_TOKEN
```

### Crear un proveedor

```bash
curl -X POST http://127.0.0.1:8000/api/providers/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Stripe", "api_key": "sk_test_...", "environment": "sandbox"}'
```

### Crear una transacción

```bash
curl -X POST http://127.0.0.1:8000/api/transactions/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider": 1, "amount": "99.99", "currency": "EUR", "status": "pending"}'
```

### Filtrar transacciones

```bash
# Por estado
curl "http://127.0.0.1:8000/api/transactions/?status=pending" \
  -H "Authorization: Token TU_TOKEN"

# Por proveedor
curl "http://127.0.0.1:8000/api/transactions/?provider=1" \
  -H "Authorization: Token TU_TOKEN"

# Por fecha
curl "http://127.0.0.1:8000/api/transactions/?date=2026-05-10" \
  -H "Authorization: Token TU_TOKEN"
```

### Marcar una incidencia

```bash
curl -X PUT http://127.0.0.1:8000/api/transactions/1/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider": 1, "amount": "99.99", "currency": "EUR", "status": "failed", "incident_type": "impago"}'
```

---

## 7. Códigos de respuesta de la API

| Código | Significado                                      |
|--------|--------------------------------------------------|
| 200    | Petición correcta                                |
| 201    | Recurso creado correctamente                     |
| 400    | Error de validación en los datos enviados        |
| 401    | Token no proporcionado o inválido                |
| 404    | Recurso no encontrado                            |

---

## 8. Panel de administración Django

Accede a http://127.0.0.1:8000/admin/ con las credenciales de superusuario para
gestionar proveedores, transacciones y usuarios directamente desde el navegador.

---

## 9. Ejecutar los tests

```bash
python manage.py test
```

Resultado esperado: **13 tests passed, 0 errors**