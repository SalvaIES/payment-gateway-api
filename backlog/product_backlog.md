# Product Backlog — Payment Gateway API

## Épicas y User Stories

---

### Épica 1: Gestión de proveedores

| ID  | User Story                                                                 | Prioridad | Estimación |
|-----|----------------------------------------------------------------------------|-----------|------------|
| US1 | Como admin, quiero registrar un proveedor con su clave API y entorno       | Alta      | 3 pts      |
| US2 | Como admin, quiero listar todos los proveedores activos                    | Alta      | 1 pt       |
| US3 | Como admin, quiero editar los parámetros de un proveedor existente         | Media     | 2 pts      |
| US4 | Como admin, quiero desactivar un proveedor sin eliminarlo                  | Media     | 2 pts      |

---

### Épica 2: Registro de transacciones

| ID  | User Story                                                                 | Prioridad | Estimación |
|-----|----------------------------------------------------------------------------|-----------|------------|
| US5 | Como sistema, quiero crear un registro de pago con importe, moneda y estado inicial | Alta | 3 pts |
| US6 | Como admin, quiero consultar el detalle de una transacción específica      | Alta      | 1 pt       |
| US7 | Como admin, quiero listar todas las transacciones con filtros por proveedor, fecha y estado | Alta | 3 pts |

---

### Épica 3: Gestión de incidencias

| ID  | User Story                                                                 | Prioridad | Estimación |
|-----|----------------------------------------------------------------------------|-----------|------------|
| US8 | Como admin, quiero actualizar el estado de una transacción a "failed"      | Alta      | 2 pts      |
| US9 | Como admin, quiero marcar el tipo de incidencia (impago, error, devolución)| Alta      | 2 pts      |

---

### Épica 4: Seguridad y autenticación

| ID   | User Story                                                                 | Prioridad | Estimación |
|------|----------------------------------------------------------------------------|-----------|------------|
| US10 | Como usuario, quiero autenticarme con usuario y contraseña para obtener un token | Alta | 3 pts |
| US11 | Como sistema, quiero que todos los endpoints estén protegidos por token    | Alta      | 2 pts      |

---

## Sprint Planning

| Sprint (semana) | User Stories incluidas        | Hito correspondiente |
|-----------------|-------------------------------|----------------------|
| Semana 1        | —                             | Hito 1: ERD + backlog|
| Semana 2        | US1, US2, US5, US10, US11     | Hito 2: Modelos base |
| Semana 3        | US3, US4, US6, US7, US8, US9  | Hito 3: Lógica completa |
| Semana 4        | Pruebas, docs, refactor       | Hito 4: Entrega final |