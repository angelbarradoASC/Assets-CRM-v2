# Correcciones de diseño 01 — Calendario, integración ERP y KPIs

Este documento convierte las primeras correcciones funcionales en reglas de diseño obligatorias para CRM v2.

> **Corrección posterior:** el ERP no forma parte del CRM. Assets tendrá un módulo/web ERP independiente. Véase `docs/05-erp-module-boundary.md`.

## 1. El CRM no es el calendario

El calendario corporativo/personal de cada usuario está en Outlook / Microsoft 365. El CRM no debe mantener un calendario paralelo ni convertirse en fuente de verdad de agenda.

Reglas:

- Se elimina el calendario propio de la página principal del CRM.
- El CRM puede leer disponibilidad y eventos relevantes de Outlook cuando tenga permisos.
- El CRM puede crear/modificar eventos mediante Microsoft Graph, asociados al empleado responsable.
- Los eventos creados por CRM/IA deberán usar una categoría/color identificable diferente de los eventos personales o creados manualmente.
- El CRM guarda sólo referencias de trazabilidad: `external_calendar_event_id`, empleado, entidad relacionada, origen, fecha de creación y estado de sincronización.
- El evento completo vive en Outlook.

## 2. El responsable de un Lead es una persona real gestionada por ERP

Cada Lead, Opportunity, Task, Activity, Project y acción automatizada que requiera identidad humana deberá poder tener un empleado responsable mediante un `employee_id` perteneciente al ERP.

La IA no debe fiarse únicamente de un nombre o usuario guardado en CRM. Antes de comunicarse o actuar en nombre de una persona consulta ERP para obtener sus datos operativos autorizados.

## 3. ERP independiente de CRM

Assets tendrá una aplicación/web ERP independiente. El ERP será el sistema de verdad para empleados, cuentas, activos, facturación y demás datos internos corporativos.

CRM no administra empleados. Mantiene referencias como:

- `owner_employee_id`
- `assigned_employee_id`
- `created_by_employee_id`

Puede conservar una proyección/cache mínima no autoritativa para mostrar nombre, cargo o avatar, pero la fuente de verdad es ERP.

## 4. Perfil de comunicación

El perfil de comunicación de cada empleado vive en ERP porque pertenece a la persona, no al pipeline comercial.

Campos orientativos:

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

CRM consume este perfil cuando necesita generar una comunicación en nombre del empleado.

## 5. Flujo obligatorio antes de una comunicación automática

1. Resolver Lead / Contact / Organization / Opportunity.
2. Resolver `owner_employee_id`.
3. Consultar ERP.
4. Obtener canal y cuenta autorizada del empleado.
5. Obtener perfil de comunicación.
6. Añadir contexto comercial del CRM.
7. Generar borrador/acción.
8. Aplicar políticas y permisos.
9. Ejecutar o solicitar aprobación según política.
10. Registrar Activity + audit trail.

## 6. Outlook por empleado

La integración Microsoft 365 es multiusuario y se resuelve a través del empleado gestionado en ERP.

Relación objetivo:

`CRM entity -> employee_id -> ERP employee -> Microsoft 365 connection -> Outlook`

El Lead/Opportunity no apunta a un calendario. Apunta a una persona responsable.

## 7. Página principal

Se elimina cualquier bloque que funcione como calendario CRM.

La portada deberá mostrar información comercial y operativa:

- KPIs comerciales;
- tareas y acciones vencidas;
- Leads sin atender;
- oportunidades con riesgo;
- follow-ups atrasados;
- pipeline;
- actividad reciente;
- alertas de integración;
- rendimiento por empleado/equipo;
- accesos rápidos.

Si se muestran próximos eventos, serán una vista puntual consumida desde Outlook, nunca un calendario mantenido por CRM.

## 8. KPIs: CRM produce datos; Power BI es la capa final

Todos los KPIs deben derivarse de datos estructurados y ser exportables. Deben existir endpoints/exports analíticos documentados, como mínimo JSON y CSV, y se evaluará OData o vistas SQL/read replica para Power BI.

