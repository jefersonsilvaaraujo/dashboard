"""Triagem de QA do footprint inteiro, incluindo bordas fora da referência."""
import sys
from pathlib import Path

import numpy as np
import pytest

rasterio=pytest.importorskip('rasterio'); pytest.importorskip('PIL')
from rasterio.io import MemoryFile
from affine import Affine

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.referencias_piloto_col9 import qualidade_footprint,validar_ano


def test_ano_2024_nao_pode_ser_consultado():
    validar_ano(1985); validar_ano(2023)
    with pytest.raises(ValueError): validar_ano(2024)


def test_qa_no_centro_nao_basta_quando_outro_pixel_do_footprint_e_ruim():
    with MemoryFile() as m:
        a=np.full((4,4),4,dtype='uint8'); a[1,1]=9
        with m.open(driver='GTiff',height=4,width=4,count=1,dtype='uint8',crs=4326,
                    transform=Affine(1,0,0,0,-1,4)) as s: s.write(a,1)
        item={'assets':{'scl':{'href':m.name}}}
        q=qualidade_footprint(item,[(.1,3.9),(2.9,3.9),(2.9,1.1),(.1,1.1)],False)
        assert 0<q['fracao_QA_adequada_footprint']<1


def test_boundless_qa_zero_nao_vira_observacao_landsat_clara():
    with MemoryFile() as m:
        with m.open(driver='GTiff',height=2,width=2,count=1,dtype='uint16',crs=4326,
                    transform=Affine(1,0,0,0,-1,2)) as s: s.write(np.full((2,2),64,dtype='uint16'),1)
        item={'assets':{'qa_pixel':{'href':m.name}}}
        q=qualidade_footprint(item,[(-.5,1.9),(1.5,1.9),(1.5,.1),(-.5,.1)],True)
        assert q['fracao_QA_adequada_footprint']<1
