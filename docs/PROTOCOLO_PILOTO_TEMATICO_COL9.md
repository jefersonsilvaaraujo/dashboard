# Protocolo operacional proposto do piloto temático

Continuidade do checkpoint Col9. Proposta preparada e materializada para
validação do pesquisador; os avaliadores ainda não responderam. Nenhuma
acurácia, limiar, resposta municipal ou treinamento é homologado por este piloto.

## Objetivo e seleção preservada

Testar a viabilidade da interpretação independente, clareza das categorias,
resolução/sazonalidade, cobertura histórica, esforço e tratamento de inconclusivos.
Não estimar acurácia representativa dos 255 municípios com o piloto isolado.

Dos 3.744 pontos probabilísticos existentes, foram sorteados **120**, um em
cada um dos **120 estratos originais** (UF×período×magnitude×estabilidade).
A seleção ocorre antes da consulta de imagens. Nenhum ponto dirigido entrou
no piloto. Não foram refeitos o sorteio dos municípios–anos, os subestratos de
pixels, as probabilidades ou os pesos da amostra-pai.

Dentro de cada estrato da amostra realizada, a ordenação pseudoaleatória é
determinada por SHA256 com semente fixa `DefesaMestrado-piloto-20261111-v1`.
O primeiro ponto compõe o piloto; os demais têm ordem de ampliação pré-fixada.
São 114 estratos com 32 pontos disponíveis e seis com 16. A probabilidade
**condicional à amostra-pai realizada** é 1/32 ou 1/16. Não usar essa seleção
de um ponto por estrato como desenho inferencial definitivo nem multiplicar
probabilidades condicionais para inventar pesos finais sem derivação multifásica.
Os pesos originais permanecem na gestão técnica, separados da ficha cega.

Composição técnica, não fornecida aos avaliadores:

| Dimensão | Quantidade |
|---|---|
| UF | MA31, MT30, TO27, RO18, PA14 |
| Período do destino | 1986–1999:23; 2000–2009:23; 2010–2019:23; 2020–2021:20; 2022:16; 2023:15 |
| Subestratos de pixel originais | VN→UA34; VN→outros30; outras origens→UA32; outras origens→outros24 |

Essas composições resultam do sorteio dentro dos estratos, sem forçar uma
distribuição de respostas esperadas. Os quatro subestratos estão presentes.
Uma amostra de 120 pontos não cobre todos os 255 municípios individualmente;
o universo e os pesos da amostra original não são redefinidos por essa limitação.

## Blindagem e organização

Cada ponto recebe alias P001…P120 sem município, classe, estrato ou magnitude
codificados. Os dois avaliadores recebem os mesmos casos/imagens e ordens de
apresentação diferentes. Os pacotes não incluem classes MapBiomas, matrizes,
taxas, limiares, pesos, notas dirigidas ou respostas do outro avaliador.
Coordenadas e anos são necessários para interpretar a referência e permanecem
visíveis. Isso é cegamento em relação ao produto avaliado, não anonimato geográfico.

Entregar somente o ZIP A ao avaliador A e somente o ZIP B ao avaliador B.
`gestao_restrita/` contém a ligação com a amostra-pai e a ordem futura, não deve
ser enviada. “Restrita” é uma convenção de organização, não controle de acesso
do sistema operacional. O pesquisador deve guardar os pacotes e respostas em
locais separados. Nenhum envio a pessoas foi realizado automaticamente.

Cada pacote tem ficha CSV, instruções, índice HTML, pranchas, pixels GeoJSON,
GeoTIFFs e metadados das cenas, além de manifesto/hash. Casos sem imagem
continuam na lista e têm indicação de indisponibilidade, sem substituição.
Os arquivos de resposta iniciais ficam vazios. Preservar versões e adicionar
respostas em cópias datadas; nunca sobrescrever a interpretação independente.

## Referências e pranchas

Consultar t e t+1 entre 1985–2023. Não consultar ou incorporar 2024.
Sentinel-2 é priorizado a partir de 2016, Landsat nos anos anteriores; em caso
de falha Sentinel na janela principal, tentar Landsat no mesmo caso/ano.
Landsat tem janela anual; Sentinel principal maio–outubro. Para anos ≥2020,
adicionar consulta novembro/dezembro. Esses limites são orçamento de busca,
não definição de ausência de imagem em todo o acervo mundial.

