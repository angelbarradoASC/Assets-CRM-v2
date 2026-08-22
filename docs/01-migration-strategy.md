# Estrategia de migración CRM v2

## Objetivo

Crear un clon funcional del CRM actual, aislarlo y evolucionarlo sin modificar el sistema productivo hasta que cada integración haya sido migrada y validada.

## Principios de compatibilidad

1. El CRM legado continúa siendo la fuente de verdad durante la primera etapa.
2. CRM v2 trabaja inicialmente con una copia de datos.
3. Ninguna integración externa cambia de destino hasta ser probada explícitamente.
4. No se eliminan campos o endpoints legacy hasta conocer todos sus consumidores.
5. Los IDs legacy deben conservarse o mapearse mediante referencias estables.
6. Todo cambio de esquema deberá tener estrategia de rollback.

## Fase A — Inventario

Registrar:

- modelos y tablas actuales;
- endpoints;
- autenticación;
- consumidores conocidos;
- jobs, webhooks, scripts y automatizaciones;
- dependencias de GCP, CloudLedger y billing;
- procesos manuales relevantes.

## Fase B — Clon funcional

Copiar al nuevo repositorio la estructura necesaria para ejecutar el CRM de forma aislada:

- backend Django;
- modelos;
- migraciones;
- endpoints CRM/pipeline;
- frontend privado;
- configuración local segura;
- fixtures o proceso de importación de datos.

El clon debe funcionar antes de cualquier refactor estructural.

## Fase C — Copia de datos

La copia de datos debe ser reproducible.

Opciones preferentes:

1. dump/restore de PostgreSQL a una base aislada, o
2. export/import por tablas si necesitamos transformar datos durante la carga.

Nunca se usará la misma base de datos de producción para CRM v2 durante el desarrollo.

## Fase D — Caracterización

Crear pruebas de comportamiento para las funciones existentes más importantes:

- listado de clientes;
- creación y edición;
- pipeline;
- actividades;
- contratos;
- productos;
- facturación;
- expediente;
- autenticación;
- permisos.

El objetivo no es demostrar que el legado está bien diseñado. Es poder saber cuándo hemos roto algo que actualmente funciona.

## Fase E — Limpieza incremental

Orden recomendado:

1. separar configuración e infraestructura del dominio;
2. identificar código muerto;
3. modularizar frontend;
4. separar servicios específicos del núcleo;
5. resolver duplicidad `Company` / `ClientProfile`;
6. introducir capa de compatibilidad para APIs legacy;
7. mejorar autenticación y permisos;
8. añadir Commerce.

## Modelo de cliente durante la transición

No se unificará `Company` y `ClientProfile` mediante una migración destructiva inmediata.

Primero se construirá una representación canónica y una tabla de correspondencias. Sólo después de reconciliar los registros y consumidores podremos retirar estructuras legacy.

## Migración de integraciones

Cada integración tendrá un estado:

- `legacy`
- `dual-run`
- `v2-shadow`
- `v2-primary`
- `legacy-retired`

Durante `dual-run` o `v2-shadow`, se compararán resultados del legado y CRM v2 cuando sea viable.

## Cutover

El cambio definitivo sólo puede producirse cuando:

- los datos estén reconciliados;
- los consumidores estén inventariados;
- las integraciones críticas apunten a v2;
- exista rollback;
- los tests de regresión pasen;
- no queden escrituras exclusivas sobre el CRM antiguo.

## Retirada

El CRM legado pasará primero a modo de sólo lectura y se mantendrá durante un periodo de seguridad antes de su retirada definitiva.
