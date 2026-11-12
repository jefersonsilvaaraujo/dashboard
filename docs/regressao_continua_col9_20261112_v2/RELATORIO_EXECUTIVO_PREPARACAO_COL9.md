# Conclusão e pendências — preparação de regressão
12/11/2026. **Preparação concluída; objetivos/desfecho principal/treinamento
ainda dependem de apreciação e autorização posteriores.**

X tem 9.690 linhas e 53 atributos, mais CD_MUN/ano_t como chaves. Há 255 linhas
de 2023 separadas sem resposta. C/D/R, qualidade, disponibilidade e partições
estão em arquivos independentes, sem imputação ou aprendizado.

R mediana 2,3067%, máximo 52,9902%; C mediana 1.627,79 ha, máximo 118.394,66 ha;
menor D 2.080,13 ha. Assimetria/heterogeneidade confirmam respostas não equivalentes.
Propõem-se R principal e C secundário independente para o orientador; A/B/C
permanecem exploratórios, sem novos rótulos homologados.

Foram reintersectados 835.818 focos 2003–2023 em bloco separado, sem presumir
zeros. Biomas 2019 têm 6 divergências de fechamento: frações fora de X, sem
normalização. PRODES/fogo/socioeconomia têm bloqueios/condições documentados,
sem impedir a base principal.

Zero duplicatas, colunas proibidas ou janelas diretamente posteriores a t.
São 50 atributos Col 9 sujeitos à análise algorítmica e 3 estáticos permitidos
em princípio; 527.085 metadados registram as diferenças.

Passaram 125 testes distintos: 70 principais+55 geoespaciais,20 novos.
Verificados 2080 caminhos dos três checkpoints
anteriores, zero divergências; 255 NPZs, geometrias e legado preservados.
Rasters conferem em tamanho/mtime/hashes prévios. Não houve banco, Docker,
implantação, treinamento, busca ou desempenho no teste.

Foram criados seis scripts em modelagem/, novo arquivo de testes e nove
documentos. pyarrow 26.0.1 foi habilitado em pasta temporária isolada, sem
alterar o ambiente do dashboard. Os scripts e fontes anteriores não mudaram.

Tentativas iniciais permanecem preservadas. O alarme de biomas levou à
separação do bloco, não alteração de geometria. Uma autorreferência de
hash foi corrigida por manifesto aditivo, mantendo dados/manifesto/código
executado anteriores; nenhuma tabela mudou. Auditoria final: auditoria_v3/.

Pendências: apreciação do orientador; estimando/objetivos; dependência dos
blocos; regime de históricos no teste; qualidade/coortes; harmonizações e
autorização futura. A análise contínua não homologa conversão ambiental real.
