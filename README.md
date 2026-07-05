# 🔁 AutoLoop FFmpeg & Python

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Termux-lightgrey)

## 🇪🇸 ESP: Español

Un script automatizado para **Termux y Linux** que utiliza Python y FFmpeg para crear bucles de archivos de vídeo (MP4) o audio (MP3) de la duración que quieras.

### ✨ Características Principales

- 🎵 **Detección inteligente de ritmo** con librosa (opcional): detecta tempo y beats para elegir el punto de loop
- ⚡ **Rápido siempre que se puede** — intenta primero `-c copy` (sin recodificar) y solo recodifica con libx264 si el corte no cae en un keyframe
- 🎯 **Puntos de loop óptimos** — usa picos de energía y beats para evitar cortes feos
- 🔄 **Fallback automático** — si librosa no está instalado, o no detecta suficientes beats, usa un método simple basado en porcentajes de la duración
- 📊 **Análisis en JSON** — guarda tempo, beats y puntos de loop usados
- 🎬 **Soporte para audio y video** — MP3, MP4, y otros formatos comunes
- 📱 **Pensado para Termux** — funciona en móviles, con fallback de instalación para Debian 12+/Termux moderno

> ⚠️ **Nota honesta sobre el rendimiento**: el script SIEMPRE intenta primero el método rápido (`-c copy`, sin recodificar — segundos para generar horas de contenido). Pero si el punto de corte no cae en un keyframe del vídeo (algo bastante común), FFmpeg falla y el script cae automáticamente al método alternativo, que sí recodifica con `libx264`/`aac`. Esto es más lento y el archivo final puede pesar más que el original, pero garantiza que el loop quede bien sincronizado.

### ⚙️ Requisitos

**Mínimos:**
- Python 3.6+
- FFmpeg

**Opcionales (para detección avanzada de ritmo):**
```bash
pip install librosa numpy
```

En Termux o Debian 12+/Ubuntu 23.04+, si `pip install` te da un error de tipo `externally-managed-environment`, usa:
```bash
pip install --break-system-packages librosa numpy
```

`loop.sh` ya intenta esto automáticamente por ti, así que normalmente no necesitas hacerlo a mano.

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

El script usa un enfoque en capas para encontrar el mejor punto de loop:

1. **Librosa (si está instalado)**: detecta tempo, beats y picos de energía, y elige un punto de corte alineado a un beat exacto
2. **Método simple (fallback)**: si librosa no está disponible, o detecta muy pocos beats, o los puntos calculados no son válidos, usa porcentajes fijos de la duración total (ej. entre el 20% y el 85% del archivo)

El resultado se guarda siempre en un JSON para que puedas revisar qué puntos usó.

### 📊 Archivos generados

- `nombre_loop_XXmin.ext` — el archivo final con el loop
- `nombre_analisis.json` — datos del análisis (tempo, beats, puntos de loop usados)

### 🎥 Videos probados

