"""Produz nove documentos de preparação em pasta nova, sem modelos."""
import argparse,json,re
from pathlib import Path
import sys
import pandas as pd
PROJETO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJETO))
from processamento.relatorios_oficiais_col9 import tabela
from processamento.relatorios_oficiais_col9 import formatar_prosa
FENCE=chr(96)*3

def revisar_prosa(txt):
    dentro=False;linhas=[]
    for linha in txt.splitlines():
        if linha.startswith(FENCE):
            dentro=not dentro;linhas.append(linha);continue
        if not dentro:
            linha=linha.replace('Asymetria','Assimetria').replace('eano_t','e ano_t').replace('emmodelagem/','em modelagem/')
            linha=linha.replace(' at.',' a t.').replace(' at\n',' a t\n').replace('emt+','em t+').replace('priorizarR','priorizar R')
            linha=re.sub(r'\b(para|de|em|e)(?=[CDRQXY]|VN\b|CRC\b)',r'\1 ',linha)
            linha=linha.replace('Recomenda-seC','Recomenda-se C')
            linha=re.sub(r':(?=[^\s/\d])',': ',linha)
            linha=re.sub(r'(?<=[A-Za-zÀ-ÿ)])\.(?=\d{4}\b)','. ',linha)
            linha=formatar_prosa(linha).rstrip('\n')
        linhas.append(linha)
    return '\n'.join(linhas).strip()+'\n'

