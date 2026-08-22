# Leads, categorias e integracion con Nexus

## Objetivo

Redisenar la gestion comercial del CRM v2 conservando los datos existentes y preparando una migracion progresiva desde Nexus y otras integraciones. El CRM actual se mantiene en produccion mientras este modelo se valida en paralelo.

## Hallazgos del legado

### 1. Company esta haciendo demasiadas cosas

En el CRM actual `Company` representa a la vez empresa, lead, prospecto, cliente, pipeline comercial y parte del contexto operativo. Esto simplifica el arranque pero mezcla conceptos que evolucionan de forma distinta.

### 2. ClientProfile duplica otra idea de cliente

Existe una segunda representacion de cliente ligada al usuario Django y a proyectos GCP. No debe seguir siendo un segundo eje del dominio comercial.

### 3. Nexus sincroniza directamente contra Company

La integracion actual de Nexus:

- busca empresas por dominio, email o nombre;
- crea una `Company` si no la encuentra;
- actualiza `pipeline_stage` directamente sobre la empresa;
- guarda el contacto principal en campos de Company;
- crea notas del pipeline;
- representa los tags como notas de texto;
- autentica contra el CRM mediante JWT y credenciales de usuario.

Esto hace que un dato descubierto por Nexus pase demasiado pronto a ser una entidad CRM definitiva.

### 4. Las verticales de Nexus son una taxonomia independiente

Nexus mantiene una tabla propia de `SalesVertical` con:

- slug;
- nombre;
- aliases;
- reglas de scoring;
- configuracion de descubrimiento;
- tags CRM;
- sector CRM.

Por tanto, `vertical` y `sector` no significan lo mismo y no deberian forzarse a compartir una unica enumeracion.

---

# Propuesta de CRM v2

## 1. Separar Empresa, Persona, Lead y Oportunidad

### Organization

Entidad real sobre la que hacemos negocio.

Campos base:

- id
- name
- legal_name
- tax_id
- domains
- organization_type
- website
- phone
- address
- country
- province
- lifecycle_status
- source
- created_at
- updated_at

`Organization` no tiene etapa comercial. Una empresa puede existir aunque no haya ninguna venta activa.

### Contact

Persona asociada a una Organization.

Campos:

- id
- organization_id
- name
- role
- email
- phone
- linkedin
- preferred_channel
- source
- is_primary

Una empresa puede tener varios contactos. Se elimina el absurdo de `contact_name`, `contact_email`, `contact_phone` incrustados como unico contacto de Company.

### Lead

Registro de entrada sin necesidad de que la identidad este completamente resuelta.

Campos propuestos:

- id
- source
- source_ref
- organization_id nullable
- contact_id nullable
- raw_name
- raw_domain
- raw_email
- raw_phone
- status
- qualification_score
- fit_score
- intent_score
- confidence
- category_ids
- tags
- owner
- first_seen_at
- last_seen_at
- converted_at
- discarded_reason

Estados iniciales:

- new
- enriching
- qualified
- unqualified
- duplicate
- converted
- discarded

Un lead descubierto por Nexus entra aqui. No crea automaticamente una Organization definitiva salvo que pase resolucion/deduplicacion.

### Opportunity

Representa una posibilidad comercial concreta.

Una Organization puede tener muchas Opportunities simultaneas.

Campos:

- id
- organization_id
- primary_contact_id
- title
- stage
- value
- probability
- expected_close_date
- product_or_offer
- owner
- source_lead_id
- lost_reason
- won_at
- lost_at

Pipeline recomendado:

- discovery
- qualified
- contacted
- engaged
- meeting
- proposal
- negotiation
- won
- lost
- nurture

Los estados `email_1`, `email_2`, `email_3`, `whatsapp_1` y `phone_1` no son etapas de negocio. Son actividades/cadencias y deben salir del pipeline.

## 2. Activities como historial unico

Crear `Activity` para:

- email
- call
- whatsapp
- meeting
- note
- proposal
- task
- automated_action

Campos importantes:

- organization_id
- contact_id
- lead_id
- opportunity_id
- type
- direction
- status
- occurred_at
- due_at
- source
- external_ref
- body/summary
- metadata

Esto sustituye progresivamente la proliferacion de notas y campos `last_contact`, `next_followup`, `sequence_step`, etc. Esos valores pueden derivarse de actividades o mantenerse temporalmente como compatibilidad.

---

# Categorias: no usar una unica lista de verticales

## Problema

Actualmente el CRM tiene `sector`, Nexus tiene `SalesVertical`, y cada vertical incluye `crm_sector`. Esta traduccion produce casos absurdos como Restaurantes -> sector `otros` o Administracion publica -> `otros`.

## Propuesta

Separar cuatro conceptos.

### A. Industry

Que es la organizacion.

Ejemplos:

- professional_services
- real_estate
- manufacturing
- retail
- hospitality
- healthcare
- legal
- public_sector
- education
- technology
- financial_services
- nonprofit
- other

Debe ser una taxonomia relativamente estable y amplia.

### B. Segment

Subsegmento comercial flexible.

Ejemplos:

- asesoria_fiscal
- gestoria
- inmobiliaria_residencial
- restaurante_independiente
- clinica_dental
- ayuntamiento
- zapateria
- taller_automocion

No lo hardcodearia como choices de Django. Tabla administrable.

### C. Campaign / Target Profile

Define como queremos prospectar, no que es la empresa.

Ejemplos:

