# Nota científica — ocorrência e relevância da conversão

Encaminhamento do pesquisador: nenhum limiar A/B/C homologado; experimento
principal retrospectivo, horizonte t+1; 2024 reservado; sem treinamento definitivo
ou desfecho binário homologado. Esta nota apresenta alternativas para decisão,
sem alterar matrizes, estoques ou o significado aprovado de VN/UA.

## Ocorrência não determina relevância

No suporte válido comum de t e t+1, C é a área mapeada de VN(t)→UA(t+1),
D é a vegetação nativa inicial elegível e R=100 C/D. Os 9.690 pares calculados
têm C>0; assim, um indicador de simples ocorrência produziria evento em todas
as comparações desse acervo. Isso descreve o suporte mapeado; não comprova
ausência de erro, relevância ecológica ou confirmação em referência independente.
Uma tarefa de ocorrência binária nesse suporte tem pouca variação observada,
mas isso não autoriza inventar um limiar para obter classes equilibradas.

“Conversão relevante” precisa de uma hipótese sobre magnitude, estoque inicial,
localização, formação vegetal, duração e consequências. Não equivale a
significância estatística, infração legal, desmatamento PRODES ou diferença
líquida de estoques. A mesma perda pode ser pequena na área regional e crítica
para um remanescente local; nenhuma área/percentual isolado mede biodiversidade.

## Alternativas conceituais a avaliar

| Alternativa | Pergunta ambiental | Benefício | Limitação/decisão necessária |
|---|---|---|---|
| Ocorrência C>0 com referência válida | Houve algum pixel de conversão? | distingue existência de magnitude | sensível a poucos pixels/erros; todos os pares atuais são positivos mapeados |
| Magnitude contínua C e R | Quanto se converteu e qual fração do estoque? | preserva informação e evita dicotomia prematura | distribuição assimétrica, suporte e erro precisam tratamento; objetivo alternativo exige aprovação |
| Limiar relativo R≥tau | A pressão anual sobre o estoque inicial excedeu uma fração substantiva? | comparabilidade relativa | denominadores pequenos e diferenças entre formações podem dominar |
| Limiar absoluto C≥A_min | A área municipal convertida excedeu uma escala de interesse? | leitura direta em hectares | favorece municípios grandes; soma dispersa não é mancha contínua |
| Conjunção relativa **e** absoluta | A perda satisfaz simultaneamente pressão e escala mínimas? | reduz eventos por um só critério extremo | exclui perda absoluta grande com fração pequena e perda local crítica de área pequena |
| Regra relativa **ou** absoluta | Algum dos dois mecanismos justifica atenção? | inclui relevância por qualquer escala | amplia a definição e precisa justificativa explícita; não é a regra A/B/C atualmente comparada |
| Relevância contextual | A conversão afeta formação vulnerável, remanescente, conectividade ou área de interesse? | aproxima o evento do impacto ambiental | exige fontes/protocolo adicionais; não assumir qualidade de habitat pelo código Col9 |
| Conversão com persistência | A mudança inicial continua antrópica em observações posteriores? | investiga instabilidade/transitoriedade | usa futuro da resposta e muda disponibilidade/horizonte de confirmação; não prova uso contínuo entre mapas |

A/B/C são escalas operacionais possíveis, não padrões oficiais. A representa
0,25% e 25 ha; B 0,50% e 100 ha; C 1,00% e 250 ha, simultaneamente.
O piso efetivo é `max(A_min,tau D/100)`, com cruzamentos em D=10.000,
20.000 e 25.000 ha. Essas relações permitem discutir que estoque e escala
se pretende proteger; as prevalências 96,13%, 90,37% e 75,18% não definem
qual é ambientalmente correto. Os três permanecem não homologados.

## Persistência: definições e horizonte

Uma opção seria exigir VN em t, UA em t+1 e **UA em t+2**, sempre no mesmo
pixel e com observação válida. Permanecer no grupo UA permite mudança de
pastagem para agricultura; exigir o mesmo código específico é uma opção
mais restritiva, sensível à troca de uso e à instabilidade de subclasses.
O grupo/código exigido precisa ser decidido antes do cálculo.

