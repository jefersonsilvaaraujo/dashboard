# 🌱 Painel Interativo da Cobertura do Solo - MapBiomas

Este painel interativo desenvolvido em **Python com Streamlit** tem como objetivo permitir a **análise da dinâmica de uso e cobertura do solo** em municípios da fronteira Cerrado-Amazônia, com base nos dados do projeto **MapBiomas** (séries históricas de 1985 a 2023).

## 🔍 Funcionalidades

- Visualização interativa de gráficos por ano, década e classe de cobertura
- Filtros por município, classe de uso do solo e intervalo de anos
- Comparação entre dois anos selecionados
- Cálculo do Índice de Antropização
- Alertas automáticos de perda de vegetação nativa
- Exibição de mapas com marcador geográfico (1985 e 2023)
- Geração de relatório PDF completo com gráficos e mapas

## 🗂 Estrutura de diretórios esperada

```
dashboard/
├── app.py
├── estatisticas_coverage_historico.csv
├── municipios_coord.csv
└── municipios_shapefile/
    ├── municipios_1985.png
    ├── municipios_1985.pgw
    ├── municipios_2023.png
    ├── municipios_2023.pgw
```

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
