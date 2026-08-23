# Correcciones de diseño 01 — Calendario, empleados/ERP y KPIs

Este documento convierte las primeras correcciones funcionales en reglas de diseño obligatorias para CRM v2.

## 1. El CRM no es el calendario

El calendario corporativo/personal de cada usuario está en Outlook / Microsoft 365. El CRM no debe mantener un calendario paralelo ni convertirse en fuente de verdad de agenda.

Reglas:

- Se elimina el calendario propio de la página principal del CRM.
- El CRM puede leer disponibilidad y eventos relevantes de Outlook cuando tenga permisos.
- El CRM puede crear/modificar eventos mediante la API de Microsoft Graph, siempre asociados al empleado responsable.
- Los eventos creados por el CRM/IA deberán usar una categoría/color identificable diferente de los eventos personales o creados manualmente.
- El CRM guarda únicamente la referencia necesaria para trazabilidad: `external_calendar_event_id`, empleado, entidad relacionada, origen, fecha de creación y estado de sincronización.
- El evento completo vive en Outlook. No se replica un segundo calendario de negocio dentro del CRM.

## 2. El responsable de un Lead es una persona real del ERP interno

Cada Lead, Opportunity, Task, Activity, Project y acción automatizada que requiera identidad humana deberá poder tener un empleado responsable.

No basta un `assigned_to_id` sin contexto. La IA debe resolver la identidad operativa desde la ficha del empleado antes de comunicarse o actuar en su nombre.

## 3. ERP interno mínimo: Employees

CRM v2 incorpora un dominio ERP ligero desde el principio. Su primera entidad será `Employee`.

### Employee

Campos mínimos:

- `id`
- `user_id` del sistema de autenticación
- `username`
- `display_name`
- `first_name`
- `last_name`
- `job_title`
- `department`
- `manager_id`
- `email_primary`
- `email_integration`
- `phone`
- `whatsapp_phone`
- `timezone`
- `locale`
- `active`
- `calendar_provider`
- `calendar_account_ref`
- `mail_account_ref`
- `communication_profile_id`
- `created_at`
- `updated_at`

Las credenciales nunca se almacenan en esta tabla. Sólo referencias a un almacén seguro de secretos/conexiones.

## 4. Communication Profile / personalidad operativa

Cada empleado tendrá un perfil de comunicación que la IA deberá consultar antes de redactar o ejecutar comunicaciones en su nombre.

Campos propuestos:

- `employee_id`
- `tone_prompt`: descripción breve del tono habitual
- `preferred_greeting`
- `preferred_closing`
- `forbidden_words`
- `preferred_terms`
- `sentence_style`
- `formality_level`
- `language_preferences`
- `emoji_policy`
- `signature_template`
- `channel_overrides`: email / WhatsApp / LinkedIn / otros
- `examples`: pocos ejemplos cortos aprobados
- `updated_at`

Este perfil no pretende simular psicológicamente al empleado. Es una guía de comunicación operativa para evitar que diez usuarios del CRM parezcan escritos por la misma IA con corbata invisible.

## 5. Flujo obligatorio antes de una comunicación automática

Antes de que la IA envíe o prepare una comunicación:

1. Resolver entidad relacionada (Lead / Contact / Organization / Opportunity).
2. Resolver `owner_employee_id`.
3. Cargar Employee.
4. Resolver canal y cuenta autorizada del empleado.
5. Cargar Communication Profile.
6. Consultar contexto CRM permitido.
7. Generar borrador/acción.
8. Aplicar políticas del canal y permisos.
9. Ejecutar o solicitar aprobación según política.
10. Registrar Activity + audit trail.

## 6. Integración Outlook por empleado

La integración de Microsoft 365 debe ser multiusuario.

Cada empleado podrá tener:

- conexión Outlook/Exchange;
- calendario;
- correo;
- permisos/scopes concedidos;
- estado de conexión;
- última sincronización;
- errores de autenticación;
- categoría/color reservado para acciones CRM.

El Lead/Opportunity no apunta a un calendario. Apunta a un empleado. El empleado determina qué calendario y qué cuenta se utilizan.

## 7. Página principal

Se elimina el bloque "Hoy" usado como calendario.

La portada deberá mostrar información CRM, no una imitación barata de Outlook:

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

Los próximos eventos, si se muestran en algún lugar, serán una vista integrada de Outlook y no un calendario CRM.

## 8. KPIs: CRM como productor de datos, Power BI como capa analítica final

CRM v2 debe exponer datos analíticos completos. Power BI será la herramienta final de reporting y visualización avanzada.

Por tanto:

