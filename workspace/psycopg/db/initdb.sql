-- CREATE SCHEMA IF NOT EXISTS d;

-- 1. Polígonos
CREATE TABLE zonas (
    id serial PRIMARY KEY,
    nombre varchar(100),
    descripcion text,
    capacidad integer,
    abierto boolean,
    area double precision,
    geom geometry('POLYGON', 25830)
);

-- 2. Líneas
CREATE TABLE rutas (
    id serial PRIMARY KEY,
    nombre varchar(100),
    dificultad varchar(50),
    desnivel integer,
    abierta boolean,
    longitud double precision,
    geom geometry('LINESTRING', 25830)
);

-- 3. Puntos
CREATE TABLE fuentes (
    id serial PRIMARY KEY,
    nombre varchar(100),
    potable boolean,
    caudal double precision,
    ultima_revision date,
    activa boolean,
    geom geometry('POINT', 25830)
);