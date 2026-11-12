"""Mapas municipais sem basemap externo; geometrias Col9 apenas para desenho."""
import json

import plotly.express as px


def geojson_municipios(territorio):
    if not territorio.CD_MUN.is_unique:
        raise ValueError('Código territorial duplicado no mapa.')
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'id': str(int(r.CD_MUN)),
         'properties': {'CD_MUN': str(int(r.CD_MUN))},
         'geometry': json.loads(r.geojson)} for r in territorio.itertuples()
    ]}


def mapa_municipal(valores, territorio, indicador, titulo):
    if not valores.CD_MUN.is_unique or set(valores.CD_MUN) != set(territorio.CD_MUN):
        raise ValueError('Mapa e indicadores não têm a mesma seleção municipal.')
    tabela = valores.merge(territorio[['CD_MUN', 'NM_MUN', 'SIGLA_UF']], on='CD_MUN', validate='one_to_one')
    tabela['codigo_mapa'] = tabela.CD_MUN.astype(str)
    figura = px.choropleth(
        tabela, geojson=geojson_municipios(territorio), locations='codigo_mapa',
        featureidkey='properties.CD_MUN', color=indicador,
        hover_name='NM_MUN', hover_data={'SIGLA_UF': True, 'codigo_mapa': True,
                                        'area_classificada_ha': ':.4f'},
        labels={indicador: '%', 'area_classificada_ha': 'Área classificada (ha)'},
        color_continuous_scale='Viridis', range_color=(0, 100), title=titulo,
    )
    figura.update_geos(fitbounds='locations', visible=False)
    figura.update_traces(marker_line_width=0.5, marker_line_color='#555555')
    figura.update_layout(margin=dict(l=0, r=0, b=0, t=50), height=620)
    return figura
