# Script PowerShell para Deploy no Railway
Set-Location "C:\Users\Sueli\Desktop\ClientFlow"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FAZENDO PUSH DO CODIGO PARA O GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
& git push origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AGUARDANDO RAILWAY REBUILDAR (60s)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Start-Sleep -Seconds 60

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICANDO LOGS DO RAILWAY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
& railway logs

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTANDO URL DA API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://clientflow-production-8f24.up.railway.app/health" -UseBasicParsing
    Write-Host "✅ API RESPONDENDO!" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "❌ API NÃO RESPONDENDO:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
