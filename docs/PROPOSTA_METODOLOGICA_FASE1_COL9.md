# Proposta metodológica da Fase 1 Coleção 9

Status: **D1–D4 aprovadas pelo pesquisador em 11 de novembro de 2026**.
A aprovação inclui a condição de preparar uma proposta específica de transições
espaciais e variável-alvo antes da modelagem. Os indicadores descritivos foram
implementados localmente; a aplicação em execução não foi substituída.
A legenda oficial e os dados originais permanecem inalterados.

## Escopo e evidências

Esta proposta define as escolhas necessárias para concluir a Fase 1 e orientar
os gráficos e mapas da Fase 2. Usa exclusivamente a Coleção 9, 1985–2023, e a
seleção fixa de 255 municípios no limite IBGE 2025. A existência de 39 mapas
representa um intervalo de 38 anos entre os extremos.

Fontes primárias consultadas:

- [MapBiomas Coleção 9 códigos e cores versão 2](https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2024/10/Legenda-Colecao-9-LEGEND-CODE_v2.pdf): nomes, códigos e hierarquia.
- [MapBiomas Coleção 9 descrição detalhada por bioma](https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_9/downloads/legends/Legenda-Colecao-9-Descricao-Detalhada-PDF-PT.pdf): significado das classes e casos mistos.
- [Imazon divulgação da Coleção 9](https://imazon.org.br/publicacoes/mapbiomas-colecao-9-mapeamento-anual-de-cobertura-e-uso-da-terra-no-brasil-de-1985-a-2023/): distingue vegetação nativa, água e áreas naturais não vegetadas na categoria mais ampla de áreas naturais.

Nenhuma classificação de tipo da Coleção 10.1 foi usada como autoridade.
A página atual do portal MapBiomas contém coleções mais recentes; as definições
aqui foram conferidas nos documentos específicos da Coleção 9.

## O que a documentação sustenta

Os cinco grupos temáticos oficiais são Floresta, Vegetação Herbácea e Arbustiva,
Agropecuária, Área não Vegetada e Corpo D'água, além de Não observado.
Esses grupos serão preservados na legenda original. Pertencer a um grupo
temático não define sozinho um indicador de antropização ou de vegetação nativa.

Na descrição específica da Col9, a classe 25 é mista no Cerrado; a classe 33
também inclui reservatórios; a 31 corresponde a instalações aquícolas/salinas;
a 21 pode incluir regeneração inicial; pastagem natural pode permanecer em 11/12.
As classes 29/32 têm particularidades de substrato e cobertura. Esses elementos
são documentados, mas as regras dos índices abaixo são **escolhas operacionais
da dissertação**, não índices oficiais fornecidos pelo MapBiomas.

## D1 Classificação operacional proposta

Manter dois campos independentes: `grupo_oficial_col9` e, somente após validação,
`categoria_operacional_defesa_v1`. Isso permite consultar a classificação original
sem confundi-la com a interpretação adotada no estudo.

| Categoria proposta | Códigos terminais Col9 | Tratamento recomendado |
|---|---|---|
| Vegetação nativa operacional | 3, 4, 5, 6, 49, 11, 12, 50 | Numerador principal de vegetação nativa mapeada |
| Ambientes naturais de substrato/cobertura particular | 23, 29, 32 | Separados da vegetação nativa operacional; não entram como uso antrópico |
| Usos antrópicos mapeados | 9, 15, 20, 21, 24, 30, 31, 35, 39, 40, 41, 46, 47, 48, 62 | Numerador de participação de usos antrópicos |
| Superfície de água de origem não discriminada | 33 | Categoria própria; não inferir origem natural ou artificial |
| Origem natural/antrópica indeterminada na classificação adotada | 25 | Separada; entra na análise de sensibilidade |
| Não observado | 27; também 0/NoData na máscara raster | Fora dos denominadores de área classificada e das transições |

Esses conjuntos particionam as 29 classes terminais da legenda local. Códigos
agregados não são somados junto com seus descendentes. Há 22 códigos observados
no consolidado atual; as demais classes não devem ser inventadas nem removidas
da referência por estarem ausentes da amostra.

### Escolha específica para apicum e afloramento

**Recomendação:** excluir 29 e 32 do indicador principal de vegetação nativa
operacional, mantê-los como ambientes naturais separados e publicar a sensibilidade
à inclusão dos dois. Isso não altera sua posição na hierarquia oficial, que os
inclui no grupo Vegetação Herbácea e Arbustiva. A exclusão é uma opção analítica
para explicitar o que o numerador representa, não uma correção da legenda oficial.

Alternativa para validação: usar todas as classes terminais dos grupos oficiais
Floresta + Vegetação Herbácea e Arbustiva: 3, 4, 5, 6, 49, 11, 12, 32, 29, 50.
Se escolhida, a definição deverá declarar expressamente a inclusão de 29/32.
Não atribuir à versão com oito classes o significado de fração botânica exata
ou de vegetação intacta: ela continua baseada em classes de pixels mapeados.

### Casos que não devem ser simplificados

- Silvicultura entra em uso antrópico; presença de árvores não implica vegetação nativa.
- Mosaico de Usos entra no uso antrópico **mapeado**, sem assumir uniformidade dentro do pixel ou descartar possíveis estágios iniciais de regeneração.
- Aquicultura entra no uso antrópico, embora pertença ao grupo temático de água.
- A classe 25 não será automaticamente antrópica, natural ou repartida em proporções arbitrárias; a composição por bioma exige evidência espacial adicional.
- A classe 33 não representa exclusivamente água natural. Não é possível separar reservatórios a partir de seu código apenas.
- Vegetação nativa mapeada não equivale a ausência de manejo, degradação, pastejo ou vegetação secundária.
- O grupo oficial Floresta inclui a classe 4 (Formação Savânica). Um futuro indicador de floresta em sentido estrito precisará de definição própria; não renomear automaticamente o grupo inteiro.

## D2 Denominadores e consistência territorial

Definir, para município m e ano t:

- `A_classificada(m,t)`: soma de áreas de todas as classes terminais observadas,
  excluindo 27 e pixels 0/NoData. **Incluir 25 e 33** nessa soma.
- `A_VN(m,t)`: área do conjunto de vegetação nativa validado em D1.
- `A_UA(m,t)`: área do conjunto de usos antrópicos da tabela.
- `A_25(m,t)`: área da classe 25, sem conversão de seu significado.
- `A_territorio(m)`: área do limite municipal IBGE 2025, com método geodésico
  documentado e compatível com o usado nos numeradores.

**Recomendação para o primeiro painel:** usar `A_classificada` como denominador
dos percentuais temáticos e mostrar também as áreas em hectares. O denominador
permanece completo quando o usuário seleciona uma classe: selecionar só pastagem
não transforma seu percentual em 100%. Não excluir água ou classe 25 para
melhorar artificialmente o resultado.

Para estado ou conjunto de municípios, calcular `100 * soma(numeradores) /
soma(denominadores)`. Não usar média simples dos percentuais municipais.
Não somar hectares de anos diferentes como se fossem uma área única.

Percentual sobre a área territorial fixa é uma medida diferente e pode ser útil
à dissertação, mas fica condicionado à auditoria do denominador geométrico.
O atual `perc_ocupacao` será preservado como percentual de origem, sem substituição
silenciosa por novos percentuais.

### Evidência local que impede equiparar os denominadores agora

Uma apuração exploratória somente leitura do CSV original encontrou somas dos
percentuais de origem entre **98,1229% e 99,9980%** nos 9.945 pares município–ano;
2.963 pares ficam abaixo de 99%. O script de cobertura inspecionado usa área
geodésica WGS84 e lê AREA_GEOM_KM2 como referência externa.

Isso demonstra uma diferença a auditar, **não prova a sua causa**. Ela pode
envolver método de área, máscara raster, recorte ou outros fatores. Não atribuir
todo o resíduo a NoData, nem converter essa razão em indicador de completude antes
de conferir o cálculo de AREA_GEOM_KM2. Se for adotado percentual territorial,
validar o método e a cobertura espacial antes de publicar o indicador.

O limite 2025 será fixo para todos os anos, inclusive municípios criados depois
do início da série. Isso é uma reconstrução histórica sobre geografia constante,
não uma afirmação sobre limites administrativos vigentes em 1985. Na Fase 2,
consultas, filtros, contornos e estatísticas usarão exclusivamente esse cadastro;
geometrias simplificadas servirão apenas ao desenho.

## D3 Indicadores propostos

| Indicador | Fórmula | Interpretação e condição |
|---|---|---|
| Participação de vegetação nativa mapeada | `P_VN = 100 * A_VN / A_classificada` | Composição temática na área classificada; conjunto D1 deve aparecer nos metadados |
| Participação de usos antrópicos mapeados | `P_UA = 100 * A_UA / A_classificada` | Proxy descritiva de ocupação; não mede intensidade de pressão, impacto ou legalidade |
| Sensibilidade à classe 25 | de `P_UA` até `100 * (A_UA + A_25) / A_classificada` | Cenários de exclusão/inclusão da classe 25; não é intervalo de confiança nem limite da antropização real |
| Variação líquida de área | `A(t2) - A(t1)` | Estoque líquido; não é perda bruta, desmatamento ou transição pixel a pixel |
| Variação de participação | `P(t2) - P(t1)` | Pontos percentuais |
| Variação relativa de área | `100 * (A(t2)/A(t1) - 1)` | Somente se a área inicial for positiva; caso contrário NA |

**Recomendação de nome:** usar "Participação de usos antrópicos mapeados (%)".
Se for mantido "Índice de antropização", defini-lo como essa mesma proporção
simples e identificá-lo como indicador operacional da dissertação. Não atribuir
pesos a agricultura, pastagem, mineração etc. sem fundamentação e validação própria.

Os dois percentuais principais não precisam somar 100%: há água, ambientes naturais
separados e classe 25. Denominador zero ou fonte ausente resulta em NA, nunca em zero.
Ausência de linha para uma classe só poderá ser tratada como zero depois de
confirmar que o par município–ano está observado e que o código é válido.

No primeiro incremento, não incluir taxa composta como indicador principal. Se
necessária depois, a taxa entre 1985 e 2023 usa **38 intervalos anuais**, áreas
positivas e interpretação de estoque, não 39 intervalos.

## D4 Comparações e limitações

Recomenda-se média anual das áreas para gráficos por década, informando número
de anos: 1985–1989 tem cinco, 1990–1999/2000–2009/2010–2019 têm dez e 2020–2023
tem quatro. A comparação de extremos usa os anos efetivamente escolhidos.

Para mudanças de área agregada, preservar o aviso sobre máscara de 2002. Para
transições espaciais, exigir pixels válidos nos dois anos e auditar o intervalo
2001–2003 em Buriticupu. Essas transições e sua validação não estão concluídas
por esta proposta. Não chamar diferença de estoque de desmatamento PRODES.

A classe 62 mantém a identificação beta. As estimativas são de cobertura
mapeada, sem equivalência automática a observação de campo ou precisão perfeita.
Nenhum resultado deste módulo deve misturar o cadastro legado de 268 municípios,
PNGs de outra coleção ou o ano 2024.

## Dimensão das escolhas na base atual

Resultados exploratórios sobre a soma das áreas classificadas de todos os 255
municípios, sem homologar nenhum indicador científico:

| Ano | Área classes 29+32 (ha) | Sua participação na área classificada | Área classe 25 (ha) | Sua participação na área classificada |
|---|---:|---:|---:|---:|
| 1985 | 261.791,8198 | 0,332458% | 249.919,2506 | 0,317381% |
| 2023 | 260.266,2528 | 0,330521% | 332.974,5573 | 0,422856% |

Em 2023, incluir 29/32 no numerador de vegetação altera o percentual regional em
cerca de 0,331 ponto percentual; incluir 25 no uso antrópico altera o percentual
regional em cerca de 0,423 ponto percentual. Efeitos municipais podem ser maiores;
valores regionais não autorizam ignorar a sensibilidade local.
O [registro da apuração](evidencias/fase1_sensibilidade_metodologica_20261111.json)
identifica o consolidado verificado no checkpoint, sem modificar a fonte.

## Validação solicitada antes de implementar os indicadores

| Decisão | Proposta recomendada | Alternativa explícita |
|---|---|---|
| D1 Vegetação nativa | Oito classes; 29/32 separados, com cenário ampliado | Dez classes dos dois grupos oficiais; inclusão de 29/32 declarada |
| D2 Percentuais | Denominador área classificada, com hectares e auditoria geométrica separada | Percentual territorial fixo, condicionado à validação prévia do método de área |
| D3 Usos antrópicos | Conjunto da tabela; 25 separada e cenário de sensibilidade; nome descritivo | Mesmo conjunto sob o nome Índice de antropização, com fórmula e limites explícitos |
| D4 Décadas | Média anual, com períodos incompletos identificados | Comparação entre anos de referência, identificando a duração dos intervalos |

O pesquisador aprovou o conjunto recomendado D1–D4. A classificação operacional
foi versionada em referencias/metodologia_col9.json, separada da legenda oficial.
A definição do alvo continua pendente da proposta específica e de validação própria.

## Relatório do incremento de proposta anterior à aprovação

Foram preparados esta proposta e o registro exploratório, com acréscimo no diário
de decisões. Não houve mudança de código produtivo, SQL, testes existentes ou
configuração do app. As verificações deste incremento foram documentais,
conferência dos 29 códigos e apuração decimal do CSV original.
Conferiu-se também que os seis conjuntos propostos cobrem os 29 códigos da
legenda sem sobreposição, que o JSON é válido e que a soma 29+32 de 2023 coincide
com a tabela. Não foi executada
uma nova suíte automatizada; os 36 testes aprovados pertencem ao checkpoint anterior.
A Fase 1 permanece aberta até validar as decisões e implementar/testar o contrato
metodológico. A Fase 2 ainda não foi iniciada neste incremento. Implantação será
apresentada antes de qualquer alteração da aplicação em execução.
