# CRM v2 — Diseño objetivo completo

## 1. Propósito

Este documento define cómo debería quedar **Assets CRM v2** después de sanear el CRM legado, sin asumir que el modelo actual es correcto por el simple hecho de existir.

El objetivo no es crear un CRM genérico ni otro producto paralelo. Es construir una versión limpia del CRM real de Assets, conservar la estética actual, mantener las altas existentes y ofrecer una base estable para Nexus, Commerce, facturación, proyectos y futuras integraciones.

Este documento es una propuesta. No implica todavía cambios en `assets-web-api` ni en `Nexus-UI`.

---

## 2. Principios de diseño

1. **Una sola representación de empresa/organización.**
2. **Los contactos son entidades propias**, no columnas incrustadas en la empresa.
3. **Un lead no es una empresa.** Un lead representa interés/comercialización alrededor de una organización o persona.
4. **Una oportunidad no es un lead.** Una organización puede generar varias oportunidades a lo largo del tiempo.
5. **Las actividades no son estados del pipeline.** Email, llamada, WhatsApp, reunión o propuesta son actividades.
6. **El pipeline representa madurez comercial**, no pasos de automatización.
7. **Las clasificaciones del CRM no dependen de Nexus.**
8. **No existirán verticales como concepto estructural del CRM.**
9. **Nexus tampoco deberá mantener verticales como dominio funcional permanente.** Sus reglas de búsqueda pasarán a ser perfiles/campañas configurables.
10. **Las integraciones consumen API**, no conocen el esquema interno de base de datos.
11. **Compatibilidad temporal con legado**, pero sin perpetuar el modelo antiguo.
12. **Datos existentes se preservan** y se mantiene trazabilidad `legacy_id`.
13. **Nada específico de GCP pertenece al núcleo CRM.**
14. **Commerce es un dominio adicional**, no una deformación de Sales CRM.
15. **La estética actual se conserva como referencia**, pero el frontend se modulariza.

---

# 3. Modelo funcional objetivo

## 3.1 Organization

Representa una entidad con la que Assets mantiene una relación.

Ejemplos:
- empresa privada;
- ayuntamiento;
- organismo público;
- asociación;
- proveedor;
- partner;
- cliente;
- prospecto.

Campos principales:

- `id`
- `legacy_company_id`
- `name`
- `legal_name`
- `tax_id`
- `domain`
- `extra_domains`
- `organization_type`
- `industry_id`
- `segment_id`
- `status`
- `website`
- `phone`
- `country`
- `province`
- `city`
- `postal_code`
- `address`
- `source_id`
- `owner_id`
- `created_at`
- `updated_at`
- `archived_at`

### Organization status

No debe mezclarse con el pipeline comercial.

Propuesta:

- `prospect`
- `customer`
- `former_customer`
- `partner`
- `supplier`
- `inactive`

Una organización puede ser `prospect` aunque tenga oportunidades en distintos estados.

---

## 3.2 Contact

Persona vinculada a una organización.

Campos:

- `id`
- `organization_id`
- `first_name`
- `last_name`
- `job_title`
- `department`
- `email`
- `phone`
- `mobile`
- `linkedin_url`
- `preferred_channel`
- `is_primary`
- `do_not_contact`
- `source_id`
- `created_at`
- `updated_at`

Una organización puede tener múltiples contactos.

Esto elimina el actual problema de almacenar `contact_name`, `contact_email`, `contact_phone` directamente sobre `Company`.

---

## 3.3 Lead

Representa una entrada comercial aún no suficientemente cualificada.

Puede provenir de:

- Nexus;
- formulario web;
- llamada;
- email;
- referido;
- evento;
- importación;
- alta manual;
- otra integración.

Campos:

- `id`
- `organization_id` nullable
- `contact_id` nullable
- `source_id`
- `campaign_id` nullable
- `status`
- `score`
- `confidence`
- `assigned_to_id`
- `summary`
- `qualification_notes`
- `created_at`
- `qualified_at`
- `rejected_at`
- `converted_opportunity_id` nullable

### Estados de Lead

- `new`
- `reviewing`
- `qualified`
- `unqualified`
- `duplicate`
- `converted`
- `discarded`

Un resultado de Nexus puede existir como Lead sin convertir inmediatamente una empresa detectada en una entidad comercial consolidada.

