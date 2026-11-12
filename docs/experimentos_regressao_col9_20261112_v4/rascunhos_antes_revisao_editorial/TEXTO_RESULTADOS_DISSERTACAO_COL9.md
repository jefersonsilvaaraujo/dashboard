# Texto proposto para resultados e discussão da dissertação
O protocolo foi auditado e congelado antes do ajuste, utilizando 9.690
observações município–ano de 255 municípios e a Coleção 9 em 1985–2023.
Compararam-se regressões Ridge/Elastic Net, Random Forest e XGBoost,
além de média, mediana e persistência. O ajuste de hiperparâmetros ocorreu
por avanço temporal no desenvolvimento, e a seleção final pela validação
de 2015–2017. A avaliação reservada abrangeut 2019–2022; 2024 não foi utilizado.

Para a taxa percentual R, o melhor modelo supervisionado segundo validação
foixgboost comT 3, MAE de validação
0,660 pontos percentuais. No teste, obteve
MAE 2,288 p.p., RMSE 5,795 p.p., viés
-1,858 p.p. e R²0,186. A persistência apresentou
MAE 1,989 p.p. no mesmo suporte. Essa comparação não foi
utilizada para trocar o modelo escolhido na validação.

A validação espacial reteve integralmente cada estado do desenvolvimento
do seu fold. As predições dos modelos porUF escolhidos na validação externa
à UF tiveramMAE micro 2,211 p.p. para R e
1.282,871 ha para C. As médias macro entreUFs foram
1,978 p.p. e 1.544,396 ha, respectivamente.
Essas agregações têm pesos distintos, e RO possui apenas cinco municípios.

No experimento independente de área, o vencedor supervisionado por validação
foirandom_forest comT 3. No teste, MAE
1.278,089 ha, RMSE 2.809,216 ha, viés
-946,659 ha e R²0,580; persistência:
MAE 1.232,931 ha. As previsões de C não foram derivadas de R usando
D futuro. A interpretação absoluta difere da pressão relativaR e foi mantida
separada na análise, com retorno à escala original após transformações.

As ablaçõesT 0–T 3 compartilharam coorte e partições. A análise de focos foi
separada, comparandoT 0–T 4 na coorte 2003–2022, mantendoNA quando inexistiam
registros e sem tratar focos como área queimada. A sensibilidade com históricos
congelados reutilizou modelos/hiperparâmetros, alterando apenas entradas históricas,
sem retuning. Essas comparações não demonstram causalidade ou ausência de
dependência temporal nos produtos derivados daColeção 9.

Os resultados expressam desempenho de regressão contra conversão mapeada.
Não corrigem erro cartográfico nem validam conversão ambiental real. A baixa
coincidência descritiva das transições anuais com referências, a lacuna de 2023,
a filtragem retrospectiva e a exploração científica anterior dos anos finais
limitam afirmações confirmatórias. O teste foi separado do ajuste e aberto
uma única vez para avaliação final, mas não era completamente cego à formulação
do estudo. Previsões fora dos limites físicos foram explicitamente reportadas,
sem truncamento silencioso. Importância preditiva não foi interpretada causalmente.
