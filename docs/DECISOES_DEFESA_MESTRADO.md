# Decisões e checkpoints Defesa Mestrado

## Continuidade — piloto e experimento retrospectivo definidos pelo pesquisador

Entrega computacional aprovada provisoriamente, validação temática aberta,
nenhum A/B/C homologado. O pesquisador definiu predição retrospectiva temporal
e espacial como experimento principal, sem alegação operacional histórica.
2024 continua reservado para uso metodológico separado. Treinamento definitivo
e desfecho binário homologado permanecem não autorizados.

Preparada proposta de120 pontos probabilísticos, um por estrato original,
sem substituição por disponibilidade, com320 recortes, pranchas/GeoTIFFs e
dois pacotes cegos em ordens diferentes. Nenhuma resposta foi preenchida.
Nota de relevância/persistência explicita t+2/t+3, redução do período e
impossibilidade de usar2024 automaticamente. Protocolo retrospectivo mantém
255×38, catálogo de blocos e partições temporal/LOSO, registrando que o teste
não é completamente cego à formulação científica do evento.

89 testes distintos aprovados (70 principais +19 geoespaciais); acervo anterior,
banco e aplicação preservados. Documentação, limitações, pacotes ativos e
aprovações ainda necessárias no
[relatório do piloto](PENDENCIAS_DECISOES_PILOTO_COL9.md).

## 11 de novembro de 2026 Validação temática e avaliação A/B/C

Executada a avaliação dos candidatos solicitados (0,25%/25 ha, 0,50%/100 ha,
1%/250 ha), AND, três níveis de elegibilidade e seis variantes de classes.
Tabelas globais/ano/UF/município e casos próximos/discordantes em saídas novas.
Sorteados 234 pares probabilísticos em 120 estratos e 3.744 pontos, além de
33 pares dirigidos/528 pontos. Acervo Mapas-Estudo inventariado conforme indicação
do pesquisador; classificações derivadas não foram promovidas a referência independente.

Referências Sentinel/Landsat e complementos de fim de ano foram adquiridos e
inspecionados, com mudanças tardias compatíveis e casos ambíguos documentados.
As respostas probabilísticas permanecem pendentes e não há estimativa de acurácia
ou recomendação definitiva de tau/A_min. A interpretação visual assistida por IA
é preliminar e separada das fichas cegas propostas para adjudicação.

Especificação/índices de treino preparados sem Y, com 2023 sem desfecho.
Disponibilidade efetiva e retrospectividade da Col9 explicitadas; partições
temporal/LOSO propostas, sem alegar teste totalmente cego após exploração científica.
Regressão: 77 testes distintos (61 principais +16 geoespaciais) passaram.
Nenhuma escrita no banco, modificação do dashboard ou alteração do acervo
consolidado/rasters/checkpoints anteriores. Relatórios e pendências no
[checkpoint A/B/C](ENTREGA_VALIDACAO_CIENTIFICA_COL9.md).

## 11 de novembro de 2026 Transições espaciais e implantação autorizada

Entrada atual do diário; as entradas abaixo preservam o estado histórico de
cada checkpoint, inclusive as referências à implantação então pendente.

O pesquisador aprovou provisoriamente as Fases 1/2 e a identificação pixel a
pixel como ponto de partida. Autorizou matrizes completas para 255 municípios,
1985–2023, em suporte válido comum. Não autorizou tau/A_min definitivos,
variável-alvo binária ou treinamento. A execução, auditoria de Buriticupu e
sensibilidades estão documentadas no
[protocolo](PROTOCOLO_TRANSICOES_COL9.md) e no
[relatório exploratório](RELATORIO_EXPLORATORIO_TRANSICOES_COL9.md).

