# Verificador de Status do Railway - ClientFlow
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  VERIFICANDO DEPLOYMENT DO RAILWAY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$url = "https://clientflow-production-8f24.up.railway.app/health"
$maxTentativas = 12
$intervalo = 10

for ($i = 1; $i -le $maxTentativas; $i++) {
    Write-Host "[$i/$maxTentativas] Testando API..." -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        Write-Host " ✅ SUCESSO!" -ForegroundColor Green
        Write-Host "`nResposta da API:" -ForegroundColor Yellow
        Write-Host $response.Content -ForegroundColor White
        Write-Host "`n🎉 DEPLOYMENT BEM-SUCEDIDO!" -ForegroundColor Green
        Write-Host "URL: $url" -ForegroundColor Cyan
        Write-Host "Docs: https://clientflow-production-8f24.up.railway.app/docs`n" -ForegroundColor Cyan
        break
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode) {
            Write-Host " ❌ Erro $statusCode" -ForegroundColor Red
        } else {
            Write-Host " ⏳ Aguardando..." -ForegroundColor Yellow
        }
        
        if ($i -lt $maxTentativas) {
            Write-Host "   Aguardando ${intervalo}s antes da próxima tentativa...`n"
            Start-Sleep -Seconds $intervalo
        } else {
            Write-Host "`n❌ API não respondeu após $maxTentativas tentativas" -ForegroundColor Red
            Write-Host "Verifique os logs no dashboard do Railway" -ForegroundColor Yellow
        }
    }
}

Write-Host "`nPressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
