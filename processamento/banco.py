"""Conexão com o PostgreSQL, migrações do esquema e registro de cargas.

A conexão usa as variáveis padrão do PostgreSQL (PGHOST, PGPORT, PGDATABASE,
PGUSER, PGPASSWORD), definidas pelo docker-compose no serviço etl.
"""
import hashlib
import os
from pathlib import Path

import psycopg

import config

MIGRACOES_DIR = config.PROJETO_DIR / "db" / "migrations"


def conectar():
    if not os.environ.get("PGHOST"):
        raise RuntimeError("Defina PGHOST/PGUSER/PGPASSWORD/PGDATABASE (o serviço etl do docker-compose já define).")
    return psycopg.connect(autocommit=True)


def aplicar_migracoes(conexao):
    """Aplica, em ordem, os arquivos de db/migrations ainda não aplicados (um por transação)."""
    conexao.execute(
        "CREATE TABLE IF NOT EXISTS public.migracao ("
        " versao text PRIMARY KEY, aplicada_em timestamptz NOT NULL DEFAULT now())"
    )
    aplicadas = {linha[0] for linha in conexao.execute("SELECT versao FROM public.migracao")}
    for arquivo in sorted(MIGRACOES_DIR.glob("*.sql")):
        if arquivo.name in aplicadas:
            continue
        with conexao.transaction():
            conexao.execute(arquivo.read_text(encoding="utf-8"))
            conexao.execute("INSERT INTO public.migracao (versao) VALUES (%s)", (arquivo.name,))
        print(f"Migração aplicada: {arquivo.name}")


def sha256(caminho):
    digest = hashlib.sha256()
    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1 << 20), b""):
            digest.update(bloco)
    return digest.hexdigest()


def registrar_carga(conexao, fonte, arquivos, registros, versao=None, referencia=None):
    """Registra a proveniência de uma carga e devolve o carga_id.

    `arquivos` é um caminho ou uma lista de caminhos; para vários arquivos o hash
    registrado combina os hashes individuais (em ordem de nome).
    """
    if isinstance(arquivos, (list, tuple)):
        arquivos = sorted(arquivos)
        pasta_comum = Path(os.path.commonpath([a.parent for a in arquivos]))
        nome = f"{pasta_comum.name} ({len(arquivos)} arquivos)"
        combinado = "".join(f"{a.name}:{sha256(a)}\n" for a in arquivos)
        hash_carga = hashlib.sha256(combinado.encode()).hexdigest()
    else:
        nome, hash_carga = arquivos.name, sha256(arquivos)

    return conexao.execute(
        "INSERT INTO ref.carga (fonte, versao, referencia, arquivo, sha256, registros)"
        " VALUES (%s, %s, %s, %s, %s, %s) RETURNING carga_id",
        (fonte, versao, referencia, nome, hash_carga, registros),
    ).fetchone()[0]
