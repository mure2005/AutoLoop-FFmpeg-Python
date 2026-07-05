Perfecto, aquí tienes el README.md completo listo para copiar y pegar:

---

```markdown
# 🔁 AutoLoop FFmpeg & Python

---

## 🇪🇸 ESP: Español

Un script automatizado y ultra rápido para **Termux y Linux** que utiliza Python y FFmpeg para crear bucles infinitos de archivos de vídeo (MP4) o audio (MP3). 

### ✨ Características Principales

- 🎵 **Detección inteligente de ritmo** con librosa (opcional)
- ⚡ **Ultra rápido** - Sin recodificación, usa `-c copy`
- 🎯 **Puntos de loop óptimos** - Detecta automáticamente estribillos y secciones rítmicas
- 🔄 **Múltiples fallbacks** - Si librosa no está disponible, usa FFmpeg o método simple
- 📊 **Análisis en JSON** - Guarda la información del loop para referencia
- 🎬 **Soporte para audio y video** - MP3, MP4, y más formatos
- 📱 **Optimizado para Termux** - Funciona perfectamente en móviles

Lo mejor de este método es que **no renderiza ni recodifica el archivo**, sino que clona los flujos de audio y vídeo de forma nativa utilizando `-c copy` de FFmpeg. ¡Un vídeo o canción de varias horas se genera en cuestión de segundos y sin consumir apenas batería!

### ⚙️ Requisitos

**Mínimos:**
- Python 3.6+
- FFmpeg

**Opcionales (para detección avanzada):**
```bash
pip install librosa numpy
```

En Termux puedes instalar todo con:
```bash
pkg update && pkg install -y python ffmpeg
pip install librosa numpy
```

### 🚀 Cómo usarlo

1. Descarga `autoloop.py` y `loop.sh` en la misma carpeta.
2. Dale permisos de ejecución al script de Bash:
   ```bash
   chmod +x loop.sh
   ```
3. Ejecuta el comando pasando el nombre del archivo y la duración deseada en minutos:
   ```bash
   ./loop.sh mi_video.mp4 60
   ```
   *(Esto creará un loop de mi_video.mp4 que dure 60 minutos)*

### 🎯 Ejemplos de uso

```bash
# Loop de 10 minutos (predeterminado)
./loop.sh cancion.mp3

# Loop de 60 minutos para video
./loop.sh video.mp4 60

# Loop de 5 minutos con detección de ritmo
./loop.sh tema_original.mp3 5
```

### 🧠 Cómo funciona la detección de ritmo

El script utiliza un enfoque de múltiples capas para encontrar el mejor punto de loop:

1. **Librosa (avanzado)**: Detecta tempo, beats y segmentos musicales
2. **FFmpeg (alternativo)**: Analiza volumen y silencios
3. **Método simple (fallback)**: Calcula puntos basados en la duración

El resultado es un loop perfectamente sincronizado con el ritmo de la música.

### 📊 Archivos generados

- `nombre_looped_XXmin.ext` - El archivo con loop
- `nombre_analisis.json` - Datos del análisis (tempo, beats, puntos de loop)

### 🎥 Videos probados

- [LATINOAMERICANO REMASTERED](https://youtu.be/EOQsGuYuQ-I?is=KoWRe-6NuKAUGv8W)
- [Electroman Adventures](https://youtu.be/Pb6KyewC_Vg?is=74jIqElizOj632Ln)
- [Jumper](https://youtu.be/ZXHO4AN_49Q?is=V8LRf2ud2SMeIuZZ)

### 🛠️ Solución de problemas

**Error: ModuleNotFoundError: No module named 'matplotlib'**
```bash
# Opción 1: Instalar matplotlib
pip install matplotlib