O procedimento de implantação foi apresentado e o pesquisador confirmou
“Sim, implantar somente o app”. A implantação foi concluída, com retorno
preparado, mantendo a identidade do contêiner PostgreSQL e seu volume.
Verificações HTTP e testes funcionais da página Col9 e legado passaram na
imagem implantada. A ferramenta de navegação bloqueou a conferência visual
por não conseguir confirmar com segurança a URL; essa etapa permanece pendente.
Evidências e limitações no
[relatório de implantação](RELATORIO_IMPLANTACAO_COL9_20261111.md).

Regressão científica/aplicação: 51 testes principais e 12 geoespaciais passaram
(63 distintos; dois módulos são ignorados no ambiente principal e executados
no geoespacial). Nenhum ETL, migração, exclusão, substituição de tabela ou
treinamento foi executado. Fontes brutas, banco e código do painel legado
permanecem preservados. As próximas decisões são científicas, não ajuste de
limiares para balancear classes ou maximizar desempenho futuro.

## 11 de novembro de 2026 Aprovação D1–D4 e implementação das Fases 1 e 2

O pesquisador aprovou D1–D4 com área classificada como denominador, sensibilidades
29/32 e 25, médias anuais por década e separação entre classificação oficial e
operacional. A classificação foi implementada em referencias/metodologia_col9.json
e analise_col9.py. O nome principal é Participação de usos antrópicos mapeados (%).

A condição adicional de modelagem foi registrada em
[proposta de variável-alvo](PROPOSTA_VARIAVEL_ALVO_CONVERSAO_COL9.md): conversão
pixel a pixel em máscara comum, taxa relativa à vegetação inicial elegível,
validação do limiar e auditoria de Buriticupu. Nenhum alvo/limiar foi consolidado.

Relatórios de aceite local e limitações:

- [Fase 1](RELATORIO_FASE1_COL9.md): metodologia e auditoria independente dos 9.945 pares município–ano.
- [Fase 2](RELATORIO_FASE2_COL9.md): cinco abas, gráficos, filtros, mapas municipais e PNGs Col9 1985/2023.

Verificação territorial: 255 geometrias originais do banco idênticas às do
GeoPackage por SHA-256 de WKB NDR. A aplicação agora recusa divergência desse
contrato. Mapas regionais têm hashes e passam por verificação de proveniência.

Resultados: 52 testes distintos aprovados em lotes (49 na suíte principal, dois
geoespaciais e um adicional de integridade de imagens), além de smoke test em
Python 3.12. App.py/dados.py legados mantiveram seus hashes. Banco, dados e app
em execução preservados. Nenhuma migração, carga ou implantação foi executada.

O procedimento de implantação e retorno foi apresentado no relatório F2, ainda
sem execução. As Fases 3–5 e a validação da proposta de alvo continuam abertas.

## 11 de novembro de 2026 Proposta científica da Fase 1

Preparada a [proposta metodológica Col9](PROPOSTA_METODOLOGICA_FASE1_COL9.md),
com decisões D1–D4 para validação pelo pesquisador antes da implementação:
vegetação nativa operacional, tratamento de 25/29/32/33, usos antrópicos,
denominadores e indicadores derivados. A hierarquia oficial Col9 é preservada.
Foram consultados os documentos específicos da Col9 de códigos e de descrição
por bioma, sem inferir equivalência com a Coleção 10.1.

Apuração somente leitura do consolidado registrou a sensibilidade das escolhas
e uma diferença entre soma de percentuais de origem e 100%. A causa ainda não foi
atribuída; não chamar todo o resíduo de NoData. Evidência em
[JSON exploratório](evidencias/fase1_sensibilidade_metodologica_20261111.json).

Arquivos novos: esta proposta e o JSON de evidências; este diário foi atualizado.
Nenhum código produtivo, teste, dado, legenda, SQL ou serviço foi alterado neste
incremento. Não houve nova execução dos testes automatizados. O resultado de
36 testes do checkpoint anterior permanece histórico. A Fase 1 ainda não está
concluída: aguarda a validação metodológica solicitada pelo usuário e, depois,
implementação e testes. A Fase 2 aguarda essa definição.

