# Reprodução, testes e preservação

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