### Leads
- leads creados y nuevos por periodo
- leads por fuente, campaña y responsable
- leads sin asignar / sin atender
- tiempo hasta primera acción / primer contacto
- tasa de contacto, respuesta, calificación y descarte
- conversión Lead → Opportunity
- conversión Lead → Organization/Contact
- duplicados y fusiones
- calidad/confianza media de leads automáticos

### Pipeline / Opportunities
- oportunidades creadas y abiertas
- pipeline bruto y ponderado
- valor medio
- oportunidades por etapa
- edad media por etapa
- ciclo medio total
- velocidad de pipeline
- conversiones entre etapas
- win rate / loss rate
- win/loss por responsable, fuente y producto
- motivos de pérdida
- oportunidades estancadas
- oportunidades sin próxima acción
- forecast mensual/trimestral
- forecast vs realizado

### Actividad comercial
- emails enviados/recibidos/respuestas
- llamadas
- WhatsApps
- reuniones
- tareas creadas/completadas/vencidas
- actividades por empleado y entidad
- tiempo entre contactos
- follow-ups en plazo / vencidos
- actividad → reunión
- reunión → propuesta
- propuesta → cierre

### Ventas / ingresos
- ventas cerradas
- nuevos clientes
- ingresos contratados
- ingreso medio por cliente
- ticket medio
- MRR/ARR cuando proceda
- up-sell / cross-sell / expansión
- renovaciones
- churn / revenue churn / retención
- lifetime value cuando haya datos suficientes
- ventas por empleado, producto, segmento, origen y geografía

### Clientes / Organizations
- organizaciones activas
- prospectos / clientes / clientes nuevos
- clientes sin actividad X días
- contactos por organización
- cuentas sin contacto principal
- cuentas sin responsable
- cuentas con incidencias
- antigüedad de cliente
- productos/servicios activos por cliente

### Productividad por empleado
- cartera de leads
- cartera de oportunidades
- pipeline
- actividades
- SLA de primera respuesta
- seguimiento en plazo
- reuniones
- propuestas
- cierres
- ingresos cerrados
- ciclo de venta
- tasa de conversión
- carga y vencimiento de tareas

Los datos maestros del empleado provienen de ERP; CRM calcula sus métricas comerciales.

### Automatización / IA
- acciones generadas y ejecutadas automáticamente
- acciones que requirieron aprobación
- acciones rechazadas
- borradores editados
- tasa de aceptación de borradores
- errores de automatización
- ahorro temporal estimado
- comunicaciones por empleado/perfil
- desviaciones de política
- uso por modelo/agente/versión de prompt

### Integraciones
- estado y disponibilidad
- última sincronización correcta
- errores
- latencia
- registros procesados/rechazados
- reintentos
- desfase de sincronización
- autenticaciones expiradas

### Calidad de datos
- campos críticos incompletos
- duplicados
- contactos sin email/teléfono
- organizaciones sin dominio/CIF cuando aplique
- registros huérfanos
- inconsistencias de ownership
- tasa de enriquecimiento
- antigüedad de datos

## 9. Modelo analítico para Power BI

Dimensiones potenciales:

- `dim_date`
- `dim_employee` (proyección de la identidad ERP)
- `dim_organization`
- `dim_contact`
- `dim_source`
- `dim_campaign`
- `dim_product`
- `dim_stage`
- `dim_geography`

Hechos potenciales:

- `fact_leads`
- `fact_opportunities`
- `fact_activities`
- `fact_tasks`
- `fact_sales`
- `fact_pipeline_snapshots`
- `fact_integrations`
- `fact_ai_actions`

No hace falta un data warehouse separado desde la primera versión, pero el modelo transaccional deberá permitir construir estas proyecciones sin una sesión de espiritismo posterior.

## 10. Decisiones fijadas

- Outlook es fuente de verdad de calendario.
- CRM puede escribir en Outlook mediante API y distinguir sus eventos con categoría/color.
- La identidad y conexiones de empleado proceden del ERP.
- ERP es una web/módulo independiente de Assets.
- CRM no administra empleados, activos, cuentas ni facturación ERP.
- El perfil de comunicación vive en ERP.
- CRM consume ERP por API antes de ejecutar acciones en nombre de una persona.
- La portada no contiene calendario CRM.
- CRM produce KPIs y Power BI es la capa final de BI.
- Todos los KPIs relevantes deben ser exportables.
