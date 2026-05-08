from django.contrib.gis.db import models


class Zona(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    capacidad = models.IntegerField(null=True, blank=True)
    abierto = models.BooleanField(null=True, blank=True)
    area = models.FloatField(null=True, blank=True)
    geom = models.PolygonField(srid=25830, null=True, blank=True)

    class Meta:
        db_table = 'd\".\"zonas'
        managed = False


class Ruta(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    dificultad = models.CharField(max_length=50, null=True, blank=True)
    desnivel = models.IntegerField(null=True, blank=True)
    abierta = models.BooleanField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    geom = models.LineStringField(srid=25830, null=True, blank=True)

    class Meta:
        db_table = 'd\".\"rutas'
        managed = False


class Fuente(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    potable = models.BooleanField(null=True, blank=True)
    caudal = models.FloatField(null=True, blank=True)
    ultima_revision = models.DateField(null=True, blank=True)
    activa = models.BooleanField(null=True, blank=True)
    geom = models.PointField(srid=25830, null=True, blank=True)

    class Meta:
        db_table = 'd\".\"fuentes'
        managed = False
