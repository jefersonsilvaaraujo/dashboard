"""Atualiza o banco: aplica as migrações pendentes e recarrega os dados.

Pode ser executado quantas vezes for preciso (idempotente).

Uso (pelo docker-compose):  docker compose run --rm etl
"""
import mapbiomas_col10
import municipios
from banco import aplicar_migracoes, conectar


def main():
    with conectar() as conexao:
        aplicar_migracoes(conexao)
        municipios.carregar_no_banco(conexao)
        mapbiomas_col10.carregar_no_banco(conexao)


if __name__ == "__main__":
    main()
