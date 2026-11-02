"""Helpers para rangos de fecha compatibles con columnas DATE y DATETIME."""
from datetime import date, timedelta


def normalizar(fecha):
    if not fecha:
        return fecha
    return fecha.split("T")[0] if "T" in fecha else fecha


def rango_exclusivo(inicio, fin_inclusive):
    inicio_n = normalizar(inicio)
    fin_n = normalizar(fin_inclusive)
    fin_excl = (date.fromisoformat(fin_n) + timedelta(days=1)).isoformat()
    return inicio_n, fin_excl


def rango_dia(fecha):
    return rango_exclusivo(fecha, fecha)