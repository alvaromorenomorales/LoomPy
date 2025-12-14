# Script para solucionar el problema de PyTorch en Windows
# Descarga e instala Visual C++ Redistributables

Write-Host "Solucionando problema de PyTorch en Windows..." -ForegroundColor Green
Write-Host ""

# URL del instalador de Visual C++ Redistributables
$vcRedistUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
$installerPath = "$env:TEMP\vc_redist.x64.exe"

Write-Host "Descargando Visual C++ Redistributables..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $vcRedistUrl -OutFile $installerPath
    Write-Host "Descarga completada." -ForegroundColor Green
} catch {
    Write-Host "Error al descargar: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Instalando Visual C++ Redistributables..." -ForegroundColor Yellow
Write-Host "Esto puede tardar unos minutos. Por favor, acepta los permisos de administrador si se solicitan." -ForegroundColor Cyan

try {
    Start-Process -FilePath $installerPath -ArgumentList "/install", "/quiet", "/norestart" -Wait
    Write-Host "Instalación completada." -ForegroundColor Green
} catch {
    Write-Host "Error durante la instalación: $_" -ForegroundColor Red
    Write-Host "Intenta ejecutar manualmente: $installerPath" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Limpiando archivos temporales..." -ForegroundColor Yellow
Remove-Item $installerPath -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "¡Listo! Ahora intenta ejecutar el proyecto de nuevo:" -ForegroundColor Green
Write-Host "  python -m src.main" -ForegroundColor Cyan
Write-Host ""
