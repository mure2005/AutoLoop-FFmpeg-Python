#!/bin/bash
# AutoLoop - Loop perfecto

echo "🎵 AutoLoop"
echo "================================="

if [ -z "$1" ]; then
    echo ""
    echo "Uso: ./loop.sh <archivo> [minutos]"
    echo ""
    echo "Ejemplos:"
    echo "  ./loop.sh cancion.mp3 5"
    echo "  ./loop.sh video.mp4 10"
    echo "  ./loop.sh \"LATINOAMERICANO REMASTERED.mp4\" 180"
    echo ""
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "❌ Archivo no encontrado: $1"
    exit 1
fi

# Verificar FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Instalando FFmpeg..."
    sudo apt install ffmpeg -y || {
        echo "❌ No se pudo instalar FFmpeg. Instálalo manualmente."
        exit 1
    }
fi

# Verificar librosa
if ! python3 -c "import librosa" 2>/dev/null; then
    echo "📦 Instalando librosa..."
    # En Debian 12+/Termux moderno, pip bloquea instalar en el entorno
    # global (PEP 668). --break-system-packages lo permite igualmente.
    if ! python3 -m pip install --break-system-packages librosa numpy 2>/dev/null; then
        echo "⚠️ Fallo con --break-system-packages, probando instalación normal..."
        python3 -m pip install librosa numpy || {
            echo "⚠️ No se pudo instalar librosa. El script seguirá con el método simple de loop."
        }
    fi
fi

# Ejecutar
python3 autoloop_pro.py "$@"