- Todos los KPIs deben derivarse de datos estructurados, no de contadores incrustados en frontend.
- Deben existir endpoints/exports analíticos documentados.
- Deben poder exportarse como mínimo en JSON y CSV.
- Debe contemplarse OData o vistas SQL/read replica para Power BI si aporta ventaja operacional.
- Cada métrica deberá definir fórmula, granularidad, dimensiones y timestamp de cálculo.

### Catálogo inicial de KPIs

#### Leads
- leads creados
- leads nuevos por periodo
- leads por fuente
- leads por campaña
- leads por responsable
- leads sin asignar
- leads sin atender
- tiempo medio hasta primera acción
- tiempo medio hasta primer contacto
- tasa de contacto
- tasa de respuesta
- tasa de calificación
- tasa de descarte
- tasa de conversión Lead → Opportunity
- tasa de conversión Lead → Organization/Contact
- duplicados detectados
- leads fusionados
- calidad/confianza media de leads automáticos

#### Pipeline / Opportunities
- oportunidades creadas
- oportunidades abiertas
- pipeline bruto
- pipeline ponderado
- valor medio por oportunidad
- oportunidades por etapa
- edad media por etapa
- tiempo medio total de ciclo
- velocidad de pipeline
- conversiones entre etapas
- tasa de win
- tasa de loss
- win/loss por responsable
- win/loss por fuente
- win/loss por producto/servicio
- motivos de pérdida
- oportunidades estancadas
- oportunidades sin próxima acción
- forecast mensual/trimestral
- forecast vs realizado

#### Actividad comercial
- emails enviados
- emails recibidos
- respuestas
- llamadas
- WhatsApps
- reuniones
- tareas creadas/completadas/vencidas
- actividades por empleado
- actividades por Lead/Opportunity
- tiempo entre contactos
- follow-ups realizados en plazo
- follow-ups vencidos
- ratio actividad → reunión
- ratio reunión → propuesta
- ratio propuesta → cierre

#### Ventas / ingresos
- ventas cerradas
- nuevos clientes
- ingresos contratados
- ingreso medio por cliente
- ticket medio
- MRR/ARR cuando proceda
- expansión/up-sell/cross-sell
- renovaciones
- churn
- revenue churn
- retención
- lifetime value cuando haya datos suficientes
- ventas por empleado
- ventas por producto
- ventas por segmento/sector
- ventas por origen
- ventas por geografía

#### Clientes / Organizations
- organizaciones activas
- prospectos
- clientes
- clientes nuevos
- clientes sin actividad X días
- contactos por organización
- cuentas sin contacto principal
- cuentas sin responsable
- cuentas con incidencias
- antigüedad de cliente
- productos/servicios activos por cliente

#### Productividad / Employees
- cartera de leads por empleado
- cartera de oportunidades
- pipeline por empleado
- actividades por empleado
- SLA de primera respuesta
- tasa de seguimiento en plazo
- reuniones obtenidas
- propuestas emitidas
- cierres
- ingresos cerrados
- ciclo medio de venta
- tasa de conversión individual
- carga de tareas
- tareas vencidas

#### Automatización / IA
- acciones generadas por IA
- acciones ejecutadas automáticamente
- acciones que requirieron aprobación
- acciones rechazadas
- borradores editados antes del envío
- tasa de aceptación de borradores
- errores de automatización
- ahorro temporal estimado
- comunicaciones por perfil de empleado
- desviaciones de política
- uso por modelo/agente/versión de prompt

#### Integraciones
- estado por integración
- disponibilidad
- última sincronización correcta
- errores por periodo
- latencia
- registros procesados
- registros rechazados
- reintentos
- desfase de sincronización
- autenticaciones expiradas

#### Calidad de datos
- campos críticos incompletos
- duplicados
- contactos sin email/teléfono
- organizaciones sin dominio/CIF cuando aplique
- registros huérfanos
- inconsistencias de ownership
- tasa de enriquecimiento
- antigüedad de datos

## 9. Modelo analítico para Power BI

Además del modelo transaccional, CRM v2 deberá poder proyectar un modelo analítico tipo estrella:

Dimensiones potenciales:
- `dim_date`
- `dim_employee`
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

No es necesario construir un data warehouse separado en la primera versión. Sí debemos diseñar el modelo transaccional de forma que después no haya que exorcizarlo para poder analizarlo.

## 10. Decisiones fijadas por esta corrección

- Outlook es la fuente de verdad del calendario.
- CRM puede escribir en Outlook por API y marca sus eventos con categoría/color propio.
- La integración de calendario/correo es por empleado.
- Se incorpora ERP mínimo al CRM v2.
- `Employee` es entidad de primer nivel.
- Toda acción de IA en nombre de alguien debe resolver su ficha de empleado.
- Cada empleado tendrá un Communication Profile.
- La portada no contiene calendario CRM.
- CRM produce datos/KPIs; Power BI es la capa final de BI.
- Todos los KPIs relevantes deben ser exportables.