# Opción 2: Usar versión sin matplotlib (recomendado)
# El script ya incluye fallbacks automáticos
```

**Error: agglomerative() unexpected keyword argument**
```bash
# Actualizar librosa
pip install --upgrade librosa
# O usar la versión del script que ya maneja este error
```

**El loop no suena bien**
```bash
# Probar con diferentes duraciones
./loop.sh cancion.mp3 3  # Loop más corto
./loop.sh cancion.mp3 15 # Loop más largo
```

---

## 🇬🇧 ENG: English

An automated and ultra-fast script for **Termux and Linux** that uses Python and FFmpeg to create seamless infinite loops of video (MP4) or audio (MP3) files.

### ✨ Key Features

- 🎵 **Intelligent beat detection** with librosa (optional)
- ⚡ **Ultra fast** - No re-encoding, uses `-c copy`
- 🎯 **Optimal loop points** - Automatically detects choruses and rhythmic sections
- 🔄 **Multiple fallbacks** - If librosa isn't available, uses FFmpeg or simple method
- 📊 **JSON analysis** - Saves loop information for reference
- 🎬 **Audio & Video support** - MP3, MP4, and more formats
- 📱 **Optimized for Termux** - Works perfectly on mobile devices

The best part of this method is that **it does not re-encode or re-render the file**. Instead, it clones the audio and video streams natively using FFmpeg's `-c copy`. A video or song that lasts for hours can be generated in just a few seconds without draining your battery!

### ⚙️ Requirements

**Minimum:**
- Python 3.6+
- FFmpeg

**Optional (for advanced detection):**
```bash
pip install librosa numpy
```

On Termux, install everything with:
```bash
pkg update && pkg install -y python ffmpeg
pip install librosa numpy
```

### 🚀 How to Use

1. Download `autoloop.py` and `loop.sh` into the same folder.
2. Give execution permissions to the Bash script:
   ```bash
   chmod +x loop.sh
   ```
3. Run the command with the file name and desired duration in minutes:
   ```bash
   ./loop.sh my_video.mp4 60
   ```
   *(This will create a loop of my_video.mp4 that lasts 60 minutes)*

### 🎯 Usage Examples

```bash
# 10-minute loop (default)
./loop.sh song.mp3

# 60-minute loop for video
./loop.sh video.mp4 60

# 5-minute loop with beat detection
./loop.sh original_track.mp3 5
```

### 🧠 How beat detection works

The script uses a multi-layer approach to find the best loop point:

1. **Librosa (advanced)**: Detects tempo, beats, and musical segments
2. **FFmpeg (alternative)**: Analyzes volume and silences
3. **Simple method (fallback)**: Calculates points based on duration

The result is a perfectly synchronized loop with the music's rhythm.

### 📊 Generated files

- `name_looped_XXmin.ext` - The looped file
- `name_analysis.json` - Analysis data (tempo, beats, loop points)

### 🎥 Tested Videos

- [LATINOAMERICANO REMASTERED](https://youtu.be/EOQsGuYuQ-I?is=KoWRe-6NuKAUGv8W)
- [Electroman Adventures](https://youtu.be/Pb6KyewC_Vg?is=74jIqElizOj632Ln)
- [Jumper](https://youtu.be/ZXHO4AN_49Q?is=V8LRf2ud2SMeIuZZ)

### 🛠️ Troubleshooting

**Error: ModuleNotFoundError: No module named 'matplotlib'**
```bash
# Option 1: Install matplotlib
pip install matplotlib

# Option 2: Use version without matplotlib (recommended)
# The script already includes automatic fallbacks
```

**Error: agglomerative() unexpected keyword argument**
```bash
# Update librosa
pip install --upgrade librosa
# Or use the script version that already handles this error
```

**The loop doesn't sound smooth**
```bash
# Try different durations
./loop.sh song.mp3 3  # Shorter loop
./loop.sh song.mp3 15 # Longer loop
```

---

### 📜 License

MIT License - Feel free to use, modify, and distribute.

### 🙏 Credits

- FFmpeg team for the amazing multimedia framework
- librosa team for the audio analysis tools
- Community contributors and testers

---

**⭐ Star this repo if you find it useful!**