Até 24 cenas por consulta e seis tentativas por fonte/janela. Ordenação por
nuvens na janela principal e data recente no complemento. As tentativas,
falhas HTTP/QA, cenas e datas ficam registradas; nenhuma falha sorteia outro ponto.
As consultas usam catálogos públicos
[Earth Search](https://element84.com/earth-search/) e
[Planetary Computer](https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/).
Assinaturas temporárias de leitura ficam somente em memória, sem credenciais no pacote.

A seleção automática verifica QA nas células que tocam o footprint completo,
não só no centro, e também o QA central. Sentinel usa SCL4/5/6; Landsat exclui
fill/cloud/dilated/cirrus/shadow/snow conforme bits documentados pelo
[USGS](https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands).
O QA é triagem de referência, não rótulo temático. Névoa, sombras e mistura
podem escapar. Saturação/radiometria e registro entre sensores exigem revisão.

GeoTIFFs mantêm CRS e transformada; bandas Landsat são DN com escala/offset
documentados e Sentinel é TCI8bits. Pranchas usam visualização RGB e delimitam
os quatro cantos da célula Col9 projetados na cena, com contexto e zoom.
O footprint é exato para a grade nominal, mas não corrige erro de registro
entre sensores. A referência ainda deve sustentar a cobertura do pixel inteiro.

## Procedimento dos avaliadores

Usar [instruções padronizadas](INSTRUCOES_AVALIADORES_PILOTO_COL9.md).
Interpretar cada ano antes de comparar, registrar VN/UA/OUTROS/INCONCLUSIVO,
confiança, mistura, georregistro, cenas, justificativa, limites temporais e tempo
ativo. Não exigir resposta conclusiva por prazo. A conversão interpretada do
pixel não é o desfecho municipal homologado.

Antes da coleta, calibrar instruções em exemplos **fora** destes 120 pontos,
sem revelar a classe do mapa. Cada avaliador trabalha sem consultar o outro.
Após entregar respostas individuais, a gestão pode produzir uma lista de
divergências para adjudicação, com registro separado de decisão/motivo/versão.
Concordância entre avaliadores é diagnóstico do protocolo, não acurácia do mapa.

Casos sem referência, nublados, com lacuna SLC-off, pixel misto, manejo não
identificável, datas inadequadas ou registro incerto permanecem inconclusivos.
Solicitar complemento no mesmo ponto; se não resolver, conservar a não resposta.
Landsat compartilha sensor com a Col9 e pode ter erros correlacionados;
Sentinel não é verdade de campo. Alta resolução/contexto não certifica uso nativo
versus plantado sem evidência adequada. Não comparar só cores ou supor que toda
abertura é pastagem. Nenhuma classificação dos avaliadores foi preenchida por IA.

## Esforço previsto, ainda não medido

O piloto tem 66 casos com ano de destino até 2015 e 54 recentes. Hipóteses de
planejamento: 15–25 minutos por caso histórico e 8–12 por caso recente, para
cada avaliador, incluindo consulta à ficha/evidências existentes. Resultado:

| Atividade | Horas-pessoa estimadas |
|---|---:|
| Interpretação individual dos120 por avaliador | 23,7–38,3 |
| Duas interpretações independentes | 47,4–76,6 |
| Calibração comum sem revelar o mapa | cerca de4 |
| Conferência de fichas/arquivos | 2–4 |
| Adjudicação e complementação | 6–16, dependente das dificuldades |
| Orçamento inicial total | aproximadamente60–100 |

Não são tempos observados nem compromisso de precisão. Registrar minutos
ativos e interrupções permitirá revisar o orçamento. Busca externa extensa e
referência de campo podem excedê-lo. Propor sinalização ao gestor ao atingir
20 minutos em caso recente ou 30 em histórico, sem impor resposta ou substituição.

## Critérios propostos de revisão/ampliação

Limites abaixo são **gatilhos de planejamento a aprovar**, não padrões oficiais:

1. Ausência de par de imagens/alta proporção de inconclusivos, por exemplo >20%
   no piloto ou em um domínio UF/período, ou um domínio sem qualquer resposta:
   priorizar referência adicional nos mesmos pontos e revisar orçamento.
2. Divergência entre avaliadores >20%, ou padrão de divergência em campos
   naturais/pastagens e bordas: rever definições/calibrar em exemplos externos,
   versionar instruções e repetir respostas afetadas preservando as originais.
3. Problema de georregistro recorrente: auditar o procedimento; não deslocar
   seletivamente pontos para obter concordância. Completar suporte antes de expandir.
4. Tempos acima do orçamento ou grandes diferenças entre épocas: atualizar
   estimativa e capacidade, sem retirar da ficha os casos difíceis.
5. Se o protocolo estiver estável e houver recursos/aprovação, propor rodada2
   com a próxima posição congelada **em cada** estrato, adicionando120 casos da
   amostra-pai. Não ampliar somente estratos com imagens fáceis nem usar o ponto
   seguinte como substituição do inconclusivo anterior. Novas rodadas são adição.

Uma avaliação representativa posterior precisará definir precisão-alvo para
comissão/omissão e área de conversão, resposta por domínio, não resposta e
variância compatível com os dois estágios originais. Completar a amostra-pai
é alternativa distinta de expandir o piloto. Reusar interpretações requer
protocolo compatível, trilha de versões e análise do desenho; não assumir que
120 pontos com uma unidade por estrato permitem estimar variância de acurácia.
Os princípios de
[Olofsson et al. (2014)](https://doi.org/10.1016/j.rse.2014.02.015) orientam o
desenho/resposta/inferência, sem fixar os gatilhos acima.

## Reprodução e dependências

Seleção: `processamento/piloto_interpretacao_col9.py`; aquisição:
`referencias_piloto_col9.py`; montagem: `pacote_avaliadores_col9.py`.
Usar ambiente geoespacial anterior com Pillow; versões efetivas constam do
checkpoint. Comandos de exemplo para nova pasta, sem sobrescrever:

```powershell
python processamento/piloto_interpretacao_col9.py --amostra validacao_cientifica_col9/checkpoint_20261111/amostragem --saida validacao_cientifica_col9/NOVO_PILOTO
python processamento/referencias_piloto_col9.py --piloto validacao_cientifica_col9/NOVO_PILOTO --manifesto referencias/manifesto_rasters_transicoes_col9.json --workers 3
python processamento/pacote_avaliadores_col9.py --piloto validacao_cientifica_col9/NOVO_PILOTO --instrucoes docs/INSTRUCOES_AVALIADORES_PILOTO_COL9.md --saida validacao_cientifica_col9/NOVO_PILOTO/pacotes
```

Aquisição tem checkpoints por caso e confere hashes ao retomar; protocolo alterado
exige novo lote. Uma tentativa parcial não é removida/substituída silenciosamente.
O sorteio e os arquivos cegos podem ser reproduzidos sem rede. A aquisição remota
pode mudar; conservar metadados/recortes/hashes preserva a evidência desta execução.
O banco e o dashboard não participam dessas rotinas.
