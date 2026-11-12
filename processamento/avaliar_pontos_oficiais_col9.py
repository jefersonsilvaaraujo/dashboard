"""Diagnóstico reproduzível dos pontos oficiais Col9. Sem banco, rótulos ou correções.

CSV é a referência principal por vínculo explícito na página oficial. Vetor é uma
segunda versão, nunca fonte de preenchimento dos anos/classes ausentes no CSV.
Saídas exclusivamente novas. As medidas de concordância são descritivas.
"""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import sys
import unicodedata

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
from shapely import points, covers

PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJETO))
from processamento.cenarios_validacao_col9 import VN, UA, sha, csv_novo
from processamento.manifesto_transicoes_col9 import grade, conferir_grade

ANOS = np.arange(1985, 2024)
# Códigos da legenda da referência: 19/36 são categorias agrícolas agregadas,
# não novas classes terminais adicionadas à legenda do raster Col9.
ROTULOS = {
    'FORMACAO FLORESTAL': 3, 'FORMACAO SAVANICA': 4, 'MANGUE': 5,
    'FLORESTA INUNDAVEL': 6, 'FLORESTA PLANTADA': 9,
    'CAMPO ALAGADO E AREA PANTANOSA': 11, 'FORMACAO CAMPESTRE': 12,
    'OUTRA FORMACAO NAO FLORESTAL': 13, 'PASTAGEM': 15,
    'LAVOURA TEMPORARIA': 19, 'CANA': 20, 'PRAIA E DUNA': 23,
    'INFRAESTRUTURA URBANA': 24, 'OUTRA AREA NAO VEGETADA': 25,
    'NAO OBSERVADO': 27, 'AFLORAMENTO ROCHOSO': 29,
    'MINERACAO': 30, 'AQUICULTURA': 31, 'APICUM': 32,
    'RIO, LAGO E OCEANO': 33, 'LAVOURA PERENE': 36,
    'RESTINGA HERBACEA': 50,
}
PRIORIDADES = [5103809, 2109908, 5107107, 5105507, 2102325]


def normalizar(s):
    if pd.isna(s):
        return ''
    return ''.join(c for c in unicodedata.normalize('NFKD', str(s).upper().strip())
                   if not unicodedata.combining(c))


def codificar(s):
    # Sem aproximação textual: rótulo corrompido/ambíguo permanece desconhecido.
    return s.map(lambda x: ROTULOS.get(normalizar(x), -1)).to_numpy(dtype=np.int16)


def grupos(a, referencia=False, extras_o=(), extras_d=()):
    a = np.asarray(a)
    conhecido = np.isin(a, list(ROTULOS.values()) + VN + UA + [21, 49])
    g = np.where(conhecido & ~np.isin(a, [0, 13, 27]), 3, -1).astype(np.int8)
    g[np.isin(a, VN + list(extras_o))] = 1
    destinos = UA + list(extras_d) + ([19, 36] if referencia else [])
    g[np.isin(a, destinos)] = 2
    return g


def evento(a, b, referencia=False, extras_o=(), extras_d=()):
    g0 = grupos(a, referencia, extras_o, extras_d)
    g1 = grupos(b, referencia, extras_o, extras_d)
    return (g0 > 0) & (g1 > 0), (g0 == 1) & (g1 == 2)


def resumo_binario(ref, mapa, pesos=None):
    ref = np.asarray(ref, bool); mapa = np.asarray(mapa, bool)
    w = np.ones(len(ref)) if pesos is None else np.asarray(pesos, float)
    if ref.shape != mapa.shape or ref.shape != w.shape:
        raise ValueError('Dimensões incompatíveis.')
    if not np.isfinite(w).all() or (w <= 0).any():
        raise ValueError('Pesos inválidos.')
    tp, fp, fn, tn = [float(w[m].sum()) for m in
                     (ref & mapa, ~ref & mapa, ref & ~mapa, ~ref & ~mapa)]
    def razao(n, d): return n/d if d else None
    return {'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn,
            'precisao_descritiva': razao(tp, tp+fp),
            'sensibilidade_descritiva': razao(tp, tp+fn),
            'concordancia_descritiva': razao(tp+tn, tp+fp+fn+tn),
            'F1_descritivo': razao(2*tp, 2*tp+fp+fn)}


