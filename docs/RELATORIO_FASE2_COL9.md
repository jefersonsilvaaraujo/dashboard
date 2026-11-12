# Relatório da Fase 2 Coleção 9

Data: 11 de novembro de 2026. **Fase 2 descritiva implementada e testada localmente**,
com gráficos, filtros e mapas para 255 municípios, exclusivamente em 1985–2023.
A aplicação em execução não foi reconstruída, reiniciada ou substituída.

## Funcionalidades entregues

Página independente `pages/01_Colecao_9_255.py`, com cinco abas:

1. Indicadores: participação de vegetação nativa e usos antrópicos, séries anuais,
   áreas/denominadores e cenários 29+32/25.
2. Classes: áreas anuais, participação percentual com denominador completo e
   distribuição no último ano selecionado; cores próprias da legenda Col9.
3. Comparações temporais: médias anuais por década com número de anos e períodos
   incompletos; comparação entre anos de referência e variação líquida de área.
4. Mapas: coroplético municipal dos indicadores/sensibilidades, com ano e recorte
   definidos pelos filtros; pré-visualizações raster regionais Col9 em 1985/2023.
5. Auditoria e dados: confrontos de área município–ano, classificação oficial e
   operacional separadas, dados e metadados exportáveis.

Filtros por UF, código IBGE e período controlam a mesma seleção territorial nas
consultas analíticas e no coroplético. O filtro de classes afeta as séries temáticas,
comparações e detalhamento, preservando os denominadores/conjuntos dos indicadores
operacionais. Não há correspondência implícita por nome.

As duas pré-visualizações raster são **contexto regional fixo dos 255**, explicitado
na interface; não são apresentadas como se respondessem ao filtro municipal. O
coroplético é o mapa que acompanha o recorte selecionado. Ele mostra uma estatística
por município, não a localização de cada classe de pixel.

## Mapas e proveniência

| Arquivo | Conteúdo |
|---|---|
| visualizacao_col9.py | FeatureCollection e coroplético com verificação de igualdade dos códigos entre indicadores e geometrias |
| processamento/mapas_col9.py | Geração independente dos PNGs 1985/2023, sem importação do ETL legado |
| mapas_col9/colecao9_255_1985.png | Nova pré-visualização regional Col9 |
| mapas_col9/colecao9_255_2023.png | Nova pré-visualização regional Col9 |
| mapas_col9/manifesto.json | Hashes de imagens, rasters, complemento e território; grade e método de desenho |
| mapas_col9/ambiente_geracao.json | Python/bibliotecas/GDAL/PROJ e hash do gerador efetivamente utilizado |
| dados_col9.py | Recusa imagens de outra coleção/anos/território ou com hash divergente |
| testes/test_mapas_col9_geo.py | Complemento somente em zeros dentro dos alvos, preservação de valores existentes e recusa de grades incompatíveis |
| testes/test_fase2_integracao.py | Filtros, denominador, período de um ano e contagem territorial |
| testes/verificar_fase2_container.py | Smoke test sem pytest na imagem do app, usando código montado somente leitura |

