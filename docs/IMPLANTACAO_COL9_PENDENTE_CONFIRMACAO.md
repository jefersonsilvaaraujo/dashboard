# Implantação das Fases 1 e 2 preparada para confirmação

Estado atualizado: **implantação executada após confirmação expressa do pesquisador**.
Este arquivo preserva o procedimento apresentado antes da confirmação. O resultado
está em [Relatório da implantação](RELATORIO_IMPLANTACAO_COL9_20261111.md).
Checkpoint: `deploy/checkpoint_col9_20261111_152856/`.

## Preparação executada sem implantar

- Imagem candidata: `defesa-mestrado-app:candidata-checkpoint_col9_20261111_152856`.
- Cópia identificada da imagem anterior: `defesa-mestrado-app:antes-checkpoint_col9_20261111_152856`.
- Registro de IDs de app/db, imagem anterior e volume nomeado em `antes.json`;
  identidade da candidata testada em `preparado.json`. Nenhuma credencial foi registrada.
- Build com resultados pesados e segredos excluídos do contexto.
- Teste em contêiner temporário da **imagem candidata**, sem montar o código da
  aplicação por cima: Col9 com 255 municípios, gráficos, filtros, hashes das
  geometrias/imagens, denominador, seleção vazia e dez abas legadas passaram.
- App e banco em execução mantiveram seus IDs; nenhum serviço foi substituído.

Evidência: `docs/evidencias/implantacao_col9_preparacao_final_20261111.txt`.
O script de preparação foi corrigido para a sintaxe da versão instalada do
Docker Compose e para o tratamento de argumentos do PowerShell antes desse teste.
Não foi alterada permanentemente a política de execução do Windows.

## Ação apresentada para confirmação do pesquisador

Recriar **somente o serviço app** usando a candidata já testada. Haverá uma breve
indisponibilidade do dashboard durante a substituição desse contêiner. O serviço
db e seu volume não serão recriados, reiniciados ou migrados. Nenhum ETL será executado.

Antes da troca, o procedimento verifica novamente a identidade do banco, do
volume, do app antigo e da imagem candidata. A troca usa `up --no-deps --no-build app`.
Depois, verifica saúde e executa a verificação funcional sobre o código da imagem
realmente em execução, tanto da Col9 quanto das dez abas legadas.

Comando apresentado e depois executado mediante confirmação nesta conversa:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deploy/implantacao_col9.ps1 -Acao Implantar -Checkpoint D:/mestrado/dashboard/deploy/checkpoint_col9_20261111_152856 -ConfirmadoPeloPesquisador
```

A opção de política acima se limita ao processo PowerShell desse comando; não
modifica a política permanente. O script completo está em `deploy/implantacao_col9.ps1`.

Verificação de acesso após implantação: `http://127.0.0.1:8501/` e
`http://127.0.0.1:8501/Colecao_9_255`, além do health e dos testes funcionais.
O status final de implantação depende dos resultados, não apenas de HTTP 200.

## Retorno em caso de falha

Restaurar somente app à imagem anterior preservada, sem tocar no banco. O retorno
faz parte do procedimento proposto para autorização; nenhuma reversão SQL é necessária.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File deploy/implantacao_col9.ps1 -Acao Retornar -Checkpoint D:/mestrado/dashboard/deploy/checkpoint_col9_20261111_152856 -ConfirmadoPeloPesquisador
```

Se o estado dos serviços ou da candidata tiver mudado desde a preparação, o script
interrompe a ação para revisão. Não podar imagens nem remover o checkpoint antes
da aceitação funcional. Nenhuma confirmação será inferida do tempo decorrido.
