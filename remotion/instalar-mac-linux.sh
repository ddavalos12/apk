#!/usr/bin/env bash
# Instalador para macOS y Linux. Ejecutar desde esta carpeta:
#   bash instalar-mac-linux.sh
set -euo pipefail
cd "$(dirname "$0")"

tiene() { command -v "$1" >/dev/null 2>&1; }

case "$(uname -s)" in
  Darwin)
    if ! tiene brew; then
      echo "==> Instalando Homebrew..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
    fi
    tiene node   || brew install node
    tiene ffmpeg || brew install ffmpeg
    ;;
  Linux)
    if tiene apt-get; then
      sudo apt-get update
      tiene ffmpeg || sudo apt-get install -y ffmpeg
      if ! tiene node || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 18 ]; then
        curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
        sudo apt-get install -y nodejs
      fi
      # Librerías que necesita Chrome Headless para renderizar
      sudo apt-get install -y libnss3 libdbus-1-3 libatk1.0-0 libgbm-dev libasound2t64 2>/dev/null \
        || sudo apt-get install -y libnss3 libdbus-1-3 libatk1.0-0 libgbm-dev libasound2
      sudo apt-get install -y libxrandr2 libxkbcommon-dev libxfixes3 libxcomposite1 libxdamage1 libatk-bridge2.0-0 libpango-1.0-0 libcairo2 libcups2
    elif tiene dnf; then
      sudo dnf install -y nodejs ffmpeg-free nss atk at-spi2-atk libdrm libxkbcommon libXcomposite libXdamage libXrandr mesa-libgbm pango alsa-lib cups-libs
    else
      echo "Instala manualmente Node.js (>=18) y FFmpeg con tu gestor de paquetes." >&2
    fi
    ;;
esac

echo "==> Instalando dependencias de Remotion..."
npm install
echo "==> Descargando Chrome Headless Shell para renderizar..."
npx remotion browser ensure

echo
node -v
ffmpeg -version | head -1
echo
echo "Listo. Prueba:  npm run studio   (editor visual)"
echo "                npm run render   (genera out/video.mp4)"
