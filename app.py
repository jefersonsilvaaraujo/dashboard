import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from plotly.io import write_image
import os

# Caminhos relativos a este arquivo, para o app funcionar a partir de qualquer pasta
base_dir = os.path.dirname(os.path.abspath(__file__))

def caminho(*partes):
    return os.path.join(base_dir, *partes)

# Funções auxiliares
def geo_to_pixel(lon, lat, pgw):
    A, D, B, E, C, F = pgw
    x = int((lon - C) / A)
    y = int((lat - F) / E)
    return x, y

def marcar_com_pin(cd_mun, rotulo, base_image, df_coord, pgw):
    # Mapa sobre fundo branco (o PNG tem fundo transparente e cores indexadas)
    base_rgba = base_image.convert("RGBA")
    imagem_marcada = Image.new("RGB", base_rgba.size, "white")
    imagem_marcada.paste(base_rgba, mask=base_rgba)
    draw = ImageDraw.Draw(imagem_marcada)

    linha = df_coord[df_coord["CD_MUN"] == cd_mun]

    if not linha.empty:
        lon, lat = linha.iloc[0][["longitude", "latitude"]]
        x, y = geo_to_pixel(lon, lat, pgw)
        raio = 10
        haste = 15
        draw.line((x, y, x, y + haste), fill="red", width=3)
        draw.ellipse((x - raio, y - raio, x + raio, y + raio), fill="red", outline="black", width=1)
        fonte = ImageFont.load_default()
        draw.text((x + 10, y - 5), rotulo, fill="black", font=fonte)

    return imagem_marcada

def indice_antropizacao(dados, por):
    """Percentual da área em classes antrópicas sobre a área total."""
    total = dados.groupby(por)["area_ha"].sum()
    antropica = dados[dados["tipo"] == "Antrópico"].groupby(por)["area_ha"].sum()
    return (antropica.reindex(total.index, fill_value=0) / total * 100).rename("índice").reset_index()

# Carregar dados
df = pd.read_csv(caminho("historico", "estatisticas_coverage_historico.csv"), sep=";", decimal=",")

