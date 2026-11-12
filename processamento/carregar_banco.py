"""Atualiza o banco: aplica as migrações pendentes e recarrega os dados.

Pode ser executado quantas vezes for preciso (idempotente).

Uso (pelo docker-compose):  docker compose run --rm etl
"""
import mapbiomas_col10
import municipios
import painel
import prodes
import queimadas
from banco import aplicar_migracoes, conectar


def main():
    with conectar() as conexao:
        aplicar_migracoes(conexao)
        municipios.carregar_no_banco(conexao)
        mapbiomas_col10.carregar_no_banco(conexao)
        queimadas.carregar_no_banco(conexao)
        queimadas.exportar_csv(conexao)
        prodes.carregar_no_banco(conexao)
        prodes.exportar_csv(conexao)
        # Painel integrado: depende de todas as fontes acima
        painel.atualizar(conexao)
        tabela = painel.ler_painel(conexao)
        painel.exportar_csv(tabela)
        painel.gerar_dicionario(conexao, tabela)


if __name__ == "__main__":
    main()