## 11 de novembro de 2026 Fase 0 e primeiro incremento da Fase 1

O [diagnóstico](DIAGNOSTICO_FASE0.md) registra o inventário, divergências,
dependências entre abas e a sequência de aceite. As fases posteriores permanecem
abertas; este checkpoint não declara o painel integrado nem a modelagem Col9 validados.

### Decisões e alterações

- Preservar app.py, dados.py, sete migrações antigas, cadastro dos 268, todas as
  tabelas/views, rasters, CSVs e PNGs legados. Nenhuma carga ou migração executada.
- Separar contratos `col9_255_1985_2023` e `legado_10_1` em contratos_series.py.
  A página escolhe explicitamente COL9.id e o módulo recusa outra identidade.
  A leitura não admite fallback silencioso para as fontes legadas.
- Centralizar consultas Col9 em dados_col9.py, com cache de 30 minutos; consultas
  estáticas sem interpolação de parâmetros da UI. A validação usa o cadastro
  independente, não só contagens. Código IBGE identifica os municípios nos filtros.
- Versionar 29 classes terminais e proveniência da legenda oficial. Os 22 códigos
  observados têm cobertura. A paleta da classe 6 foi corrigida apenas na Col9.
  O tipo natural/antrópico e os índices científicos continuam sem homologação.
- Guardar NUMERIC no banco; converter para float8 só na leitura de visualização.
  Teste no banco confirma a recuperação das quatro casas decimais ao arredondar.
  Não recalcular áreas por pixels * 0,09: o processamento original usa área geodésica.
- Exportar metadados da série, fonte da legenda, hashes do CSV/GPKG/script e a
  ressalva Buriticupu 2002. [Manifesto de 81 fontes](evidencias/fontes_col9_sha256_20261111.csv)
  inclui os 78 CSVs; os hashes não certificam a igualdade pixel a pixel dos rasters.
- Suprimir detalhes internos de exceções SQL na página. Manter mensagens de
  integridade específicas e aviso da revisão metodológica pendente.
- Acrescentar alerta ao README e à orientação dos testes: ETL padrão substitui
  dados legados e não é pré-requisito para testar uma base já carregada.

### Validação executada

| Verificação | Resultado |
|---|---|
| Auditoria SQL em READ ONLY | 113364/255/39/1985–2023, cinco UFs, sem duplicações/lacunas, 255 geometrias válidas EPSG:4674 |
| Legado | 268 municípios preservados; app e db healthy; hashes locais app.py/dados.py iguais aos da imagem |
| Permissões | dashboard_app/dashboard_leitura com SELECT/USAGE e sem escrita nos objetos auditados |
| Regressão preexistente | 16 testes passaram em 331,86s, incluindo CSV/banco e AppTest de todas as abas |
| Contrato e integração Col9 | 19 testes passaram em 265,07s: adulterações, completude, identidade, domínios, precisão, privilégios e UI |
| Unitários isolados | 16 passaram em 1,78s, executados para acompanhar a demora da suíte local |
| Python 3.12 | AppTest em contêiner temporário usando a imagem app e checkout montado :ro; 255 municípios, filtro IBGE, seleção vazia e proveniência passaram |
| Paridade com consolidado original | 1 teste passou em 262,83s; SHA-256 do consolidado e todas as 113.364 linhas conferidos, tolerância absoluta 0,00005 e sem tolerância relativa |
| git diff --check | Sem erros de whitespace; Git avisa apenas sobre conversão LF/CRLF |

Logs: [legado](evidencias/fase0_testes_legado_20261111.txt),
[Col9](evidencias/fase1_testes_20261111.txt),
[paridade consolidado](evidencias/fase1_paridade_consolidado_20261111.txt),
[contêiner final](evidencias/fase1_container_20261111.txt).
Os avisos de contexto Streamlit em execução de testes não são erros de aplicação.
O PowerShell registrou a saída informativa stderr do Docker como NativeCommandError
no log do contêiner, mas o comando terminou com exit code 0 e todas as asserções passaram.
Os três usos de use_container_width da página nova foram atualizados para width='stretch'.