---

## 3.4 Opportunity

Representa una posibilidad comercial real.

Campos:

- `id`
- `organization_id`
- `primary_contact_id`
- `name`
- `pipeline_stage`
- `probability`
- `estimated_value`
- `currency`
- `expected_close_date`
- `owner_id`
- `source_lead_id`
- `product_or_service_id` nullable
- `lost_reason_id` nullable
- `created_at`
- `closed_at`

### Pipeline propuesto

El pipeline debe ser corto, comprensible y transversal:

1. `discovery`
2. `qualified`
3. `contacted`
4. `engaged`
5. `meeting`
6. `proposal`
7. `negotiation`
8. `won`
9. `lost`
10. `nurture`

Se eliminan del pipeline estados como:

- `email_1`
- `email_2`
- `email_3`
- `whatsapp_1`
- `phone_1`

Esos elementos pasan a Activity/Sequence.

---

## 3.5 Activity

Registro único de interacción o acción.

Tipos:

- `note`
- `email`
- `call`
- `whatsapp`
- `meeting`
- `demo`
- `proposal`
- `task`
- `system_event`

Campos:

- `id`
- `organization_id`
- `contact_id` nullable
- `lead_id` nullable
- `opportunity_id` nullable
- `activity_type`
- `direction` (`inbound`, `outbound`, `internal`)
- `subject`
- `content`
- `status`
- `occurred_at`
- `due_at`
- `completed_at`
- `created_by_id`
- `source_system`
- `external_id`

Todo lo que hoy termina convertido en nota genérica debe convertirse en Activity estructurada.

---

## 3.6 Task

Tarea de trabajo explícita.

- `id`
- `organization_id` nullable
- `contact_id` nullable
- `opportunity_id` nullable
- `project_id` nullable
- `title`
- `description`
- `priority`
- `status`
- `assigned_to_id`
- `due_at`
- `source_system`

Puede convivir con Activity: una Task pendiente genera Activity al completarse.

---

# 4. Clasificación: sustituir verticales

## 4.1 Industry

Clasificación amplia y relativamente estable.

Ejemplos:

- Public Sector
- Professional Services
- Healthcare
- Retail
- Hospitality
- Real Estate
- Manufacturing
- Education
- Technology
- Financial Services
- Other

No debe crecer con cada campaña comercial.

## 4.2 Segment

Subclasificación más concreta y administrable.

Ejemplos:

- Ayuntamiento
- Diputación
- Asesoría fiscal
- Gestoría laboral
- Clínica dental
- Clínica privada
- Agencia inmobiliaria
- Restaurante
- Hotel
- Taller
- Comercio minorista

`Segment` pertenece al CRM y es opcional.

## 4.3 Tags

Sistema real de etiquetas N:N.

Ejemplos:

- `nis2`
- `finops`
- `automatizacion`
- `whatsapp`
- `alto-potencial`
- `contacto-pendiente`
- `sector-publico`
- `zaragoza`
- `nexus`

Nunca se guardan como notas de texto.

## 4.4 Campaign

La campaña define el contexto comercial temporal.

Ejemplos:

- “Asesorías Zaragoza — WhatsApp automation — Q4 2026”
- “Ayuntamientos 20k–100k habitantes — NIS2”
- “Clínicas dentales — automatización recepción”

La campaña contiene:

- objetivo;
- criterios de búsqueda;
- propuesta de valor;
- mensaje;
- scoring;
- geografía;
- producto/servicio;
- cadencia.

Esto reemplaza el concepto de vertical usado actualmente en Nexus.

---

# 5. Qué cambiar en Nexus

Nexus deberá dejar de tener `SalesVertical` como dominio estructural.

Actualmente una vertical mezcla:

- sector;
- aliases;
- queries de descubrimiento;
- scoring;
- señales;
- tags CRM;
- mapping a `crm_sector`.

Esto se divide en componentes independientes.

## 5.1 Search Profile

Define únicamente cómo descubrir candidatos.

Campos conceptuales:

- `name`
- `search_terms`
- `aliases`
- `geography`
- `sources`
- `inclusion_rules`
- `exclusion_rules`
- `link_hints`
- `discovery_queries`

## 5.2 Scoring Profile

Define cómo puntuar un candidato.

- señales positivas;
- señales negativas;
- pesos;
- umbral de aceptación;
- confianza mínima.

