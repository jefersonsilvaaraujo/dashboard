import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from plotly.io import write_image
import os

# Funções auxiliares
def geo_to_pixel(lon, lat, pgw):
    A, D, B, E, C, F = pgw
    x = int((lon - C) / A)
    y = int((lat - F) / E)
    return x, y

def marcar_com_pin(nome_municipio, base_image, df_coord, pgw):
    imagem_marcada = base_image.copy()
    draw = ImageDraw.Draw(imagem_marcada)

    nome_municipio = nome_municipio.strip().lower()
    df_coord["nome_normalizado"] = df_coord["nome_municipio"].str.strip().str.lower()
    linha = df_coord[df_coord["nome_normalizado"] == nome_municipio]

    if not linha.empty:
        lon, lat = linha.iloc[0][["longitude", "latitude"]]
        x, y = geo_to_pixel(lon, lat, pgw)
        raio = 10
        haste = 15
        draw.line((x, y, x, y + haste), fill="red", width=3)
        draw.ellipse((x - raio, y - raio, x + raio, y + raio), fill="red", outline="black", width=1)
        fonte = ImageFont.load_default()
        draw.text((x + 10, y - 5), nome_municipio.title(), fill="black", font=fonte)

    return imagem_marcada

# Carregar dados
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = "historico/estatisticas_coverage_historico.csv"
df = pd.read_csv(csv_path, sep=";", decimal=",")

