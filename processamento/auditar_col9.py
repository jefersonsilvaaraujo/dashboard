"""Auditoria somente leitura. Não importa nem executa o ETL legado.

Uso: python processamento/auditar_col9.py --saida /evidencias/auditoria_col9_d1d4
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dados_col9
from analise_col9 import auditar_areas, indicadores


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saida', type=Path, required=True)
    args = parser.parse_args()
    if args.saida.exists():
        raise FileExistsError('Diretório de evidências já existe; escolher outro para preservar o checkpoint.')
    base, _ = dados_col9.carregar()
    territorio = dados_col9.carregar_territorio()
    tabela = auditar_areas(base, territorio)
    anual = indicadores(base)
    campos = ['razao_classificada_cadastrada_pct', 'razao_classificada_geodesica_wgs84_pct',
              'desvio_cadastro_geodesica_pct', 'diferenca_classificada_geodesica_wgs84_ha']
    resumo = {'metodologia': dados_col9.proveniencia(), 'pares_municipio_ano': len(tabela),
              'municipios': int(tabela.CD_MUN.nunique()), 'anos': int(tabela.ano.nunique()),
              'causa_diferencas': 'não atribuída; nenhuma diferença é automaticamente NoData',
              'estatisticas': {c: {'min': float(tabela[c].min()), 'mediana': float(tabela[c].median()),
                                    'max': float(tabela[c].max())} for c in campos}}
    args.saida.mkdir(parents=True)
    tabela.to_csv(args.saida / 'auditoria_municipio_ano.csv', sep=';', index=False, encoding='utf-8-sig', float_format='%.10f')
    anual.to_csv(args.saida / 'indicadores_anuais_255.csv', sep=';', index=False, encoding='utf-8-sig', float_format='%.10f')
    (args.saida / 'resumo.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in resumo.items() if k != 'metodologia'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
