"""Pranchas finais com legendas explícitas; somente predições já fixadas."""
import argparse
import json
from pathlib import Path
import sys

import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import pandas as pd

PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJETO))
from modelagem.protocolo_experimentos_col9_v4 import carregar_manifesto, gravar_json
from modelagem.interpretar_regressao_col9_v4 import escolher_tabela, salvar_figura
from processamento.cenarios_validacao_col9 import sha


def executar(raiz):
    carregar_manifesto(raiz)
    resultado = raiz/'teste/RESULTADOS_IMUTAVEIS_TESTE.parquet'
    registro = json.loads((raiz/'TESTE_CONCLUIDO.json').read_text(encoding='utf-8'))
    assert sha(resultado) == registro['artefatos_sha256'][resultado.name]
    dados = pd.read_parquet(resultado)
    winners = json.loads((raiz/'VENCEDORES_PELA_VALIDACAO.json').read_text(encoding='utf-8'))
    mf = json.loads((PROJETO/'referencias/manifesto_rasters_transicoes_col9.json').read_text(encoding='utf-8'))
    gpkg = Path(mf['base_dados'])/mf['territorio']['arquivo']
    assert sha(gpkg) == mf['territorio']['sha256']
    geo = gpd.read_file(gpkg).to_crs(5880)
    geo.CD_MUN = geo.CD_MUN.astype(str)
    saida = raiz/'apresentacao/figuras_publicacao'
    saida.mkdir()
    plt.rcParams.update({'font.size':10, 'axes.titlesize':11})
    for target, rotulo, unidade in [('R_pct', 'Taxa de conversão mapeada', 'pontos percentuais'), ('C_ha', 'Área de conversão mapeada', 'hectares')]:
        w = next(x for x in winners if x['coorte']=='principal' and x['contexto']=='temporal' and x['target']==target and x['categoria']=='supervisionado')
        a = escolher_tabela(dados, w)
        fig, ax = plt.subplots(figsize=(7,6), layout='constrained')
        pontos = ax.scatter(a.observado, a.previsto, s=13, alpha=.6, c=a.ano_t, cmap=plt.get_cmap('viridis',4), norm=BoundaryNorm([2018.5,2019.5,2020.5,2021.5,2022.5],4))
        limite = max(a.observado.max(), a.previsto.max())
        inicio = min(0,a.previsto.min())
        ax.plot([inicio,limite],[inicio,limite],'k--',lw=1)
        ax.set(xlabel=f'Observado ({unidade})', ylabel=f'Previsto ({unidade})', title=f'{rotulo}\n{w["bloco"]}/{w["algoritmo"]}: escolhido na validação')
        fig.colorbar(pontos, ax=ax, ticks=[2019,2020,2021,2022], label='Ano t: resposta em t+1', shrink=.75)
        salvar_figura(fig, saida/f'observado_previsto_{target}.png')
        imp = pd.read_csv(raiz/'interpretacao_pre_teste/IMPORTANCIAS_VALIDACAO.csv',sep=';')
        imp = imp[imp.target.eq(target)&~imp.variavel_ou_grupo.str.startswith('GRUPO_')].sort_values('mean').tail(15)
        fig,ax = plt.subplots(figsize=(10,5.5),layout='constrained')
        ax.barh(imp.variavel_ou_grupo, imp['mean'], xerr=imp['std'], color='#4c78a8')
        ax.axvline(0,color='black',lw=.7)
        ax.set(xlabel=f'Incremento de MAE na validação ({unidade})',title='Importância por permutação de trajetórias municipais dentro da UF\nBarras: desvio padrão de cinco permutações; não são intervalos de confiança')
        salvar_figura(fig,saida/f'importancias_validacao_{target}.png')
        municipal = a.groupby('CD_MUN')[['observado','previsto','erro']].mean().reset_index()
        mapa = geo.merge(municipal,on='CD_MUN',validate='one_to_one')
        fig,axs = plt.subplots(1,3,figsize=(16,5),layout='constrained')
        inferior = min(municipal.observado.min(),municipal.previsto.min())
        superior = max(municipal.observado.max(),municipal.previsto.max())
        for coluna,ax,titulo in zip(['observado','previsto'],axs[:2],['Observado no mapa','Previsto pelo modelo']):
            mapa.plot(column=coluna,ax=ax,legend=True,cmap='YlGnBu',vmin=inferior,vmax=superior,linewidth=.15,edgecolor='#666',legend_kwds={'shrink':.65})
            ax.set_title(titulo);ax.axis('off')
        limite = float(abs(municipal.erro).max())
        mapa.plot(column='erro',ax=axs[2],legend=True,cmap='RdBu_r',vmin=-limite,vmax=limite,linewidth=.15,edgecolor='#666',legend_kwds={'shrink':.65})
        axs[2].set_title('Erro: previsto − observado');axs[2].axis('off')
        fig.suptitle(f'{rotulo} ({unidade})\nMédias municipais em t=2019–2022, 255 polígonos IBGE 2025',fontsize=12)
        salvar_figura(fig,saida/f'mapas_municipais_{target}.png')
        loso = pd.read_parquet(raiz/f'apresentacao/PREDICOES_LOSO_VENCEDORES_{target}.parquet')
        municipal = loso.groupby('CD_MUN')[['previsto','erro']].mean().reset_index()
        mapa = geo.merge(municipal,on='CD_MUN',validate='one_to_one')
        fig,axs = plt.subplots(1,2,figsize=(11,5),layout='constrained')
        mapa.plot(column='previsto',ax=axs[0],legend=True,cmap='YlGnBu',linewidth=.15,edgecolor='#666',legend_kwds={'shrink':.65})
        limite = float(abs(municipal.erro).max())
        mapa.plot(column='erro',ax=axs[1],legend=True,cmap='RdBu_r',vmin=-limite,vmax=limite,linewidth=.15,edgecolor='#666',legend_kwds={'shrink':.65})
        for ax,titulo in zip(axs,['Previsto pelo composto LOSO','Erro: previsto − observado']):
            ax.set_title(titulo);ax.axis('off')
        fig.suptitle(f'{rotulo} ({unidade}) | t=2019–2022\nModelos por UF escolhidos na validação dos estados não retidos',fontsize=12)
        salvar_figura(fig,saida/f'mapas_LOSO_{target}.png')
    gravar_json({'origem_sha256':sha(resultado),'apenas_revisao_visual':True,'novos_ajustes_ou_predicoes':False,
                 'sha256':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}},saida/'manifesto_figuras_publicacao.json')
    print('Oito figuras em PNG/SVG concluídas, sem alterar predições ou figuras anteriores.',flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',type=Path,required=True)
    a=p.parse_args();executar(a.checkpoint)
