param(
    [ValidateSet('Preparar','Implantar','Retornar')][string]$Acao='Preparar',
    [string]$Checkpoint,
    [switch]$ConfirmadoPeloPesquisador
)
$ErrorActionPreference='Stop'
$raizCol9=Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $raizCol9
if (-not $Checkpoint) {
    if ($Acao -ne 'Preparar') { throw 'Informe o checkpoint preparado para implantar/retornar.' }
    $Checkpoint=Join-Path $PSScriptRoot ('checkpoint_col9_'+(Get-Date -Format 'yyyyMMdd_HHmmss'))
}
$Checkpoint=[IO.Path]::GetFullPath($Checkpoint)

function Docker-Col9 {
    param([string[]]$Argumentos)
    $preferenciaCol9=$ErrorActionPreference
    $ErrorActionPreference='Continue'
    $saidaCol9=& docker.exe @Argumentos 2>&1 | ForEach-Object { $_.ToString() }
    $codigoCol9=$LASTEXITCODE
    $ErrorActionPreference=$preferenciaCol9
    if ($codigoCol9 -ne 0) { throw ('Docker falhou: '+($Argumentos -join ' ')+[Environment]::NewLine+($saidaCol9 -join [Environment]::NewLine)) }
    return $saidaCol9
}
function Estado-Col9([string]$Nome) {
    $idCol9=(Docker-Col9 -Argumentos @('inspect','--format','{{.Id}}',$Nome)) -join ''
    $imagemCol9=(Docker-Col9 -Argumentos @('inspect','--format','{{.Image}}',$Nome)) -join ''
    $saudeCol9=(Docker-Col9 -Argumentos @('inspect','--format','{{.State.Health.Status}}',$Nome)) -join ''
    return @{nome=$Nome;id=$idCol9;imagem=$imagemCol9;saude=$saudeCol9}
}
function Volume-Col9 {
    $montagensCol9=((Docker-Col9 -Argumentos @('inspect','--format','{{json .Mounts}}','dashboard-mestrado-db-1')) -join '') | ConvertFrom-Json
    $vCol9=@($montagensCol9 | Where-Object { $_.Destination -eq '/var/lib/postgresql/data' })
    if ($vCol9.Count -ne 1 -or -not $vCol9[0].Name) { throw 'Volume nomeado do banco não identificado.' }
    return $vCol9[0].Name
}
function Conferir-BancoCol9($Anterior) {
    $dbCol9=Estado-Col9 'dashboard-mestrado-db-1'
    if ($dbCol9.id -ne $Anterior.db.id -or (Volume-Col9) -ne $Anterior.volume_db) { throw 'Identidade/volume do banco mudou; interrompido.' }
}
function Testar-ImagemCol9([string]$Override) {
    Docker-Col9 -Argumentos @('compose','-f','docker-compose.yml','-f',$Override,'run','--rm','--no-deps','-T',
        '--workdir','/app','--volume',($raizCol9.Replace('\','/')+'/testes:/verificacao:ro'),
        '--env','COL9_RAIZ_APP=/app','--env','COL9_VERIFICAR_LEGADO=1',
        'app','python','/verificacao/verificar_fase2_container.py')
}

if ($Acao -eq 'Preparar') {
    if (Test-Path -LiteralPath $Checkpoint) { throw 'Checkpoint existente; não será sobrescrito.' }
    New-Item -ItemType Directory -Path $Checkpoint | Out-Null
    $sufixoCol9=Split-Path $Checkpoint -Leaf
    $antesCol9=@{app=(Estado-Col9 'dashboard-mestrado-app-1'); db=(Estado-Col9 'dashboard-mestrado-db-1');
        volume_db=(Volume-Col9); tag_anterior=('defesa-mestrado-app:antes-'+$sufixoCol9);
        tag_candidata=('defesa-mestrado-app:candidata-'+$sufixoCol9); preparado_em=(Get-Date -Format o)}
    if ($antesCol9.app.saude -ne 'healthy' -or $antesCol9.db.saude -ne 'healthy') { throw 'Serviços atuais não estão saudáveis.' }
    $antesCol9 | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $Checkpoint 'antes.json')
    Docker-Col9 -Argumentos @('image','tag',$antesCol9.app.imagem,$antesCol9.tag_anterior)
    Docker-Col9 -Argumentos @('build','--tag',$antesCol9.tag_candidata,'--file','Dockerfile','.')
    $candidatoCol9=Join-Path $Checkpoint 'candidato.compose.yml'
    @('services:','  app:',('    image: '+$antesCol9.tag_candidata)) | Set-Content -Encoding UTF8 $candidatoCol9
    @('services:','  app:',('    image: '+$antesCol9.tag_anterior)) | Set-Content -Encoding UTF8 (Join-Path $Checkpoint 'retorno.compose.yml')
    Testar-ImagemCol9 $candidatoCol9
    Conferir-BancoCol9 $antesCol9
    $appConferidoCol9=Estado-Col9 'dashboard-mestrado-app-1'
    if ($appConferidoCol9.id -ne $antesCol9.app.id) { throw 'O contêiner app mudou durante a preparação.' }
    $imagemCandidataCol9=(Docker-Col9 -Argumentos @('image','inspect','--format','{{.Id}}',$antesCol9.tag_candidata)) -join ''
    @{status='pronto_para_confirmacao'; imagem_candidata=$imagemCandidataCol9; tag=$antesCol9.tag_candidata;
      app_original_preservado=$true; db_preservado=$true} | ConvertTo-Json |
      Set-Content -Encoding UTF8 (Join-Path $Checkpoint 'preparado.json')
    Write-Output ('PREPARADO; nenhuma implantação executada. Checkpoint: '+$Checkpoint)
    exit 0
}

if (-not $ConfirmadoPeloPesquisador) { throw 'Implantação/retorno exige confirmação explícita do pesquisador nesta conversa.' }
$antesCol9=Get-Content -Raw -Encoding UTF8 (Join-Path $Checkpoint 'antes.json') | ConvertFrom-Json
$preparadoCol9=Get-Content -Raw -Encoding UTF8 (Join-Path $Checkpoint 'preparado.json') | ConvertFrom-Json
Conferir-BancoCol9 $antesCol9
if ($Acao -eq 'Implantar') {
    $atualCol9=Estado-Col9 'dashboard-mestrado-app-1'
    if ($atualCol9.id -ne $antesCol9.app.id) { throw 'Estado do app mudou desde a preparação; revisar antes de implantar.' }
    $imagemTagCol9=(Docker-Col9 -Argumentos @('image','inspect','--format','{{.Id}}',$preparadoCol9.tag)) -join ''
    if ($imagemTagCol9 -ne $preparadoCol9.imagem_candidata) { throw 'Tag candidata não corresponde à imagem testada.' }
    $overrideCol9=Join-Path $Checkpoint 'candidato.compose.yml'
} else { $overrideCol9=Join-Path $Checkpoint 'retorno.compose.yml' }
Docker-Col9 -Argumentos @('compose','-f','docker-compose.yml','-f',$overrideCol9,'up','-d','--no-deps','--no-build','app')
$saudavelCol9=$false
for ($tentativaCol9=0;$tentativaCol9 -lt 24;$tentativaCol9++) {
    $atualCol9=Estado-Col9 'dashboard-mestrado-app-1'
    if ($atualCol9.saude -eq 'healthy') { $saudavelCol9=$true; break }
    Start-Sleep -Seconds 5
}
Conferir-BancoCol9 $antesCol9
if (-not $saudavelCol9) { throw 'App não saudável. Aplicar o retorno aprovado para a imagem anterior.' }
# Verificação do código da imagem realmente em execução, com conexões somente leitura.
Get-Content -Raw -Encoding UTF8 testes/verificar_fase2_container.py |
    & docker exec -i -e COL9_RAIZ_APP=/app -e COL9_VERIFICAR_LEGADO=1 dashboard-mestrado-app-1 python -
if ($LASTEXITCODE -ne 0) { throw 'Verificação funcional do app em execução falhou; avaliar retorno.' }
Conferir-BancoCol9 $antesCol9
@{acao=$Acao;app=(Estado-Col9 'dashboard-mestrado-app-1');db=(Estado-Col9 'dashboard-mestrado-db-1');volume_db=(Volume-Col9);
  concluido_em=(Get-Date -Format o)} | ConvertTo-Json -Depth 6 |
  Set-Content -Encoding UTF8 (Join-Path $Checkpoint ($Acao.ToLower()+'_'+(Get-Date -Format 'yyyyMMdd_HHmmss')+'.json'))
Write-Output ('Concluído '+$Acao+'; banco e volume preservados.')
