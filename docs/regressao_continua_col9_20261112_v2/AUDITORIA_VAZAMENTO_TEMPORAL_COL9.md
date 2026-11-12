# Auditoria de vazamento e dependência temporal

Permitidos em princípio: 3 atributos territoriais estáticos, sob convenção
retrospectiva dos limites 2025, não fronteiras administrativas observadas em 1985.

Sujeitos à análise: 50 atributos da família Col 9. O fenômeno construído termina
até t, mas filtros/integração do produtor podem depender de anos posteriores.
O envelope conservador é 2023, sem afirmar uso efetivo de todos os anos em
cada pixel. Datas exatas desconhecidas permanecem nulas. Aceitar vintage
retrospectivo não demonstra ausência de informação antecipatória.

Proibidos: C/R correntes, D da máscara t/t+1, Q/cobertura comum do desfecho,
classe t+1, alvo/candidato binário, adjudicação futura e janela centrada
posterior a t. Código e ano são chaves; UF não entra automaticamente em X.

Foram auditados 527.085 registros por atributo/município–ano, com zero fim
do fenômeno posterior a t e zero coluna proibida. Janelas municipais são
ordenadas, completas e para trás; falta inicial ficaNA com flag.
Um contrafactual modifica todos os dados posteriores ao corte e confirma
X anterior idêntico. Isso não comprova independência do algoritmo MapBiomas.

O teste de Buriticupu 2002 distingue VN observada emt de D do suporte futuro.
Respostas e qualidade estão fisicamente separadas. Nenhuma precisão dos
pontos oficiais corrigiu C/R ou entrou como atributo.

## Ablações futuras, não executadas
T 0: território sem qualquer Col 9, retirando todo o bloco de risco.
T 1: T 0+composição/qualidade somente de t, ainda retrospectiva.
T 2: T 1+variação líquida/tendências passadas de estoque.
T 3: T 2+conversões históricas encerradas até t.
T 4 opcional: focos, comparando no mesmo período e suporte disponível;
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
ser aprovada e pré-especificada, não escolhida pelo desempenho. T 3 e a
baseline última taxa exigem essa decisão; T 0–T 2 não usam conversão histórica explícita.

No LOSO, atributos observacionais da UF retida não são dados de ajuste;
isso é transferência com covariáveis locais conhecidas, não cenário sem
qualquer histórico. Uma ablação sem histórico de conversão da UF retida
deve ser distinguida. Não usar rótulos/erros retidos para selecionar o regime.

Quantis e assimetrias globais desta preparação são diagnóstico autorizado,
inclusive em anos já explorados do teste. Não reutilizá-los como parâmetros
de transformação, seleção ou limites aprendidos. Nenhum desempenho foi consultado.
