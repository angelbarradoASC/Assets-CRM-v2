# Baseline del CRM legado

## Fuente

Repositorio productivo: `angelbarradoASC/assets-web-api`

Este documento describe el punto de partida. No implica cambios sobre producción.

## Arquitectura observada

### Backend

- Django.
- Django REST Framework.
- SimpleJWT.
- PostgreSQL en producción.
- SQLite como fallback local.
- Aplicación principal `api`.
- Aplicación específica `gcp_billing`.

### Frontend

- HTML, CSS y JavaScript servido desde `frontend/PRIV/`.
- Pantalla principal de CRM: `frontend/PRIV/clientes.html`.
- `frontend/PRIV/crm.html` redirige a `clientes.html`.
- Diseño visual oscuro con sidebar, topbar, panel de empresas y panel de detalle.

## Núcleo funcional observado

### Company

`Company` representa empresa/lead y contiene:

- identidad de empresa;
- estado prospect/active/churned;
- pipeline comercial;
- datos de contacto;
- marca representada;
- sector;
- canal de entrada;
- seguimiento;
- secuencias comerciales;
- servicios contratados;
- relación con consultor;
- CloudLedger tenant slug.

Actualmente es la entidad central más cercana a un CRM real.

### ClientProfile

Existe además `ClientProfile`, ligado a `django.contrib.auth.User`, usado para clientes autenticados y servicios/proyectos.

Esto genera una bifurcación conceptual: una misma noción de cliente puede terminar representada como `Company`, `User`, `ClientProfile` y, en algunos casos, proyectos asociados.

### GCPProject

Los endpoints CRM tradicionales incluyen gestión de proyectos GCP directamente dentro del flujo de cliente.

Esta dependencia específica no debería formar parte del núcleo conceptual de CRM v2.

## APIs observadas

- `/api/crm/clientes/`
- `/api/crm/clientes/<user_id>/`
- `/api/crm/clientes/<user_id>/proyectos/`
- `/api/crm/proyectos/<project_id>/`
- `/api/admin/companies/`
- `/api/pipeline/`
- endpoints de billing, intake, CloudLedger y administración.

## Autenticación

- JWT con SimpleJWT.
- Endpoints de token y refresh.
- Roles derivados de `User.is_staff` y `User.is_superuser`.

### Riesgo detectado

Los tokens JWT tienen una vida configurada de 3650 días. CRM v2 debe revisar este diseño antes de convertirse en sistema principal.

## Frontend CRM

`clientes.html` contiene actualmente una gran cantidad de responsabilidades:

- navegación;
- filtros;
- alta de cliente;
- edición;
- pipeline;
- actividades;
- contratos;
- productos;
- facturación;
- expediente;
- llamadas a API;
- renderizado y estado UI.

Mantendremos inicialmente su estética, pero su estructura deberá modularizarse progresivamente.

## Regla de migración

El primer clon funcional debe preservar el comportamiento y datos antes de refactorizar. No se hará una migración destructiva ni se eliminarán modelos hasta disponer de equivalencias verificadas.
