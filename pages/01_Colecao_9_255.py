"""Análise descritiva Col9/255, independente do dashboard legado."""
import json
from pathlib import Path

import plotly.express as px
import streamlit as st

import dados_col9
from contratos_series import COL9
from analise_col9 import indicadores, serie_classes, medias_decadas, comparar_anos, auditar_areas, classificar
from visualizacao_col9 import mapa_municipal

st.set_page_config(page_title='Coleção 9 — 255 municípios', layout='wide')
st.title('MapBiomas Coleção 9 — 255 municípios')
st.caption('1985–2023 · limites fixos IBGE 2025 · metodologia D1–D4 aprovada · análise descritiva')


def baixar_csv(rotulo, tabela, arquivo, chave):
    st.download_button(rotulo, tabela.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig'),
                       file_name=arquivo, mime='text/csv', key=chave)


try:
    base, legenda = dados_col9.carregar(COL9.id)
    territorio = dados_col9.carregar_territorio()
    if set(base.CD_MUN) != set(territorio.CD_MUN):
        raise ValueError('Cobertura e geometria não compartilham os mesmos 255 códigos IBGE.')
except (ValueError, RuntimeError) as exc:
    st.error(str(exc))
    st.stop()
except Exception:
    st.error('Não foi possível consultar a Coleção 9. Verifique a conexão e as permissões de leitura.')
    st.stop()

cadastro = territorio.copy()
cadastro['rotulo'] = cadastro.NM_MUN + ' (' + cadastro.SIGLA_UF + ')'
st.sidebar.header('Filtros — Coleção 9')
ufs = sorted(cadastro.SIGLA_UF.unique())
ufs_selecionadas = st.sidebar.multiselect('Estados', ufs, default=ufs)
possiveis = cadastro[cadastro.SIGLA_UF.isin(ufs_selecionadas)].sort_values(['SIGLA_UF', 'NM_MUN'])
rotulos = possiveis.set_index('CD_MUN').rotulo.to_dict()
selecionados = st.sidebar.multiselect('Municípios (vazio = todos dos estados selecionados)',
                                     list(rotulos), format_func=lambda c: rotulos[c])
periodo = st.sidebar.slider('Período', 1985, 2023, (1985, 2023))
classes = legenda[legenda.classe_cobertura.isin(base.classe_cobertura.unique())].sort_values('classe_cobertura')
rotulos_classes = {int(r.classe_cobertura): f'{int(r.classe_cobertura)} — {r.nome_classe}' for r in classes.itertuples()}
filtro_classes = st.sidebar.multiselect('Classes nos gráficos temáticos (vazio = todas)',
                                        list(rotulos_classes), format_func=lambda c: rotulos_classes[c])
codigos_municipais = selecionados or possiveis.CD_MUN.tolist()
territorio_filtro = territorio[territorio.CD_MUN.isin(codigos_municipais)]
escopo = base[base.CD_MUN.isin(codigos_municipais) & base.ano.between(*periodo)].copy()
if escopo.empty:
    st.info('Nenhum registro para os filtros selecionados.')
    st.stop()

codigos_classes = filtro_classes or list(rotulos_classes)
amostra = escopo[escopo.classe_cobertura.isin(codigos_classes)]
municipios_n = escopo.CD_MUN.nunique()
anos_n = escopo.ano.nunique()
rotulo_fonte = f'Coleção 9 · {municipios_n} municípios selecionados dos 255 · {periodo[0]}–{periodo[1]}'
st.caption(rotulo_fonte)
st.info('O filtro de classes afeta gráficos temáticos, comparações e dados detalhados. '
        'Os indicadores operacionais usam todas as classes do território/período selecionado. '
        'Seus denominadores incluem 25 e 33 e excluem não observado.')
c1, c2, c3, c4 = st.columns(4)
c1.metric('Municípios no filtro', str(municipios_n))
c2.metric('Anos no filtro', str(anos_n))
c3.metric('Classes no filtro', str(amostra.classe_cobertura.nunique()))
c4.metric('Registros no filtro', f'{len(amostra):,}'.replace(',', '.'))

anual = indicadores(escopo)
serie = serie_classes(escopo, codigos_classes).merge(
    legenda[['classe_cobertura', 'nome_classe']], on='classe_cobertura', validate='many_to_one')
serie['classe'] = serie.classe_cobertura.astype(str) + ' — ' + serie.nome_classe
cores = {f'{int(r.classe_cobertura)} — {r.nome_classe}': r.cor_rgb for r in legenda.itertuples()}
abas = st.tabs(['Indicadores', 'Classes', 'Comparações temporais', 'Mapas', 'Auditoria e dados'])

