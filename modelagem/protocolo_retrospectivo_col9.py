"""Contrato retrospectivo de blocos e índices; não constrói X/Y e não treina."""
import argparse
import json
from pathlib import Path
import sys

import pandas as pd

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import conferir_acervo,csv_novo,sha
from modelagem.contrato_matriz_col9 import divisao_temporal,divisao_loso

BLOCOS=[
 ('cobertura','mb_composicao_t','Áreas e proporções das classes Col9; VN/UA e 25/29/32/33 separados',
  'derivavel_acervo_harmonizado','Consolidado Col9 255×39','t','produto retrospectivo; dependência temporal do classificador a auditar'),
 ('cobertura','mb_qualidade_observacao_t','Área classificada, não observados e diferença territorial somente de t',
  'derivavel_acervo_harmonizado','Consolidado/auditoria Col9','t','não usar máscara comum t/t+1 ou Q do desfecho'),
 ('cobertura','mb_variacao_liquida_passada','Variação líquida VN em t−1→t, não desmatamento',
  'derivavel_acervo_harmonizado','Estoques Col9 nos mesmos 255','t−1 até t','histórico inicial ausente é NA'),
 ('cobertura','mb_tendencia_3_5_anos','Tendência e variabilidade em janelas somente para trás',
  'derivavel_acervo_harmonizado','Estoques Col9','t−k+1 até t','sem janela central/interpolação futura'),
 ('cobertura','mb_conversao_passada','C/R históricos encerrados até t, separados da resposta corrente',
  'derivavel_acervo_harmonizado','Matrizes Col9; origem no máximo t−1','até t','não usar C(m,t) ou R(m,t) do par a prever'),
 ('territorio','area_localizacao','Área geodésica e localização do recorte fixo',
  'derivavel_acervo_harmonizado','Geometria 255 IBGE2025 verificada','estático','recorte retrospectivo, sem herdar cadastro de 268'),
 ('territorio','biomas_fracoes','Fração de biomas na geometria canônica',
  'acervo_presente_nao_harmonizado','IBGE biomas2019 local','estático','reinterseção nos 255; não herdar percentuais legados'),
 ('territorio','relevo_solos','Relevo e solos, regras de agregação ainda por definir',
  'fonte_adicional','MDE/solo documentado a selecionar','estático','conferir licença, resolução e validade'),
 ('territorio','acessibilidade_protecao','Distâncias e frações de estradas, proteção/terras com vigência histórica',
  'fonte_adicional','Camadas históricas a selecionar','vigência até t','não propagar estradas/decretos futuros para todos os anos'),
 ('territorio','vizinhos_255','Grafo da geometria canônica e covariáveis passadas vizinhas',
  'acervo_presente_nao_harmonizado','Geometrias disponíveis; grafo ainda não calculado','até t','sem resposta futura de vizinho; protocolo LOSO precisa regra própria'),
 ('queimadas_focos','focos_civil_sazonal','Contagem, densidade e sazonalidade civil até t',
  'acervo_presente_nao_harmonizado','ZIPs INPE2003–2025 e CSV legado; interseção251/255','até t','não reutilizar janela agosto–julho; quatro municípios ausentes'),
 ('queimadas_focos','frp_meteo_nos_focos','FRP e atributos condicionados à ocorrência de foco',
  'acervo_presente_nao_harmonizado','Shapefiles/CSV INPE com cobertura variável','até t','não são médias climáticas municipais; falta antes de2003 não é zero'),
 ('area_queimada','ha_frequencia_fogo','Área queimada, recorrência e sobreposição VN em recorte anual',
  'fonte_adicional','Versão MapBiomas Fogo ou outra fonte a aprovar','até t','produto distinto da Col9; sem equivalência automática de coleções'),
 ('prodes','incremento_residuo','Incrementos e resíduos separados em janela documentada',
  'acervo_presente_nao_harmonizado','Raster PRODES2025 e CSV legado251/255','janela termina até t','reinterseção nos 255, heterogeneidade por bioma/época, produto retrospectivo'),
 ('prodes','estoque_historico','Acumulados e estoques passados do produto, separados de Y',
  'acervo_presente_nao_harmonizado','PRODES local','até t','não usar alvo legado; floresta primária PRODES não equivale à VN operacional'),
 ('socioeconomia','PAM_PPM','Área/produção agrícola e rebanhos com referência anual',
  'fonte_adicional','IBGE SIDRA/PAM/PPM a adquirir','referência até t','malhas municipais históricas exigem correspondência, não ratear automaticamente'),
 ('socioeconomia','populacao_PIB','População, censos, PIB e estrutura produtiva',
  'fonte_adicional','IBGE a adquirir','referência até t','publicação tardia é metadado retrospectivo; revisão/futuro não se resolve por shift')
]