O venv original não foi alterado.
O total deste checkpoint é de **36 testes distintos aprovados** (16 legados,
16 unitários Col9 e quatro de integração Col9), além da verificação no contêiner.

Para reproduzir os testes locais deste checkpoint,
as dependências ausentes foram instaladas em pasta temporária. Preparação equivalente
em um ambiente de desenvolvimento próprio:

```powershell
# Instalar requirements-dev.txt em ambiente de desenvolvimento separado.
# A base já deve existir. Não executar ETL como parte deste roteiro.
python -m pytest testes/test_paridade.py -q
python -m pytest testes/test_contratos_series.py testes/test_col9_integracao.py -q
```

A auditoria pode ser repetida no contêiner com os nomes de banco/papel verificados
neste ambiente; o script inicia sua própria transação somente leitura:

```powershell
Get-Content -Raw -Encoding UTF8 db/auditoria/fase0.sql | docker exec -i dashboard-mestrado-db-1 psql -X -U dashboard_admin -d dashboard -v ON_ERROR_STOP=1
```

O teste de paridade Col9 procura o consolidado em MESTRADO_DADOS ou na pasta-mãe
do checkout; registra skip se o arquivo externo não estiver disponível. Os testes
de banco usam a configuração do app já adotada por test_paridade.py e não imprimem
valores de credenciais. O SQL de auditoria requer administrador para o catálogo;
as consultas são protegidas por transação somente leitura.

### Implantação e reversão

As alterações são locais. **A imagem do app em execução não foi reconstruída nem
substituída.** Os contêineres temporários de verificação foram removidos ao terminar.
O dashboard servido continua na versão anterior, saudável.

O checkpoint de fontes e os hashes estão descritos no diagnóstico. Para desfazer
somente este incremento, comparar e restaurar seletivamente README.md,
testes/test_paridade.py e pages/01_Colecao_9_255.py a partir do ZIP. Retirar do
checkout apenas os módulos/referências/testes novos deste incremento, após conferir
que não receberam edições posteriores. Não usar git reset/clean nem restauração
global, pois havia conteúdo do pesquisador sem rastreamento. Nenhum rollback SQL
é necessário: o banco não foi modificado.

Quando for feita a implantação do app, conservar a imagem anterior e reconstruir
somente esse serviço. O código novo é copiado pelo Dockerfile, incluindo pages/ e
referencias/. Os comandos de implantação previstos, ainda não executados, são:

```powershell
docker compose build app
docker compose up -d --no-deps app
docker compose ps
```

Não executar etl, down -v ou recriação do banco. Antes de qualquer futura migração,
fazer backup durável do PostgreSQL e verificar a restauração em instância isolada.

### Pendências e condições para os próximos incrementos

1. Concluir F1 científica: descrição detalhada e classificação operacional das
   classes, tipos, denominadores e regras de índices. O PDF de códigos só sustenta
   códigos, nomes, grupos e cores, não uma taxonomia natural/antrópico completa.
2. Completar F2: percentuais, décadas, comparação 1985–2023, mapa vetorial e mapas
   temáticos com proveniência Col9, sem reinterpretar PNGs legados.
3. F3: recuperar as quatro entradas ausentes de PRODES/queimadas e auditar a
   geometria/ano dos demais 251; presença de registros não prova comparabilidade.
   Não preencher ausências com zero e não reaproveitar denominadores antigos.
4. F4: construir painel/vizinhança independentes, testar máscara comum de pixels
   válidos e sensibilidade de 2002, definir alvo e validação temporal/espacial.
5. F5: versionar bootstrap Col9 por estado/proveniência sem reimportar fatos
   existentes, backup restaurável, testes em checkout limpo e implantação controlada.
