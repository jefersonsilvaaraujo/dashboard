import json

import numpy as np
import pytest

from processamento.exportar_matriz_col9 import extrair


def test_exportacao_respeita_eixos_ano_origem_destino_e_celulas_zero(tmp_path):
    pasta=tmp_path/'municipios'/'2102325'; pasta.mkdir(parents=True)
    p=np.zeros((2,3,3),dtype=np.int64); p[0,0,1]=7; p[1,1,0]=11
    h=p*.087
    np.savez(pasta/'matriz.npz',classes=np.array([3,15,27]),anos=np.array([2001,2002,2003]),
             pixels=p,area_ha=h,tripla_pixels=p//2,tripla_area_ha=h/2)
    (pasta/'concluido.json').write_text(json.dumps({'npz':'matriz.npz'}),encoding='utf-8')
    tabela=extrair(tmp_path,2102325,2001)
    assert len(tabela)==9 and tabela.pixels.sum()==7
    assert tabela.query('classe_origem==3 and classe_destino==15').pixels.iloc[0]==7
    assert tabela.query('classe_origem==15 and classe_destino==3').pixels.iloc[0]==0
    outra=extrair(tmp_path,2102325,2002)
    assert outra.pixels.sum()==11 and outra.ano_destino.eq(2003).all()
    tripla=extrair(tmp_path,2102325,2001,'tripla')
    assert tripla.pixels.sum()==3
    with pytest.raises(ValueError): extrair(tmp_path,2102325,2000)
