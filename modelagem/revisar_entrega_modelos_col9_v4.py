"""Revisão editorial aditiva e discussão; não executa modelos nem muda escolhas."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys

import pandas as pd

PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJETO))
from modelagem.protocolo_experimentos_col9_v4 import carregar_manifesto


def executar(raiz, docs):
    carregar_manifesto(raiz)
    snapshot = docs/'rascunhos_antes_revisao_editorial'
    snapshot.mkdir()
    for arq in docs.glob('*.md'):
        if arq.name in {'PROTOCOLO_EXPERIMENTAL_CONGELADO_COL9.md', 'RELATORIO_AUDITORIA_PRE_TREINO_COL9.md', 'DIARIO_DECISOES_CIENTIFICAS_COL9.md'}:
            continue  # registros anteriores ao ajuste permanecem intocados
        shutil.copy2(arq, snapshot/arq.name)
        texto = arq.read_text(encoding='utf-8')
        for i in range(5):
            texto = texto.replace(f'T {i}', f'T{i}')
        for a, b in {'daCol 9':'da Coleção 9', 'Col 9':'Coleção 9', 'Ablacões':'Ablações',
                     'emT':'em T', 'deT':'de T', 'vencedorT':'vencedor T', 'porMAE':'por MAE',
                     'porUF':'por UF', 'dentrodaUF':'dentro da UF', 'DPdas':'DP das', 'éIC':'é IC',
                     'emParquet':'em Parquet', 'emPNG':'em PNG', 'emskops':'em skops',
                     'emMETRICAS':'em METRICAS', 'emAJUSTES':'em AJUSTES', 'emapresentacao':'em apresentacao',
                     'eR²':'e R²', 'validação,2018':'validação, 2018', 'paraR':'para R', 'paraC':'para C'}.items():
            texto = texto.replace(a, b)
        # Alinhamentos de tabela válidos, preservando números e identificadores.
        texto = re.sub(r'(?<=:) +(?=\|)', '', texto)
        arq.write_text(texto, encoding='utf-8')
    adicional = '''

## Leitura substantiva dos resultados

A persistência é a referência central: já foi a melhor opção geral para R na
validação (MAE 0,6547 p.p., contra 0,6602 do XGBoost/T3). No teste, o MAE
do XGBoost foi aproximadamente 15,0% maior que o da persistência (2,2883
contra 1,9895 p.p.). Para C, a Random Forest/T3 venceu na validação, mas seu
MAE de teste foi aproximadamente 3,7% maior que o da persistência (1.278,09
contra 1.232,93 ha). Esses resultados não autorizam afirmar superioridade dos
modelos supervisionados sobre a continuidade recente da conversão mapeada.
As escolhas anteriores ao teste permanecem registradas, sem troca de vencedor.

Os erros cresceram nos intervalos com resposta em 2022 e 2023. Para R, o
XGBoost/T3 teve MAE de 0,6882 e 0,6394 p.p. em t=2019 e 2020; em t=2021
e 2022, 3,5519 e 4,2735 p.p. A subestimação é forte: viés global de
−1,8578 p.p. e de −3,9941 p.p. em t=2022. Isso descreve dificuldade diante
dos picos cartográficos; não demonstra aumento ambiental real na mesma medida,
nem permite separar mudança do processo ambiental de instabilidade de classificação.

As ablações mostram ganhos dos históricos em relação a T0 dentro da mesma
coorte, mas ganhos incrementais de T3 sobre T2 não são uniformes. Na coorte
2003, acrescentar focos em T4 não trouxe redução consistente de MAE entre os
quatro algoritmos. O resultado não justifica interpretar ausência de efeito
ambiental dos incêndios: os atributos representam registros observados de focos,
com limitações instrumentais e de cobertura, não área queimada harmonizada.

Na sensibilidade do vencedor principal para R, congelar os históricos em 2018
aumentou o MAE de 2,2883 para 2,7086 p.p.; para C, de 1.278,09 para
1.548,35 ha. Os modelos são os mesmos. A comparação evidencia dependência das
entradas recentes nesse experimento, sem provar ausência de informação futura
no processamento retrospectivo do produtor. Ela não representa uma simulação
operacional histórica completa.

No LOSO de R, o MAE variou de 1,0913 p.p. (RO, 20 observações) a 2,6366
p.p. (MA, 380). O composto micro foi 2,2110 p.p.; os modelos por estado
foram escolhidos sem a UF retida. Comparar diretamente esse valor com o teste
temporal não isola efeito espacial, porque modelos e conjuntos de ajuste diferem.
Houve três previsões negativas no fold MA de Elastic Net, preservadas e reportadas.

A conclusão sustentada é que há associação preditiva com a série mapeada,
sobretudo com sua continuidade recente, mas a generalização aos picos finais é
limitada. A contribuição científica deve incluir esse limite, a ausência de
estimativa representativa própria da acurácia de transições e a lacuna de
referência em 2023. Uma nova transformação ou protocolo motivado por estes
resultados exigiria nova decisão e avaliação independente; o teste encerrado
não poderá fundamentar uma nova alegação confirmatória sobre o mesmo suporte.
'''
    for nome in ['RESUMO_EXECUTIVO_MODELOS_COL9.md', 'TEXTO_RESULTADOS_DISSERTACAO_COL9.md']:
        arq = docs/nome
        with arq.open('a', encoding='utf-8') as f:
            f.write(adicional)
    tecnico = '''# Reprodução, testes e preservação

O protocolo JSON e seus dois scripts de congelamento/execução permaneceram
inalterados após o congelamento. As revisões técnicas v1–v3 antecederam os
ajustes científicos e resolveram exclusivamente a leitura segura de estruturas
de modelos: tipos numpy.dtype e sklearn.tree._tree.Tree foram explicitamente
revisados. Não houve mudança de fontes, grades, partições ou critério de escolha.
Uma interrupção da sessão durante o desenvolvimento foi retomada por grupo
concluído com hashes; tentativas incompletas foram preservadas no disco e não
entraram na avaliação final. O tempo do recibo de desenvolvimento corresponde
somente à retomada, portanto não é apresentado como tempo total de treinamento.

São 140 testes distintos aprovados: 70 no ambiente da aplicação, 55 no ambiente
geográfico e 15 na revisão ativa da modelagem. Repetições não foram somadas.
Os 16 avisos dos testes novos correspondem a uma coluna sintética inteiramente
ausente, incluída para verificar o comportamento do imputador. Os módulos
geográficos/modelagem são omitidos apenas nos ambientes que não possuem suas
dependências; cada grupo foi executado no ambiente apropriado. As três revisões
inativas têm testes marcados como descontinuados, sem substituir os anteriores.
Os ajustes sintéticos dos testes não constituem novos experimentos científicos.

O fechamento confere 108 grupos, 504 modelos finais e 191.760 linhas de
predições, incluindo coortes, respostas, estados e regimes. Essas linhas não são
observações independentes: o teste canônico possui 1.020 município–anos.
Parâmetros de normalização de y, medianas de imputação, tamanhos de ajuste e
exclusão das UFs foram recalculados independentemente para os 504 modelos.
As tabelas de cobertura por ajuste ficam em auditoria_final. A auditoria de
colunas não demonstra ausência de dependência futura do algoritmo cartográfico.

## Uso do pacote

Consultar primeiro MANIFESTO_FINAL_MODELOS_COL9.json e o recibo externo do ZIP.
Conferir SHA-256 antes de carregar modelos. Usar Python 3.14.6 e criar um
ambiente isolado com requirements-lock.txt, mantendo as fontes originais nos
caminhos dos manifestos. Os dados de desenvolvimento e teste, X e y, continuam
em arquivos separados; isso é separação lógica auditada, não um cofre inacessível
ao pesquisador que já explorou cientificamente os anos finais.

O pacote inclui modelos em skops e JSON nativo do XGBoost, sem pickle/joblib.
O carregador ler_modelo em modelagem/executar_regressao_col9_v4.py verifica
tipos desconhecidos contra a lista estrutural explicitamente revisada; não se
deve ampliar automaticamente essa lista. Tabelas/figuras podem ser lidas sem
carregar modelos. Os mesmos arquivos de previsões devem ser usados para novas
apresentações, sem nova abertura ou seleção no teste.

Para reprodução integral futura, usar diretórios novos nos argumentos --saida
e --checkpoint: primeiro protocolo_experimentos_col9_v4.py, depois os testes,
executar_regressao_col9_v4.py --fase desenvolvimento, auditar_ajustes_regressao_col9_v4.py,
interpretar_regressao_col9_v4.py --fase validacao e somente então --fase teste
no executor. Essa sequência não deve ser executada novamente no checkpoint
encerrado e não gera uma segunda avaliação independente. A fonte canônica
externa e as bibliotecas fixadas continuam necessárias; o pacote não duplica
os 159 GB de rasters, o banco ou o GeoPackage original. Caminhos dos artefatos
de modelo são relativos à raiz do repositório e devem permanecer assim.

## Pendências para discussão científica

Discutir a falta de ganho sobre a persistência, o aumento de erro nos picos
finais e o significado ambiental limitado da conversão mapeada. A homologação
de A/B/C permanece ausente. Novas fontes PRODES, área queimada e socioeconomia
continuam condicionadas à harmonização; não foram incluídas. Eventuais novos
experimentos precisam de protocolo e estratégia de avaliação que reconheçam o
teste já utilizado. Não há pendência de treinamento dentro do desenho autorizado.
Nenhum DOCX foi atualizado, banco alterado ou dashboard implantado nesta etapa.
'''
    with (docs/'REPRODUCAO_TESTES_PENDENCIAS_COL9.md').open('x', encoding='utf-8') as f:
        f.write(tecnico)
    with (docs/'ENTREGA_MODELOS_COL9.md').open('a', encoding='utf-8') as f:
        f.write('\n13. [Reprodução, testes e pendências](REPRODUCAO_TESTES_PENDENCIAS_COL9.md)\n')
    print('Revisão editorial e discussão científica concluídas; rascunhos preservados.', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint', type=Path, required=True)
    p.add_argument('--docs', type=Path, required=True)
    a = p.parse_args()
    executar(a.checkpoint, a.docs)
