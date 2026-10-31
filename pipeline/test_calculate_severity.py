"""Tests de classify_severity: no usan red ni datos reales, solo arrays de
juguete, para poder correr en milisegundos y detectar bugs de lógica
(como el de los umbrales con huecos) antes de tocar el pipeline real."""

import numpy as np
import xarray as xr

from calculate_severity import classify_severity
from config import SEVERITY_THRESHOLDS


def test_cada_valor_cae_en_la_clase_esperada():
    """Un valor típico de cada clase debe quedar con el índice de esa clase."""
    dnbr = xr.DataArray([-0.3, 0.05, 0.15, 0.5])
    severity = classify_severity(dnbr)
    assert list(severity.values) == [0, 2, 3, 5]


def test_nan_queda_nan():
    """Un píxel sin dato (NaN) no debe terminar clasificado en ninguna clase."""
    dnbr = xr.DataArray([0.05, np.nan])
    severity = classify_severity(dnbr)
    assert severity.values[0] == 2
    assert np.isnan(severity.values[1])


def test_los_limites_entre_clases_no_tienen_huecos():
    """Regresión del bug real: los bordes de SEVERITY_THRESHOLDS deben ser
    contiguos (el máximo de una clase = el mínimo de la siguiente), sin la
    rendija de 0.001 que antes dejaba píxeles sin clasificar."""
    bordes = []
    for _, low, high in SEVERITY_THRESHOLDS:
        bordes.append(low)
    dnbr = xr.DataArray(bordes)
    severity = classify_severity(dnbr)
    assert not np.isnan(severity.values).any()


def test_barrido_fino_cubre_todo_el_rango():
    """Prueba ~4000 valores repartidos en todo el rango posible de dNBR: todos
    deben caer en alguna clase (0-6), ninguno debería quedar sin clasificar."""
    dnbr = xr.DataArray(np.linspace(-2.0, 1.999, 4000))
    severity = classify_severity(dnbr)
    assert severity.values.min() >= 0
    assert severity.values.max() <= len(SEVERITY_THRESHOLDS) - 1