df["decada"] = (df["ano"] // 10) * 10

# Legenda MapBiomas Coleção 10.1 (gerada por processamento/mapbiomas_col10.py)
legenda_df = pd.read_csv(caminho("historico", "legenda_mapbiomas.csv"))

df = df.merge(legenda_df, on="classe_cobertura", how="left")
df["nome_classe"] = df["nome_classe"].fillna("Classe " + df["classe_cobertura"].astype(str))
df["cor_rgb"] = df["cor_rgb"].fillna("#999999")
mapa_cores = dict(zip(df["nome_classe"], df["cor_rgb"]))

classes_nativas = legenda_df.loc[legenda_df["grupo"].isin(["Floresta", "Vegetação Herbácea e Arbustiva"]), "nome_classe"].tolist()
classes_agropecuarias = legenda_df.loc[legenda_df["grupo"] == "Agropecuária", "nome_classe"].tolist()

# Município identificado pelo código IBGE; o rótulo leva a UF para separar homônimos
df["rotulo_mun"] = df["NM_MUN"] + " (" + df["SIGLA_UF"] + ")"
municipios_por_rotulo = df.drop_duplicates("CD_MUN").set_index("rotulo_mun")["CD_MUN"]

# Sidebar
st.sidebar.title("Filtros")
opcoes_municipios = ["Todos"] + sorted(municipios_por_rotulo.index)
cidade = st.sidebar.selectbox("Escolha um município:", opcoes_municipios, index=0)
cd_mun = municipios_por_rotulo[cidade] if cidade != "Todos" else None
anos = sorted(df["ano"].unique())
ANO_INICIAL, ANO_FINAL = anos[0], anos[-1]
ANOS_MAPAS = (1985, 2024)  # anos com mapas gerados por processamento/mapas.py
intervalo_anos = st.sidebar.slider("Selecione o intervalo de anos:", min_value=min(anos), max_value=max(anos), value=(min(anos), max(anos)))

classes_disponiveis = sorted(df["nome_classe"].unique())
col1, col2 = st.sidebar.columns([1, 1])
selecionar_todos = col1.button("Selecionar todas")
limpar_todos = col2.button("Limpar todas")

if "classes_selecionadas" not in st.session_state:
    st.session_state.classes_selecionadas = classes_disponiveis
if selecionar_todos:
    st.session_state.classes_selecionadas = classes_disponiveis
if limpar_todos:
    st.session_state.classes_selecionadas = []

classes_selecionadas = st.sidebar.multiselect("Filtrar por classe de cobertura (opcional):", classes_disponiveis, default=st.session_state.classes_selecionadas)

# Filtro geral
df_filtrado = df[(df["ano"] >= intervalo_anos[0]) & (df["ano"] <= intervalo_anos[1])]
if cidade != "Todos":
    df_filtrado = df_filtrado[df_filtrado["CD_MUN"] == cd_mun]
df_filtrado = df_filtrado[df_filtrado["nome_classe"].isin(classes_selecionadas)]

# Série anual por classe (soma os municípios quando "Todos" está selecionado)
df_serie = df_filtrado.groupby(["ano", "nome_classe"], as_index=False)["area_ha"].sum()

# Título e subtítulo
st.title("Painel Interativo da Cobertura do Solo - MapBiomas")
st.caption(f"Fonte: MapBiomas Brasil, Coleção 10.1 ({ANO_INICIAL}–{ANO_FINAL})")
if cidade == "Todos":
    st.subheader("Análise Geral para Todos os Municípios")
else:
    st.subheader(f"Análise para {cidade}")

    # Mostrar mapas da região de estudo
    st.markdown(f"#### Localização do Município no Mapa (Comparativo {ANOS_MAPAS[0]} vs {ANOS_MAPAS[1]})")
    col1, col2 = st.columns(2)

    df_coord = pd.read_csv(caminho("coordenadas", "municipios_coord.csv"))

    for ano, col in zip(ANOS_MAPAS, [col1, col2]):
        png_path = caminho("municipios_shapefile", f"municipios_{ano}.png")
        pgw_path = caminho("municipios_shapefile", f"municipios_{ano}.pgw")

        try:
            image = Image.open(png_path)
            with open(pgw_path) as f:
                pgw = list(map(float, f.readlines()))

            imagem_marcada = marcar_com_pin(cd_mun, cidade, image, df_coord, pgw)
            largura_desejada = 800
            altura_desejada = int(imagem_marcada.height * (largura_desejada / imagem_marcada.width))
            imagem_marcada = imagem_marcada.resize((largura_desejada, altura_desejada))

            buffer = BytesIO()
            imagem_marcada.save(buffer, format="PNG")
            buffer.seek(0)

            col.image(buffer, caption=f"Região de estudo em {ano}", use_container_width=True)

        except Exception as e:
            col.warning(f"Erro ao carregar mapa de {ano}: {e}")

    # Uso e cobertura do próprio município nos mesmos anos
    st.markdown(f"#### Uso e Cobertura do Município ({ANOS_MAPAS[0]} vs {ANOS_MAPAS[1]})")
    col1, col2 = st.columns(2)
    for ano, col in zip(ANOS_MAPAS, [col1, col2]):
        mapa_municipio = caminho("mapas_municipios", f"{cd_mun}_{ano}.png")
        if os.path.exists(mapa_municipio):
            col.image(mapa_municipio, caption=f"{cidade} em {ano}", use_container_width=True)
        else:
            col.warning(f"Mapa de {ano} não encontrado. Rode processamento/mapas.py.")

    # Legenda: classes presentes no município em algum dos dois anos, da maior para a menor área
    df_mapas = df[(df["CD_MUN"] == cd_mun) & df["ano"].isin(ANOS_MAPAS)]
    classes_mapa = (
        df_mapas.groupby(["nome_classe", "cor_rgb"])["area_ha"].max()
        .sort_values(ascending=False).reset_index()
    )
    itens_legenda = "".join(
        f"<span style='display:inline-flex;align-items:center;margin:0 14px 6px 0'>"
        f"<span style='width:12px;height:12px;background:{cor};border:1px solid #888;margin-right:5px'></span>"
        f"{nome}</span>"
        for nome, cor in zip(classes_mapa["nome_classe"], classes_mapa["cor_rgb"])
    )
    st.markdown(f"<div style='font-size:0.85rem'>{itens_legenda}</div>", unsafe_allow_html=True)

    # Diferença entre os dois anos em indicadores-resumo
    def area_em(ano, filtro):
        return df_mapas.loc[(df_mapas["ano"] == ano) & filtro, "area_ha"].sum()

    def variacao(inicial, final):
        return f"{(final - inicial) / inicial * 100:+.1f}% desde {ANOS_MAPAS[0]}" if inicial > 0 else None

    def hectares(valor):
        return f"{valor:,.0f} ha".replace(",", ".")

    nativa = [area_em(ano, df_mapas["nome_classe"].isin(classes_nativas)) for ano in ANOS_MAPAS]
    antropica = [area_em(ano, df_mapas["tipo"] == "Antrópico") for ano in ANOS_MAPAS]
    total = [area_em(ano, df_mapas["area_ha"] > 0) for ano in ANOS_MAPAS]
    indice = [a / t * 100 if t > 0 else 0 for a, t in zip(antropica, total)]

    m1, m2, m3 = st.columns(3)
    m1.metric(f"Vegetação nativa em {ANOS_MAPAS[1]}", hectares(nativa[1]), variacao(*nativa))
    m2.metric(f"Área antrópica em {ANOS_MAPAS[1]}", hectares(antropica[1]), variacao(*antropica), delta_color="inverse")
    m3.metric(f"Índice de antropização em {ANOS_MAPAS[1]}", f"{indice[1]:.1f}%",
              f"{indice[1] - indice[0]:+.1f} p.p. desde {ANOS_MAPAS[0]}", delta_color="inverse")
    st.caption("Mapas: MapBiomas Coleção 10 (raster 30 m). Áreas e indicadores: estatísticas da Coleção 10.1.")

# Abas principais
abas = st.tabs(["Evolução Temporal", "Distribuição Anual", "Participação Percentual", "Análise por Década", "Comparação Entre Anos", "Análises Especiais", "Análises por Estados" ])

with abas[0]:
    st.markdown("#### Gráfico de Linha")
    fig1 = px.line(
        df_serie,
        x="ano",
        y="area_ha",
        color="nome_classe",
        color_discrete_map=mapa_cores,
        labels={"ano": "Ano", "area_ha": "Área (ha)", "nome_classe": "Classe de Cobertura"},
        title="Evolução da Cobertura do Solo"
    )
    fig1.update_layout(legend_title="Classe de Cobertura", hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("#### Gráfico de Área Acumulada")
    fig_area = px.area(
        df_serie,
        x="ano",
        y="area_ha",
        color="nome_classe",
        color_discrete_map=mapa_cores,
        labels={"ano": "Ano", "area_ha": "Área (ha)", "nome_classe": "Classe de Cobertura"},
        title="Área Acumulada por Classe ao Longo do Tempo"
    )
    fig_area.update_layout(legend_title="Classe de Cobertura")
    st.plotly_chart(fig_area, use_container_width=True)

    st.markdown("#### Gráfico de Dispersão por Ano")
    fig_scatter = px.scatter(
        df_serie,
        x="ano",
        y="area_ha",
        color="nome_classe",
        size="area_ha",
        color_discrete_map=mapa_cores,
        labels={"ano": "Ano", "area_ha": "Área (ha)"},
        title="Dispersão das Áreas por Classe e Ano"
    )
    fig_scatter.update_layout(legend_title="Classe de Cobertura")
    st.plotly_chart(fig_scatter, use_container_width=True)

with abas[1]:
    ano_analise = st.selectbox("Selecione o ano para análise detalhada:", options=anos, index=len(anos)-1, key="ano_distribuicao")
    df_ano = df_filtrado[df_filtrado["ano"] == ano_analise]
    fig2 = px.bar(
        df_ano.sort_values("area_ha", ascending=False),
        x="nome_classe",
        y="area_ha",
        color="nome_classe",
        color_discrete_map=mapa_cores,
        title=f"Distribuição da Cobertura em {ano_analise}"
    )
    fig2.update_layout(xaxis_title="Classe", yaxis_title="Área (ha)", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

with abas[2]:
    ano_percentual = st.selectbox("Selecione o ano para o gráfico de participação percentual:", options=anos, index=len(anos)-1, key="ano_percentual")
    df_pizza = df_filtrado[df_filtrado["ano"] == ano_percentual]
    fig3 = px.pie(
        df_pizza,
        names="nome_classe",
        values="area_ha",
        color="nome_classe",
        color_discrete_map=mapa_cores,
        title=f"Participação Percentual das Classes em {ano_percentual}"
    )
    st.plotly_chart(fig3, use_container_width=True)

with abas[3]:
    df_decada = df_filtrado.groupby(["decada", "nome_classe"], as_index=False)["area_ha"].sum()
    fig_dec = px.bar(
        df_decada,
        x="decada",
        y="area_ha",
        color="nome_classe",
        barmode="stack",
        color_discrete_map=mapa_cores,
        title="Distribuição da Cobertura por Década"
    )
    fig_dec.update_layout(xaxis_title="Década", yaxis_title="Área (ha)", legend_title="Classe de Cobertura")
    st.plotly_chart(fig_dec, use_container_width=True)

with abas[4]:
    st.markdown("### Comparação Entre Anos")
    ano_comp1 = st.selectbox("Ano 1:", options=anos, index=0, key="ano1")
    ano_comp2 = st.selectbox("Ano 2:", options=anos, index=len(anos)-1, key="ano2")

    df_ano1 = df_filtrado[df_filtrado["ano"] == ano_comp1].groupby("nome_classe")["area_ha"].sum()
    df_ano2 = df_filtrado[df_filtrado["ano"] == ano_comp2].groupby("nome_classe")["area_ha"].sum()

    df_diff = pd.DataFrame({"Ano 1": df_ano1, "Ano 2": df_ano2})
    df_diff["Variação Absoluta"] = df_diff["Ano 2"] - df_diff["Ano 1"]
    df_diff["Variação Percentual"] = ((df_diff["Ano 2"] - df_diff["Ano 1"]) / df_diff["Ano 1"]) * 100
    st.dataframe(df_diff.fillna(0).round(2), use_container_width=True)

    df_plot = df_diff.fillna(0).reset_index()
    df_melt = df_plot.melt(id_vars="nome_classe", value_vars=["Ano 1", "Ano 2"], var_name="Ano", value_name="Área (ha)")
    fig_comp = px.bar(
        df_melt,
        x="nome_classe",
        y="Área (ha)",
        color="Ano",
        barmode="group",
        title=f"Comparação da Cobertura do Solo entre {ano_comp1} e {ano_comp2}"
    )
    fig_comp.update_layout(xaxis_title="Classe de Cobertura", yaxis_title="Área (ha)")
    st.plotly_chart(fig_comp, use_container_width=True)

# Estatísticas descritivas
st.markdown("### Estatísticas Descritivas")
st.dataframe(df_filtrado.describe(include="all"), use_container_width=True)

# Tabela interativa
st.markdown("### Dados Filtrados")
st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)

with abas[5]:
    st.markdown("### Análises Especiais")

    # 1. Alerta de perda crítica de vegetação nativa
    if cidade != "Todos":
        df_mun = df[(df["CD_MUN"] == cd_mun) & df["nome_classe"].isin(classes_nativas)]
        area_nativa = df_mun.groupby("ano")["area_ha"].sum()
        nativa_inicial = area_nativa.get(ANO_INICIAL, 0)
        nativa_final = area_nativa.get(ANO_FINAL, 0)
        perda_percentual = (nativa_inicial - nativa_final) / nativa_inicial * 100 if nativa_inicial > 0 else 0

        if perda_percentual > 30:
            st.warning(f"⚠️ Alerta: {cidade} perdeu mais de 30% de sua vegetação nativa entre {ANO_INICIAL} e {ANO_FINAL} ({perda_percentual:.2f}%).")

    # 2. Ranking de crescimento e perda por classe
    st.markdown(f"#### Ranking de Variação por Classe ({ANO_INICIAL}–{ANO_FINAL})")
    df_var = df[df["ano"].isin([ANO_INICIAL, ANO_FINAL])]
    if cidade != "Todos":
        df_var = df_var[df_var["CD_MUN"] == cd_mun]
    df_pivot = (
        df_var.pivot_table(index="nome_classe", columns="ano", values="area_ha", aggfunc="sum")
        .reindex(columns=[ANO_INICIAL, ANO_FINAL]).fillna(0)
    )
    df_pivot["variação"] = df_pivot[ANO_FINAL] - df_pivot[ANO_INICIAL]
    top_ganhos = df_pivot.sort_values("variação", ascending=False).head(5)
    top_perdas = df_pivot.sort_values("variação").head(5)

    col1, col2 = st.columns(2)
    col1.markdown("**Maiores Ganhos**")
    col1.dataframe(top_ganhos[[ANO_INICIAL, ANO_FINAL, "variação"]].round(2))
    col2.markdown("**Maiores Perdas**")
    col2.dataframe(top_perdas[[ANO_INICIAL, ANO_FINAL, "variação"]].round(2))

    # 3. Gráfico de mudança líquida
    st.markdown(f"#### Variação Líquida por Classe ({ANO_INICIAL}–{ANO_FINAL})")
    fig_dif = px.bar(df_pivot.reset_index(), x="nome_classe", y="variação",
                     title="Mudança Líquida de Área (ha) por Classe",
                     color="variação",
                     color_continuous_scale="RdYlGn")
    fig_dif.update_layout(xaxis_title="Classe", yaxis_title="Área (ha)", showlegend=False)
    st.plotly_chart(fig_dif, use_container_width=True)

    # 4. Ano de maior alteração
    st.markdown("#### Ano de Maior Alteração de Cobertura")
    df_mudanca = df_filtrado.groupby(["ano", "nome_classe"])["area_ha"].sum().unstack().fillna(0)
    df_mudanca_dif = df_mudanca.diff().abs().sum(axis=1)
    ano_maior_alteracao = df_mudanca_dif.idxmax()
    valor_maior = df_mudanca_dif.max()
    st.info(f"📌 O ano com maior alteração total de cobertura foi {ano_maior_alteracao}, com mudança acumulada de {valor_maior:.2f} ha.")

    # 5. Índice de Antropização
    st.markdown("#### Índice de Antropização por Ano")
    df_idx = indice_antropizacao(df_filtrado, "ano")
    fig_ant = px.line(df_idx, x="ano", y="índice", title="Índice de Antropização ao Longo do Tempo",
                      labels={"índice": "% Área Antropizada"})
    st.plotly_chart(fig_ant, use_container_width=True)

with abas[6]:
    st.markdown("Análises por Estado")

    estados_disponiveis = sorted(df["SIGLA_UF"].unique())
    estados_selecionados = st.multiselect("Filtrar estados:", estados_disponiveis, default=estados_disponiveis)
    df_estado = df[df["SIGLA_UF"].isin(estados_selecionados)]

    # 1. Quantidade de municípios por estado
    st.markdown("### 1. Quantidade de Municípios por Estado")
    df_mun = df_estado.groupby("SIGLA_UF")["CD_MUN"].nunique().reset_index(name="Quantidade de Municípios")
    st.dataframe(df_mun)
    fig_uf1 = px.bar(df_mun, x="SIGLA_UF", y="Quantidade de Municípios", title="Quantidade de Municípios por Estado")
    st.plotly_chart(fig_uf1, use_container_width=True)

    # 2. Perda de vegetação nativa por estado
    st.markdown(f"### 2. Perda de Vegetação Nativa por Estado ({ANO_INICIAL}–{ANO_FINAL})")
    df_nat = df_estado[df_estado["nome_classe"].isin(classes_nativas) & df_estado["ano"].isin([ANO_INICIAL, ANO_FINAL])]
    df_nat_pivot = (
        df_nat.pivot_table(index=["SIGLA_UF", "nome_classe"], columns="ano", values="area_ha", aggfunc="sum")
        .reindex(columns=[ANO_INICIAL, ANO_FINAL]).fillna(0)
    )
    df_nat_pivot["variação"] = df_nat_pivot[ANO_FINAL] - df_nat_pivot[ANO_INICIAL]
    df_nat_agg = df_nat_pivot.groupby("SIGLA_UF")["variação"].sum().reset_index()
    fig_uf2 = px.bar(df_nat_agg, x="SIGLA_UF", y="variação", title="Perda Total de Vegetação Nativa (ha)", labels={"variação": "Perda (ha)"})
    st.plotly_chart(fig_uf2, use_container_width=True)

    # 3. Evolução da cobertura agropecuária por estado
    st.markdown(f"### 3. Evolução da Cobertura Agropecuária ({ANO_INICIAL}–{ANO_FINAL})")
    df_agro = df_estado[df_estado["nome_classe"].isin(classes_agropecuarias) & df_estado["ano"].isin([ANO_INICIAL, ANO_FINAL])]
    df_agro_pivot = (
        df_agro.pivot_table(index=["SIGLA_UF", "nome_classe"], columns="ano", values="area_ha", aggfunc="sum")
        .reindex(columns=[ANO_INICIAL, ANO_FINAL]).fillna(0)
    )
    df_agro_pivot["crescimento"] = df_agro_pivot[ANO_FINAL] - df_agro_pivot[ANO_INICIAL]
    fig_uf3 = px.bar(df_agro_pivot.reset_index(), x="SIGLA_UF", y="crescimento", color="nome_classe",
                     color_discrete_map=mapa_cores, title="Crescimento da Cobertura Agropecuária por Estado")
    st.plotly_chart(fig_uf3, use_container_width=True)

    # 4. Urbanização por estado
    st.markdown("### 4. Urbanização por Estado ao Longo do Tempo")
    df_urb = df_estado[df_estado["classe_cobertura"] == 24]
    df_urb_agg = df_urb.groupby(["ano", "SIGLA_UF"])["area_ha"].sum().reset_index()
    fig_uf4 = px.line(df_urb_agg, x="ano", y="area_ha", color="SIGLA_UF", title="Evolução da Área Urbanizada por Estado")
    st.plotly_chart(fig_uf4, use_container_width=True)

    # 5. Índice médio de antropização por estado
    st.markdown("### 5. Índice Médio de Antropização por Estado")
    df_idx_reset = indice_antropizacao(df_estado, ["SIGLA_UF", "ano"])
    fig_uf5 = px.line(df_idx_reset, x="ano", y="índice", color="SIGLA_UF", title="Índice de Antropização por Estado")
    st.plotly_chart(fig_uf5, use_container_width=True)

    # 6. Diversidade de classes por estado
    st.markdown("### 6. Diversidade de Classes por Estado")
    df_div = df_estado.groupby(["SIGLA_UF", "ano"])["nome_classe"].nunique().reset_index(name="n_classes")
    fig_uf6 = px.line(df_div, x="ano", y="n_classes", color="SIGLA_UF", title="Número de Classes de Uso e Cobertura por Estado")
    st.plotly_chart(fig_uf6, use_container_width=True)

    # 7. Década de maior alteração por estado
    st.markdown("### 7. Década com Maior Alteração de Uso e Cobertura por Estado")
    df_alt = df_estado.groupby(["SIGLA_UF", "decada", "nome_classe"])["area_ha"].sum().unstack().fillna(0)
    df_alt_diff = (
        df_alt.groupby(level=0)
        .apply(lambda g: g.diff().abs().sum(axis=1))
        .reset_index(level=1, drop=True)
        .reset_index(name="alteracao")
    )

    # Linha da década com a maior alteração em cada estado
    df_alt_max = df_alt_diff.loc[df_alt_diff.groupby("SIGLA_UF")["alteracao"].idxmax()].reset_index(drop=True)
    df_alt_max["decada"] = df_alt_max["decada"].astype(str)
    fig_uf7 = px.bar(df_alt_max, x="SIGLA_UF", y="alteracao", color="decada", title="Década com Maior Alteração por Estado", labels={"alteracao": "Mudança Total (ha)"})
    st.plotly_chart(fig_uf7, use_container_width=True)

st.sidebar.markdown("---")

# Botão para gerar relatório em PDF
if cidade != "Todos":
    gerar_pdf = st.sidebar.button("📄 Gerar Relatório em PDF")
    if gerar_pdf:
        try:
            with st.spinner("Gerando relatório PDF..."):
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
                width, height = A4
                
                # Página 1 - Capa
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, height-100, f"Relatório de Análise Ambiental")
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, height-130, f"Município: {cidade}")
                c.setFont("Helvetica", 12)
                c.drawString(50, height-160, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                
                # Sumário
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, height-220, "Sumário")
                c.setFont("Helvetica", 11)
                y_pos = height-250
                sumario_items = [
                    f"1. Mapas com Localização e Uso do Município ({ANOS_MAPAS[0]} e {ANOS_MAPAS[1]})",
                    "2. Evolução Temporal da Cobertura",
                    "3. Distribuição por Classes",
                    "4. Análise de Participação Percentual",
                    "5. Análise por Décadas",
                    "6. Comparação Entre Anos",
                    "7. Análises Especiais"
                ]
                for item in sumario_items:
                    c.drawString(70, y_pos, item)
                    y_pos -= 20
                
                # Texto introdutório
                c.setFont("Helvetica", 10)
                y_pos = height-400
                texto_intro = [
                    "Este relatório apresenta uma visão abrangente da dinâmica de uso e cobertura",
                    "do solo para o município selecionado. Foram considerados dados do MapBiomas",
                    f"(Coleção 10.1) de {ANO_INICIAL} a {ANO_FINAL}, com foco em variações de área, indicadores de antropização",
                    "e alertas ambientais. Os mapas destacam a posição geográfica do município",
                    "em diferentes anos, permitindo rápida referência espacial."
                ]
                for linha in texto_intro:
                    c.drawString(50, y_pos, linha)
                    y_pos -= 15
                
                c.showPage()
                
                # Página 2 e 3 - Mapas da região com pin
                df_coord = pd.read_csv(caminho("coordenadas", "municipios_coord.csv"))

                for ano in ANOS_MAPAS:
                    try:
                        png_path = caminho("municipios_shapefile", f"municipios_{ano}.png")
                        pgw_path = caminho("municipios_shapefile", f"municipios_{ano}.pgw")

                        if os.path.exists(png_path) and os.path.exists(pgw_path):
                            image = Image.open(png_path)
                            with open(pgw_path, 'r') as f:
                                pgw = [float(line.strip()) for line in f.readlines()]

                            imagem_marcada = marcar_com_pin(cd_mun, cidade, image, df_coord, pgw)
                            
                            # Redimensionar imagem para caber na página
                            max_width = 500
                            max_height = 400
                            img_width, img_height = imagem_marcada.size
                            ratio = min(max_width/img_width, max_height/img_height)
                            new_width = int(img_width * ratio)
                            new_height = int(img_height * ratio)
                            imagem_marcada = imagem_marcada.resize((new_width, new_height))
                            
                            # Salvar imagem temporária
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                                imagem_marcada.save(tmp_file.name, format="PNG")

                                # Adicionar ao PDF
                                c.setFont("Helvetica-Bold", 14)
                                c.drawString(50, height-50, f"Localização de {cidade} em {ano}")
                                c.drawImage(tmp_file.name, 50, height-500, width=new_width, height=new_height)

                            # Limpar arquivo temporário (fora do "with": no Windows não se apaga arquivo aberto)
                            os.unlink(tmp_file.name)
                        else:
                            c.setFont("Helvetica", 12)
                            c.drawString(50, height-100, f"Mapa de {ano} não encontrado")
                            
                    except Exception as e:
                        c.setFont("Helvetica", 10)
                        c.drawString(50, height-100, f"Erro ao processar mapa de {ano}: {str(e)}")

                    c.showPage()

                # Página 4 - Uso e cobertura do município, lado a lado
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, height-50, f"Uso e Cobertura de {cidade} ({ANOS_MAPAS[0]} e {ANOS_MAPAS[1]})")
                largura_mapa = (width - 120) / 2
                altura_maxima = 0
                for i, ano in enumerate(ANOS_MAPAS):
                    mapa_municipio = caminho("mapas_municipios", f"{cd_mun}_{ano}.png")
                    x = 50 + i * (largura_mapa + 20)
                    if os.path.exists(mapa_municipio):
                        mapa_rgba = Image.open(mapa_municipio).convert("RGBA")
                        mapa_branco = Image.new("RGB", mapa_rgba.size, "white")
                        mapa_branco.paste(mapa_rgba, mask=mapa_rgba)
                        escala = min(largura_mapa / mapa_branco.width, 520 / mapa_branco.height)
                        largura_img, altura_mapa = mapa_branco.width * escala, mapa_branco.height * escala
                        altura_maxima = max(altura_maxima, altura_mapa)
                        c.drawImage(ImageReader(mapa_branco), x, height-90-altura_mapa, width=largura_img, height=altura_mapa)
                        c.setFont("Helvetica", 11)
                        c.drawString(x, height-75, str(ano))
                    else:
                        c.setFont("Helvetica", 10)
                        c.drawString(x, height-100, f"Mapa de {ano} não encontrado")

                # Legenda das classes presentes no município
                c.setFont("Helvetica", 9)
                y_legenda = height-115-altura_maxima
                for i, (nome, cor) in enumerate(zip(classes_mapa["nome_classe"], classes_mapa["cor_rgb"])):
                    coluna, linha_legenda = i % 3, i // 3
                    x = 50 + coluna * 170
                    y = y_legenda - linha_legenda * 15
                    c.setFillColor(HexColor(cor))
                    c.rect(x, y, 9, 9, fill=1, stroke=1)
                    c.setFillColor(HexColor("#000000"))
                    c.drawString(x + 14, y + 1, nome)
                c.showPage()

                # Função auxiliar para adicionar gráficos
                def adicionar_grafico_pdf(fig, titulo, c, width, height):
                    try:
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(50, height-50, titulo)
                        
                        # Exportar gráfico como imagem
                        img_bytes = fig.to_image(format="png", width=600, height=400)
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                            tmp_file.write(img_bytes)
                            tmp_file.flush()
                            
                            # Adicionar ao PDF
                            c.drawImage(tmp_file.name, 50, height-500, width=500, height=350)

                        # Limpar arquivo temporário (fora do "with": no Windows não se apaga arquivo aberto)
                        os.unlink(tmp_file.name)
                            
                    except Exception as e:
                        c.setFont("Helvetica", 10)
                        c.drawString(50, height-100, f"Erro ao gerar gráfico: {str(e)}")
                    
                    c.showPage()
                
                # Gráficos das abas (somente se as variáveis existirem)
                if 'fig1' in locals():
                    adicionar_grafico_pdf(fig1, "Evolução da Cobertura do Solo", c, width, height)
                
                if 'fig_area' in locals():
                    adicionar_grafico_pdf(fig_area, "Área Acumulada por Classe", c, width, height)
                
                if 'fig_scatter' in locals():
                    adicionar_grafico_pdf(fig_scatter, "Dispersão das Áreas por Classe e Ano", c, width, height)
                
                if 'fig2' in locals():
                    adicionar_grafico_pdf(fig2, f"Distribuição da Cobertura em {ano_analise}", c, width, height)
                
                if 'fig3' in locals():
                    adicionar_grafico_pdf(fig3, f"Participação Percentual das Classes em {ano_percentual}", c, width, height)
                
                if 'fig_dec' in locals():
                    adicionar_grafico_pdf(fig_dec, "Distribuição da Cobertura por Década", c, width, height)
                
                if 'fig_comp' in locals():
                    adicionar_grafico_pdf(fig_comp, f"Comparação da Cobertura entre {ano_comp1} e {ano_comp2}", c, width, height)
                
                # Página final com estatísticas
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, height-50, "Resumo Estatístico")
                
                # Calcular algumas estatísticas básicas
                df_mun_filtered = df_filtrado[df_filtrado["CD_MUN"] == cd_mun]

                if not df_mun_filtered.empty:
                    total_area_inicial = df_mun_filtered[df_mun_filtered["ano"] == ANO_INICIAL]["area_ha"].sum()
                    total_area_final = df_mun_filtered[df_mun_filtered["ano"] == ANO_FINAL]["area_ha"].sum()

                    c.setFont("Helvetica", 11)
                    y_pos = height-100
                    stats_text = [
                        f"Área total registrada em {ANO_INICIAL}: {total_area_inicial:,.0f} ha",
                        f"Área total registrada em {ANO_FINAL}: {total_area_final:,.0f} ha",
                        f"Período analisado: {df_mun_filtered['ano'].min()} - {df_mun_filtered['ano'].max()}",
                        f"Classes de cobertura identificadas: {df_mun_filtered['nome_classe'].nunique()}",
                        f"Anos com dados disponíveis: {len(df_mun_filtered['ano'].unique())}"
                    ]
                    
                    for linha in stats_text:
                        c.drawString(50, y_pos, linha)
                        y_pos -= 20
                
                # Finalizar PDF
                c.save()
                buffer.seek(0)
                
                st.sidebar.download_button(
                    label="📄 Baixar Relatório PDF",
                    data=buffer.getvalue(),
                    file_name=f"relatorio_{cidade.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                
                st.sidebar.success("Relatório PDF gerado com sucesso!")
                
        except Exception as e:
            st.sidebar.error(f"Erro ao gerar relatório PDF: {str(e)}")
            st.sidebar.info("Verifique se todas as dependências estão instaladas e os arquivos de mapa estão disponíveis.")

st.sidebar.download_button(
    label="Exportar dados filtrados (.csv)",
    data=df_filtrado.to_csv(index=False, sep=";", decimal=","),
    file_name="dados_filtrados.csv",
    mime="text/csv"
)
