# 🌱 Painel Interativo da Cobertura do Solo - MapBiomas

Este painel interativo desenvolvido em **Python com Streamlit** tem como objetivo permitir a **análise da dinâmica de uso e cobertura do solo** em municípios da fronteira Cerrado-Amazônia, com base nos dados do projeto **MapBiomas** (Coleção 10.1, séries históricas de 1985 a 2024).

## 🔍 Funcionalidades

- Visualização interativa de gráficos por ano, década e classe de cobertura
- Filtros por município, classe de uso do solo e intervalo de anos
- Comparação entre dois anos selecionados
- Cálculo do Índice de Antropização
- Alertas automáticos de perda de vegetação nativa
- Exibição de mapas com marcador geográfico (1985 e 2024)
- Geração de relatório PDF completo com gráficos e mapas

## 🗂 Estrutura de diretórios

```
dashboard/
├── app.py
├── historico/
│   ├── estatisticas_coverage_historico.csv   # cobertura por município, ano e classe (gerado)
│   └── legenda_mapbiomas.csv                 # nome, cor, grupo e tipo de cada classe (gerado)
├── coordenadas/
│   └── municipios_coord.csv                  # código IBGE, UF, área e centroide (gerado)
├── municipios_shapefile/
│   ├── municipios_1985.png / .pgw            # mapa da região de estudo (gerado)
│   └── municipios_2024.png / .pgw
├── mapas_municipios/                         # <CD_MUN>_<ano>.png, uso e cobertura de cada município (gerado)
└── processamento/                            # scripts que geram os arquivos acima
```

Os municípios são identificados pelo código IBGE (`CD_MUN`). No seletor do painel o nome aparece com a UF, pois há homônimos na área de estudo (ex.: Pau D'Arco no PA e no TO).

## 🔄 Atualização dos dados

O app lê apenas os CSVs agregados. Eles são gerados pelos scripts em `processamento/` a partir dos dados brutos, que **não são versionados** e ficam na pasta-mãe do projeto (ou no caminho definido na variável de ambiente `MESTRADO_DADOS`):

| Arquivo esperado | Fonte |
|---|---|
| `municipios_base/50km_todosMun.shp` | Limites municipais da área de estudo (IBGE, SIRGAS 2000) |
| `mapbiomas_col10/MAPBIOMAS_BRAZIL-COVERAGE_STATISTICS-COL.10.1-MUNICIPALITIES_STATES_BIOMES.xlsx` | [MapBiomas, estatísticas da Coleção 10.1](https://doi.org/10.58053/MapBiomas/SJZOLT) |
| `mapbiomas_col10/rasters/brazil_coverage_{ano}.tif` (1985 e 2024) | [MapBiomas, rasters anuais da Coleção 10](https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_10/lulc/coverage/) |
| `municipios_base/area_estudo.csv` (opcional) | Lista de `CD_MUN` para restringir a área de estudo |

```bash
pip install -r processamento/requirements.txt
python processamento/municipios.py
python processamento/mapbiomas_col10.py
python processamento/mapas.py
```

Os mapas usam os rasters da Coleção 10 (não há rasters públicos da 10.1); para 1985 e 2024 as áreas por classe diferem menos de 0,1% das estatísticas da Coleção 10.1.

Indicadores derivados da legenda oficial:

- **Vegetação nativa**: classes dos grupos *Floresta* e *Vegetação Herbácea e Arbustiva*.
- **Índice de antropização**: área das classes de tipo *Antrópico* dividida pela área total.

## 🛠 Requisitos

- Python 3.8+
- Pip

### Bibliotecas Python

```bash
pip install streamlit pandas plotly Pillow reportlab
```

---

## 💻 Como executar localmente

1. **Clone o repositório:**

```bash
git clone https://github.com/seuusuario/dashboard.git
cd dashboard
```

2. **(Opcional) Crie e ative um ambiente virtual:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Execute a aplicação:**

```bash
streamlit run app.py
```

5. **Acesse no navegador:**

```
http://localhost:8501
```

---

## 📄 Geração de Relatório

- Ao selecionar um município, é possível gerar um **relatório PDF completo** com gráficos, indicadores e mapas.
- O botão de geração do relatório está disponível no painel lateral (sidebar).

---

## 🌐 Publicação em Servidor

A aplicação pode ser hospedada em uma VPS com **Apache ou Nginx** como proxy reverso.
Recomenda-se executar a aplicação como serviço systemd utilizando um usuário próprio (ex: `streamlituser`).

---

## 📋 Licença

Este projeto é distribuído sob licença livre para fins acadêmicos e científicos.

---

## 🙋‍♂️ Autor

[Jeferson Silva (Jef EAD)](https://jefead.com.br)  
Desenvolvido como parte de um projeto de pesquisa sobre predição de risco ambiental com Machine Learning.


## 🚀 Implantação em Servidor (VPS com Apache)

### 1. Pré-requisitos

- VPS com Apache2 instalado e ativo
- Python 3.8+ e pip
- Sistema operacional Linux (Ubuntu recomendado)
- A aplicação deve estar clonada em `/opt/dashboard/`

### 2. Criar um usuário para a aplicação

```bash
sudo adduser streamlituser
sudo usermod -aG sudo streamlituser
```

### 3. Instalar dependências no ambiente do usuário

```bash
sudo su - streamlituser
cd /opt/dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Criar serviço systemd para executar o Streamlit

```bash
sudo nano /etc/systemd/system/streamlit_dashboard.service
```

Conteúdo do arquivo:

```
[Unit]
Description=Streamlit Dashboard - JefEAD
After=network.target

[Service]
User=streamlituser
WorkingDirectory=/opt/dashboard
ExecStart=/opt/dashboard/venv/bin/streamlit run app.py --server.port=8501 --server.headless=true
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative o serviço:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable streamlit_dashboard
sudo systemctl start streamlit_dashboard
```

Verifique com:

```bash
sudo systemctl status streamlit_dashboard
```

### 5. Configurar proxy reverso no Apache

Ative os módulos:

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
```

Edite seu arquivo de host virtual:

```bash
sudo nano /etc/apache2/sites-available/jefead.com.br.conf
```

Inclua:

```
<VirtualHost *:80>
    ServerName jefead.com.br

    ProxyPreserveHost On
    ProxyPass /dashboard http://localhost:8501/
    ProxyPassReverse /dashboard http://localhost:8501/
</VirtualHost>
```

Reinicie o Apache:

```bash
sudo systemctl reload apache2
```

---

Essas configurações garantem que a aplicação continue funcionando sem afetar outros serviços como WordPress ou Moodle.