| Regra candidata | Última informação necessária | Último t usando somente 1985–2023 | Consequência |
|---|---|---:|---|
| Conversão anual principal | mapa t+1 | 2022 | horizonte principal de ocorrência t+1 |
| Início em t+1 confirmado em t+2 | mapa t+2 | 2021 | ocorrência prevista no primeiro ano, confirmação com atraso de um ano; resposta composta até t+2 |
| Início em t+1 confirmado em t+2 e t+3 | mapa t+3 | 2020 | confirmação mais tardia e série utilizável menor |

Uma regra de t+2 não pode ser chamada simplesmente de desfecho conhecido em
t+1. Deve ser descrita como **início de conversão em t+1 com confirmação
posterior**, ou como desfecho composto de dois anos. A previsão dos atributos
continua feita em t; mapas t+1/t+2 não entram em X. Para t=2022 a confirmação
em t+2 exigiria 2024: como esse ano está reservado, o resultado seria **não
observado**, nunca não persistente. Não se libera 2024 para preencher esse caso.
Tampouco há rótulo t+1 observado para t=2023 na Col9.

Mapas anuais são observações/classificações discretas: UA em dois mapas
consecutivos não comprova manejo ininterrupto durante todo o intervalo.
Persistência pode reduzir certas oscilações, mas também remover conversão
real seguida de regeneração e deslocar a pergunta ambiental. Não é um filtro
de erro automaticamente validado. Excluir 2023, onde há picos explorados,
também muda a composição do teste; não se pode comparar resultados como se
o mesmo conjunto e a mesma resposta tivessem sido utilizados.

## Suporte e denominadores de uma eventual variante persistente

Há pelo menos duas decisões distintas, ainda abertas:

1. Usar interseção válida t/t+1/t+2, com D3 = VN(t) nesse suporte, e taxa
   persistente sobre D3. É internamente coerente, mas muda o denominador em
   relação ao par original. Informar D3/D2 e exclusões; não reescrever a matriz anual.
2. Manter D2 original e informar observação parcial da persistência. Se CP é a
   conversão confirmada persistente e L é a conversão original sem observação
   válida em t+2, os limites lógicos seriam CP e CP+L, ou suas taxas sobre D2.
   São limites por ausência de observação, não intervalos de confiança nem
   correção do erro temático. Não transformar L em zero conversão persistente.

As matrizes anuais 29×29 não guardam o vínculo de identidade de cada pixel
entre três datas. Duas matrizes consecutivas não permitem reconstruir
persistência pixel a pixel. Seria necessária uma rotina separada sobre os
rasters originais, com novo manifesto/saídas e testes. O teste de máscara
tripla de Buriticupu verifica suporte; não homologa por si só uma regra de
permanência em UA. Os flags t+2 dos poucos pontos amostrados não são totais municipais.

## Proposta de encaminhamento científico

Manter o resultado anual contínuo C/R e o horizonte t+1 como referência da
discussão; usar o piloto para verificar definição de referência, interpretação
temporal, confusão de classes, custos e inconclusivos. Comparar A/B/C como
hipóteses ambientais, sem escolher pelo balanceamento ou desempenho de ML.
A seleção eventual deve declarar a escala de estoque/área e as consequências
de incluir/excluir casos reais perto das fronteiras, com evidência temática.

Se houver interesse em persistência, propor primeiro uma análise de sensibilidade
separada, com o mesmo suporte e período comparável quando possível e todos os
casos sem confirmação marcados. Sua inclusão no desfecho principal ou mudança
para alvo contínuo exige nova decisão do pesquisador. Nenhum cálculo persistente,
novo Y, reclassificação ou modelo foi produzido nesta etapa.

Os princípios de amostragem/resposta/inferência de
[Olofsson et al. (2014)](https://doi.org/10.1016/j.rse.2014.02.015) apoiam a
necessidade de evidência independente e incerteza coerente; não fornecem
tau, A_min ou uma definição universal de relevância ambiental.