def executar(raiz,docs):
    if docs.exists():raise FileExistsError('Relatórios anteriores preservados.')
    docs.mkdir(parents=True)
    def escrever(n,t):
        with (docs/n).open('x',encoding='utf-8') as f:f.write(revisar_prosa(t))
    def ler(n):return pd.read_csv(raiz/'diagnosticos'/n,sep=';',encoding='utf-8-sig')
    au=json.loads((raiz/'auditoria_v3/auditoria.json').read_text(encoding='utf-8'))
    cat=json.loads((raiz/'metadados/catalogo_atributos.json').read_text(encoding='utf-8'))
    d=ler('DISTRIBUICAO_GLOBAL_C_D_R.csv').iloc[0]
    est=ler('DISTRIBUICAO_POR_ESTADO.csv');quint=ler('DISTRIBUICAO_ESTOQUE_ELEGIVEL.csv');peri=ler('DISTRIBUICAO_PERIODOS.csv')
    g=pd.read_parquet(raiz/'matriz/TERRITORIO_CANONICO_COL9.parquet');bad=g[g.biomas_fechamento_fora_tolerancia_01pp]
    aus=pd.read_csv(raiz/'auditoria_v3/AUSENCIAS_POR_ATRIBUTO.csv',sep=';')
    medidas=pd.DataFrame([{'medida':v,'mínimo':d[v+'_min'],'p05':d[v+'_p05'],'p25':d[v+'_p25'],
        'mediana':d[v+'_mediana'],'p75':d[v+'_p75'],'p95':d[v+'_p95'],'p99':d[v+'_p99'],
        'máximo':d[v+'_max'],'média':d[v+'_media'],'DP':d[v+'_dp'],'assimetria':d[v+'_assimetria']} for v in ['R_pct','C_ha','D_ha']])
    escrever('PROTOCOLO_DESFECHO_CONTINUO_COL9.md',f'''
# Protocolo do desfecho contínuo candidato — Coleção 9
12/11/2026. Proposta para apreciação do orientador, sem homologação de objetivos ou treinamento.

## Estimando
R(m,t)=100×C(m,t)/D(m,t), taxa percentual anual de conversão mapeada na ZCS
Cerrado–Amazônia. C é a área geodésica em hectares dos pixels VN(t)→UA(t+1)
na máscara válida comum. D é a vegetação nativa inicial nessa mesma máscara,
diferente da VN observada somente em t. São255 municípios IBGE2025 fixos,
39 mapas Col9 e38 transições: t=1985–2022,9.690 pares. As255 linhas de2023
ficam separadas sem resposta.2024 permanece reservado e não foi utilizado.

VN=[3,4,5,6,49,11,12,50]; UA=[9,15,20,21,24,30,31,35,39,40,41,46,47,48,62].
A legenda oficial não muda;25 é separada e29/32 permanecem naturais específicas.
As sensibilidades e cenários A/B/C anteriores são preservados como exploratórios.

Fisicamente0≤C≤D e0≤R≤100. D=0 ou suporte insuficiente implicaria resposta
não avaliável, nunca zero imputado. Atualmente todos os9.690 pares têm C>0 eD>0;
isso não permite presumir ausência de zeros em observações futuras.

Recomenda-se C emha como resposta secundária de experimento independente
complementar, caso aprovado. Não é estatisticamente equivalente aR. Converter
R prevista emC usando D realizado utilizaria suporte futuro indisponível emt.
Uma aproximação pela VN observada emt teria outro estimando e não seria C exato.

## Distribuição e heterogeneidade
{tabela(medidas)}

O maior R é52,9902% em Figueirópolis D'Oeste no par2022→2023. O maior C é
118.394,66ha em Vila Bela da Santíssima Trindade em1985→1986. Não houve exclusão
de extremos, truncamento ou winsorização. Asymetria, IQR, MAD, quantis e dispersão
por município/UF/ano estão nas tabelas de diagnóstico, sem testes iid de significância.

{tabela(est,['SIGLA_UF','n','R_pct_mediana','C_ha_mediana','taxa_razao_somas_pct'])}

A taxa por razão das somas é100ΣC/ΣD; globalmente1,7670%, diferente da média
não ponderada3,2364%. Agregar pela razão das somas não equivale à média das taxas.
Somar C ao longo do tempo não identifica área única sem reconversões/repetições.

{tabela(quint,['quintil_D_descritivo','n','D_ha_min','D_ha_max','R_pct_mediana','C_ha_mediana'])}

No quintil de menor D, a mediana de R é3,8323% e de C503,84ha; no maior,
R1,1331% e C7.616,89ha. Isso demonstra sensibilidade ao denominador e não
equivalência das respostas, sem inferir causalidade. Os quintis globais são apenas
descritivos; não são limiares de elegibilidade ou parâmetros de aprendizado.

{tabela(peri,['periodo','n','R_pct_mediana','C_ha_mediana','taxa_razao_somas_pct'])}

Os períodos referem-se ao ano t; os extremos têm5 e3 anos. Mudanças abruptas
entre taxas/áreas de intervalos consecutivos são tabeladas separadamente; não
são novas transições nem variação líquida de estoque.

## Máscara e transformações candidatas
Q=100D/VN inicial observada mede elegibilidade, não acurácia temática. Todos
os pares foram mantidos com flags separados Q≥99,5/99,9/99,95%; os dois últimos
retirariam apenas Buriticupu2002→2003 (Q≈99,7016%). Nenhum corte foi selecionado.
A auditoria anterior com máscara tripla2001–2003 permanece preservada; suporte
coincidente não valida o tema e diferenças não são automaticamente NoData.

log1p(C/1ha) tem assimetria−0,3876 no diagnóstico. Melhor aparência estatística
não justifica sua adoção. C/R originais foram preservados. Uma futura inversão
expm1 precederá métricas emha; inverter a média log não recupera automaticamente
a média original. R direta é primeira candidata; logit(R/100) exige interior(0,1)
e decisão para eventuais0/100, sem epsilon arbitrário. Links/perdas limitados
devem ser pré-especificados no desenvolvimento. Nada foi aplicado definitivamente.

## Limitações ambientais
R/C são conversão mapeada, não área real corrigida, relevância ecológica
demonstrada, variação líquida ou desmatamento PRODES. A comparação oficial
anterior apresentou precisão descritiva26,81% e sensibilidade35,12% no ano exato,
sem inferência representativa própria. Em2023 há somente um ponto local com
referência; datação, filtros temporais e qualidade das referências permanecem
limitações. Não corrigir hectares multiplicando pela precisão pontual.
A resposta contínua evita dicotomização ainda não fundamentada, mas não remove
erro de medição. Persistência emt+2 não integra a resposta nem utiliza2024.
''')
    escrever('DICIONARIO_VARIAVEIS_REGRESSAO_COL9.md',f'''
# Dicionário dos53 atributos candidatos
Chaves: CD_MUN, string de7 dígitos, eano_t. Não são preditores numéricos automáticos.
UF/nome ficam no índice/partições, fora de X. Nenhum atributo foi selecionado.

Composição percentual:100×área do grupo(t)/toda área classificada(t), incluindo
25/33 e excluindo0/27/NoData. Agricultura exclui pastagem/silvicultura/mosaico.
Formações florestais aqui=[3,5,6,49], savânica=4, campestre=12; não são partição
completa de VN nem substituem a hierarquia oficial.

{tabela(pd.DataFrame(cat)[['variavel','bloco','unidade','formula','primeiro_ano_historico_suficiente','inicio_fenomeno_offset','fim_fenomeno_offset','status_temporal']])}

Tendências usam inclinação descritiva por pesos temporais fixos em janelas
completas, sem modelo preditivo. Estoque3/5 anos disponível desde1987/1989;
conversão histórica3/5 desde1988/1990. Em1985 não há conversão anterior.
Flags de lacuna não imputam valores.

As três variáveis territoriais derivam apenas dos polígonos canônicos2025:
área Geod WGS84, latitude/longitude de ponto interior representative_point
calculado emEPSG5880 e convertido para4326. Não é centróide/população.
O catálogo resume o pacote territorial2019/2025, mas frações de biomas2019
ficam separadas e não fornecem valores às três variáveis de X.

CATALOGO_ATRIBUTOS_COL9.csv/json registra fonte, versão, unidade, fórmula,
referência temporal, publicação/revisão conhecida ou desconhecida, risco e
seleção=false. DISPONIBILIDADE_ATRIBUTOS_COL9.parquet contém527.085 combinações
dos9.945 município–anos com53 atributos: presença, motivo de ausência,
limites do fenômeno e dependência algorítmica. Datas exatas não comprovadas
permanecem nulas; lançamento tardio não prova disponibilidade histórica.

Arquivos independentes: índice, X, C/D/R, qualidade/eligibilidade, metadados
e partições. D eQ correntes nunca entram em X; VN somente emt não éD.
''')
    escrever('AUDITORIA_INTEGRIDADE_MATRIZ_COL9.md',f'''
# Auditoria de integridade
Auditoria final: auditoria_v3/auditoria.json.

São255 códigos iguais ao conjunto WKB canônico,38 intervalos por município,
9.690 chaves únicas/ordenadas em1985–2022 e255 linhas de2023 com C/D/R
ausentes e ano de resposta observado nulo. Não houve retorno à base268.
X contém53 atributos e duas chaves, sem colunas proibidas ou janelas posteriores
at. C/D/R conferem com as métricas auditadas;0≤C≤D,0≤R≤100 eR=100C/D.
Os255 estoques NPZ foram verificados por hash e pelo CSV aprovado:
erro máximo5,06671×10⁻⁵ha, compatível com arredondamento, sem alterar fontes.

{tabela(aus[aus.n_ausentes.gt(0)],['variavel','n_ausentes','pct_ausentes','primeiro_ano_historico_suficiente'])}

As ausências estruturais não foram substituídas por zero. Frações de biomas
não estão em X; zeros de interseção bruta representam interseções vazias
na camada consultada, sem certificar compatibilidade dos suportes.

Foram verificados{au['n_caminhos_anteriores_distintos']} caminhos dos três checkpoints
anteriores, zero divergências;255 NPZs e código legado preservados. Os39 rasters
conferem em tamanho/mtime e hashes prévios;159GB não foram relidos integralmente.
Não houve migração, escrita no banco, Docker ou implantação. Isso descreve
operações, não comparação binária do volume PostgreSQL.

Passaram125 testes distintos:70 principais e55 geoespaciais, incluindo20 novos.
Os seis módulos geoespaciais ignorados pelo ambiente principal foram executados
no apropriado. O contrafactual altera dados posteriores e verifica invariância
de X anterior: testa a janela implementada, não o classificador externo.
''')
    escrever('INVENTARIO_VARIAVEIS_PENDENTES_COL9.md',f'''
# Inventário de blocos e pendências
A base principal foi concluída sem depender da harmonização dos complementos.

| Bloco | Situação | Uso |
|---|---|---|
| Col9/histórico |harmonizado255×39|50 atributos sujeitos à análise temporal |
| Território básico |canônico2025|3 atributos estáticos |
| BiomasIBGE2019 |reinterseção executada,6 divergências de fechamento|tabela separada, fora de X |
| FocosINPE |21 ZIPs2003–2023 reintersectados|bloco separado, sem zeros presumidos |
| PRODES |TIFF/QML2023/2025 e CSV legado|bloqueio temporal/vintage/suporte para X |
| Área queimada |sem série local harmonizada identificada|fonte adicional, não substituída por focos |
| PAM/PPM/população/PIB |fontes oficiais identificadas|aquisição/vintage/território pendentes |
| Relevo/solo/infraestrutura/grafo |não harmonizados255|nenhuma variável criada/herdada268 |

## Biomas
{tabela(bad,['CD_MUN','NM_MUN','biomas_fechamento_area_pct'])}

Não se atribuiu o desvio automaticamente ao mar, erro ou NoData nem se
normalizaram frações para100%.0,1 ponto percentual é alarme de fechamento,
não elegibilidade temática. Interseções, frações brutas e hashes do shapefile
estão emTERRITORIO_CANONICO_COL9.parquet eINTERSECOES_BIOMAS_CANONICOS_COL9.csv.

## Focos
835.818 registros de2003–2023 foram reintersectados pelas coordenadas nos255
polígonos. Não houve data inválida/fora do ano, duplicata exata, ID conflitante
ou atribuição múltipla nos arquivos auditados. Ao longo da série há registros
nos255 municípios, com cobertura anual desigual. O legado251/255 não foi
reutilizado para calcular o novo bloco.

O calendário éUTC conforme INPE: termina antes do corte local de t, mas
difere do ano civil local em suas bordas. Não há campo de satélite individual;
a referência/AQUA_M-T deriva da documentação/configuração, não de verificação
por detecção. Fonte:[FAQ INPE](https://data.inpe.br/queimadas/faq/).
Contagens são registros detectados, não fogo verdadeiro nem hectares queimados.

Mês sem linha ficaNA com motivo; meses com registros não medem completude
instrumental.1985–2002 ficamNA. Shapefiles antigos, inclusive com início
em31/janeiro, exigem auditoria de sensor/janela e não completam a série
automaticamente. FRP/chuva/risco condicionados a focos não foram integrados
nem tratados como clima médio municipal. O bloco não foi anexado ao X-base.

## PRODES e área queimada
Inventário registra arquivos/versões/tamanhos. Arquivos2024 ou posteriores
foram apenas identificados por nome, sem seus valores. Nos CSVs legados
somente código e ano foram lidos para inventário, sem medidas2024/2025.
O Brasil2023 já auditado evita recorrer ao2025, mas faltam proveniência
exata/vintage e dicionário de intervalos por bioma, máscaras e correspondência
temporal. Não propagar estoque2023 para t nem assumir ausência de linha=zero.
Reinterseção futura deve conferir cobertura nos255 limites; nenhuma taxa
PRODES substitui Y MapBiomas.

Área queimada exige fonte própria, como
[INPE AQ1km](https://terrabrasilis.dpi.inpe.br/queimadas/aq1km/), produto30m
ou MapBiomas Fogo com versão/grade/máscara documentadas. Foco não equivale
a cicatriz e coleção de Fogo não equivale à coleção de cobertura.

## Socioeconomia
[PAM5457](https://sidra.ibge.gov.br/tabela/5457): áreas plantada/destinada,
colhida e produção, com unidades/revisões por cultura.
[PPM3939](https://sidra.ibge.gov.br/tabela/3939): rebanhos por espécie;
não somar espécies indiscriminadamente.
[PIB5938](https://sidra.ibge.gov.br/tabela/5938): referência2010, nominal,
com revisões/cobertura/deflator a definir. População:censos e estimativasIBGE,
com tabela/ano e data de publicação a conferir. Não foram adquiridos valores
nem inventadas datas efetivas de disponibilidade.

Integrar por código oficial, nunca aproximação de nomes. Emancipações e
limites históricos exigem correspondência aos255 fixos; código igual não
comprova suporte territorial igual. Sem compatibilidade, manter bloqueio/NA,
sem rateio ou interpolação com dados futuros. Detalhes no inventário JSON.
''')
    escrever('AUDITORIA_VAZAMENTO_TEMPORAL_COL9.md','''
# Auditoria de vazamento e dependência temporal

Permitidos em princípio:3 atributos territoriais estáticos, sob convenção
retrospectiva dos limites2025, não fronteiras administrativas observadas em1985.

Sujeitos à análise:50 atributos da família Col9. O fenômeno construído termina
até t, mas filtros/integração do produtor podem depender de anos posteriores.
O envelope conservador é2023, sem afirmar uso efetivo de todos os anos em
cada pixel. Datas exatas desconhecidas permanecem nulas. Aceitar vintage
retrospectivo não demonstra ausência de informação antecipatória.

Proibidos:C/R correntes, D da máscara t/t+1, Q/cobertura comum do desfecho,
classe t+1, alvo/candidato binário, adjudicação futura e janela centrada
posterior a t. Código e ano são chaves; UF não entra automaticamente em X.

Foram auditados527.085 registros por atributo/município–ano, com zero fim
do fenômeno posterior a t e zero coluna proibida. Janelas municipais são
ordenadas, completas e para trás; falta inicial ficaNA com flag.
Um contrafactual modifica todos os dados posteriores ao corte e confirma
X anterior idêntico. Isso não comprova independência do algoritmo MapBiomas.

O teste de Buriticupu2002 distingue VN observada emt de D do suporte futuro.
Respostas e qualidade estão fisicamente separadas. Nenhuma precisão dos
pontos oficiais corrigiu C/R ou entrou como atributo.

## Ablações futuras, não executadas
T0:território sem qualquer Col9, retirando todo o bloco de risco.
T1:T0+composição/qualidade somente de t, ainda retrospectiva.
T2:T1+variação líquida/tendências passadas de estoque.
T3:T2+conversões históricas encerradas até t.
T4 opcional:focos, comparando no mesmo período e suporte disponível;
não atribuir ganho a mudança silenciosa de coorte.
PRODES/fogo/socioeconomia exigem harmonização e decisão antes de entrar.

Retirar só conversão passada não elimina filtragem futura contida no mapa
de t. As ablações avaliariam informação preditiva, não causalidade ou prova
de ausência de dependência. Um cenário estritamente sem futuro do produtor
exigiria vintages/classificações truncados emt ou fonte com linhagem comprovada.

## Regime de históricos no teste
Em origem móvel anual, uma conversão encerrada até t pode coincidir com
resposta de intervalo anterior no bloco reservado. Usá-la como covariável
histórica não autoriza reajustar o modelo com rótulos do teste.
A escolha entre origem móvel e históricos congelados antes do teste deve
ser aprovada e pré-especificada, não escolhida pelo desempenho. T3 e a
baseline última taxa exigem essa decisão; T0–T2 não usam conversão histórica explícita.

No LOSO, atributos observacionais da UF retida não são dados de ajuste;
isso é transferência com covariáveis locais conhecidas, não cenário sem
qualquer histórico. Uma ablação sem histórico de conversão da UF retida
deve ser distinguida. Não usar rótulos/erros retidos para selecionar o regime.

Quantis e assimetrias globais desta preparação são diagnóstico autorizado,
inclusive em anos já explorados do teste. Não reutilizá-los como parâmetros
de transformação, seleção ou limites aprendidos. Nenhum desempenho foi consultado.
''')
    escrever('PROTOCOLO_REGRESSAO_RETROSPECTIVA_COL9.md','''
# Protocolo proposto de regressão retrospectiva
12/11/2026. Proposta ao orientador; nenhum treinamento, otimização ou homologação.

## Pergunta, modelos e baselines
Prever R(m,t), conversão mapeada t→t+1, com fenômenos observados até t,
nos255 limites fixos. C emha terá experimento secundário próprio, se aprovado.
A análise é retrospectiva, sem reivindicar disponibilidade operacional histórica.
A lista53 é candidata. CD_MUN/ano_t são chaves, UF agrupamento e Q não é atributo.

Comparar Ridge/Elastic Net regularizados, Random Forest Regressor e XGBoost
Regressor. LogisticRegression classificatória não é baseline contínua.
Versões/sementes serão fixadas na autorização futura, não por instalação de
estimadores agora. Nenhum modelo adicional foi incluído automaticamente.

Referências simples:média/mediana do treino do fold; histórico municipal
calculado apenas no treino, com fallback global do treino para município/UF
retidos. Grupos territoriais não podem usar estatísticas reservadas.
Última taxa encerrada antes do intervalo é candidata quando disponível,
condicionada à decisão origem móvel versus histórico congelado na auditoria.
Comparar no mesmo suporte; falta de histórico não vira zero.
Não foram calculadas previsões dessas baselines.

## Escalas, limites e perdas
R direta em pontos percentuais é a primeira candidata. Forest com médias de
folhas/pesos não negativos respeita o intervalo de treino; lineares/boosting
quadrático podem extrapolar[0,100]. Futuramente contar/reportar extrapolações;
não truncar silenciosamente. Restrição/link limitado precisa pré-especificação,
comparando métricas originais e procedimento declarado, nunca escolha pelo teste.

Logit deR/100 exige interior(0,1) e regra para eventuais endpoints, sem epsilon
arbitrário. Após inversão, o estimando não é automaticamente a média original.
Transformações monotônicas só serão escolhidas no desenvolvimento; métricas
principais sempre após inversão correta.

ParaC:direta não negativa, log1p(C/1ha) e perdas robustas são alternativas.
Gamma exigiria C estritamente positivo; a série atual não garante zeros ausentes
no futuro. Tweedie seria opcional com justificativa. Hectares não são contagem
Poisson por definição. Nada foi escolhido pela assimetria ou desempenho.

Converter R prevista usando D realizado é informação futura, não previsão
genuína emha. O experimentoC precisa estimando/modelo próprio e mesmas partições.
Não comparar respostas por uma métrica que misture unidades.

## Métricas e calibração regressiva
Proposta principal:MAE deR em pontos percentuais. Complementares:RMSE na mesma
unidade; viés=média(previsto−observado), sinal explícito; R², podendo ser negativo
eNA quando variância da resposta é nula, sem substituir indefinições por sucesso.
ParaC, MAE/RMSE/viés emha e R² próprio. MAPE não é principal por valores próximos
de zero. Modelos transformados retornam à escala original antes das métricas.

Reportar micro município–ano e macro por município/UF/ano, tamanho das coortes,
erros por magnitude, estoque e qualidade. Limites de faixas aprendidas devem
ser estimados no treino e congelados; não importar quintis globais do diagnóstico.
Analisar heterocedasticidade/extremos e dependência do erro em relação ao estoque.
D pode aparecer na análise posterior do erro, nunca como atributo corrente.
Ponderação por área/estoque altera o estimando e deve ser complementar.

Calibração:comparar magnitudes previstas/observadas por faixas de previsão
congeladas no desenvolvimento, com tamanho de grupos; não ajustar calibração
nos rótulos do teste. Brier/AUROC não são métricas principais desta regressão.

## Validação temporal
| Papel | Anos t | Chaves |
|---|---|---:|
| Treino inicial |1985–2013|7395|
| Embargo |2014|255|
| Validação |2015–2017|765|
| Embargo |2018|255|
| Teste reservado |2019–2022|1020|

Avanço interno:até2001/2003–2005; até2005/2007–2009; até2009/2011–2013,
com um ano de embargo. Escolhas ficam no desenvolvimento; eventual reajuste
final até2017 depende de congelamento anterior ao teste. Nenhuma busca foi feita.

O embargo separa pares adjacentes que compartilham ano de mapa, mas não remove
autocorrelação ou filtros longos. Não escolher extensão pelo melhor teste.
Anos finais/extremos já foram explorados cientificamente:o teste não é
completamente cego à formulação, embora separado do ajuste futuro.
2024 não é teste externo e não será usado.

## Validação espacial
Cinco folds MA/MT/PA/RO/TO, retirando integralmente cada UF de ajuste,
imputação, seleção, escala, transformação, validação interna e calibração
em todos os anos. Avaliar a UF retida apenas emt2019–2022; demais UFs mantêm
os cortes. Não combinar previsões LOSO para ajustar o mesmo modelo ou escolher
o melhor estado. Matrizes de partições materializam a regra.

Covariáveis conhecidas da UF retida emt são distintas de usá-la no ajuste;
o regime dos históricos deve ser pré-especificado. Considerar correlação
de fronteira e eventual buffer como proposta adicional, não criar
automaticamente grafo/buffer nem herdar268. RO tem5 municípios, limitando
interpretação de incerteza espacial. Não assumir amostras iid.

## Controle de aprendizado, interpretação e incerteza
Imputação, padronização, seleção, regularização, transformações aprendidas,
calibração e grupos dependem somente do treino do fold. Flags já criados
são determinísticos; imputação não ocorreu. Coluna inteiramente ausente no
treino exige regra do treino, sem aprender em validação/teste.
Disponibilidade nativa de um algoritmo não dispensa transparência de ausência/coorte.

Prever comparações com baselines, importâncias documentadas com cautela à
correlação, erros por grupos e mapas municipais deR prevista/resíduos, além
deC quando houver experimento independente. Importância é associação preditiva,
não causalidade. Não apresentar mapas binários de probabilidade como principal.

Incerteza preditiva exige método próprio respeitando dependência temporal/
espacial e pressupostos de intervalos, quantis ou conformal. Não prometer
cobertura automática. Ela não mede acurácia cartográfica nem corrige a resposta.

Fontes técnicas:[vazamento, scikit-learn](https://scikit-learn.org/stable/common_pitfalls.html),
[métricas](https://scikit-learn.org/stable/modules/model_evaluation.html),
[objetivos XGBoost](https://xgboost.readthedocs.io/en/stable/parameter.html),
consultadas12/11/2026 e arquivadas. O desenho é da pesquisa, não dessas páginas.

Aprovar antes de treinar:estimando/objetivos; papel deC; admissibilidade/ablações;
históricos no teste; coorte/qualidade; perdas/métricas e plano congelado.
A guarda da preparação sempre recusa treino/otimização.
''')
    escrever('NOTA_DECISAO_CIENTIFICA_ORIENTADOR_COL9.md','''
# Proposta de adequação metodológica da variável-alvo: da conversão significativa binária à magnitude contínua da conversão mapeada da vegetação nativa

**Nota para discussão com o orientador —12/11/2026. Proposta, não alteração homologada.**

O objetivo original previa ocorrência de conversão significativa de vegetação
nativa no ano seguinte, em escala município–ano. A estrutura já construída
compreende39 mapas da Coleção9,38 matrizes de transição e9.690 observações
nos255 municípios IBGE2025. Ela permite medir C emhectares deVN(t)→UA(t+1)
eR=100C/D sobre a vegetação inicial elegível. São medidas mapeadas, diferentes
de conversão ambiental real corrigida, variação líquida e desmatamento PRODES.

A comparação com referências oficiais mostrou precisão descritiva26,81% e
sensibilidade35,12% no ano exato; ampliar janelas aumenta coincidência sem
confirmar a data anual. Não há estimativa representativa própria da acurácia
das transições no recorte.2023 tem apenas um ponto local com referência.
Persistem incertezas de suporte, interpretação, datação e dependência dos produtos.
Mudar para resposta contínua não elimina esses problemas.

A/B/C combinam percentuais e áreas mínimas, mas nenhum limiar foi homologado.
Prevalências96,13%,90,37% e75,18% não justificam ajustar limiares para balancear
classes. Relevância ambiental exige definição substantiva de pressão, estoque,
escala e consequências, não conveniência de classificação ou desempenho futuro.

Propõe-se priorizarR como candidata principal por preservar a magnitude
observada e comparação relativa, evitando dicotomização sem fundamento suficiente.
Sua mediana é2,3067%, máximo52,9902%; C tem mediana1.627,79ha e máximo118.394,66ha.
As posições dos municípios diferem entre as respostas. Recomenda-seC como
resposta secundária com experimento de regressão independente, se aprovado,
sem convertê-la usando D futuro realizado.

Redação proposta de objetivo geral:**avaliar a capacidade de modelos de regressão,
em validação temporal e espacial, de predizer a magnitude anual da conversão
mapeada de vegetação nativa no horizonte t+1 na ZCS Cerrado–Amazônia**.
Objetivos específicos:comparar baselines/modelos, contribuição de blocos,
heterogeneidade/erros/calibração e análise complementar emha, mantendo A/B/C
exploratórios. A hipótese passa a tratar de associação/informação preditiva
além de referências históricas, sem presumir causalidade ou conversão real validada.
Essas mudanças ainda exigem concordância do orientador.

A preparação entrega53 atributos candidatos, respostas/qualidade separadas,
histórico até t,2023 sem resposta e partições propostas. Modelos:Ridge/Elastic Net,
Random Forest Regressor e XGBoost Regressor. Métricas:MAE/RMSE/viés em pontos
percentuais e R² complementar; paraC, unidades emha. Nenhum treinamento,
otimização ou seleção de transformação foi executado.

Mantêm-se treino1985–2013, embargo2014, validação2015–2017, embargo2018 e
teste2019–2022, com avanço interno; LOSO retém integralmente cada estado do
desenvolvimento e o avalia no período reservado. Extremos/anos finais já foram
explorados:o teste não é completamente cego à formulação.2024 fica reservado.

Riscos restantes:erro/datação da resposta, filtragem retrospectiva, dependência
espacial/temporal, denominadores, coortes complementares e incompatibilidades
territoriais. Atributos construídos até t podem carregar informação posterior
no produto do classificador. Propõem-se ablações e decisão sobre origem móvel
versus históricos congelados no teste, sem resolver isso por publicação tardia.
Importância de variáveis será associação preditiva.

Solicita-se apreciação sobre objetivos/hipótese;R principal e papel deC;
A/B/C exploratórios; admissibilidade/ablações dos blocos; históricos, qualidade
e métricas; plano congelado de avaliação. Até concordância e posterior autorização
do pesquisador, não há objetivos alterados, desfecho definitivo ou treinamento homologados.
''')
    escrever('RELATORIO_EXECUTIVO_PREPARACAO_COL9.md',f'''
# Conclusão e pendências — preparação de regressão
12/11/2026. **Preparação concluída; objetivos/desfecho principal/treinamento
ainda dependem de apreciação e autorização posteriores.**

X tem9.690 linhas e53 atributos, mais CD_MUN/ano_t como chaves. Há255 linhas
de2023 separadas sem resposta. C/D/R, qualidade, disponibilidade e partições
estão em arquivos independentes, sem imputação ou aprendizado.

R mediana2,3067%, máximo52,9902%; C mediana1.627,79ha, máximo118.394,66ha;
menor D2.080,13ha. Assimetria/heterogeneidade confirmam respostas não equivalentes.
Propõem-seR principal eC secundário independente para o orientador; A/B/C
permanecem exploratórios, sem novos rótulos homologados.

Foram reintersectados835.818 focos2003–2023 em bloco separado, sem presumir
zeros. Biomas2019 têm6 divergências de fechamento:frações fora deX, sem
normalização. PRODES/fogo/socioeconomia têm bloqueios/condições documentados,
sem impedir a base principal.

Zero duplicatas, colunas proibidas ou janelas diretamente posteriores at.
São50 atributos Col9 sujeitos à análise algorítmica e3 estáticos permitidos
em princípio;527.085 metadados registram as diferenças.

Passaram125 testes distintos:70 principais+55 geoespaciais,20 novos.
Verificados{au['n_caminhos_anteriores_distintos']} caminhos dos três checkpoints
anteriores, zero divergências;255 NPZs, geometrias e legado preservados.
Rasters conferem em tamanho/mtime/hashes prévios. Não houve banco, Docker,
implantação, treinamento, busca ou desempenho no teste.

Foram criados seis scripts emmodelagem/, novo arquivo de testes e nove
documentos. pyarrow26.0.1 foi habilitado em pasta temporária isolada, sem
alterar o ambiente do dashboard. Os scripts e fontes anteriores não mudaram.

Tentativas iniciais permanecem preservadas. O alarme de biomas levou à
separação do bloco, não alteração de geometria. Uma autorreferência de
hash foi corrigida por manifesto aditivo, mantendo dados/manifesto/código
executado anteriores; nenhuma tabela mudou. Auditoria final:auditoria_v3/.

Pendências:apreciação do orientador; estimando/objetivos; dependência dos
blocos; regime de históricos no teste; qualidade/coortes; harmonizações e
autorização futura. A análise contínua não homologa conversão ambiental real.
''')
    escrever('CHECKPOINT_REPRODUCAO_PREPARACAO_COL9.md',f'''
# Checkpoint e reprodução
Ativo:{raiz.as_posix()}. Tentativas anteriores preservadas.
Artefatos candidatos, sem autorização de treino.

1. [Desfecho](PROTOCOLO_DESFECHO_CONTINUO_COL9.md)
2. [Dicionário](DICIONARIO_VARIAVEIS_REGRESSAO_COL9.md)
3. [Integridade](AUDITORIA_INTEGRIDADE_MATRIZ_COL9.md)
4. [Vazamento](AUDITORIA_VAZAMENTO_TEMPORAL_COL9.md)
5. [Inventário](INVENTARIO_VARIAVEIS_PENDENTES_COL9.md)
6. [Regressão](PROTOCOLO_REGRESSAO_RETROSPECTIVA_COL9.md)
7. [Nota ao orientador](NOTA_DECISAO_CIENTIFICA_ORIENTADOR_COL9.md)
8. [Conclusão](RELATORIO_EXECUTIVO_PREPARACAO_COL9.md)

matriz/:índices, X principal/X2023, C/D/R e2023 ausentes, qualidade,
território e partições. metadados/:catálogo, disponibilidade, fontes e código
executado. diagnosticos/:distribuições/extremos/estoques/máscara.
complementares/:focos separados e inventários. auditoria_v3/:auditoria final.
fontes/:documentação consultada com URL/data/hash.

Entradas grandes não são duplicadas:rasters, NPZs, GeoPackage, CSV aprovado,
biomas e ZIPs de focos continuam nos caminhos dos manifestos. O pacote inclui
Parquets, tabelas, scripts, testes, relatórios, fontes documentais e logs.
Nenhuma senha, modelo ajustado ou previsão do teste integra a entrega.

Ambiente:Python3.14.6,numpy2.5.4,pandas2.3.3,pyarrow26.0.1,
geopandas1.2.0,shapely2.2.0,pyproj3.8.0. Parquet está em dependência
temporária isolada. Scripts recusam sobrescrever:usar destino novo.

{FENCE}powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = "$env:TEMP/defesa_regressao_col9_deps_20261112;$env:TEMP/defesa_mestrado_geo_testdeps_20261111"
$geoPython = 'D:/mestrado/.venv_territorial/Scripts/python.exe'
$novaExecucao = 'validacao_cientifica_col9/preparacao_regressao_reproducao_001'
$matrizesOriginais = 'resultados_transicoes_col9/integral_255_1985_2023_20261111'
& $geoPython modelagem/preparar_regressao_continua_col9.py --matrizes $matrizesOriginais --saida $novaExecucao
& $geoPython modelagem/diagnosticar_resposta_continua_col9.py --checkpoint $novaExecucao --saida "$novaExecucao/diagnosticos"
& $geoPython modelagem/blocos_complementares_regressao_col9.py --checkpoint $novaExecucao --saida "$novaExecucao/complementares"
& $geoPython modelagem/auditar_preparacao_regressao_col9.py --checkpoint $novaExecucao --saida "$novaExecucao/auditoria_v3"
& $geoPython modelagem/relatorios_preparacao_regressao_col9.py --checkpoint $novaExecucao --docs "$novaExecucao/relatorios"
{FENCE}

O fechamento dos biomas é auditado sem bloquear X. A emissão do manifesto
complementar foi corrigida no código atual; o código/manifesto executados
anteriores permanecem preservados em cadeia aditiva de integridade.
Testes sintéticos independem do acervo; para integração em outro destino,
ajustar o fixture ou reproduzir a estrutura de pastas.

manifesto_final_preparacao.json guarda hashes, versões, fontes e resultados;
o recibo final guarda SHA256 do ZIP e conferência deCRC/hashes internos.
2024 não foi utilizado; nenhuma alteração científica foi homologada.
''')
    print('Nove documentos gerados:',docs,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--docs',type=Path,required=True)
    a=p.parse_args();executar(a.checkpoint,a.docs)

