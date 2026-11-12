"""Executar no ambiente geoespacial; dispensado no ambiente leve do app."""
import pytest
import numpy as np

pytest.importorskip('rasterio')
pytest.importorskip('geopandas')
from processamento.mapas_col9 import aplicar_complemento


def test_complemento_preserva_pixels_classificados_e_so_atua_no_alvo():
    original = np.array([[3,0,0],[0,0,15]],dtype=np.uint8)
    patch = np.array([[4,5,6],[27,9,21]],dtype=np.uint8)
    alvos = np.array([[True,True,False],[True,True,True]])
    novo, n = aplicar_complemento(original,patch,alvos)
    assert novo.tolist() == [[3,5,0],[0,9,15]]
    assert n == 2
    assert original.tolist() == [[3,0,0],[0,0,15]]


def test_complemento_recusa_grades_diferentes():
    with pytest.raises(ValueError):
        aplicar_complemento(np.zeros((2,2)),np.zeros((3,3)),np.ones((2,2),bool))
