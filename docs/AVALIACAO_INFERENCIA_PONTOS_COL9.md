# Possibilidade de inferência estatística — pontos oficiais Col 9

Data: 12/11/2026. Decisão analítica desta execução: **somente diagnósticos descritivos**.
Não se estimaram acurácias representativas, área corrigida por erro ou IC populacionais.
O desenho nacional é probabilístico; isso não garante a validade automática de
qualquer subconjunto de pontos, anos, classes ou municípios.

## O que foi verificado

No arquivo completo há 85.152 IDs únicos e 756 estratos observados CARTA_2×DECLIVIDAD.
PESO_AMOS e PROB_AMOS_ foram lidos com vírgula decimal; o produto é 1 dentro de
erro numérico. O peso é constante em cada estrato. O recorte intercepta 119
estratos,117 com algum ponto sem marcação de treino. Isso permite reconhecer a
estrutura, mas não demonstra que a probabilidade original seja a probabilidade
condicional do conjunto independente depois das exclusões e da não resposta.

Há 143 estratos nacionais comn=1, dos quais 16 têm ponto no recorte;
um desses pontos está marcado como treino. Mesmo antes das demais limitações,
a variância intrasestrato não pode ser estimada diretamente para esses estratos.
Não foi criada uma regra arbitrária de colapso nem um bootstrap iid para contornar isso.

O apêndice oficial registra 10 mil pontos de treinamento; o arquivo identifica 9.999.
Não foi localizada documentação suficiente das probabilidades do conjunto
remanescente para garantir que os pesos fornecidos continuem corretos após remover
os marcados. Não se presume que a diferença de um ID não tenha efeito.

Além disso, a disponibilidade 2023 é seletiva: 4.053 classes nacionais e apenas um
ponto local. Não há mecanismo de não resposta/inclusão documentado para extrapolar
essa fração a 255 municípios. Os rótulos agregados/ambíguos e filtros COUNT/BORDA
geram novos subconjuntos, que não podem ser tratados como sorteio simples sem evidência.

## Estimação de domínio e pesos: o que seria necessário

Pesos nacionais podem, em princípio, servir à estimação de domínio municipal ou
regional quando o desenho e a inclusão estão documentados. Não se exige uma
amostra municipal separada por definição. Deve-se trabalhar com o desenho nacional
completo e o indicador de domínio I_D; unidades fora do domínio contribuem zero.
Não se renormalizam pesos por município apenas para reproduzir sua área territorial.

Sob sorteio estratificado simples realmente válido, um total de célula de erro
seria estimado por soma_h (N_h/n_h) soma_i I_D(i) I_célula(i). Precisão e
sensibilidade seriam razões desses totais, com variância de razão por
linearização/replicação estratificada e correções de população finita apropriadas.
Seriam necessários N_h/unidade populacional, probabilidades válidas, tratamento
documentado da retirada para treino, da não resposta e dos estratos isolados.
Essas condições **não foram verificadas integralmente** para nosso desfecho/domínio.

Os mesmos pontos reaparecem em 38 comparações: 268.981 pares comparáveis não são
268.981 unidades independentes. Uma avaliação conjunta deve somar a contribuição
temporal dentro de cada ID e respeitar sua inclusão e estrato no cálculo de
variância. Bootstrap por linha ponto-ano, IC binomial simples e multiplicação
de amostra por 38 produziriam precisão artificial. Tampouco independência espacial
entre pontos implica independência dos anos ou dos erros de um pixel persistente.

## Produtos permitidos e interpretação

Foram disponibilizadas matrizes binárias de frequências e somas de pesos publicados,
mais razões **descritivas**. Os pesos não foram calibrados para o recorte nem
convertidos em hectares corrigidos. Os resultados ponderados são uma sensibilidade,
sem reivindicar inferência válida. Não há IC nos arquivos; a ausência é deliberada.

Nenhum ponto em dois municípios, poucos pontos VN nos remanescentes de outros,
eventos raros e referências ausentes impedem afirmações municipais robustas.
“Sem evento na amostra” não significa “sem evento municipal”. A validação original
de classes gerais não foi dimensionada especificamente para nosso evento VN→UA,
e a amostra adicional de classes raras descrita pelo produtor não foi presumida
como parte desse CSV nem fundida aos 85.152 pontos.

Três distinções de independência são necessárias: ausência de uso explícito no
treinamento, independência da interpretação e independência do insumo/sistema.
Excluir os marcados melhora a primeira, mas não comprova as demais. A referência
e o mapa compartilham sensores/imagens e o conjunto foi revisado ao longo das
coleções; a identificação individual de treinamento/participação em revisões é incompleta.
Não se declara circularidade universal, nem independência absoluta sem documentação.

## Pendências verificáveis

1. Esclarecer com a documentação do produtor a versão exata, o ID de treinamento
   não identificado e a cobertura 2023, sem enviar mensagens em nome do pesquisador.
2. Obter informação de inclusão/retirada por estrato e mecanismo de atualização
   da referência; verificar a unidade dos pesos e a disponibilidade dos estratos.
3. Definir tratamento científico para estratos isolados e ausência temática/temporal,
   sem escolher procedimentos para favorecer resultados.
4. Só então avaliar a precisão necessária para o evento regional e para cada
   domínio municipal; municípios com suporte insuficiente continuarão sem estimativa.

Detalhes numéricos e condições estão em
`diagnosticos/avaliacao_suporte_inferencial.json`, com tabelas de estratos e IDs.
A continuidade desta estratégia prioriza documentação e fontes oficiais existentes;
não depende de novos pacotes de interpretação humana.
