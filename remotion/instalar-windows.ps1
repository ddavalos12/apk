# Instalador para Windows (PowerShell). Ejecutar desde esta carpeta:
#   powershell -ExecutionPolicy Bypass -File .\instalar-windows.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

function Tiene($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

if (-not (Tiene winget)) {
  Write-Error 'No se encontró winget. Instala "App Installer" desde la Microsoft Store y vuelve a ejecutar.'
}

if (-not (Tiene node)) {
  Write-Host '==> Instalando Node.js LTS...'
  winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements
}
if (-not (Tiene ffmpeg)) {
  Write-Host '==> Instalando FFmpeg...'
  winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
}

# Recargar PATH para usar lo recién instalado en esta misma ventana
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')

Write-Host '==> Instalando dependencias de Remotion...'
npm install
Write-Host '==> Descargando Chrome Headless Shell para renderizar...'
npx remotion browser ensure

Write-Host ''
node -v
ffmpeg -version | Select-Object -First 1
Write-Host ''
Write-Host 'Listo. Prueba:  npm run studio   (editor visual)'
Write-Host '                npm run render   (genera out\video.mp4)'