def persistencia(mapa):
    """t+2 somente disponível até 2023; indisponível = -1, nunca falso/zero."""
    mapa = np.asarray(mapa)
    if mapa.ndim != 2 or mapa.shape[1] != 39:
        raise ValueError('Esperada série completa 1985–2023.')
    comum, conv = evento(mapa[:, :-1], mapa[:, 1:])
    p = np.full(conv.shape, -1, dtype=np.int8)
    rev_vn = p.copy(); rev_classe = p.copy()
    futuro = grupos(mapa[:, 2:])
    valido = conv[:, :-1] & (futuro > 0)
    p[:, :-1] = np.where(valido, futuro == 2, -1)
    rev_vn[:, :-1] = np.where(valido, futuro == 1, -1)
    rev_classe[:, :-1] = np.where(valido, mapa[:, 2:] == mapa[:, :-2], -1)
    return comum, conv, p, rev_vn, rev_classe


def ler_celulas(src, linhas, colunas, banda=1, vizinhanca=True):
    """Leitura ordenada por linha, sem reamostragem nem deslocamento dos pontos."""
    offsets = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)] if vizinhanca else [(0, 0)]
    rr = np.asarray(linhas)[:, None] + np.array([x[0] for x in offsets])
    cc = np.asarray(colunas)[:, None] + np.array([x[1] for x in offsets])
    dentro = (rr >= 0) & (rr < src.height) & (cc >= 0) & (cc < src.width)
    out = np.zeros(rr.shape, dtype=src.dtypes[banda-1])
    ii, jj = np.nonzero(dentro)
    if not len(ii):
        return out, dentro
    ordenados = np.argsort(rr[ii, jj], kind='stable')
    ii, jj = ii[ordenados], jj[ordenados]
    bordas = np.r_[0, np.flatnonzero(np.diff(rr[ii, jj]))+1, len(ii)]
    for a, b in zip(bordas[:-1], bordas[1:]):
        inds, slots = ii[a:b], jj[a:b]
        cols = cc[inds, slots]; row = int(rr[inds[0], slots[0]])
        c0, c1 = int(cols.min()), int(cols.max())+1
        dados = src.read(banda, window=Window(c0, row, c1-c0, 1))[0]
        out[inds, slots] = dados[cols-c0]
    if src.nodata is not None:
        dentro &= out != src.nodata
    return out, dentro