with abas[0]:
    ultimo = anual.iloc[-1]
    st.subheader(f'Composição da área classificada em {int(ultimo.ano)}')
    p1, p2 = st.columns(2)
    p1.metric('Vegetação nativa mapeada (%)', f'{ultimo.vegetacao_nativa_pct:.2f}')
    p2.metric('Participação de usos antrópicos mapeados (%)', f'{ultimo.usos_antropicos_pct:.2f}')
    st.caption('Vegetação nativa: 3, 4, 5, 6, 49, 11, 12, 50. Usos antrópicos: '
               '9, 15, 20, 21, 24, 30, 31, 35, 39, 40, 41, 46, 47, 48, 62. '
               'Percentuais = 100 × soma das áreas da categoria / soma da área classificada.')
    campos = {'vegetacao_nativa_pct': 'Vegetação nativa principal',
              'vegetacao_nativa_ampliada_pct': 'Vegetação nativa incluindo 29 e 32',
              'usos_antropicos_pct': 'Usos antrópicos principal',
              'usos_antropicos_com25_pct': 'Usos antrópicos incluindo 25'}
    linhas = anual.melt(id_vars='ano', value_vars=list(campos), var_name='cenario', value_name='participacao_pct')
    linhas['cenario'] = linhas.cenario.map(campos)
    fig = px.line(linhas, x='ano', y='participacao_pct', color='cenario',
                  labels={'ano': 'Ano', 'participacao_pct': '% da área classificada', 'cenario': 'Cenário'}, title=rotulo_fonte)
    st.plotly_chart(fig, width='stretch')
    st.caption('Sensibilidades são cenários de inclusão das classes indicadas, sem interpretação '
               'como intervalo de confiança. Os percentuais principais não precisam somar 100%. '
               'São indicadores descritivos, sem medida de intensidade de impacto ou legalidade.')
    st.dataframe(anual, hide_index=True, width='stretch')
    baixar_csv('Baixar indicadores e sensibilidades', anual, 'col9_indicadores_descritivos.csv', 'indicadores')

with abas[1]:
    st.subheader('Evolução de área e participação por classe')
    for valor, unidade in [('area_ha', 'Área (ha)'), ('participacao_pct', '% da área classificada')]:
        fig = px.line(serie, x='ano', y=valor, color='classe', color_discrete_map=cores,
                      labels={'ano': 'Ano', valor: unidade, 'classe': 'Classe Col9'}, title=rotulo_fonte)
        st.plotly_chart(fig, width='stretch')
    st.caption('A seleção de uma única classe não altera o denominador. Classe ausente vale zero '
               'somente em município–ano cuja observação já foi validada.')
    final = serie[serie.ano.eq(periodo[1])]
    fig = px.bar(final, x='classe', y='area_ha', color='classe', color_discrete_map=cores,
                 title=f'Distribuição em {periodo[1]} · {rotulo_fonte}',
                 labels={'classe': 'Classe Col9', 'area_ha': 'Área (ha)'})
    st.plotly_chart(fig, width='stretch')
    baixar_csv('Baixar série por classe e denominador', serie, 'col9_serie_classes.csv', 'series')

with abas[2]:
    st.subheader('Médias anuais por década')
    decadas = medias_decadas(escopo, codigos_classes).merge(legenda[['classe_cobertura', 'nome_classe']], on='classe_cobertura', validate='many_to_one')
    decadas['classe'] = decadas.classe_cobertura.astype(str) + ' — ' + decadas.nome_classe
    decadas['periodo_rotulo'] = decadas.periodo + ' (' + decadas.anos_observados.astype(str) + ' anos)'
    fig = px.bar(decadas, x='periodo_rotulo', y='media_anual_area_ha', color='classe',
                 color_discrete_map=cores, title=rotulo_fonte,
                 labels={'periodo_rotulo': 'Período efetivamente observado', 'media_anual_area_ha': 'Média anual de área (ha)'})
    st.plotly_chart(fig, width='stretch')
    st.caption('1985–1989 e 2020–2023 são décadas incompletas; filtros podem produzir outros períodos incompletos. '
               'Hectares de anos diferentes não são somados como uma única área.')
    st.dataframe(decadas, hide_index=True, width='stretch')
    baixar_csv('Baixar médias anuais por década', decadas, 'col9_medias_decadas.csv', 'decadas')
    st.subheader('Variação líquida de área entre anos de referência')
    anos = sorted(escopo.ano.unique())
    if len(anos) > 1:
        inicial = st.selectbox('Ano de referência inicial', anos[:-1], index=0)
        finais = [a for a in anos if a > inicial]
        final_ref = st.selectbox('Ano de referência final', finais, index=len(finais)-1)
        comparacao = comparar_anos(escopo, inicial, final_ref, codigos_classes).merge(legenda[['classe_cobertura', 'nome_classe']], on='classe_cobertura', validate='one_to_one')
        fig = px.bar(comparacao, x='nome_classe', y='variacao_liquida_ha', title=rotulo_fonte,
                     labels={'nome_classe': 'Classe Col9', 'variacao_liquida_ha': 'Variação líquida de área (ha)'})
        st.plotly_chart(fig, width='stretch')
        st.dataframe(comparacao, hide_index=True, width='stretch')
        baixar_csv('Baixar comparação entre anos', comparacao, 'col9_variacao_liquida_area.csv', 'comparacao')
    else:
        st.info('Selecione um período com pelo menos dois anos para comparar estoques.')
    st.warning('Variação líquida de área não é desmatamento, transição espacial ou variável-alvo de conversão significativa em t+1.')

