
# 🚀 Implantação de Aplicação Streamlit em uma VPS com Apache + HTTPS

Este guia documenta todo o processo de **instalação, configuração e execução** de uma aplicação Streamlit em uma VPS, utilizando **Apache2 como proxy reverso**, **certificado SSL via Let's Encrypt**, e deploy com **diretório específico como `/dashboard`**.

---

## ✅ Requisitos da VPS

- Sistema Operacional: Ubuntu 20.04 ou superior
- Acesso root (ou via `sudo`)
- Domínio configurado apontando para o IP da VPS (ex: `jefead.com.br`)
- Portas 80 e 443 liberadas no firewall

---

## 🔧 Passo 1: Instalar Dependências

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install apache2 libapache2-mod-proxy-html libxml2-dev -y
sudo apt install python3-pip python3-venv -y
sudo apt install certbot python3-certbot-apache -y
sudo a2enmod proxy proxy_http ssl headers rewrite
```

---

## 🌐 Passo 2: Configurar Domínio e Certificado SSL

```bash
sudo certbot --apache -d jefead.com.br
```

---

## 📁 Passo 3: Estrutura de Diretórios da Aplicação

```bash
sudo mkdir -p /home/streamlitapp/dashboard
sudo chown -R $USER:$USER /home/streamlitapp
cd /home/streamlitapp/dashboard
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 Passo 4: Instalar Dependências do Projeto

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Passo 5: Configurar Streamlit

```bash
mkdir -p ~/.streamlit
nano ~/.streamlit/config.toml
```

```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false
port = 8501
baseUrlPath = "dashboard"
```

---

## 🧩 Passo 6: Criar Serviço systemd para o Streamlit

```bash
sudo nano /etc/systemd/system/streamlit-dashboard.service
```

```ini
[Unit]
Description=Streamlit Dashboard Service
After=network.target

[Service]
User=streamlitapp
Group=streamlitapp
WorkingDirectory=/home/streamlitapp/dashboard
Environment="PATH=/home/streamlitapp/dashboard/venv/bin"
ExecStart=/home/streamlitapp/dashboard/venv/bin/streamlit run app.py

Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable streamlit-dashboard
sudo systemctl start streamlit-dashboard
```

---

## 🌍 Passo 7: Configurar Apache como Proxy Reverso

```bash
sudo nano /etc/apache2/sites-available/000-default-le-ssl.conf
```

```apache

RewriteEngine On

RewriteCond %{HTTP:Upgrade} websocket [NC]
RewriteCond %{HTTP:Connection} upgrade [NC]
RewriteRule ^/dashboard/(.*) ws://127.0.0.1:8501/dashboard/$1 [P,L]

ProxyPreserveHost On

ProxyPass /dashboard http://localhost:8501/dashboard
ProxyPassReverse /dashboard http://localhost:8501/dashboard

ProxyPass /dashboard/static http://localhost:8501/dashboard/static
ProxyPassReverse /dashboard/static http://localhost:8501/dashboard/static

RequestHeader set X-Forwarded-Proto "https"
```

```bash
sudo a2ensite 000-default-le-ssl.conf
sudo systemctl reload apache2
```

---

## 🔄 Passo 8: Atualizar Aplicação

```bash
cd /home/streamlitapp/dashboard
git pull
sudo systemctl restart streamlit-dashboard
```

---

## ✅ Verificação Final

```bash
sudo systemctl status streamlit-dashboard
journalctl -u streamlit-dashboard -f
```

---

## 📁 Estrutura Recomendada

```
/home/streamlitapp/dashboard/
├── app.py
├── requirements.txt
├── historico/
├── coordenadas/
├── municipios_shapefile/
└── .streamlit/
```

---

## ✨ Resultado Esperado

🔗 **https://seudominio.com/dashboard**

---

## 🙌 Créditos

Manual criado para ambiente de produção utilizando **MapBiomas + Streamlit + Apache2 + HTTPS**.
