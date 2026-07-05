#!/bin/bash
# Ejecuta el script de python pasando los archivos que tú quieras

# Detectar entorno
if [ -d "/data/data/com.termux" ]; then
    echo "📱 Modo Termux detectado"
    PYTHON="python3"
else
    echo "💻 Modo escritorio"
    PYTHON="python3"
fi

# Verificar archivo
if [ -z "$1" ]; then
    echo "Uso: ./loop.sh <archivo> [minutos]"
    echo "Ejemplo: ./loop.sh video.mp4 60"
    exit 1
fi

# Verificar dependencias
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg no encontrado. Instalando..."
    if [ -d "/data/data/com.termux" ]; then
        pkg install ffmpeg
    else
        sudo apt install ffmpeg -y
    fi
fi

# Instalar dependencias Python si es necesario
if ! $PYTHON -c "import librosa" 2>/dev/null; then
    echo "📦 Instalando librosa para mejor detección..."
    $PYTHON -m pip install librosa numpy --quiet
fi

# Ejecutar
$PYTHON autoloop.py "$1" "$2"

# Mantener terminal abierta en móviles
if [ -d "/data/data/com.termux" ]; then
    echo "Presiona Enter para salir..."
    read
fi