df["decada"] = (df["ano"] // 10) * 10

# Legenda MapBiomas
cores_mapbiomas = {
    3:  ("Formação Florestal", "#006400"),
    4:  ("Formação Savânica", "#DAA520"),
    5:  ("Mangue", "#8B4513"),
    6:  ("Floresta Alagável", "#00BFFF"),
    9:  ("Silvicultura", "#A52A2A"),
    11: ("Área Úmida Natural", "#B0C4DE"),
    12: ("Campo Natural", "#D2B48C"),
    15: ("Pastagem", "#F5DEB3"),
    18: ("Agricultura (Outros)", "#F4A460"),
    19: ("Lavoura Temporária", "#FFA500"),
    20: ("Cana-de-açúcar", "#B22222"),
    21: ("Mosaico de Usos", "#FFDEAD"),
    23: ("Praia e Duna", "#EEE8AA"),
    24: ("Área Urbana", "#FF0000"),
    25: ("Outras Áreas Não Vegetadas", "#8B0000"),
    29: ("Afloramento Rochoso", "#A9A9A9"),
    30: ("Mineração", "#808000"),
    31: ("Aquicultura", "#1E90FF"),
    39: ("Soja", "#FFA07A")
}
legenda_df = pd.DataFrame([
    {"classe_cobertura": k, "nome_classe": v[0], "cor_rgb": v[1]}
    for k, v in cores_mapbiomas.items()
])

df = df.merge(legenda_df, on="classe_cobertura", how="left")
df = df.dropna(subset=["nome_classe"])

# Sidebar
st.sidebar.title("Filtros")
opcoes_municipios = ["Todos"] + sorted(df["NM_MUN"].unique())
cidade = st.sidebar.selectbox("Escolha um município:", opcoes_municipios, index=0)
anos = sorted(df["ano"].unique())
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
    df_filtrado = df_filtrado[df_filtrado["NM_MUN"] == cidade]
df_filtrado = df_filtrado[df_filtrado["nome_classe"].isin(classes_selecionadas)]

# Título e subtítulo
st.title("Painel Interativo da Cobertura do Solo - MapBiomas")
if cidade == "Todos":
    st.subheader("Análise Geral para Todos os Municípios")
else:
    st.subheader(f"Análise para {cidade}")

    # Mostrar mapas de 1985 e 2023
    st.markdown("#### Localização do Município no Mapa (Comparativo 1985 vs 2023)")
    col1, col2 = st.columns(2)

    coord_path = "coordenadas/municipios_coord.csv"
    df_coord = pd.read_csv(coord_path)

    for ano, col in zip(["1985", "2023"], [col1, col2]):
        png_path = f"municipios_shapefile/municipios_{ano}.png"
        pgw_path = f"municipios_shapefile/municipios_{ano}.pgw"

        try:
            image = Image.open(png_path)
            with open(pgw_path) as f:
                pgw = list(map(float, f.readlines()))

            imagem_marcada = marcar_com_pin(cidade, image, df_coord, pgw)
            largura_desejada = 800
            altura_desejada = int(imagem_marcada.height * (largura_desejada / imagem_marcada.width))
            imagem_marcada = imagem_marcada.resize((largura_desejada, altura_desejada))

            buffer = BytesIO()
            imagem_marcada.save(buffer, format="PNG")
            buffer.seek(0)

            col.image(buffer, caption=f"{cidade} em {ano}", use_container_width=True)

        except Exception as e:
            col.warning(f"Erro ao carregar mapa de {ano}: {e}")

# Abas principais
abas = st.tabs(["Evolução Temporal", "Distribuição Anual", "Participação Percentual", "Análise por Década", "Comparação Entre Anos", "Análises Especiais", "Análises por Estados" ])

with abas[0]:
    st.markdown("#### Gráfico de Linha")
    fig1 = px.line(
        df_filtrado,
        x="ano",
        y="area_ha",
        color="nome_classe",
        color_discrete_map={row.nome_classe: row.cor_rgb for _, row in legenda_df.iterrows()},
        labels={"ano": "Ano", "area_ha": "Área (ha)", "nome_classe": "Classe de Cobertura"},
        title="Evolução da Cobertura do Solo"
    )
    fig1.update_layout(legend_title="Classe de Cobertura", hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("#### Gráfico de Área Acumulada")
    fig_area = px.area(
        df_filtrado,
        x="ano",
        y="area_ha",
        color="nome_classe",
        color_discrete_map={row.nome_classe: row.cor_rgb for _, row in legenda_df.iterrows()},
        labels={"ano": "Ano", "area_ha": "Área (ha)", "nome_classe": "Classe de Cobertura"},
        title="Área Acumulada por Classe ao Longo do Tempo"
    )
    fig_area.update_layout(legend_title="Classe de Cobertura")
    st.plotly_chart(fig_area, use_container_width=True)

    st.markdown("#### Gráfico de Dispersão por Ano")
    fig_scatter = px.scatter(
        df_filtrado,
        x="ano",
        y="area_ha",
        color="nome_classe",
        size="area_ha",
        color_discrete_map={row.nome_classe: row.cor_rgb for _, row in legenda_df.iterrows()},
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
        color_discrete_map={row.nome_classe: row.cor_rgb for _, row in legenda_df.iterrows()},
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
        color_discrete_map={row.nome_classe: row.cor_rgb for _, row in legenda_df.iterrows()},
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
        color_discrete_map={row.nome_classe: row.cor_rgb for _, row in legenda_df.iterrows()},
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
        df_mun = df[df["NM_MUN"] == cidade]
        df_comp = df_mun[df_mun["ano"].isin([1985, 2023])].pivot(index="nome_classe", columns="ano", values="area_ha").fillna(0)
        vegetacao_nativa = ["Formação Florestal", "Formação Savânica"]
        uso_antropico = ["Pastagem", "Soja", "Agricultura (Outros)", "Área Urbana"]

        perda_total = df_comp.loc[vegetacao_nativa].sum(axis=1).sum() - df_comp.loc[vegetacao_nativa][2023].sum()
        perda_percentual = (perda_total / df_comp.loc[vegetacao_nativa][1985].sum()) * 100 if df_comp.loc[vegetacao_nativa][1985].sum() > 0 else 0

        if perda_percentual > 30:
            st.warning(f"⚠️ Alerta: {cidade} perdeu mais de 30% de sua vegetação nativa entre 1985 e 2023 ({perda_percentual:.2f}%).")

    # 2. Ranking de crescimento e perda por classe
    st.markdown("#### Ranking de Variação por Classe (1985–2023)")
    df_var = df[df["ano"].isin([1985, 2023])]
    if cidade != "Todos":
        df_var = df_var[df_var["NM_MUN"] == cidade]
    df_pivot = df_var.pivot_table(index="nome_classe", columns="ano", values="area_ha", aggfunc="sum").fillna(0)
    df_pivot["variação"] = df_pivot[2023] - df_pivot[1985]
    top_ganhos = df_pivot.sort_values("variação", ascending=False).head(5)
    top_perdas = df_pivot.sort_values("variação").head(5)

    col1, col2 = st.columns(2)
    col1.markdown("**Maiores Ganhos**")
    col1.dataframe(top_ganhos[[1985, 2023, "variação"]].round(2))
    col2.markdown("**Maiores Perdas**")
    col2.dataframe(top_perdas[[1985, 2023, "variação"]].round(2))

    # 3. Gráfico de mudança líquida 1985–2023
    st.markdown("#### Variação Líquida por Classe (1985–2023)")
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
    antropicas = ["Pastagem", "Soja", "Agricultura (Outros)", "Área Urbana", "Mineração", "Cana-de-açúcar"]
    df_ant = df_filtrado.copy()
    df_ant["tipo"] = df_ant["nome_classe"].apply(lambda x: "Antropizado" if x in antropicas else "Natural")
    df_idx = df_ant.groupby(["ano", "tipo"])["area_ha"].sum().unstack().fillna(0)
    df_idx["índice"] = (df_idx["Antropizado"] / (df_idx["Antropizado"] + df_idx["Natural"])) * 100
    fig_ant = px.line(df_idx.reset_index(), x="ano", y="índice", title="Índice de Antropização ao Longo do Tempo",
                      labels={"índice": "% Área Antropizada"})
    st.plotly_chart(fig_ant, use_container_width=True)

with abas[6]:
    st.markdown("Análises por Estado")

    estados_disponiveis = sorted(df["SIGLA_UF"].unique())
    estados_selecionados = st.multiselect("Filtrar estados:", estados_disponiveis, default=estados_disponiveis)
    df_estado = df[df["SIGLA_UF"].isin(estados_selecionados)]

    # 1. Quantidade de municípios por estado
    st.markdown("### 1. Quantidade de Municípios por Estado")
    df_mun = df_estado.groupby("SIGLA_UF")["NM_MUN"].nunique().reset_index(name="Quantidade de Municípios")
    st.dataframe(df_mun)
    fig1 = px.bar(df_mun, x="SIGLA_UF", y="Quantidade de Municípios", title="Quantidade de Municípios por Estado")
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Perda de vegetação nativa por estado
    st.markdown("### 2. Perda de Vegetação Nativa por Estado (1985–2023)")
    nativas = ["Formação Florestal", "Formação Savânica"]
    df_nat = df_estado[df_estado["nome_classe"].isin(nativas) & df_estado["ano"].isin([1985, 2023])]
    df_nat_pivot = df_nat.pivot_table(index=["SIGLA_UF", "nome_classe"], columns="ano", values="area_ha", aggfunc="sum").fillna(0)
    df_nat_pivot["variação"] = df_nat_pivot[2023] - df_nat_pivot[1985]
    df_nat_agg = df_nat_pivot.groupby("SIGLA_UF")["variação"].sum().reset_index()
    fig2 = px.bar(df_nat_agg, x="SIGLA_UF", y="variação", title="Perda Total de Vegetação Nativa (ha)", labels={"variação": "Perda (ha)"})
    st.plotly_chart(fig2, use_container_width=True)

    # 3. Evolução da cobertura agrícola por estado
    st.markdown("### 3. Evolução da Cobertura Agrícola (1985–2023)")
    agro = ["Soja", "Pastagem", "Agricultura (Outros)", "Cana-de-açúcar"]
    df_agro = df_estado[df_estado["nome_classe"].isin(agro) & df_estado["ano"].isin([1985, 2023])]
    df_agro_pivot = df_agro.pivot_table(index=["SIGLA_UF", "nome_classe"], columns="ano", values="area_ha", aggfunc="sum").fillna(0)
    df_agro_pivot["crescimento"] = df_agro_pivot[2023] - df_agro_pivot[1985]
    fig3 = px.bar(df_agro_pivot.reset_index(), x="SIGLA_UF", y="crescimento", color="nome_classe", title="Crescimento de Cobertura Agrícola por Estado")
    st.plotly_chart(fig3, use_container_width=True)

    # 4. Urbanização por estado
    st.markdown("### 4. Urbanização por Estado ao Longo do Tempo")
    df_urb = df_estado[df_estado["nome_classe"] == "Área Urbana"]
    df_urb_agg = df_urb.groupby(["ano", "SIGLA_UF"])["area_ha"].sum().reset_index()
    fig4 = px.line(df_urb_agg, x="ano", y="area_ha", color="SIGLA_UF", title="Evolução da Área Urbana por Estado")
    st.plotly_chart(fig4, use_container_width=True)

    # 5. Índice médio de antropização por estado
    st.markdown("### 5. Índice Médio de Antropização por Estado")
    antropicas = ["Pastagem", "Soja", "Agricultura (Outros)", "Área Urbana", "Mineração", "Cana-de-açúcar"]
    df_ant = df_estado.copy()
    df_ant["tipo"] = df_ant["nome_classe"].apply(lambda x: "Antropizado" if x in antropicas else "Natural")
    df_idx = df_ant.groupby(["SIGLA_UF", "ano", "tipo"])["area_ha"].sum().unstack().fillna(0)
    df_idx["índice"] = (df_idx["Antropizado"] / (df_idx["Antropizado"] + df_idx["Natural"])) * 100
    df_idx_reset = df_idx.reset_index()
    fig5 = px.line(df_idx_reset, x="ano", y="índice", color="SIGLA_UF", title="Índice de Antropização por Estado")
    st.plotly_chart(fig5, use_container_width=True)

    # 6. Diversidade de classes por estado
    st.markdown("### 6. Diversidade de Classes por Estado")
    df_div = df_estado.groupby(["SIGLA_UF", "ano"])["nome_classe"].nunique().reset_index(name="n_classes")
    fig6 = px.line(df_div, x="ano", y="n_classes", color="SIGLA_UF", title="Número de Classes de Uso e Cobertura por Estado")
    st.plotly_chart(fig6, use_container_width=True)

    # 7. Década de maior alteração por estado
    st.markdown("### 7. Década com Maior Alteração de Uso e Cobertura por Estado")
    df_alt = df_estado.groupby(["SIGLA_UF", "decada", "nome_classe"])["area_ha"].sum().unstack().fillna(0)
    df_alt_diff = df_alt.groupby(level=0).apply(lambda g: g.diff().abs().sum(axis=1)).reset_index(name="alteracao")
    df_alt_max = df_alt_diff.groupby("SIGLA_UF").agg({"decada": "first", "alteracao": "max"}).reset_index()
    fig7 = px.bar(df_alt_max, x="SIGLA_UF", y="alteracao", color="decada", title="Década com Maior Alteração por Estado", labels={"alteracao": "Mudança Total (ha)"})
    st.plotly_chart(fig7, use_container_width=True)

st.sidebar.markdown("---")

# Botão para gerar relatório em PDF
# if cidade != "Todos":
#     gerar_pdf = st.sidebar.button("📄 Gerar Relatório em PDF")
#     if gerar_pdf:
#         buffer = BytesIO()
#         buffer = BytesIO()
#         c = canvas.Canvas(buffer, pagesize=A4)
#         c.setFont("Helvetica-Bold", 14)
#         c.drawString(50, 800, f"Relatório de Análise Ambiental - {cidade}")
#         c.setFont("Helvetica", 10)
#         c.drawString(50, 785, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

#         # Exportar o primeiro gráfico (fig1) como imagem temporária
#         img_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
#         img_bytes = fig1.to_image(format="png", engine="kaleido")
#         with open(img_temp.name, "wb") as f:
#             f.write(img_bytes)
#         c.drawImage(img_temp.name, 50, 500, width=500, height=250)
#         c.showPage()

#         # Exportar outros gráficos
#         from plotly.io import write_image
#         import tempfile

#         figures = [fig_area, fig_scatter, fig2, fig3, fig_dec, fig_comp, fig_dif, fig_ant]

#         for fig in figures:
#             img_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
#             img_bytes = fig.to_image(format="png", engine="kaleido")
#             with open(img_temp.name, "wb") as f:
#                 f.write(img_bytes)
#             c.drawImage(img_temp.name, 50, 500, width=500, height=250)
#             c.showPage()

#         # Inserir mapas com pin (1985 e 2023)
#         mapas = []
#         for ano in ["1985", "2023"]:
#             try:
#                 png_path = f"../municipios_shapefile/municipios_{ano}.png"
#                 pgw_path = f"../municipios_shapefile/municipios_{ano}.pgw"
#                 image = Image.open(png_path)
#                 with open(pgw_path) as f:
#                     pgw = list(map(float, f.readlines()))
#                 imagem_marcada = marcar_com_pin(cidade, image, df_coord, pgw)
#                 mapa_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
#                 imagem_marcada.save(mapa_path, format="PNG")
#                 mapas.append((ano, mapa_path))
#             except:
#                 continue

#         for ano, path in mapas:
#             c.drawImage(path, 50, 500, width=500, height=250)
#             c.drawString(50, 480, f"Mapa de {cidade} em {ano}")
#             c.showPage()

#         # Sumário
#         c.setFont("Helvetica-Bold", 12)
#         c.drawString(50, 780, "Sumário")
#         c.setFont("Helvetica", 10)
#         c.drawString(70, 760, "1. Introdução")
#         c.drawString(70, 745, "2. Mapas com Localização (1985 e 2023)")
#         c.drawString(70, 730, "3. Análises Gráficas")
#         c.drawString(70, 715, "4. Indicadores e Alertas")
#         c.drawString(70, 700, "5. Índice de Antropização")
#         c.showPage()

#         # Texto descritivo adicional nas seções
#         c.setFont("Helvetica", 10)
#         c.drawString(50, 780, "Este relatório apresenta uma visão abrangente da dinâmica de uso e cobertura do solo para o município selecionado.")
#         c.drawString(50, 765, "Foram considerados dados do MapBiomas de 1985 a 2023, com foco em variações de área, indicadores de antropização e alertas ambientais.")
#         c.drawString(50, 750, "Os mapas com localização geográfica do município destacam a posição em diferentes anos, permitindo rápida referência espacial.")
#         c.drawString(50, 735, "Os gráficos seguintes ilustram as principais tendências de uso da terra, evolução por classe, participação percentual e análises de mudança.")
#         c.drawString(50, 720, "Ao final, são apresentados indicadores importantes, como o índice de antropização e o ano com maior alteração de cobertura.")
#         c.showPage()

#         # Finaliza PDF
#         c.save()
#         buffer.seek(0)

#         st.sidebar.download_button(
#             label="📄 Baixar Relatório PDF",
#             data=buffer.getvalue(),
#             file_name=f"relatorio_{cidade}.pdf",
#             mime="application/pdf"
#         )

st.sidebar.download_button(
    label="Exportar dados filtrados (.csv)",
    data=df_filtrado.to_csv(index=False, sep=";", decimal=","),
    file_name="dados_filtrados.csv",
    mime="text/csv"
)