def extrair(m, pts, geom, pasta):
    base = Path(m['base_dados']); v = np.zeros((len(pts), 39, 9), np.uint8)
    patch_usado = np.zeros((len(pts), 39), bool)
    evidencia = []
    with rasterio.Env(GDAL_CACHEMAX=256*1024*1024), rasterio.open(base/m['complemento']['arquivo']) as patch:
        for j, ano in enumerate(ANOS):
            r = m['rasters'][str(ano)]; path = base/r['arquivo']; st = path.stat()
            if st.st_size != r['bytes'] or st.st_mtime_ns != r['mtime_ns']:
                raise ValueError(f'Fonte mudou desde manifesto SHA256: {path}')
            with rasterio.open(path) as src:
                conferir_grade(r['grade'], grade(src))
                if j == 0:
                    lin, col = rasterio.transform.rowcol(src.transform, pts.LON, pts.LAT)
                    lin, col = np.array(lin), np.array(col)
                    xx, yy = rasterio.transform.xy(src.transform, lin, col)
                    pts['linha_raster'] = lin; pts['coluna_raster'] = col
                    pts['centro_lon'] = xx; pts['centro_lat'] = yy
                    pts['distancia_centro_pixels'] = np.hypot((pts.LON-xx)/src.transform.a, (pts.LAT-yy)/src.transform.e)
                    pol = geom.set_index('CD_MUN').geometry.reindex(pts.CD_MUN)
                    pts['centro_pixel_no_mesmo_municipio'] = covers(pol.to_numpy(), points(xx, yy))
                    if not ((lin >= 0) & (lin < src.height) & (col >= 0) & (col < src.width)).all():
                        raise ValueError('Ponto selecionado fora da grade raster.')
                valores, ok = ler_celulas(src, lin, col)
                valores[~ok] = 0
                if ano != 2002:
                    sel = np.flatnonzero(pts.CD_MUN.isin(m['complemento']['municipios']))
                    if len(sel):
                        dx, dy = m['complemento']['offset_col_linha']
                        banda = m['complemento']['descricoes'].index(f'classification_{ano}')+1
                        p, vp = ler_celulas(patch, lin[sel]-dy, col[sel]-dx, banda)
                        # Mesmo domínio de centro de pixel usado na matriz consolidada.
                        rr = lin[sel, None]+np.repeat([-1, 0, 1], 3)
                        cc = col[sel, None]+np.tile([-1, 0, 1], 3)
                        x, y = src.transform * (cc+.5, rr+.5)
                        gg = geom.set_index('CD_MUN').geometry.reindex(pts.CD_MUN.iloc[sel]).to_numpy()
                        no_mun = covers(np.repeat(gg, 9), points(x.ravel(), y.ravel())).reshape(len(sel), 9)
                        aplicar = (valores[sel] == 0) & vp & ~np.isin(p, [0, 27]) & no_mun
                        vv = valores[sel].copy(); vv[aplicar] = p[aplicar]; valores[sel] = vv
                        patch_usado[sel, j] = aplicar[:, 4]
                conhecidos = pd.read_csv(PROJETO/'referencias/legenda_col9.csv').classe_cobertura.to_numpy()
                if not np.isin(valores, np.r_[conhecidos, 0]).all():
                    raise ValueError('Código raster desconhecido.')
                v[:, j] = valores
                evidencia.append({'ano': int(ano), 'sha256_preexistente': r['sha256'],
                                  'stat_confere': True, 'grade_confere': True, 'arquivo': r['arquivo']})
            print(f'Extração oficial {ano}: {len(pts)} pontos, nove células, leitura somente.', flush=True)
    csv_novo(pts.drop(columns='geometry', errors='ignore'), pasta/'pontos_selecionados.csv')
    np.savez_compressed(pasta/'extracao_rasters.npz', TARGETID=pts.TARGETID.to_numpy(), anos=ANOS,
                        classes_vizinhanca=v, complemento_centro=patch_usado)
    return v, patch_usado, evidencia


def avaliar_coortes(long, pasta):
    tabelas = []; anuais = []; globais = []
    for versao, d in long.groupby('versao_referencia'):
        for coorte, filtro in {
            'todos': np.ones(len(d), bool),
            'sem_marcacao_treino': d.AMOSTRA_AM.eq(0),
            'sem_treino_sem_borda': d.AMOSTRA_AM.eq(0) & d.sem_borda,
            'sem_treino_count3_sem_borda': d.AMOSTRA_AM.eq(0) & d.sem_borda & d.count3,
        }.items():
            z = d.loc[filtro & d.comparavel].copy()
            for chaves in [[], ['ano_destino'], ['SIGLA_UF'], ['CD_MUN', 'NM_MUN', 'SIGLA_UF']]:
                it = [((), z)] if not chaves else z.groupby(chaves, sort=True)
                linhas = []
                for key, a in it:
                    key = key if isinstance(key, tuple) else (key,)
                    r = dict(zip(chaves, key)); r.update(versao_referencia=versao, coorte=coorte,
                        n_pares=len(a), n_pontos=int(a.TARGETID.nunique()))
                    r.update(resumo_binario(a.evento_referencia, a.evento_mapa))
                    rw = resumo_binario(a.evento_referencia, a.evento_mapa, a.peso)
                    r.update({f'pesos_publicados_{k}': val for k, val in rw.items()})
                    r['escopo'] = 'descritivo_sem_IC_sem_inferencia_populacional'
                    linhas.append(r)
                nome = 'global' if not chaves else ('ano' if chaves[0] == 'ano_destino' else ('estado' if chaves[0] == 'SIGLA_UF' else 'municipio'))
                tabelas.append((nome, pd.DataFrame(linhas)))
            # Matriz binária de frequências completas, inclusive zeros explícitos.
            for ano, a in z.groupby('ano_destino'):
                for mm in (False, True):
                    for rr in (False, True):
                        b = a.loc[a.evento_mapa.eq(mm) & a.evento_referencia.eq(rr)]
                        anuais.append({'versao_referencia': versao, 'coorte': coorte,
                            'ano_destino': ano, 'evento_mapa': mm, 'evento_referencia': rr,
                            'n': len(b), 'soma_pesos_publicados': b.peso.sum()})
    for nome in ['global', 'ano', 'estado', 'municipio']:
        csv_novo(pd.concat([d for k, d in tabelas if k == nome], ignore_index=True), pasta/f'concordancia_{nome}.csv')
    csv_novo(pd.DataFrame(anuais), pasta/'matrizes_binarias_descritivas.csv')