Resolução visual: 1400×1037; EPSG:4326; máscara pelos 255 polígonos originais.
Vizinho mais próximo, sem interpolação contínua de códigos. A redução de resolução
é estritamente visual, conforme o conceito de reamostragem da
[documentação Rasterio](https://rasterio.readthedocs.io/en/stable/topics/resampling.html).
Não foram reescritos os rasters nem reaproveitadas imagens da Coleção 10/10.1.

O complemento de 38 bandas do MA preencheu apenas zeros dentro dos três municípios
alvo no desenho, preservando pixels já classificados. Foram preenchidos 304 pixels
na imagem reduzida de cada ano; isso **não** é uma recontagem dos pixels recuperados
nos rasters originais. Bandas, orientação, resolução e encaixe da grade foram
verificados. Os dois PNGs foram abertos e inspecionados visualmente.

O ambiente geoespacial existente usa pandas 2.3.3, enquanto o app usa 3.1.0;
as versões exatas para reprodução das imagens estão registradas no manifesto de
ambiente. O teste do app foi executado também em Python 3.12, imagem existente.

## Testes realizados

| Execução | Resultado |
|---|---|
| Suíte principal com legado e novos testes | 49 passaram, um módulo geoespacial dispensado no venv leve; 95,98s |
| Testes de complemento no ambiente geoespacial | Dois passaram; 0,98s |
| Teste adicional de coleção/hash de imagens | Um passou; 1,65s |
| Smoke test em contêiner temporário Python 3.12 | Passou: 255 municípios, cinco abas, sete gráficos, hashes, filtro de classe sem alterar indicadores, município, um ano e seleção vazia |
| Verificação das geometrias banco/GeoPackage | 255/255 originais idênticas por SHA-256 WKB NDR |
| Revisão visual dos dois PNGs | Concluída |
| git diff --check | Sem erros de whitespace |

Total: **52 testes distintos aprovados**, além do smoke test e das verificações
territoriais/visuais. Todos os testes preexistentes foram mantidos.

Logs: [suíte principal](evidencias/fases1_2_testes_20261111.txt),
[teste de proveniência](evidencias/fase2_testes_proveniencia_mapas_20261111.txt),
[geração de mapas](evidencias/fase2_mapas_execucao_20261111.txt),
[Python 3.12](evidencias/fases1_2_container_20261111.txt).
O stderr informativo do Docker aparece como NativeCommandError no PowerShell;
os comandos de verificação terminaram com exit code 0. A primeira tentativa de
geração detectou Pillow ausente; a dependência foi instalada em pasta temporária
isolada e a geração final passou, sem alterar o venv original.

## Implantação prevista e reversão

**Nenhum comando abaixo foi executado.** Esta é a apresentação do procedimento,
anterior a qualquer implantação. Conferir os relatórios e o estado do checkout,
preservando os arquivos locais já existentes, antes de iniciar.

1. Guardar uma referência durável da imagem atual e do código. O checkpoint desta
   edição está em `C:\Users\jefsl\AppData\Local\Temp\defesa_mestrado_d1d4_20261111_140153\fontes_antes.zip`
   (60 arquivos), mas uma pasta temporária não substitui um backup durável.
2. Garantir que módulos, referências e PNGs novos estejam no checkout usado no
   build. O Dockerfile atual os copia; não adicionar credenciais ao contexto.
3. Reconstruir e subir **somente app**, preservando db e o volume. Não executar etl.

```powershell
# Reservar previamente esse nome para a imagem de retorno; não sobrescrever um checkpoint existente.
$imagemAnteriorCol9 = docker inspect --format '{{.Image}}' dashboard-mestrado-app-1
docker image tag $imagemAnteriorCol9 defesa-mestrado-app:antes-col9-d1d4
docker compose build app
docker compose up -d --no-deps app
docker compose ps
```

Após a implantação, verificar health, página principal e rota Col9, filtros,
downloads, imagens e permissões. O nome da tag deve identificar exatamente a imagem
em execução antes da troca. Não podar imagens enquanto o checkpoint for necessário.

Retorno previsto somente da aplicação:

```powershell
docker image tag defesa-mestrado-app:antes-col9-d1d4 dashboard-mestrado-app
docker compose up -d --no-deps --no-build app
```

Não há rollback SQL: nenhum dado foi alterado. Para desfazer as edições locais,
comparar/restaurar seletivamente a página, dados_col9.py e metadados do checkpoint,
preservando mudanças posteriores do pesquisador. Não usar reset/clean/restauração
global. A reprodução em checkout limpo e a implantação efetiva pertencem à Fase 5.

## Pendências científicas e fases seguintes

Os PNGs são pré-visualizações, não cartografia para mensuração ou produto final
diagramado da dissertação. Não houve verificação visual do navegador completo;
a interação foi verificada por AppTest e os PNGs por inspeção direta.
PRODES/queimadas ainda têm as quatro lacunas territoriais conhecidas e não foram
misturados à Col9. Transições, limiar e alvo seguem a
[proposta específica](PROPOSTA_VARIAVEL_ALVO_CONVERSAO_COL9.md), pendente de validação.
Nenhum modelo foi treinado e nenhum alvo derivou da diferença líquida de áreas.