with abas[3]:
    st.subheader('Indicadores municipais no mesmo território de referência')
    ano_mapa = st.selectbox('Ano do mapa municipal', sorted(escopo.ano.unique()), index=anos_n-1)
    opcoes_mapa = {'Vegetação nativa (%)': 'vegetacao_nativa_pct',
                   'Participação de usos antrópicos mapeados (%)': 'usos_antropicos_pct',
                   'Vegetação nativa incluindo 29 e 32 (%)': 'vegetacao_nativa_ampliada_pct',
                   'Usos antrópicos incluindo 25 (%)': 'usos_antropicos_com25_pct'}
    indicador_mapa = st.selectbox('Indicador municipal', list(opcoes_mapa))
    municipal = indicadores(escopo[escopo.ano.eq(ano_mapa)], ('CD_MUN',))
    fig = mapa_municipal(municipal, territorio_filtro, opcoes_mapa[indicador_mapa],
                         f'{indicador_mapa} · {ano_mapa} · Col9 · {municipios_n} municípios dos 255')
    st.plotly_chart(fig, width='stretch')
    st.caption('Cada polígono mostra a estatística do município, não a localização dos pixels de cada classe. '
               'Limite IBGE 2025 simplificado somente para desenho; áreas auditadas usam geometria original.')
    st.subheader('Pré-visualizações da cobertura Col9 em 1985 e 2023')
    pasta = Path(__file__).resolve().parents[1] / 'mapas_col9'
    try:
        manifesto = dados_col9.carregar_mapas_regionais(pasta)
    except (ValueError, OSError):
        manifesto = None
        st.error('Pré-visualizações não passaram na verificação de proveniência; imagens não exibidas.')
    if manifesto:
        for coluna, ano in zip(st.columns(2), (1985, 2023)):
            with coluna:
                st.image(str(pasta / manifesto['mapas'][str(ano)]['arquivo']), caption=f'Col9 · {ano} · região completa dos 255 municípios')
        st.caption('Contexto regional fixo: estas duas imagens mostram todos os 255 municípios, independentemente '
                   'dos filtros acima. Vizinho mais próximo, máscara do território e complemento dos três municípios '
                   'do Maranhão aplicados somente ao desenho. Não usar imagens reduzidas para quantificar áreas ou transições.')
        st.download_button('Baixar proveniência dos mapas regionais', json.dumps(manifesto, ensure_ascii=False, indent=2),
                           file_name='col9_mapas_manifesto.json', mime='application/json')
    elif not (pasta / 'manifesto.json').exists():
        st.info('Pré-visualizações regionais ainda não geradas. O mapa municipal acima usa exclusivamente o território Col9.')

with abas[4]:
    st.subheader('Auditoria independente de áreas por município e ano')
    auditoria = auditar_areas(escopo, territorio_filtro)
    st.caption('Compara área classificada, área cadastrada e áreas geodésicas WGS84/GRS80 da geometria original. '
               'Diferenças não são automaticamente NoData e não alteram os percentuais de origem.')
    st.dataframe(auditoria, hide_index=True, width='stretch')
    baixar_csv('Baixar auditoria de áreas', auditoria, 'col9_auditoria_municipio_ano.csv', 'auditoria')
    st.subheader('Dados e classificação oficial/operacional')
    detalhes = classificar(amostra).merge(legenda.rename(columns={'grupo': 'grupo_oficial_col9'}),
                                         on='classe_cobertura', validate='many_to_one')
    detalhes = detalhes.rename(columns={'perc_ocupacao': 'perc_ocupacao_origem'})
    st.dataframe(detalhes, hide_index=True, width='stretch')
    baixar_csv('Baixar dados detalhados', detalhes, 'col9_dados_detalhados.csv', 'detalhes')
    st.download_button('Baixar proveniência e metodologia', json.dumps(dados_col9.proveniencia(), ensure_ascii=False, indent=2),
                       file_name='col9_proveniencia_metodologia.json', mime='application/json')

st.info('Escopo científico: Coleção 9, limites fixos IBGE 2025, 255 municípios, 1985–2023. '
        'PRODES, queimadas e modelagem legados não foram incorporados. A ressalva de máscara de 2002 '
        'em Buriticupu permanece; transições exigem pixels válidos comuns aos anos comparados.')