## 5.3 Campaign

Une:

`SearchProfile + ScoringProfile + oferta + mensajes + cadencia + destino CRM`.

Nexus deja de preguntarse “¿qué vertical es esto?” y pasa a ejecutar campañas/configuraciones.

## 5.4 Integración CRM de Nexus

Flujo objetivo:

`Prospect discovered`
→ `LeadCandidate`
→ deduplicación
→ `Lead`
→ asociación opcional a `Organization` y `Contact`
→ cualificación
→ creación de `Opportunity` si procede.

No:

`resultado scraping → create_company()`.

---

# 6. Deduplicación

La deduplicación debe convertirse en servicio explícito.

Orden recomendado de señales:

1. CIF/NIF exacto.
2. Dominio exacto.
3. Email exacto de contacto.
4. Teléfono normalizado.
5. Nombre legal normalizado + localidad.
6. Similaridad de nombre con evidencia secundaria.

Resultados:

- `exact_match`
- `probable_match`
- `new_entity`
- `manual_review`

Nunca fusionar automáticamente sólo por parecido de nombre.

---

# 7. Sources y procedencia

Crear `Source` / `SourceReference` para saber de dónde procede cada dato.

Ejemplos:

- Nexus
- Web form
- Manual
- Gmail
- LinkedIn
- Import CSV
- Google Places
- Public registry

Debe poderse saber:

- quién creó el dato;
- cuándo;
- sistema externo;
- external ID;
- campaña;
- evidencia original cuando proceda.

---

# 8. Productos y servicios

Eliminar booleanos tipo:

- `service_finops`
- `service_cloud`
- `service_security`
- etc.

Sustituir por catálogo N:N.

## ServiceOffering

- `id`
- `code`
- `name`
- `description`
- `active`

Relaciones:

- Organization ↔ ServiceOffering
- Opportunity ↔ ServiceOffering
- Contract ↔ ServiceOffering

Así añadir un producto nuevo no requiere modificar el modelo Django.

---

# 9. Contracts

Entidad contractual independiente:

- organización;
- servicios/productos;
- fecha inicio;
- fecha fin;
- renovación;
- importe;
- moneda;
- estado;
- documentación;
- responsable.

No debe depender de GCP ni de un proyecto concreto.

---

# 10. Billing

Facturación como módulo desacoplado del CRM comercial.

El CRM sólo necesita conocer:

- contrato;
- importe;
- estado de factura;
- fechas;
- cliente;
- referencias al sistema financiero.

Si `omni-facturacion` termina siendo el sistema contable real, CRM v2 debe integrarse vía API, no duplicar toda la lógica fiscal.

---

# 11. Projects

Un Project representa trabajo entregable a cliente.

No existe `GCPProject` en el core.

Modelo genérico:

- `id`
- `organization_id`
- `name`
- `description`
- `status`
- `owner_id`
- `start_date`
- `end_date`
- `budget`
- `external_system`
- `external_id`

Los proyectos GCP pasan a integración especializada de Cloud/FinOps.

---

# 12. Integraciones especializadas

## CloudLedger

Se conecta a Organization/Project por referencias externas.

## GCP Billing

Deja de modelar clientes del CRM.

Se convierte en integración de servicio/proyecto.

## Nexus

Productor de Leads, Activities y Campaign data.

## Commerce

Dominio independiente conectado al shell común del CRM.

## Gmail / correo

Correo entrante/saliente debe generar Activity y enlazar por identidad/contacto.

---

# 13. Commerce dentro del CRM v2

Commerce aparece como módulo en la misma navegación y sistema de autenticación.

No mezcla sus compradores con Sales CRM.

Entidades principales:

- MarketplaceAccount
- MarketplaceCustomer
- MarketplaceIdentity
- Product
- InventoryUnit
- Purchase
- Listing
- Sale
- Return
- MarketplaceFee
- Opportunity
- Decision
- Evidence
- Portfolio

Una Organization comercial de Assets y un MarketplaceCustomer son conceptos diferentes.

---

# 14. Frontend objetivo

Conservar:

- estética oscura actual;
- sidebar;
- tipografías/identidad;
- tarjetas;
- distribución general.

Corregir:

- HTML monolítico;
- CSS duplicado;
- lógica JS incrustada;
- menús hardcodeados;
- vistas enormes;
- estados dispersos.

