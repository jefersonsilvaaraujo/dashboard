# Imagem do processamento (ETL). O código do projeto e os dados brutos são
# montados pelo docker-compose, então não são copiados para a imagem.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY processamento/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /projeto/processamento
CMD ["python", "carregar_banco.py"]
