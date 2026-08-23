# Límite de dominio — ERP de Assets vs CRM v2

## Decisión

El ERP **NO forma parte del CRM**.

Assets tendrá una aplicación/web ERP independiente, con su propio dominio funcional y su propia API. CRM v2 se integra con ese módulo y consume únicamente los datos necesarios para operar.

## ERP: sistema de verdad corporativo

El ERP será dueño de, entre otros:

- empleados y colaboradores;
- usuarios internos y su relación con empleados;
- puestos, departamentos y jerarquía;
- cuentas corporativas;
- cuentas bancarias cuando corresponda;
- facturación;
- compras y gastos;
- proveedores;
- activos físicos y tecnológicos;
- inventario interno;
- licencias y suscripciones;
- centros de coste;
- sociedades / entidades legales;
- contratos laborales/mercantiles cuando proceda;
- teléfonos y números corporativos;
- correos y cuentas de integración;
- referencias a credenciales/conexiones;
- políticas de comunicación por empleado;
- otros datos maestros corporativos.

## CRM: sistema comercial

CRM v2 será dueño de:

- Leads;
- Organizations;
- Contacts;
- Opportunities;
- Activities;
- Tasks comerciales;
- Campaigns;
- Products/Services comerciales;
- relaciones comerciales;
- pipeline;
- seguimiento;
- audit trail comercial;
- métricas CRM.

## Datos de empleado en CRM

CRM no tendrá una tabla maestra de empleados duplicada.

Las entidades comerciales utilizarán referencias como:

- `owner_employee_id`
- `assigned_employee_id`
- `created_by_employee_id`

Estos IDs pertenecen al ERP.

El CRM podrá mantener una **proyección/cache mínima no autoritativa** para rendimiento, por ejemplo:

- `employee_id`
- `display_name`
- `job_title`
- `avatar_url`
- `active`
- `last_synced_at`

La fuente de verdad siempre será ERP.

## Comunicación automática

Antes de que una IA ejecute una comunicación en nombre de una persona:

1. CRM resuelve el `employee_id` responsable.
2. Consulta ERP por API.
3. ERP devuelve los datos operativos autorizados necesarios:
   - nombre;
   - cargo;
   - cuenta de correo autorizada;
   - teléfono/WhatsApp autorizado;
   - timezone/locale;
   - perfil de comunicación;
   - referencias a conexiones Microsoft 365 u otros canales.
4. CRM aporta contexto comercial: Lead, Contact, Organization, Opportunity, histórico permitido.
5. La IA genera la comunicación.
6. Las políticas determinan si se ejecuta o requiere aprobación.
7. El canal correspondiente ejecuta la acción.
8. CRM registra Activity + audit trail.

## Calendario

Outlook sigue siendo la fuente de verdad de agenda.

La relación es:

`CRM entity -> employee_id -> ERP employee -> Microsoft 365 connection -> Outlook calendar`

CRM no almacena un calendario propio.

Puede guardar referencias a eventos creados o relacionados:

- `external_calendar_event_id`
- `employee_id`
- `related_entity_type`
- `related_entity_id`
- `sync_status`

## Perfil de comunicación

El perfil de comunicación vive en ERP porque es una característica del empleado, no de una oportunidad comercial concreta.

Puede incluir:

- tono;
- formalidad;
- saludos/cierres;
- palabras prohibidas;
- términos preferidos;
- estilo de frase;
- idioma;
- política de emojis;
- firma;
- reglas por canal;
- ejemplos breves aprobados.

CRM consume este perfil cuando necesita comunicarse en nombre del empleado.

## Integración CRM ↔ ERP

API objetivo, orientativa:

- `GET /api/v1/employees/{id}`
- `GET /api/v1/employees/{id}/communication-profile`
- `GET /api/v1/employees/{id}/integrations`
- `GET /api/v1/employees?active=true`
- `GET /api/v1/legal-entities`
- `GET /api/v1/products-services` si el catálogo comercial se comparte

La autenticación máquina-a-máquina no debe depender de tokens humanos de larga duración.

## Regla arquitectónica

El CRM **referencia personas internas; no las administra**.

El ERP **administra personas y recursos internos; no administra pipeline comercial**.

Ambos módulos pueden vivir bajo la misma identidad visual y portal Assets, pero mantienen límites de dominio y APIs explícitas.