## Navegación propuesta

### Inicio

Dashboard personal con:

- tareas pendientes;
- próximas acciones;
- oportunidades activas;
- leads nuevos;
- actividad reciente;
- alertas de integración.

### Organizaciones

Listado maestro de empresas/organismos.

### Leads

Bandeja de entrada comercial.

### Oportunidades

Pipeline Kanban + tabla.

### Contactos

Directorio de personas.

### Actividad

Timeline global y por entidad.

### Campañas

Campañas manuales y procedentes de Nexus.

### Proyectos

Trabajo activo con clientes.

### Contratos

Relación contractual.

### Facturación

Vista integrada, aunque la fuente real pueda estar en otro servicio.

### Commerce

Módulo Norvian Commerce.

### Administración

Usuarios, permisos, catálogos, segmentos, tags, integraciones y configuraciones.

---

# 15. Vista de Organization

La ficha de organización debe ser el centro de contexto.

Cabecera:

- nombre;
- estado;
- sector;
- segmento;
- responsable;
- tags.

Pestañas:

1. Resumen
2. Contactos
3. Oportunidades
4. Actividad
5. Proyectos
6. Contratos
7. Facturación
8. Documentos
9. Integraciones

No mezclar pipeline y ficha maestra.

---

# 16. Vista Leads

Debe comportarse como una bandeja de trabajo.

Columnas/filtros:

- fecha;
- origen;
- campaña;
- organización detectada;
- contacto;
- score;
- confianza;
- estado;
- responsable;
- próxima acción.

Acciones rápidas:

- cualificar;
- descartar;
- marcar duplicado;
- asociar organización existente;
- crear organización;
- crear contacto;
- convertir en oportunidad.

Esto encaja mucho mejor con Nexus que crear Company directamente.

---

# 17. Vista Opportunities

Kanban por `pipeline_stage`.

La oportunidad muestra:

- organización;
- contacto principal;
- servicio ofertado;
- valor;
- probabilidad;
- última actividad;
- próxima acción;
- antigüedad en fase.

Debe existir alerta de oportunidades estancadas.

---

# 18. Cadencias y automatización

Separar `Sequence` de pipeline.

Ejemplo de secuencia:

1. email inicial
2. esperar 4 días
3. follow-up
4. esperar 5 días
5. llamada
6. esperar 7 días
7. cierre/nurture

La secuencia genera Activities/Tasks.

Nunca cambia el pipeline a `email_2` porque se haya enviado el segundo email.

---

# 19. Permisos

Pasar de sólo `is_staff/is_superuser` a permisos explícitos.

Ejemplo:

- `crm.view_organization`
- `crm.edit_organization`
- `crm.view_leads`
- `crm.manage_leads`
- `crm.view_financials`
- `crm.manage_campaigns`
- `commerce.view`
- `commerce.execute`
- `admin.manage_integrations`

Roles pueden agrupar permisos, pero la autorización debe comprobar permisos.

---

# 20. Autenticación

Mantener Django auth durante la primera versión para no añadir riesgo innecesario.

Mejoras:

- access token corto;
- refresh token razonable;
- tokens de servicio diferenciados de login humano;
- scopes/permissions;
- revocación;
- auditoría;
- secreto por integración.

Eliminar JWT humanos de 10 años.

---

# 21. API v2

Crear API nueva versionada.

Ejemplos:

- `/api/v2/organizations/`
- `/api/v2/contacts/`
- `/api/v2/leads/`
- `/api/v2/opportunities/`
- `/api/v2/activities/`
- `/api/v2/tasks/`
- `/api/v2/campaigns/`
- `/api/v2/projects/`
- `/api/v2/contracts/`
- `/api/v2/integrations/`

La API antigua puede vivir temporalmente como adapter.

---

# 22. Capa de compatibilidad legacy

Mientras Nexus y otras máquinas sigan usando API v1:

`POST /api/admin/companies/`

puede traducirse internamente a:

- Organization
- Contact opcional
- Lead opcional

`PATCH /api/pipeline/{id}/`

puede traducirse a Lead/Opportunity según la tabla de mapeo.

`POST /api/pipeline/{id}/notes/`

crea Activity.

Esto permite migrar consumidor por consumidor.

---

# 23. Auditoría