- [LATINOAMERICANO REMASTERED](https://youtu.be/EOQsGuYuQ-I?is=KoWRe-6NuKAUGv8W)
- [Electroman Adventures](https://youtu.be/Pb6KyewC_Vg?is=74jIqElizOj632Ln)
- [Jumper](https://youtu.be/ZXHO4AN_49Q?is=V8LRf2ud2SMeIuZZ)
- [FNF - 2HOT but Bob and Ron sings it](https://youtu.be/WYFvDnBw-nk?is=tYAbDrTTe4j4Dy_R)
- [there is no need to be upset](https://youtu.be/GJDNkVDGM_s?is=97gmPkzJIakSf3IK)

### 🛠️ Solución de problemas

**Error: `FFmpeg no instalado`**
```bash
sudo apt install ffmpeg      # Linux
pkg install ffmpeg           # Termux
```

**Error: `externally-managed-environment` al instalar librosa**
```bash
pip install --break-system-packages librosa numpy
```

**El método rápido falla y cae al alternativo (verás "intentando método alternativo...")**
Es normal en algunos vídeos: el punto de corte no cayó en un keyframe. El script recodifica automáticamente para que el loop quede bien. Tardará más, pero funcionará.

**El loop no suena/se ve bien**
```bash
# Probar con diferentes duraciones puede cambiar los puntos de corte detectados
./loop.sh cancion.mp3 3   # Loop más corto
./loop.sh cancion.mp3 15  # Loop más largo
```

### 🚧 Limitaciones conocidas

- El corte exacto con `-c copy` depende de que el punto elegido caiga cerca de un keyframe del vídeo; si no, se recodifica automáticamente (más lento).
- La detección de ritmo con librosa puede tardar bastante en archivos muy largos (varios minutos de análisis en audios/vídeos de más de una hora).
- No hay barra de progreso durante el análisis ni la recodificación — el script puede parecer "colgado" en archivos grandes, pero está trabajando.

---

## 🇬🇧 ENG: English

An automated script for **Termux and Linux** that uses Python and FFmpeg to create loops of video (MP4) or audio (MP3) files at whatever length you want.

### ✨ Key Features

- 🎵 **Intelligent beat detection** with librosa (optional): detects tempo and beats to choose the loop point
- ⚡ **Fast when possible** — tries `-c copy` (no re-encoding) first, and only re-encodes with libx264 if the cut point doesn't land on a keyframe
- 🎯 **Optimal loop points** — uses energy peaks and beats to avoid ugly cuts
- 🔄 **Automatic fallback** — if librosa isn't installed, or doesn't detect enough beats, falls back to a simple method based on percentages of the total duration
- 📊 **JSON analysis** — saves the tempo, beats, and loop points used
- 🎬 **Audio & video support** — MP3, MP4, and other common formats
- 📱 **Built with Termux in mind** — works on mobile, with an install fallback for Debian 12+/modern Termux

> ⚠️ **Honest note on performance**: the script always tries the fast method first (`-c copy`, no re-encoding — seconds to generate hours of content). But if the cut point doesn't land on a video keyframe (fairly common), FFmpeg fails and the script automatically falls back to the alternative method, which does re-encode with `libx264`/`aac`. This is slower and the final file may be larger than the original, but it guarantees the loop is properly synced.

### ⚙️ Requirements

**Minimum:**
- Python 3.6+
- FFmpeg

**Optional (for advanced beat detection):**
```bash
pip install librosa numpy
```

On Termux or Debian 12+/Ubuntu 23.04+, if `pip install` gives you an `externally-managed-environment` error, use:
```bash
pip install --break-system-packages librosa numpy
```

`loop.sh` already tries this automatically for you, so you usually won't need to do it by hand.

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

The script uses a layered approach to find the best loop point:

1. **Librosa (if installed)**: detects tempo, beats, and energy peaks, and picks a cut point aligned to an exact beat
2. **Simple method (fallback)**: if librosa isn't available, detects too few beats, or the calculated points aren't valid, falls back to fixed percentages of the total duration (e.g. between 20% and 85% of the file)

The result is always saved to a JSON file so you can check which points were used.

### 📊 Generated files

- `name_loop_XXmin.ext` — the final looped file
- `name_analisis.json` — analysis data (tempo, beats, loop points used)

### 🎥 Tested Videos

- [LATINOAMERICANO REMASTERED](https://youtu.be/EOQsGuYuQ-I?is=KoWRe-6NuKAUGv8W)
- [Electroman Adventures](https://youtu.be/Pb6KyewC_Vg?is=74jIqElizOj632Ln)
- [Jumper](https://youtu.be/ZXHO4AN_49Q?is=V8LRf2ud2SMeIuZZ)
- [FNF - 2HOT but Bob and Ron sings it](https://youtu.be/WYFvDnBw-nk?is=tYAbDrTTe4j4Dy_R)
- [there is no need to be upset](https://youtu.be/GJDNkVDGM_s?is=97gmPkzJIakSf3IK)

### 🛠️ Troubleshooting

**Error: `FFmpeg not installed`**
```bash
sudo apt install ffmpeg      # Linux
pkg install ffmpeg           # Termux
```

**Error: `externally-managed-environment` when installing librosa**
```bash
pip install --break-system-packages librosa numpy
```

**Fast method fails and falls back to the alternative one (you'll see "trying alternative method...")**
This is normal for some videos: the cut point didn't land on a keyframe. The script automatically re-encodes so the loop stays in sync. It'll take longer, but it'll work.

**The loop doesn't sound/look smooth**
```bash
# Trying different durations can change the detected cut points
./loop.sh song.mp3 3   # Shorter loop
./loop.sh song.mp3 15  # Longer loop
```

### 🚧 Known Limitations

- The exact `-c copy` cut depends on the chosen point landing near a video keyframe; if not, it automatically re-encodes (slower).
- Beat detection with librosa can take a while on very long files (several minutes of analysis for audio/video over an hour long).
- There's no progress bar during analysis or re-encoding — the script may look "stuck" on large files, but it's working.

---

### 📜 License

MIT License - Feel free to use, modify, and distribute.

### 🙏 Credits

- FFmpeg team for the amazing multimedia framework
- librosa team for the audio analysis tools
- Community contributors and testers

---

**⭐ Star this repo if you find it useful!**
