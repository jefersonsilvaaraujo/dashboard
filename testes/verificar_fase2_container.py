"""Smoke test da imagem do app com código montado somente leitura, sem pytest."""
from pathlib import Path
import sys
import os

PROJETO=Path(os.environ.get('COL9_RAIZ_APP',str(Path(__file__).resolve().parents[1])))
sys.path.insert(0,str(PROJETO))
from streamlit.testing.v1 import AppTest
import dados_col9

pagina=PROJETO/'pages/01_Colecao_9_255.py'
at=AppTest.from_file(str(pagina),default_timeout=120).run()
assert not at.exception and not at.error
assert at.metric[0].value=='255' and len(at.tabs)==5
assert len(at.get('plotly_chart'))>=7
assert dados_col9.carregar_mapas_regionais()['municipios']==255
indicadores=[m.value for m in at.metric][4:]
at.sidebar.multiselect[2].select(15).run()
assert not at.exception and [m.value for m in at.metric][4:]==indicadores
at.sidebar.multiselect[1].select(2102325).run()
assert not at.exception and at.metric[0].value=='1'
at.sidebar.slider[0].set_value((2023,2023)).run()
assert not at.exception and any('pelo menos dois anos' in i.value for i in at.info)
at.sidebar.multiselect[0].set_value([]).run()
assert not at.exception and any('Nenhum registro' in i.value for i in at.info)
print('FASES 1/2 Python 3.12 OK: metodologia, geometrias, imagens verificadas, graficos, filtros, denominador e selecao vazia.')
if os.environ.get('COL9_VERIFICAR_LEGADO')=='1':
    legado=AppTest.from_file(str(PROJETO/'app.py'),default_timeout=180).run()
    assert not legado.exception
    assert len(legado.tabs)==10
    print('LEGADO OK: dez abas executadas sem excecoes na imagem verificada.')
