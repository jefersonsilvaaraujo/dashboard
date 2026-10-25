# Manual de implantação na VPS (Docker)

O painel roda em containers (PostgreSQL/PostGIS + Streamlit) atrás do Apache, que continua
responsável pelo domínio e pelo HTTPS em `https://jefead.com.br/dashboard`.

```
usuário ──HTTPS──► Apache ──► 127.0.0.1:8501 (container app) ──► container db (rede interna)
```

Nenhuma porta dos containers fica exposta à internet: o app e o banco só aceitam conexões da
própria VPS (`127.0.0.1`).

## Situação anterior (registro)

Antes da migração para Docker, o painel rodava pelo systemd:

| Serviço | Pasta | Situação |
|---|---|---|
| `streamlit-dashboard` | `/home/streamlitapp/dashboard` (usuário `streamlituser`) | em produção |
| `streamlit_dashboard` | `/opt/dashboard` | instalação antiga, com falha |

O Apache já está configurado (Passo 7) e não precisa de alteração.

---

## Passo 1: Pré-requisitos

- **Recursos**: ao menos 2 GB de RAM livres e 5 GB de disco para imagens e banco. Verifique com `free -h` e `df -h /`.
- **Docker Engine com o plugin Compose**: siga https://docs.docker.com/engine/install/ubuntu/ e confira:

```bash
docker --version
docker compose version
```

## Passo 2: Código

```bash
cd /home/streamlitapp/dashboard
git pull --ff-only origin main
```

## Passo 3: Configuração (.env)

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

- `POSTGRES_PASSWORD` e `APP_DB_PASSWORD`: senhas fortes e diferentes (gere com `openssl rand -hex 24`).
- `APP_BASE_URL_PATH=dashboard` (o Apache publica o painel em `/dashboard`).
- `POSTGRES_USER` e `POSTGRES_DB` iguais aos da máquina de desenvolvimento, para o restore do Passo 5.

## Passo 4: Banco de dados

```bash
docker compose up -d db
docker compose ps        # db deve ficar "healthy"
```

Na primeira inicialização o banco cria o usuário somente leitura do app (`db/init`).

## Passo 5: Dados

Os dados brutos (planilhas e rasters) ficam na máquina de desenvolvimento, onde o processamento roda.
A VPS recebe o banco pronto por um dump.

Na **máquina de desenvolvimento**, na pasta do projeto:

```bash
docker compose run --rm etl
docker compose exec -T db pg_dump -U dashboard_admin -d dashboard -Fc > dashboard.dump
scp dashboard.dump usuario@jefead.com.br:/home/streamlitapp/dashboard/
```

Na **VPS**:

```bash
cd /home/streamlitapp/dashboard
docker compose exec -T db pg_restore -U dashboard_admin -d dashboard --no-owner --exit-on-error < dashboard.dump
rm dashboard.dump
```

## Passo 6: Trocar o serviço systemd pelo container

O container usa a mesma porta (8501), então o serviço antigo precisa parar antes:

```bash
systemctl disable --now streamlit-dashboard
systemctl disable streamlit_dashboard
docker compose up -d --build app
docker compose ps        # app deve ficar "healthy"
curl -s http://127.0.0.1:8501/dashboard/_stcore/health   # deve responder "ok"
```

Abra `https://jefead.com.br/dashboard` e gere um relatório PDF para conferir os gráficos.

**Voltar ao modo anterior** (se algo der errado): `docker compose stop app` e
`systemctl enable --now streamlit-dashboard`. O serviço antigo lê os CSVs do repositório; se ele
falhar ao iniciar, instale as dependências atuais no venv dele com
`venv/bin/pip install -r requirements.txt`.

## Passo 7: Apache (referência, já configurado)

Em um servidor novo (Ubuntu 20.04+, domínio apontando para o IP, portas 80 e 443 liberadas),
instale o Apache e o certificado antes:

```bash
sudo apt update && sudo apt install -y apache2 certbot python3-certbot-apache
sudo certbot --apache -d jefead.com.br
```

Configuração do proxy:

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
sudo a2enmod proxy proxy_http proxy_wstunnel rewrite headers
sudo systemctl reload apache2
```

---

## Atualizar

**Código** (após merge no `main`):

```bash
cd /home/streamlitapp/dashboard
git pull --ff-only origin main
docker compose up -d --build app
```

Se a atualização trouxer arquivos novos em `db/migrations/`, os dados também precisam ser
atualizados (abaixo), pois o esquema chega pelo dump.

**Dados**: gere um dump novo na máquina de desenvolvimento (Passo 5) e, na VPS, restaure por cima
e reinicie o app para limpar o cache:

```bash
docker compose exec -T db pg_restore -U dashboard_admin -d dashboard --no-owner --clean --if-exists --exit-on-error < dashboard.dump
docker compose restart app
rm dashboard.dump
```

## Backup diário

```bash
mkdir -p /home/streamlitapp/backups
crontab -e
```

```cron
0 3 * * * cd /home/streamlitapp/dashboard && docker compose exec -T db pg_dump -U dashboard_admin -d dashboard -Fc > /home/streamlitapp/backups/dashboard_$(date +\%F).dump && find /home/streamlitapp/backups -name 'dashboard_*.dump' -mtime +14 -delete
```

Restaurar um backup: mesmo comando de restore do item **Dados**, apontando para o arquivo do backup.

## Diagnóstico

```bash
docker compose ps
docker compose logs -f app
docker compose logs -f db
```

## Acesso ao banco pelo QGIS (túnel SSH)

O banco não é exposto à internet. Para conectar do seu computador:

```bash
ssh -N -L 5433:127.0.0.1:5432 usuario@jefead.com.br
```

Com o túnel aberto, no QGIS: host `localhost`, porta `5433`, banco `dashboard`, usuário
`dashboard_app` (somente leitura) e a senha `APP_DB_PASSWORD` do `.env` da VPS.

## Limpeza da instalação antiga

Depois de validar o painel em Docker por alguns dias:

```bash
rm /etc/systemd/system/streamlit-dashboard.service /etc/systemd/system/streamlit_dashboard.service
systemctl daemon-reload
rm -rf /opt/dashboard
rm -rf /home/streamlitapp/dashboard/venv
```
