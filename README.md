# Assets CRM v2

Clon evolutivo del CRM actual de Assets Consultores.

## Objetivo

Construir una nueva versión del CRM manteniendo la estética y la información existente, pero corrigiendo progresivamente la arquitectura, el modelo de datos y las integraciones sin poner en riesgo el CRM de producción.

El CRM actual continúa siendo el sistema productivo durante la migración.

## Repositorios

- **Origen / producción:** `angelbarradoASC/assets-web-api`
- **CRM v2:** `angelbarradoASC/Assets-CRM-v2`
- **Commerce:** `angelbarradoASC/Norvian-Commerce-Autopilot`

## Principios

1. No modificar el CRM productivo desde este proyecto.
2. Partir de la estructura real existente, no rediseñar todo desde cero.
3. Mantener todas las altas existentes mediante migración de datos.
4. Mantener temporalmente compatibilidad con integraciones actuales.
5. Mejorar el CRM por capas, eliminando deuda técnica y duplicidades de forma controlada.
6. No introducir verticales artificiales ni una nueva taxonomía antes de necesitarlas.
7. Mantener la estética actual como referencia visual.
8. Separar progresivamente el núcleo CRM de integraciones específicas como GCP.
9. Commerce se desarrollará sobre CRM v2, no sobre el CRM legado.
10. Cada integración externa migrará de forma independiente y verificable.

## Estado de partida

El CRM legado utiliza:

- Django + Django REST Framework.
- JWT mediante SimpleJWT.
- PostgreSQL en producción y SQLite como fallback local.
- Frontend HTML/JS/CSS en `frontend/PRIV/`.
- `Company` como entidad central de prospección y pipeline.
- `ClientProfile` como segunda representación de cliente ligada a `django.contrib.auth.User` y servicios/proyectos.
- Vistas CRM, pipeline, billing, expedientes, CloudLedger y GCP dentro de la misma aplicación Django.

Existe una duplicidad conceptual importante entre `Company` y `ClientProfile`. Esta duplicidad debe resolverse en CRM v2 sin perder IDs, relaciones ni compatibilidad con consumidores existentes.

## Estrategia

### Etapa 0 — Baseline

Clonar la estructura funcional relevante del CRM actual y documentar:

- modelos;
- endpoints;
- autenticación;
- navegación;
- integraciones externas;
- esquema de datos;
- dependencias GCP/CloudLedger/billing;
- consumidores conocidos de la API.

### Etapa 1 — Clon funcional

Conseguir que CRM v2 pueda ejecutarse de forma aislada con una copia de los datos actuales.

No se cambia todavía el modelo de datos.

### Etapa 2 — Saneamiento

Eliminar duplicidades, código muerto, dependencias innecesarias y acoplamientos específicos sin romper contratos externos.

### Etapa 3 — Modelo CRM consolidado

Unificar progresivamente la representación de empresa/cliente/contacto y mantener una capa de compatibilidad para las APIs antiguas.

### Etapa 4 — Commerce

Incorporar el dominio Commerce y conectarlo con `Norvian-Commerce-Autopilot`.

### Etapa 5 — Migración de integraciones

Migrar cada consumidor del CRM legado a CRM v2 de forma independiente.

### Etapa 6 — Retirada del legado

El CRM antiguo sólo se retirará cuando ningún sistema dependa de él y los datos hayan sido reconciliados.

## Regla de datos

No se renumerarán ni descartarán registros existentes durante la migración inicial. Si posteriormente cambia el modelo interno, se conservará una tabla de correspondencias para IDs legacy y referencias externas.

## Documentación

- `docs/00-baseline.md`
- `docs/01-migration-strategy.md`
- `docs/02-data-model-audit.md`
- `docs/03-api-compatibility.md`
- `docs/04-integration-inventory.md`
- `docs/05-refactoring-backlog.md`

## Estado

**FASE ACTUAL: baseline y clonación del CRM legado.**