- `restaurantes-whatsapp-reservas`
- `asesorias-automatizacion`
- `ayuntamientos-observabilidad`

Aqui debe acabar conceptualmente gran parte de lo que Nexus llama hoy `SalesVertical`.

Una Campaign/TargetProfile puede guardar:

- aliases y expresiones de busqueda;
- reglas de descubrimiento;
- scoring;
- propuesta comercial;
- productos objetivo;
- restricciones geograficas;
- cadencia;
- criterios de exclusion.

### D. Tags

Etiquetas libres y multiples para clasificacion transversal.

Ejemplos:

- whatsapp
- automatizacion
- contacto-pendiente
- alto-potencial
- sin-email
- nexus

Los tags deben ser datos, no notas de texto.

---

# Flujo Nexus -> CRM v2

## Flujo futuro

1. Nexus descubre un Prospect.
2. Nexus envia un `LeadCandidate` al CRM v2.
3. CRM v2 intenta resolver identidad:
   - dominio;
   - CIF/NIF si existe;
   - email corporativo;
   - telefono;
   - nombre normalizado;
   - direccion;
   - fuzzy match solo como apoyo.
4. Si existe Organization, vincula el Lead.
5. Si no existe y la confianza supera el umbral, crea Organization.
6. Si la confianza es insuficiente, mantiene el Lead sin resolver.
7. Los contactos encontrados se guardan como Contact independientes.
8. La campana de Nexus se registra como Campaign/source_ref.
9. La clasificacion de Nexus se traduce a Industry + Segment + Tags, pero no gobierna el modelo del CRM.
10. El pipeline comercial solo se crea cuando aparece una Opportunity real o cuando una regla explicita convierte el lead.

## Compatibilidad temporal

Mientras exista el CRM viejo, CRM v2 debera proporcionar una capa de compatibilidad para las operaciones usadas por Nexus:

- create_company
- find_company_by_domain
- find_company_by_email
- find_company_by_name
- update_company_pipeline
- add_pipeline_note
- add_tag

Internamente esa API legacy puede traducir a las nuevas entidades.

Ejemplo:

`create_company()` legacy -> `resolve/create Organization + create Lead`

`update_company_pipeline()` -> actualiza Opportunity/Lead segun contexto y registra Activity.

`add_pipeline_note()` -> crea Activity(type=note).

`add_tag()` -> crea relacion Tag real.

Esto permite migrar CRM primero y Nexus despues.

---

# Cambios necesarios en Nexus

No modificar todavia. Inventario para una fase posterior.

## 1. Connector

`AssetsCRMConnector` debera consumir una API versionada, por ejemplo `/api/v2/...`, y dejar de conocer los detalles internos del modelo Django.

Tambien debera dejar de pedir un JWT nuevo en cada request. Debe cachear/renovar token o usar credenciales de servicio apropiadas.

## 2. Deduplicacion

Actualmente Nexus descarga el pipeline completo y busca coincidencias en memoria. Esto escala mal y mezcla logica de identidad con el cliente de API.

El CRM v2 debe ofrecer:

- `/organizations/resolve`
- `/leads/resolve`

Nexus envia identificadores y el CRM decide.

## 3. Payload de lead

El payload futuro debe conservar procedencia y evidencia:

- source = nexus
- campaign_id
- prospect_id
- discovery_method
- source_urls
- raw organization/contact data
- vertical/target_profile
- score y confidence de Nexus
- tags sugeridos
- timestamp

CRM v2 no debe aceptar silenciosamente que Nexus decida la identidad definitiva.

## 4. Verticales

Las SalesVertical de Nexus pueden seguir existiendo porque son utiles para discovery y scoring, pero deben convertirse en configuracion de prospeccion, no en el modelo maestro de categorias del CRM.

Nexus debera mapear verticales a IDs administrables del CRM o enviar el slug de origen y dejar que CRM v2 aplique el mapping.

## 5. Inbound email

Nexus no deberia convertir automaticamente cualquier dominio de un remitente entrante en una Organization. Debe enviar un Lead/Interaction candidate con evidencia y dejar que CRM v2 resuelva la identidad.

---

# Migracion de datos existentes

No se eliminan las altas actuales.

Migracion inicial propuesta:

- cada Company actual -> Organization manteniendo `legacy_company_id`;
- contacto incrustado -> Contact primario cuando exista;
- pipeline actual -> Opportunity legacy o Lead legacy segun estado;
- PipelineNote -> Activity;
- `sector` -> Industry/Segment mediante tabla de mapping;
- `represented_by`, `entry_channel`, `lead_source` -> Source/metadata;
- campos de secuencia -> metadata de compatibilidad hasta reconstruir Activities;
- ClientProfile -> relacion de acceso/portal con Organization, no duplicado comercial.

No se reasignan IDs externos sin tabla de equivalencias.

---

# Recomendacion de implementacion

Orden:

1. clonar estructura y datos del CRM actual;
2. crear tablas nuevas sin borrar las viejas;
3. migrar Company -> Organization/Contact;
4. introducir Lead y Activity;
5. introducir Opportunity;
6. crear categorias administrables Industry/Segment/Tag;
7. crear API v2;
8. construir compatibility adapter para API legacy;
9. probar Nexus contra adapter en modo shadow;
10. migrar Nexus a API v2;
11. retirar gradualmente campos y endpoints legacy.

El criterio principal es que la mejora del modelo no obligue a modificar todas las integraciones el mismo dia.
