# API Guide - Proyecto Parques

API REST para la gestión de Zonas, Rutas y Fuentes de parques naturales.

**Base URL:** `http://localhost:8000/api/proyecto_parques/`

---

## Tabla de Contenidos

1. [Entidades](#entidades)
2. [Autenticación](#autenticación)
3. [Códigos de Estado HTTP](#códigos-de-estado-http)
4. [Zonas](#zonas)
5. [Rutas](#rutas)
6. [Fuentes](#fuentes)
7. [Ejemplos Completos](#ejemplos-completos)
8. [Restricciones Espaciales](#restricciones-espaciales)

---

## Entidades

| Entidad | Descripción | Geometry |
|---------|-------------|----------|
| **Zonas** | Áreas de conservación (polígonos) | POLYGON |
| **Rutas** | Senderos y caminos (líneas) | LINESTRING |
| ** Fuentes** | Puntos de agua (puntos) | POINT |

**SRID:** 25830 (ETRS89 / UTM zone 30N)

---

## Autenticación

El API está configurado como **público** (sin autenticación requerida).

---

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| `200` | OK - Solicitud exitosa |
| `201` | Created - Recurso creado exitosamente |
| `400` | Bad Request - Datos inválidos o faltan campos obligatorios |
| `404` | Not Found - Recurso no encontrado |
| `500` | Internal Server Error - Error inesperado en el servidor |

---

## Zonas

Gestión de áreas de conservación (polígonos).

### Endpoint

```
/zonas/
```

### Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `nombre` | string | No | Nombre de la zona |
| `descripcion` | string | No | Descripción de la zona |
| `capacidad` | integer | No | Capacidad máxima de visitantes |
| `abierto` | boolean | No | Si la zona está abierta al público |
| `area` | float | No* | Área en m² (se calcula automáticamente desde geom) |
| `geom` | string (WKT) | **Sí** | Geometría POLYGON en formato WKT |

*El campo `area` se calcula automáticamente desde la geometría. Si se envía, será ignorado.

### GET - Listar todas las zonas

```bash
curl -X GET http://localhost:8000/api/proyecto_parques/zonas/
```

**Respuesta exitosa (200):**
```json
{
  "ok": true,
  "message": "2 zona(s) encontrada(s)",
  "data": [
    {
      "id": 1,
      "nombre": "Zona Norte",
      "descripcion": "Área de conservación norte",
      "capacidad": 50,
      "abierto": true,
      "area": 10000.5,
      "geom": "POLYGON((500000 4500000, 500100 4500000, 500100 4500100, 500000 4500100, 500000 4500000))"
    },
    {
      "id": 2,
      "nombre": "Zona Sur",
      "descripcion": "Área de conservación sur",
      "capacidad": 30,
      "abierto": false,
      "area": 7500.0,
      "geom": "POLYGON((500200 4500000, 500300 4500000, 500300 4500100, 500200 4500100, 500200 4500000))"
    }
  ]
}
```

### GET - Obtener zona por ID

```bash
curl -X GET "http://localhost:8000/api/proyecto_parques/zonas/?id=1"
```

**Respuesta exitosa (200):**
```json
{
  "ok": true,
  "message": "1 zona(s) encontrada(s)",
  "data": [
    {
      "id": 1,
      "nombre": "Zona Norte",
      "descripcion": "Área de conservación norte",
      "capacidad": 50,
      "abierto": true,
      "area": 10000.5,
      "geom": "POLYGON((500000 4500000, 500100 4500000, 500100 4500100, 500000 4500100, 500000 4500000))"
    }
  ]
}
```

### POST - Crear zona

```bash
curl -X POST http://localhost:8000/api/proyecto_parques/zonas/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Nueva Zona",
    "descripcion": "Descripción de la nueva zona",
    "capacidad": 100,
    "abierto": true,
    "geom": "POLYGON((500000 4500000, 500200 4500000, 500200 4500200, 500000 4500200, 500000 4500000))"
  }'
```

**Respuesta exitosa (201):**
```json
{
  "ok": true,
  "message": "Zona insertada correctamente con id=3",
  "data": [
    {
      "id": 3,
      "nombre": "Nueva Zona",
      "descripcion": "Descripción de la nueva zona",
      "capacidad": 100,
      "abierto": true,
      "area": 40000.0,
      "geom": "POLYGON((500000 4500000, 500200 4500000, 500200 4500200, 500000 4500200, 500000 4500000))"
    }
  ]
}
```

**Nota:** El campo `area` (40000.0) se calculó automáticamente desde la geometría.

### PUT - Actualizar zona

```bash
curl -X PUT http://localhost:8000/api/proyecto_parques/zonas/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": 3,
    "nombre": "Zona Actualizada",
    "capacidad": 150
  }'
```

**Respuesta exitosa (200):**
```json
{
  "ok": true,
  "message": "Zona con id=3 actualizada correctamente",
  "data": [
    {
      "id": 3,
      "nombre": "Zona Actualizada",
      "descripcion": "Descripción de la nueva zona",
      "capacidad": 150,
      "abierto": true,
      "area": 40000.0,
      "geom": "POLYGON((500000 4500000, 500200 4500000, 500200 4500200, 500000 4500200, 500000 4500000))"
    }
  ]
}
```

### DELETE - Eliminar zona

```bash
curl -X DELETE "http://localhost:8000/api/proyecto_parques/zonas/?id=3"
```

**Respuesta exitosa (200):**
```json
{
  "ok": true,
  "message": "Zona con id=3 eliminada correctamente",
  "data": [
    {
      "id": 3,
      "nombre": "Zona Actualizada",
      "descripcion": "Descripción de la nueva zona",
      "capacidad": 150,
      "abierto": true,
      "area": 40000.0,
      "geom": "POLYGON((500000 4500000, 500200 4500000, 500200 4500200, 500000 4500200, 500000 4500000))"
    }
  ]
}
```

---

## Rutas

Gestión de senderos y caminos (líneas).

### Endpoint

```
/rutas/
```

### Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `nombre` | string | No | Nombre de la ruta |
| `dificultad` | string | No | Dificultad (Fácil, Media, Alta, Extrema) |
| `desnivel` | integer | No | Desnivel en metros |
| `abierta` | boolean | No | Si la ruta está abierta al público |
| `longitud` | float | No* | Longitud en metros (se calcula automáticamente desde geom) |
| `geom` | string (WKT) | **Sí** | Geometría LINESTRING en formato WKT |

*El campo `longitud` se calcula automáticamente desde la geometría. Si se envía, será ignorado.

### GET - Listar todas las rutas

```bash
curl -X GET http://localhost:8000/api/proyecto_parques/rutas/
```

**Respuesta:**
```json
{
  "ok": true,
  "message": "2 ruta(s) encontrada(s)",
  "data": [
    {
      "id": 1,
      "nombre": "Ruta del Bosque",
      "dificultad": "Media",
      "desnivel": 250,
      "abierta": true,
      "longitud": 158.11,
      "geom": "LINESTRING(500000 4500000, 500100 4500100)"
    }
  ]
}
```

### GET - Obtener ruta por ID

```bash
curl -X GET "http://localhost:8000/api/proyecto_parques/rutas/?id=1"
```

### POST - Crear ruta

```bash
curl -X POST http://localhost:8000/api/proyecto_parques/rutas/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Ruta de la Montaña",
    "dificultad": "Alta",
    "desnivel": 500,
    "abierta": true,
    "geom": "LINESTRING(500000 4500000, 500100 4500100, 500200 4500050, 500300 4500200)"
  }'
```

**Respuesta exitosa (201):**
```json
{
  "ok": true,
  "message": "Ruta insertada correctamente con id=2",
  "data": [
    {
      "id": 2,
      "nombre": "Ruta de la Montaña",
      "dificultad": "Alta",
      "desnivel": 500,
      "abierta": true,
      "longitud": 316.23,
      "geom": "LINESTRING(500000 4500000, 500100 4500100, 500200 4500050, 500300 4500200)"
    }
  ]
}
```

**Nota:** El campo `longitud` (316.23 m) se calculó automáticamente desde la geometría.

### PUT - Actualizar ruta

```bash
curl -X PUT http://localhost:8000/api/proyecto_parques/rutas/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": 2,
    "dificultad": "Extrema",
    "abierta": false
  }'
```

### DELETE - Eliminar ruta

```bash
curl -X DELETE "http://localhost:8000/api/proyecto_parques/rutas/?id=2"
```

---

## Fuentes

Gestión de puntos de agua (fuentes).

### Endpoint

```
/fuentes/
```

### Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `nombre` | string | No | Nombre de la fuente |
| `potable` | boolean | No | Si el agua es potable |
| `caudal` | float | No | Caudal en litros por segundo |
| `ultima_revision` | date | No | Fecha de última revisión (YYYY-MM-DD) |
| `activa` | boolean | No | Si la fuente está activa |
| `geom` | string (WKT) | **Sí** | Geometría POINT en formato WKT |

### GET - Listar todas las fuentes

```bash
curl -X GET http://localhost:8000/api/proyecto_parques/fuentes/
```

**Respuesta:**
```json
{
  "ok": true,
  "message": "2 fuente(s) encontrada(s)",
  "data": [
    {
      "id": 1,
      "nombre": "Fuente Principal",
      "potable": true,
      "caudal": 2.5,
      "ultima_revision": "2024-01-15",
      "activa": true,
      "geom": "POINT(500050 4500050)"
    }
  ]
}
```

### GET - Obtener fuente por ID

```bash
curl -X GET "http://localhost:8000/api/proyecto_parques/fuentes/?id=1"
```

### POST - Crear fuente

```bash
curl -X POST http://localhost:8000/api/proyecto_parques/fuentes/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Fuente Nueva",
    "potable": true,
    "caudal": 1.5,
    "ultima_revision": "2024-06-01",
    "activa": true,
    "geom": "POINT(500150 4500150)"
  }'
```

**Respuesta exitosa (201):**
```json
{
  "ok": true,
  "message": "Fuente insertada correctamente con id=3",
  "data": [
    {
      "id": 3,
      "nombre": "Fuente Nueva",
      "potable": true,
      "caudal": 1.5,
      "ultima_revision": "2024-06-01",
      "activa": true,
      "geom": "POINT(500150 4500150)"
    }
  ]
}
```

### PUT - Actualizar fuente

```bash
curl -X PUT http://localhost:8000/api/proyecto_parques/fuentes/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": 3,
    "potable": false,
    "activa": false
  }'
```

### DELETE - Eliminar fuente

```bash
curl -X DELETE "http://localhost:8000/api/proyecto_parques/fuentes/?id=3"
```

---

## Ejemplos Completos

### Ejemplo 1: Crear una zona y verificar que el área se calcula automáticamente

```bash
# 1. Crear zona
curl -X POST http://localhost:8000/api/proyecto_parques/zonas/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Zona de Ejemplo",
    "descripcion": "Una zona de prueba",
    "abierto": true,
    "geom": "POLYGON((0 0, 100 0, 100 100, 0 100, 0 0))"
  }'
```

El `area` se calculará automáticamente: 100m × 100m = 10000 m²

### Ejemplo 2: Crear una ruta y verificar que la longitud se calcula automáticamente

```bash
# Crear ruta
curl -X POST http://localhost:8000/api/proyecto_parques/rutas/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Senderos del Parque",
    "dificultad": "Fácil",
    "desnivel": 50,
    "abierta": true,
    "geom": "LINESTRING(0 0, 0 100, 100 100)"
  }'
```

El `longitud` se calculará automáticamente: 100 + 141.42 = ~241.42 m

### Ejemplo 3: Obtener todas las entidades de un tipo

```bash
# Listar zonas
curl -X GET http://localhost:8000/api/proyecto_parques/zonas/

# Listar rutas
curl -X GET http://localhost:8000/api/proyecto_parques/rutas/

# Listar fuentes
curl -X GET http://localhost:8000/api/proyecto_parques/fuentes/
```

### Ejemplo 4: Actualizar solo algunos campos

```bash
# Actualizar solo el nombre de una zona (sin cambiar geometría)
curl -X PUT http://localhost:8000/api/proyecto_parques/zonas/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "nombre": "Zona Norte Actualizada"
  }'
```

---

## Restricciones Espaciales

El API aplica validaciones espaciales automáticas:

### Zonas

- **ST_SnapToGrid:** Redondea coordenadas a 0.0001 decimal
- **ST_IsValid:** Rechaza geometrías inválidas
- **ST_Intersects:** Rechaza zonas que intersecten con otras existentes

### Rutas

- **ST_SnapToGrid:** Redondea coordenadas a 0.0001 decimal
- **ST_IsValid:** Rechaza geometrías inválidas
- **ST_Intersects:** Rechaza rutas que intersecten con otras existentes

### Fuentes

- **ST_SnapToGrid:** Redondea coordenadas a 0.0001 decimal
- **ST_IsValid:** Rechaza geometrías inválidas
- **ST_Within:** La fuente debe estar dentro de alguna zona existente

### Mensajes de Error Comunes

```json
{
  "ok": false,
  "message": "El punto no está dentro de ninguna zona de conservación (ST_Within = False). Operación rechazada.",
  "data": null
}
```

```json
{
  "ok": false,
  "message": "La geometría intersecta con una zona ya existente (ST_Intersects = True)",
  "data": null
}
```

```json
{
  "ok": false,
  "message": "Geometría inválida tras ST_SnapToGrid (ST_IsValid = False)",
  "data": null
}
```

---

## Formato WKT

Las geometrías se envían y reciben en formato WKT (Well-Known Text):

| Tipo | Ejemplo WKT |
|------|-------------|
| POINT | `POINT(500000 4500000)` |
| LINESTRING | `LINESTRING(500000 4500000, 500100 4500100, 500200 4500050)` |
| POLYGON | `POLYGON((500000 4500000, 500100 4500000, 500100 4500100, 500000 4500100, 500000 4500000))` |

**Nota:** El SRID utilizado es 25830 (ETRS89 / UTM zone 30N), pero el API trabaja internamente con este sistema de coordenadas.

---

## Notas Adicionales

1. **Cálculo automático:** Los campos `area` (Zonas) y `longitud` (Rutas) se calculan automáticamente desde la geometría. Si el usuario envía estos valores, serán ignorados.

2. **Esquema de base de datos:** El API utiliza el esquema `public` de PostgreSQL.

3. **Unidades:**
   - Área: metros cuadrados (m²)
   - Longitud: metros (m)
   - Coordenadas: UTM zone 30N (SRID 25830)

4. **Errores de validación:** Todos los errores incluyen mensajes descriptivos en español.