def validar_previsor(nome,ano_t,fim_fenomeno,publicado_em=None,dependencia_algoritmica_ate=None):
    erros=[]; riscos=[]
    if ano_t not in range(1985,2023): erros.append('fora_das_38_transicoes_principais')
    proibidos=('area_convertida','taxa_conversao','elegibilidade_vn','vn_inicial_elegivel','classe_t1','alvo_')
    if nome in {'C_ha','D_ha','R_pct','Q_pct','Y','candidato','pixels_comuns'} or nome.startswith(proibidos):
        erros.append('desfecho_corrente_ou_qualidade_futura_proibido_em_X')
    if fim_fenomeno is None: erros.append('fim_do_fenomeno_desconhecido')
    elif int(fim_fenomeno)>ano_t: erros.append('fenomeno_posterior_a_t')
    if publicado_em is None: riscos.append('publicacao_nao_documentada')
    elif pd.Timestamp(publicado_em).year>ano_t: riscos.append('publicacao_posterior_aceita_somente_como_produto_retrospectivo')
    if dependencia_algoritmica_ate is None: riscos.append('dependencia_algoritmica_nao_auditada')
    elif int(dependencia_algoritmica_ate)>ano_t: riscos.append('conteudo_processado_com_informacao_futura_exige_decisao_e_sensibilidade')
    return {'erros':erros,'riscos':riscos,'modo':'predicao_retrospectiva','apto_operacional_historico':False}


def executar(resultados,saida):
    if saida.exists(): raise FileExistsError('Protocolo anterior preservado.')
    q=conferir_acervo(resultados)
    d=q[['CD_MUN','NM_MUN','SIGLA_UF','ano_origem','ano_destino']].rename(columns={'ano_origem':'ano_t','ano_destino':'ano_t1'})
    if len(d)!=9690 or d.ano_t.max()!=2022 or d.ano_t1.max()!=2023: raise ValueError('Chaves divergentes.')
    saida.mkdir(parents=True)
    csv_novo(d,saida/'indice_principal_9690_sem_rotulos.csv')
    d=d.copy(); d['divisao']=divisao_temporal(d.ano_t); csv_novo(d,saida/'particoes_temporais_propostas.csv')
    folds=[]
    for uf in sorted(d.SIGLA_UF.unique()):
        f=d.copy(); f['UF_retida']=uf; f['divisao']=divisao_loso(f,uf); folds.append(f)
    csv_novo(pd.concat(folds,ignore_index=True),saida/'particoes_loso_propostas.csv')
    cols=['bloco','variavel_grupo','descricao','status_acervo','fonte','janela','limitacoes']
    catalogo=pd.DataFrame(BLOCOS,columns=cols); catalogo['status_uso']='candidato_nao_selecionado'
    csv_novo(catalogo,saida/'catalogo_blocos_candidatos.csv')
    protocolo={'experimento_principal':'predição retrospectiva, sem alegação de simulação operacional histórica',
        'unidades':255,'pares':9690,'horizonte_principal':'t→t+1','anos_t':[1985,2022],
        '2023':'sem resposta t+1 na Col9; fora do índice supervisionado principal',
        '2024':'reservado para decisão metodológica separada; não usar em atributos, respostas, persistência ou teste',
        'limiares_A_B_C':'nenhum homologado','treinamento':'não autorizado, não executado',
        'teste_ja_explorado_cientificamente':True,'particoes':'proposta mantida; não homologada neste código',
        'dependencia_algoritmica_futura':'Não é resolvida pela aceitação do modo retrospectivo; manter risco e propor auditoria/ablação.',
        'codigo_sha256':sha(Path(__file__)),'consolidado_sha256':sha(resultados/'concluido.json'),
        'artefatos_sha256':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}}
    with (saida/'protocolo.json').open('x',encoding='utf-8') as f: json.dump(protocolo,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in protocolo.items() if k!='artefatos_sha256'},ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--resultados',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True); a=p.parse_args(); executar(a.resultados,a.saida)
