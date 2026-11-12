# Relatório da implantação Col9 em 11 de novembro de 2026

O pesquisador confirmou: **“Sim, implantar somente o app”**. Foi aplicada a imagem
candidata previamente construída e testada, com retorno à imagem anterior previsto
se falhassem as verificações. Somente o contêiner app foi substituído.

## Procedimento e preservação

- Checkpoint: `deploy/checkpoint_col9_20261111_152856/`.
- Imagem candidata testada: `defesa-mestrado-app:candidata-checkpoint_col9_20261111_152856`.
- Digest/ID inspecionado da candidata: `sha256:70def38d51e9a39d8f4bec50a7f1589e348065aed90f5cccf55f3b3540350ef2`.
- Imagem anterior preservada: `defesa-mestrado-app:antes-checkpoint_col9_20261111_152856`.
- Ação: Compose `up -d --no-deps --no-build app`, com override somente de imagem.
- Contêiner do banco permaneceu com ID `dcd1266f7358914f2264dbe407a30b97f98f799bf4d8a16ee66f0948bab32d57`.
- Volume permaneceu `dashboard-mestrado_dados_postgres`. Nenhum ETL, migração,
  refresh ou escrita de dados foi executado.

Os IDs posteriores e os resultados estão no recibo `implantar_*.json` do checkpoint.
Valores de credenciais não foram registrados. O procedimento foi implementado em
`deploy/implantacao_col9.ps1`, com guarda de confirmação, conferência das identidades
e opção de retorno apenas da aplicação.

## Verificação funcional após a troca

A verificação foi executada **sobre os arquivos da imagem no contêiner app em
execução**, sem montagem do checkout sobre o código da aplicação:

- Col9: 255 municípios, cinco abas, gráficos, hashes de geometria/imagens,
  filtro de classe sem alterar os indicadores, recorte municipal, período de um
  ano e seleção vazia passaram.
- Legado: dez abas executadas sem exceções.
- Saúde do app e do banco verificada. Health, rota principal e rota Col9 acessíveis.

URLs locais: [painel principal](http://127.0.0.1:8501/) e
[página Col9](http://127.0.0.1:8501/Colecao_9_255).

Evidência: [log de implantação e testes](evidencias/implantacao_col9_aplicacao_20261111.txt).
Os avisos de ScriptRunContext são do teste em modo não interativo; o comando
terminou com exit code 0. Os testes da imagem candidata também haviam passado
antes da troca. Não foi necessário retornar à imagem anterior.

## Limite da conferência visual

Foi tentada a inspeção no Chrome já aberto, por Computer Use. A ferramenta
interrompeu a operação porque não conseguiu confirmar a URL atual com segurança.
Não houve tentativa de contornar esse bloqueio nem continuação da automação UI.
Portanto, os testes funcionais automatizados após implantação foram concluídos,
mas a conferência visual completa no navegador permanece pendente. Os PNGs da
Fase 2 já haviam sido inspecionados separadamente.

## Retorno disponível

Usar o mesmo checkpoint e a ação `Retornar` do procedimento apresentado. Ela aplica
somente a imagem anterior do app, sem alterar o banco ou o volume. Não remover as
imagens/checkpoint antes da aceitação final. A aprovação provisória do pesquisador
e a limitação visual acima permanecem registradas; não há aceitação científica
implícita de transições ou limiares por causa desta implantação.