Crear `AuditEvent`.

Registrar:

- actor;
- acción;
- entidad;
- cambios;
- timestamp;
- IP/origen cuando proceda;
- integration ID;
- request correlation ID.

Debe ser posible reconstruir quién cambió una oportunidad o quién creó un lead.

---

# 24. Integraciones

Crear catálogo `Integration`:

- name
- type
- status
- last_success_at
- last_error_at
- credential_ref
- endpoint
- capabilities

Vista de salud de integraciones dentro del CRM.

Así dejamos de enterarnos de que algo dependía del CRM cuando deja de funcionar, tradición informática muy asentada pero poco recomendable.

---

# 25. Datos existentes

La migración debe conservar todo.

Primera conversión propuesta:

### Company

→ Organization

Guardar:

- `legacy_company_id`
- todos los campos originales relevantes.

### contact_name/contact_email/contact_phone

→ Contact primario.

### pipeline_stage

Mapear temporalmente:

- `new`, `investigacion` → Lead `new/reviewing`
- `qualifying` → Opportunity `qualified`
- `email_1`, `email_2`, `email_3`, `whatsapp_1`, `phone_1` → Opportunity `contacted` + Activities reconstruidas cuando haya evidencia
- `responded`, `contacted` → `engaged`
- `meeting` → `meeting`
- `proposal` → `proposal`
- `negotiation` → `negotiation`
- `won` → `won`
- `lost`, `depleted` → `lost` o Lead descartado según contexto
- `nurture` → `nurture`

No inventar Activity histórica cuando no existe evidencia de que realmente se envió el correo o se hizo la llamada.

### ClientProfile

Debe reconciliarse con Organization en una segunda pasada.

Los usuarios Django continúan siendo identidades de acceso, no entidades cliente.

---

# 26. Elementos a eliminar progresivamente

- dualidad `Company` / `ClientProfile`;
- GCP como parte del core del cliente;
- service booleans;
- pipeline basado en emails;
- tags escritos como notas;
- verticales de Nexus;
- menús hardcodeados;
- frontend HTML monolítico;
- JWT humano de larga duración;
- lógica específica de integración repartida por vistas;
- consultas de deduplicación descargando todo el pipeline y recorriéndolo en memoria.

---

# 27. Qué conservar del CRM actual

- estética visual;
- conocimiento funcional acumulado;
- altas existentes;
- actividades/notas existentes;
- contratos/facturas que ya tengan valor;
- IDs legacy;
- integraciones funcionando hasta que tengan sustituto;
- autenticación Django durante la transición;
- patrones de navegación que sean cómodos.

---

# 28. Estrategia de implementación

## Paso A — Clon funcional

Copiar el CRM actual a v2 y levantarlo aislado.

## Paso B — Snapshot de datos

Importar copia de la base de producción y comprobar recuentos/relaciones.

## Paso C — Modelo nuevo en paralelo

Crear tablas nuevas sin eliminar las legacy.

## Paso D — Migrador repetible

Construir migración idempotente legacy → v2.

## Paso E — UI nueva sobre modelo nuevo

Manteniendo estética.

## Paso F — Compatibilidad API v1

Adapters sobre el modelo nuevo.

## Paso G — Nexus

Eliminar verticales y migrar Nexus a:

- Campaign
- SearchProfile
- ScoringProfile
- Leads API v2

## Paso H — otras integraciones

Migrarlas una por una.

## Paso I — Commerce

Integrar Norvian Commerce cuando el núcleo CRM v2 esté estable.

## Paso J — retirada legacy

Sólo después de reconciliación y cero consumidores de v1.

---

# 29. Resultado objetivo

CRM v2 debe terminar siendo un sistema donde:

- una empresa existe una sola vez;
- puede tener muchos contactos;
- puede recibir muchos leads;
- puede tener varias oportunidades;
- emails/llamadas/reuniones son actividades;
- Nexus alimenta Leads y Campaigns, no crea clientes arbitrariamente;
- no existen verticales estructurales;
- las categorías son Industry + Segment + Tags;
- GCP/CloudLedger/Commerce/Nexus son integraciones o dominios conectados;
- los datos antiguos siguen trazables;
- cualquier consumidor antiguo puede migrarse sin big bang.

Este es el diseño de referencia a revisar antes de comenzar el refactor real.