# 🔁 AutoLoop FFmpeg & Python

[Castellano](#esp-español) | [English](#eng-english)

---

## 🇪🇸 ESP: Español

Un script automatizado y ultra rápido para **Termux y Linux** que utiliza Python y FFmpeg para crear bucles infinitos de archivos de vídeo (MP4) o audio (MP3). 

Lo mejor de este método es que **no renderiza ni recodifica el archivo**, sino que clona los flujos de audio y vídeo de forma nativa utilizando `-c copy` de FFmpeg. ¡Un vídeo o canción de varias horas se genera en cuestión de segundos y sin consumir apenas batería!

### ⚙️ Requisitos
Solo necesitas tener instalados Python y FFmpeg. En Termux puedes instalarlos corriendo:
```bash
pkg update && pkg install -y python ffmpeg

```
### 🚀 Cómo usarlo
 1. Descarga autoloop.py y loop.sh en la misma carpeta.
 2. Dale permisos de ejecución al script de Bash:
   ```bash
   chmod +x loop.sh
   
   ```
 3. Ejecuta el comando pasando el nombre del archivo y la duración que quieras en minutos:
   ```bash
   ./loop.sh mi_video.mp4 10
   
   ```
   *(Este comando hará que mi_video.mp4 se loopee de forma fluida hasta durar 10 minutos).*
## 🇬🇧 ENG: English
An automated and ultra-fast script for **Termux and Linux** that uses Python and FFmpeg to create seamless infinite loops of video (MP4) or audio (MP3) files.
The best part of this method is that **it does not re-encode or re-render the file**. Instead, it clones the audio and video streams natively using FFmpeg's -c copy. A video or song that lasts for hours can be generated in just a few seconds without draining your battery!
### ⚙️ Requirements
You only need Python and FFmpeg installed. On Termux, you can set them up by running:
```bash
pkg update && pkg install -y python ffmpeg

```
### 🚀 How to Use
 1. Download autoloop.py and loop.sh into the same folder.
 2. Give execution permissions to the Bash script:
   ```bash
   chmod +x loop.sh
   
   ```
 3. Run the command by passing the file name and your desired duration in minutes:
example:

   ```bash
   ./loop.sh my_video.mp4 15
   
   ```
   *(This command will seamlessly loop my_video.mp4 until it reaches a total duration of Any time in minutes).*