def executar(fontes, saida, manifesto):
    if saida.exists():
        raise FileExistsError('Saída existente preservada; use novo diretório.')
    saida.mkdir(parents=True)
    m = json.loads(manifesto.read_text(encoding='utf-8')); base = Path(m['base_dados'])
    gpkg = base/m['territorio']['arquivo']
    if sha(gpkg) != m['territorio']['sha256']:
        raise ValueError('Território não confere.')
    g = gpd.read_file(gpkg); g.CD_MUN = g.CD_MUN.astype(int)
    hashes = json.loads((PROJETO/'referencias/territorio_col9_hashes.json').read_text(encoding='utf-8'))['geometrias_sha256_wkb_ndr']
    import hashlib
    for r in g.itertuples():
        if hashlib.sha256(r.geometry.wkb).hexdigest() != hashes[str(r.CD_MUN)]:
            raise ValueError('Geometria canônica alterada.')
    g = g.to_crs(4326)
    d = pd.read_csv(next(fontes.glob('*.csv.csv')), low_memory=False)
    v = gpd.read_file('zip://'+str((fontes/'mapbiomas_85k_points_validation.zip').resolve()))
    if len(d) != 85152 or d.TARGETID.duplicated().any() or v.TARGETID.duplicated().any():
        raise ValueError('Inventário oficial inesperado.')
    v = v.set_index('TARGETID').reindex(d.TARGETID).reset_index()
    if v.geometry.isna().any(): raise ValueError('IDs das versões diferem.')
    for c in ['PESO_AMOS', 'PROB_AMOS_']:
        d[c] = pd.to_numeric(d[c].astype(str).str.replace(',', '.', regex=False), errors='raise')
    if not np.allclose(d.PESO_AMOS*d.PROB_AMOS_, 1): raise ValueError('Peso/probabilidade incoerentes.')
    pt = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.LON, d.LAT), crs=4326)
    s = gpd.sjoin(pt, g[['CD_MUN', 'NM_MUN', 'SIGLA_UF', 'geometry']], how='inner', predicate='intersects')
    if s.TARGETID.duplicated().any():
        csv_novo(s.drop(columns='geometry'), saida/'limites_multiplos.csv')
        raise ValueError('Ponto em múltiplos municípios; requer regra explícita.')
    s = s.sort_values('TARGETID').reset_index(drop=True)
    vs = v.set_index('TARGETID').reindex(s.TARGETID)
    s['CD_MUN_vetor_publicado'] = vs.CD_MUN.to_numpy()
    s['municipio_diverge_vetor'] = pd.to_numeric(s.CD_MUN_vetor_publicado, errors='coerce').ne(s.CD_MUN).to_numpy()
    nacional = []
    for a in ANOS:
        cod = codificar(d[f'CLASS_{a}'])
        nacional.append({'ano': int(a), 'n_classe_preenchida': int(d[f'CLASS_{a}'].notna().sum()),
                         'n_ref_grupo_conhecido': int((grupos(cod, True)>0).sum()),
                         'n_count_positivo': int(d[f'COUNT_{a}'].gt(0).sum())})
    csv_novo(pd.DataFrame(nacional), saida/'cobertura_nacional_ano.csv')
    dic = []
    for label in pd.unique(d.filter(regex=r'^CLASS_\d').values.ravel()):
        c = ROTULOS.get(normalizar(label), -1)
        dic.append({'rotulo_original': str(label), 'codigo_referencia': c,
            'grupo_operacional': int(grupos([c], True)[0]),
            'nota': 'ambíguo/ausente: excluído da comparação de grupos' if grupos([c], True)[0] < 0
                    else ('categoria agregada UA; não equivale a terminal raster' if c in [19,36] else 'correspondência sem equivalência forçada de subclasses')})
    csv_novo(pd.DataFrame(dic), saida/'dicionario_harmonizacao.csv')
    estratos = d.groupby(['CARTA_2', 'DECLIVIDAD'], dropna=False).agg(
        n_nacional=('TARGETID', 'size'), n_treino=('AMOSTRA_AM', 'sum'),
        peso_min=('PESO_AMOS', 'min'), peso_max=('PESO_AMOS', 'max'),
        prob_min=('PROB_AMOS_', 'min'), prob_max=('PROB_AMOS_', 'max')).reset_index()
    e = s.groupby(['CARTA_2', 'DECLIVIDAD']).agg(n_recorte=('TARGETID', 'size'),
        n_treino_recorte=('AMOSTRA_AM', 'sum')).reset_index()
    estratos = estratos.merge(e, how='left', on=['CARTA_2', 'DECLIVIDAD']).fillna({'n_recorte':0,'n_treino_recorte':0})
    csv_novo(estratos, saida/'estratos_originais_nacionais_recorte.csv')
    cov = s.groupby(['CD_MUN']).agg(n_pontos=('TARGETID', 'size'),
        n_treino=('AMOSTRA_AM','sum')).reset_index()
    cov = g.drop(columns='geometry').merge(cov, on='CD_MUN', how='left').fillna({'n_pontos':0,'n_treino':0})
    cov['n_sem_marcacao_treino'] = cov.n_pontos-cov.n_treino
    csv_novo(cov, saida/'cobertura_255_municipios.csv')
    csv_novo(s.groupby(['CD_MUN','NM_MUN','SIGLA_UF','CARTA_2','DECLIVIDAD'], dropna=False).size().rename('n_pontos').reset_index(), saida/'cobertura_municipio_estrato.csv')
    valores, patch, fontes_raster = extrair(m, s, g, saida)
    mapa = valores[:, :, 4]; pares = []; anual = []; diverg = []
    refs = {}
    for versao in ['csv_principal', 'vetor_auxiliar']:
        ref = np.full((len(s),39), -1, np.int16); ct = np.zeros_like(ref); bd = np.zeros_like(ref)
        for j, a in enumerate(ANOS):
            if versao == 'vetor_auxiliar' and a == 2023: continue
            origem = s if versao == 'csv_principal' else vs
            ref[:,j] = codificar(origem[f'CLASS_{a}']) if versao == 'csv_principal' else pd.to_numeric(origem[f'CLASS_{a}'], errors='coerce').fillna(-1).to_numpy(np.int16)
            ct[:,j] = origem[f'COUNT_{a}'].fillna(0).to_numpy(np.int16)
            bd[:,j] = origem[f'BORDA_{a}'].fillna(0).to_numpy(np.int16)
        refs[versao] = ref
        valido_r, evento_r = evento(ref[:,:-1], ref[:,1:], True)
        valido_m, evento_m = evento(mapa[:,:-1], mapa[:,1:])
        for j, a in enumerate(ANOS):
            gp = grupos(ref[:,j], True); gm = grupos(mapa[:,j])
            aa = s[['TARGETID','CD_MUN','NM_MUN','SIGLA_UF','BIOMA_250K','CARTA_2','DECLIVIDAD','AMOSTRA_AM']].copy()
            aa['ano'] = int(a); aa['versao_referencia'] = versao
            aa['classe_referencia'] = ref[:,j]; aa['classe_mapa'] = mapa[:,j]
            aa['grupo_referencia'] = gp; aa['grupo_mapa'] = gm
            aa['COUNT'] = ct[:,j]; aa['BORDA'] = bd[:,j]
            aa['comparavel'] = (gp>0)&(gm>0)&(ct[:,j]>0)
            aa['concorda_grupo'] = (gp==gm)&aa.comparavel
            aa['peso'] = s.PESO_AMOS
            aa['homogeneidade_3x3_classe'] = (valores[:,j] == mapa[:,j,None]).mean(axis=1)
            aa['homogeneidade_3x3_grupo'] = (grupos(valores[:,j]) == gm[:,None]).mean(axis=1)
            anual.append(aa)
        for j, t in enumerate(ANOS[:-1]):
            z = s[['TARGETID','CD_MUN','NM_MUN','SIGLA_UF','BIOMA_250K','CARTA_2','DECLIVIDAD','AMOSTRA_AM']].copy()
            z['ano_origem'] = int(t); z['ano_destino'] = int(t+1)
            z['versao_referencia'] = versao
            z['ref_t'] = ref[:,j]; z['ref_t1'] = ref[:,j+1]
            z['mapa_t'] = mapa[:,j]; z['mapa_t1'] = mapa[:,j+1]
            z['COUNT_t'] = ct[:,j]; z['COUNT_t1'] = ct[:,j+1]
            z['BORDA_t'] = bd[:,j]; z['BORDA_t1'] = bd[:,j+1]
            z['referencia_par_valido'] = valido_r[:,j] & (ct[:,j]>0) & (ct[:,j+1]>0)
            z['mapa_par_valido'] = valido_m[:,j]
            z['comparavel'] = z.referencia_par_valido & z.mapa_par_valido
            z['evento_referencia'] = evento_r[:,j]; z['evento_mapa'] = evento_m[:,j]
            z['sem_borda'] = (bd[:,j]==0)&(bd[:,j+1]==0)
            z['count3'] = (ct[:,j]==3)&(ct[:,j+1]==3)
            z['peso'] = s.PESO_AMOS
            z['evidencia'] = np.where(~z.comparavel,'inconclusivo',np.where(z.evento_mapa == z.evento_referencia,
                                   'concordante','discordante_com_referencia_publicada'))
            pares.append(z)
    long = pd.concat(pares,ignore_index=True); annual = pd.concat(anual,ignore_index=True)
    csv_novo(long, saida/'comparacoes_ponto_par.csv')
    # Dados anuais completos ficam em formato compacto + tabelas agregadas auditáveis.
    np.savez_compressed(saida/'referencias_harmonizadas.npz', TARGETID=s.TARGETID.to_numpy(), anos=ANOS, **refs)
    for grupos_c, nome in [(['versao_referencia','ano','classe_referencia'],'classe_ano'),
                           (['versao_referencia','CD_MUN','NM_MUN','SIGLA_UF','ano'],'municipio_ano'),
                           (['versao_referencia','SIGLA_UF','ano'],'estado_ano'),
                           (['versao_referencia','CARTA_2','DECLIVIDAD','ano'],'estrato_ano')]:
        ag = annual.groupby(grupos_c, dropna=False).agg(n_pontos=('TARGETID','size'),
            n_comparaveis=('comparavel','sum'), n_concordam_grupo=('concorda_grupo','sum'),
            n_treino=('AMOSTRA_AM','sum')).reset_index()
        csv_novo(ag, saida/f'cobertura_{nome}.csv')
    cross = annual.groupby(['versao_referencia','ano','classe_referencia','classe_mapa'],dropna=False).size().rename('n').reset_index()
    csv_novo(cross, saida/'cruzamento_classes_anuais.csv')
    ct = long.groupby(['versao_referencia','ano_destino','ref_t','ref_t1'],dropna=False).agg(
        n=('TARGETID','size'),n_comparaveis=('comparavel','sum')).reset_index()
    csv_novo(ct, saida/'cobertura_transicao_referencia.csv')
    avaliar_coortes(long, saida)
    for j,a in enumerate(ANOS[:-1]):
        # Conflitos são entre DUAS referências publicadas, não correções.
        x, y = refs['csv_principal'][:,j], refs['vetor_auxiliar'][:,j]
        ok = (grupos(x,True)>0)&(grupos(y,True)>0)
        diverg.append({'ano':int(a),'n_pontos':len(s),'n_comparaveis':int(ok.sum()),
            'n_divergem_codigo':int(((x!=y)&ok).sum()),
            'n_divergem_grupo':int(((grupos(x,True)!=grupos(y,True))&ok).sum())})
    csv_novo(pd.DataFrame(diverg), saida/'divergencias_versoes_recorte_ano.csv')
    csv_novo(long.loc[long.CD_MUN.isin(PRIORIDADES) & long.ano_destino.isin([2000,2001,2002,2003,2004,2019,2020,2021,2022,2023])],
             saida/'casos_prioritarios_controles.csv')
    _, conv, per, rev, rc = persistencia(mapa)
    temporal = []
    for j,t in enumerate(ANOS[:-1]):
        z = s[['TARGETID','CD_MUN','NM_MUN','SIGLA_UF','AMOSTRA_AM']].copy()
        z['ano_origem']=int(t); z['ano_destino']=int(t+1)
        z['mapa_t']=mapa[:,j]; z['mapa_t1']=mapa[:,j+1]
        z['mapa_tmenos1']=mapa[:,j-1] if j else -1
        z['mapa_t2']=mapa[:,j+2] if j+2<39 else -1
        z['conversao']=conv[:,j]; z['persiste_UA_t2']=per[:,j]
        z['reverte_VN_t2']=rev[:,j]; z['reverte_classe_t2']=rc[:,j]
        z['UA_tmenos1']=np.isin(mapa[:,j-1],UA).astype(np.int8) if j else -1
        z['homogeneidade_3x3_t']= (valores[:,j] == mapa[:,j,None]).mean(axis=1)
        z['homogeneidade_3x3_t1']= (valores[:,j+1] == mapa[:,j+1,None]).mean(axis=1)
        temporal.append(z)
    temporal = pd.concat(temporal,ignore_index=True)
    csv_novo(temporal,saida/'auditoria_temporal_pontos.csv')
    csv_novo(temporal.loc[temporal.conversao].groupby(['ano_destino','mapa_t','mapa_t1']).agg(
        n_conversoes=('TARGETID','size'), n_com_futuro=('persiste_UA_t2',lambda x:int((x>=0).sum())),
        n_persistem=('persiste_UA_t2',lambda x:int((x==1).sum())),
        n_revertem_VN=('reverte_VN_t2',lambda x:int((x==1).sum()))).reset_index(), saida/'persistencia_por_fluxo_ano.csv')
    info = {'executado_em_utc':datetime.now(timezone.utc).isoformat(),
        'pontos_nacionais':len(d),'pontos_recorte':len(s),'municipios_com_pontos':int(s.CD_MUN.nunique()),
        'treinamento_nacional_marcado':int(d.AMOSTRA_AM.sum()),'treinamento_recorte':int(s.AMOSTRA_AM.sum()),
        'nota_treinamento':'Apêndice informa 10000; arquivo marca9999. Não inventar o ID restante.',
        'csv_vector_max_delta_lon':float(np.max(abs(v.geometry.x.to_numpy()-d.LON))),
        'csv_vector_max_delta_lat':float(np.max(abs(v.geometry.y.to_numpy()-d.LAT))),
        'vetor_atributos_lon_lat_invertidos':bool(np.allclose(v.LON,d.LAT) and np.allclose(v.LAT,d.LON)),
        'municipio_publicado_divergente':int(s.municipio_diverge_vetor.sum()),
        'centro_pixel_fora_municipio':int((~s.centro_pixel_no_mesmo_municipio).sum()),
        'distancia_centro_pixels':s.distancia_centro_pixels.describe(percentiles=[.05,.5,.95,.99]).to_dict(),
        'anos_csv':ANOS.tolist(),'anos_vetor':ANOS[:-1].tolist(),
        'n_ref2023_recorte':int(s.CLASS_2023.notna().sum()),
        'estatistica':'Diagnósticos descritivos, inclusive ponderação publicada como sensibilidade; sem IC/representatividade.',
        'matrizes_sem_modificacao':True,'sem_Y_homologado':True,'sem_treinamento':True,
        'manifesto_rasters_sha256':sha(manifesto),'territorio_sha256':sha(gpkg),
        'fontes_raster':fontes_raster,
        'versoes':{p:importlib.metadata.version(p) for p in ['numpy','pandas','rasterio','geopandas','shapely','pyproj']}}
    (saida/'resumo_execucao.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in info.items() if k not in ['fontes_raster','distancia_centro_pixels']},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fontes',type=Path,required=True);p.add_argument('--saida',type=Path,required=True)
    p.add_argument('--manifesto',type=Path,default=PROJETO/'referencias/manifesto_rasters_transicoes_col9.json')
    a=p.parse_args();executar(a.fontes,a.saida,a.manifesto)
