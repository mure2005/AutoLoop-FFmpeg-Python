#!/usr/bin/env python3
"""
AutoLoop - Loop perfecto para audio y video
Versión estable - Sin Demucs, solo librosa y FFmpeg
"""

import sys
import os
import subprocess
import tempfile
import json
import shutil
from pathlib import Path

try:
    import librosa
    import numpy as np
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    print("⚠️ Instala librosa: pip install librosa numpy")

class AutoLoop:
    def __init__(self, archivo_entrada, duracion_minutos=10):
        self.archivo = archivo_entrada
        self.duracion_minutos = duracion_minutos
        self.verificar_ffmpeg()
        self.duracion_original = self.obtener_duracion()
        self.temp_dir = tempfile.mkdtemp()
        self.es_video = self.es_archivo_video()

    def es_archivo_video(self):
        ext = os.path.splitext(self.archivo)[1].lower()
        return ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v']

    def verificar_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ FFmpeg no instalado o no funciona: {e}")
            print("   Instala con: sudo apt install ffmpeg")
            sys.exit(1)

    def obtener_duracion(self):
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                self.archivo
            ]
            salida = subprocess.check_output(cmd).strip()
            duracion = float(salida)
            if duracion <= 0:
                print("⚠️ ffprobe devolvió una duración inválida (0s)")
            return duracion
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError) as e:
            print(f"⚠️ No se pudo obtener la duración del archivo: {e}")
            return 0

    def extraer_audio(self):
        """Extrae audio para análisis"""
        temp_audio = os.path.join(self.temp_dir, "temp_audio.wav")
        cmd = [
            "ffmpeg", "-i", self.archivo,
            "-ac", "1", "-ar", "22050",
            "-map", "0:a", "-y", temp_audio
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return temp_audio
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Error extrayendo audio: {e.stderr.decode(errors='ignore')[:300]}")
            return None

    def encontrar_puntos_loop(self):
        """Encuentra los mejores puntos de loop"""
        if not HAS_LIBROSA:
            return self.puntos_simples()

        if self.duracion_original <= 0:
            print("⚠️ Duración desconocida, usando método simple")
            return self.puntos_simples()

        print("🔍 Analizando audio para encontrar loop perfecto...")

        try:
            audio_path = self.extraer_audio()
            if not audio_path:
                return self.puntos_simples()

            # Cargar audio
            y, sr = librosa.load(audio_path, sr=22050)
            duracion = self.duracion_original

            # Detectar tempo y beats
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
            # En librosa >= 0.10, tempo puede venir como np.ndarray de 1 elemento
            # en vez de float. Lo normalizamos para evitar errores de formato.
            tempo = float(np.asarray(tempo).reshape(-1)[0])

            # Si no hay beats suficientes
            if len(beats) < 4:
                print("⚠️ Pocos beats detectados, usando método simple")
                return self.puntos_simples()

            # Detectar secciones energéticas
            rms = librosa.feature.rms(y=y)[0]
            rms_times = librosa.times_like(rms, sr=sr, hop_length=512)

            # Encontrar picos de energía
            energia_media = np.mean(rms)
            umbral = energia_media * 1.5

            picos = []
            for i in range(1, len(rms) - 1):
                if rms[i] > umbral and rms[i] > rms[i - 1] and rms[i] > rms[i + 1]:
                    picos.append(rms_times[i])

            # Si hay suficientes picos, usar los del medio
            if len(picos) >= 4:
                punto_a = picos[len(picos) // 3]
                punto_b = picos[2 * len(picos) // 3]
            else:
                # Usar beats
                punto_a = beats[len(beats) // 4]
                punto_b = beats[3 * len(beats) // 4]

            # Ajustar a beats exactos
            if len(beats) > 0:
                idx_a = min(range(len(beats)), key=lambda i: abs(beats[i] - punto_a))
                idx_b = min(range(len(beats)), key=lambda i: abs(beats[i] - punto_b))
                punto_a = beats[idx_a]
                punto_b = beats[idx_b]

                # Asegurar que punto_b > punto_a
                if punto_b <= punto_a:
                    if tempo > 0:
                        punto_b = punto_a + 4 * (60 / tempo)  # 4 beats después
                    else:
                        return self.puntos_simples()

            # Validar puntos (incluye que la duración del loop no sea ~0)
            duracion_loop = punto_b - punto_a
            if punto_a < 1 or punto_b > duracion - 1 or duracion_loop < 0.5:
                return self.puntos_simples()

            print(f"🎵 Tempo: {tempo:.1f} BPM")
            print(f"🎯 Beats: {len(beats)}")
            print(f"✂️ Loop: {punto_a:.2f}s → {punto_b:.2f}s ({duracion_loop:.2f}s)")

            return {
                'punto_a': float(punto_a),
                'punto_b': float(punto_b),
                'duracion_loop': float(duracion_loop),
                'tempo': float(tempo)
            }

        except Exception as e:
            print(f"⚠️ Error en análisis: {e}")
            return self.puntos_simples()

    def puntos_simples(self):
        """Puntos de loop simples"""
        duracion = self.duracion_original

        if duracion <= 2:
            # Duración desconocida o clip diminuto: fallback fijo
            print("⚠️ Duración muy corta o desconocida, no se puede loopear con garantías")
            return {
                'punto_a': 0.0,
                'punto_b': max(duracion, 1.0),
                'duracion_loop': max(duracion, 1.0),
                'tempo': 0
            }
        elif duracion < 30:
            punto_a = duracion * 0.1
            punto_b = duracion * 0.9
        elif duracion < 60:
            punto_a = duracion * 0.15
            punto_b = duracion * 0.85
        else:
            punto_a = duracion * 0.2
            punto_b = duracion * 0.85

        # Asegurar que sea válido
        if punto_a >= punto_b:
            punto_a = duracion * 0.2
            punto_b = duracion * 0.8

        print(f"✂️ Loop simple: {punto_a:.2f}s → {punto_b:.2f}s")

        return {
            'punto_a': float(punto_a),
            'punto_b': float(punto_b),
            'duracion_loop': float(punto_b - punto_a),
            'tempo': 0
        }

    def crear_loop(self, puntos):
        """Crea el archivo con loop"""
        punto_a = puntos['punto_a']
        punto_b = puntos['punto_b']
        duracion_loop = punto_b - punto_a

        if duracion_loop <= 0:
            print("❌ Duración de loop inválida (0s o negativa), abortando")
            return None

        # Calcular repeticiones
        target = self.duracion_minutos * 60
        repeticiones = max(2, int(target / duracion_loop) + 1)

        print(f"🔄 Repeticiones: {repeticiones}")
        print(f"⏱️ Duración final: {repeticiones * duracion_loop:.2f}s")

        nombre, ext = os.path.splitext(self.archivo)
        salida = f"{nombre}_loop_{self.duracion_minutos}min{ext}"

        # Crear archivo de lista para FFmpeg
        lista_path = os.path.join(self.temp_dir, "lista.txt")

        # ffmpeg concat demuxer necesita escapar comillas simples dentro del path
        archivo_escapado = self.archivo.replace("'", "'\\''")

        with open(lista_path, "w") as f:
            # Primero: desde inicio hasta punto_b
            f.write(f"file '{archivo_escapado}'\n")
            f.write(f"inpoint 0\n")
            f.write(f"outpoint {punto_b}\n")

            # Luego: repeticiones del segmento de loop
            for _ in range(repeticiones):
                f.write(f"file '{archivo_escapado}'\n")
                f.write(f"inpoint {punto_a}\n")
                f.write(f"outpoint {punto_b}\n")

        # Ejecutar FFmpeg
        print("🎬 Generando archivo...")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista_path, "-c", "copy", salida]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Archivo creado: {salida}")
            return salida
        except subprocess.CalledProcessError as e:
            print(f"❌ Error con método simple ({e.stderr.decode(errors='ignore')[:200]}), "
                  f"intentando método alternativo...")
            return self.crear_loop_alternativo(punto_a, punto_b, repeticiones, nombre, ext)

    def crear_loop_alternativo(self, punto_a, punto_b, repeticiones, nombre, ext):
        """Método alternativo usando segmentos extraídos"""
        salida = f"{nombre}_loop_{self.duracion_minutos}min{ext}"

        try:
            # Extraer intro (audio)
            intro_path = os.path.join(self.temp_dir, "intro.mp3")
            cmd_intro = ["ffmpeg", "-i", self.archivo, "-to", str(punto_b),
                         "-map", "0:a", "-y", intro_path]
            subprocess.run(cmd_intro, check=True, capture_output=True)

            # Extraer loop segment (audio)
            loop_path = os.path.join(self.temp_dir, "loop_segment.mp3")
            cmd_loop = ["ffmpeg", "-i", self.archivo, "-ss", str(punto_a), "-to", str(punto_b),
                        "-map", "0:a", "-y", loop_path]
            subprocess.run(cmd_loop, check=True, capture_output=True)

            # Crear lista de audio
            lista_path = os.path.join(self.temp_dir, "lista2.txt")
            with open(lista_path, "w") as f:
                f.write(f"file '{intro_path}'\n")
                for _ in range(repeticiones):
                    f.write(f"file '{loop_path}'\n")

            if self.es_video:
                # Vídeo: repetir también el segmento de vídeo, no solo el audio.
                # Reencodeamos porque el corte en punto_a/punto_b no cae en keyframe.
                intro_v = os.path.join(self.temp_dir, "intro_v.mp4")
                loop_v = os.path.join(self.temp_dir, "loop_v.mp4")

                subprocess.run(
                    ["ffmpeg", "-i", self.archivo, "-to", str(punto_b),
                     "-c:v", "libx264", "-c:a", "aac", "-y", intro_v],
                    check=True, capture_output=True
                )
                subprocess.run(
                    ["ffmpeg", "-i", self.archivo, "-ss", str(punto_a), "-to", str(punto_b),
                     "-c:v", "libx264", "-c:a", "aac", "-y", loop_v],
                    check=True, capture_output=True
                )

                lista_v_path = os.path.join(self.temp_dir, "lista_v.txt")
                with open(lista_v_path, "w") as f:
                    f.write(f"file '{intro_v}'\n")
                    for _ in range(repeticiones):
                        f.write(f"file '{loop_v}'\n")

                cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista_v_path,
                       "-c", "copy", salida]
            else:
                cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista_path,
                       "-c", "copy", salida]

            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Archivo creado (método alternativo): {salida}")
            return salida

        except subprocess.CalledProcessError as e:
            print(f"❌ Método alternativo también falló: {e.stderr.decode(errors='ignore')[:300]}")
            return None

    def limpiar(self):
        """Limpia archivos temporales"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def ejecutar(self):
        """Ejecuta el proceso completo"""
        print("=" * 60)
        print("🎵 AutoLoop - Loop Perfecto")
        print("=" * 60)
        print(f"📁 Archivo: {os.path.basename(self.archivo)}")
        print(f"⏱️ Duración: {self.duracion_original:.2f}s")
        print(f"🎯 Target: {self.duracion_minutos} minutos")
        print("=" * 60)

        if self.duracion_original <= 0:
            print("❌ No se pudo determinar la duración del archivo. Abortando.")
            self.limpiar()
            return None

        try:
            # Encontrar puntos de loop
            puntos = self.encontrar_puntos_loop()

            # Crear loop
            resultado = self.crear_loop(puntos)

            if resultado is None:
                print("❌ No se pudo generar el loop.")
                return None

            # Guardar análisis
            analisis_path = f"{os.path.splitext(self.archivo)[0]}_analisis.json"
            with open(analisis_path, "w") as f:
                json.dump(puntos, f, indent=2)
            print(f"📊 Análisis: {analisis_path}")

            print("=" * 60)
            print(f"✅ ¡Completado!")
            print("=" * 60)

            return resultado

        except Exception as e:
            print(f"❌ Error: {e}")
            return None
        finally:
            self.limpiar()

def main():
    if len(sys.argv) < 2:
        print("""
🎵 AutoLoop - Loop perfecto para audio/video
===========================================
Uso: python autoloop_pro.py <archivo> [minutos]

Ejemplos:
  python autoloop_pro.py cancion.mp3 5
  python autoloop_pro.py video.mp4 10
  python autoloop_pro.py "LATINOAMERICANO REMASTERED.mp4" 180
        """)
        sys.exit(1)

    archivo = sys.argv[1]

    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        sys.exit(1)

    minutos = 10
    if len(sys.argv) > 2:
        try:
            minutos = int(sys.argv[2])
            if minutos <= 0:
                raise ValueError
        except ValueError:
            print("⚠️ Minutos inválido, usando valor por defecto (10)")
            minutos = 10

    looper = AutoLoop(archivo, minutos)
    looper.ejecutar()

if __name__ == "__main__":
    main()
