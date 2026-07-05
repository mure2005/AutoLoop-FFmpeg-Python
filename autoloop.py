#!/usr/bin/env python3
import sys
import os
import subprocess
import numpy as np
import tempfile
import json
import shutil
from pathlib import Path

# Intentar importar librosa
try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    print("⚠️ librosa no instalado. Usando detección simple.")

class AudioLooper:
    def __init__(self, archivo_entrada, duracion_minutos=10):
        self.archivo = archivo_entrada
        self.duracion_minutos = duracion_minutos
        self.verificar_ffmpeg()
        self.info = self.obtener_info_archivo()
        self.temp_dir = tempfile.mkdtemp()
        
    def verificar_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ FFmpeg no instalado. Instala: sudo apt install ffmpeg")
            sys.exit(1)
    
    def obtener_info_archivo(self):
        """Obtiene duración y metadata del archivo"""
        try:
            cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 '{self.archivo}'"
            duracion = float(subprocess.check_output(cmd, shell=True).strip())
            return {"duracion": duracion}
        except Exception as e:
            print(f"❌ Error obteniendo info: {e}")
            sys.exit(1)
    
    def extraer_audio_temporal(self):
        """Extrae el audio a un archivo WAV temporal"""
        temp_audio = os.path.join(self.temp_dir, "temp_audio.wav")
        
        cmd = f"ffmpeg -i '{self.archivo}' -ac 1 -ar 22050 -map 0:a -y '{temp_audio}' 2>/dev/null"
        try:
            subprocess.run(cmd, shell=True, check=True)
            return temp_audio
        except subprocess.CalledProcessError:
            print("⚠️ El archivo no contiene audio. Usando detección simple.")
            return None
    
    def detectar_ritmo_librosa(self, audio_path):
        """Detección de ritmo con librosa (compatible con todas las versiones)"""
        if not HAS_LIBROSA or not audio_path:
            return self.detectar_ritmo_simple()
        
        print("🎧 Analizando ritmo con librosa...")
        
        try:
            # Cargar solo los primeros 30 segundos para análisis rápido
            y, sr = librosa.load(audio_path, sr=22050, duration=30)
            duracion = self.info["duracion"]
            
            # 1. Detectar tempo y beats
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
            
            # Si no detecta beats, usar método alternativo
            if len(beats) < 2:
                print("⚠️ Pocos beats detectados, usando método simple")
                return self.detectar_ritmo_simple()
            
            # 2. Detectar onsets
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            # 3. Detectar segmentos usando chroma (método compatible)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # Método 1: Usar agglomerative con parámetro k (versiones antiguas)
            # Método 2: Usar recurrencia (versiones nuevas)
            try:
                # Intentar con k (versión antigua)
                segments = librosa.segment.agglomerative(chroma, k=8)
            except TypeError:
                try:
                    # Intentar con n_segments (versión intermedia)
                    segments = librosa.segment.agglomerative(chroma, n_segments=8)
                except TypeError:
                    # Fallback: usar recurrencia
                    try:
                        segs = librosa.segment.recurrence_matrix(chroma)
                        segments = librosa.segment.agglomerative(segs, k=8)
                    except:
                        # Si todo falla, usar segmentación por tiempo
                        segments = np.linspace(0, chroma.shape[1], 8).astype(int)
            
            segment_times = librosa.frames_to_time(segments, sr=sr)
            
            # 4. Encontrar puntos óptimos de loop
            if len(beats) > 4:
                punto_a = beats[1] if len(beats) > 1 else beats[0]
                punto_b = beats[-2] if len(beats) > 2 else beats[-1]
            else:
                punto_a = duracion * 0.2
                punto_b = duracion * 0.85
            
            # Asegurar puntos válidos
            if punto_a >= punto_b:
                punto_a = duracion * 0.2
                punto_b = duracion * 0.85
            
            # Sincronizar con beats
            if len(beats) > 0:
                beat_anterior = beats[np.argmin(np.abs(beats - punto_a))]
                beat_siguiente = beats[np.argmin(np.abs(beats - punto_b))]
                punto_a = beat_anterior
                punto_b = beat_siguiente
                
                # Ajustar duración a múltiplo de beats
                duracion_loop = punto_b - punto_a
                beats_en_loop = duracion_loop / (60 / max(tempo, 1))
                beats_redondeados = round(beats_en_loop)
                if beats_redondeados > 0:
                    punto_b = punto_a + beats_redondeados * (60 / max(tempo, 1))
            
            print(f"🎵 Tempo: {tempo:.1f} BPM")
            print(f"🥁 Beats detectados: {len(beats)}")
            print(f"✂️ Loop: {punto_a:.2f}s → {punto_b:.2f}s")
            
            return {
                "tempo": float(tempo),
                "beats": beats.tolist(),
                "punto_a": float(punto_a),
                "punto_b": float(punto_b),
                "duracion_loop": float(punto_b - punto_a)
            }
            
        except Exception as e:
            print(f"⚠️ Error en análisis avanzado: {e}")
            print("↕️ Usando método simple...")
            return self.detectar_ritmo_simple()
    
    def detectar_ritmo_por_ffmpeg(self):
        """Método alternativo usando ffmpeg para detectar silencios"""
        print("🎧 Analizando con FFmpeg...")
        
        try:
            # Extraer volumen para detectar secciones
            cmd = f"ffmpeg -i '{self.archivo}' -af 'volumedetect' -f null - 2>&1 | grep mean_volume"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            duracion = self.info["duracion"]
            
            # Usar análisis de volumen para encontrar puntos
            punto_a = duracion * 0.2
            punto_b = duracion * 0.85
            
            print(f"✂️ Loop (FFmpeg): {punto_a:.2f}s → {punto_b:.2f}s")
            
            return {
                "tempo": 0,
                "beats": [],
                "punto_a": float(punto_a),
                "punto_b": float(punto_b),
                "duracion_loop": float(punto_b - punto_a)
            }
        except:
            return self.detectar_ritmo_simple()
    
    def detectar_ritmo_simple(self):
        """Método simple sin análisis avanzado"""
        duracion = self.info["duracion"]
        
        # Puntos inteligentes basados en duración
        if duracion < 30:
            punto_a = duracion * 0.1
            punto_b = duracion * 0.9
        elif duracion < 60:
            punto_a = duracion * 0.15
            punto_b = duracion * 0.85
        else:
            punto_a = duracion * 0.2
            punto_b = duracion * 0.85
        
        print(f"✂️ Loop simple: {punto_a:.2f}s → {punto_b:.2f}s")
        
        return {
            "tempo": 0,
            "beats": [],
            "punto_a": float(punto_a),
            "punto_b": float(punto_b),
            "duracion_loop": float(punto_b - punto_a)
        }
    
    def calcular_numero_repeticiones(self, duracion_loop):
        """Calcula cuántas veces repetir"""
        duracion_target = self.duracion_minutos * 60
        
        if duracion_loop <= 0:
            return 1
        
        repeticiones = int(np.ceil(duracion_target / duracion_loop))
        return max(repeticiones, 1)
    
    def crear_loop_inteligente(self, analisis):
        """Crea el loop usando los puntos detectados"""
        punto_a = analisis["punto_a"]
        punto_b = analisis["punto_b"]
        duracion_loop = analisis["duracion_loop"]
        
        repeticiones = self.calcular_numero_repeticiones(duracion_loop)
        
        print(f"🔄 Repeticiones: {repeticiones}")
        print(f"⏱️ Duración final: {repeticiones * duracion_loop:.2f}s (~{(repeticiones * duracion_loop)/60:.1f} minutos)")
        
        # Crear archivo de lista
        lista_path = os.path.join(self.temp_dir, "lista.txt")
        
        with open(lista_path, "w") as f:
            # Intro + primer loop
            f.write(f"file '{self.archivo}'\ninpoint 0\noutpoint {punto_b}\n")
            
            # Repeticiones del loop
            for i in range(repeticiones):
                f.write(f"file '{self.archivo}'\ninpoint {punto_a}\noutpoint {punto_b}\n")
        
        # Generar nombre de salida
        nombre, ext = os.path.splitext(self.archivo)
        salida = f"{nombre}_looped_{self.duracion_minutos}min{ext}"
        
        # Ejecutar FFmpeg
        print("🎬 Generando archivo...")
        cmd = f"ffmpeg -y -f concat -safe 0 -i '{lista_path}' -c copy '{salida}' 2>/dev/null"
        
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ Archivo creado: {salida}")
            
            # Guardar análisis
            analisis_path = f"{nombre}_analisis.json"
            with open(analisis_path, "w") as f:
                json.dump(analisis, f, indent=2)
            print(f"📊 Análisis guardado en: {analisis_path}")
            
            return salida
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en FFmpeg: {e}")
            return None
    
    def limpiar_temporales(self):
        """Limpia archivos temporales"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def ejecutar(self):
        """Punto de entrada principal"""
        print(f"🎵 Procesando: {self.archivo}")
        print(f"⏱️ Duración original: {self.info['duracion']:.2f}s")
        print(f"🎯 Target: {self.duracion_minutos} minutos")
        
        try:
            # Extraer audio para análisis
            audio_temp = self.extraer_audio_temporal()
            
            # Detectar ritmo (con fallbacks automáticos)
            if HAS_LIBROSA and audio_temp:
                analisis = self.detectar_ritmo_librosa(audio_temp)
            else:
                analisis = self.detectar_ritmo_por_ffmpeg()
            
            # Crear loop
            resultado = self.crear_loop_inteligente(analisis)
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error durante el procesamiento: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            self.limpiar_temporales()

def main():
    if len(sys.argv) < 2:
        print("""
🎵 AutoLoop con detección de ritmo avanzada
Uso: python autoloop.py <archivo> [minutos]

Ejemplos:
  python autoloop.py cancion.mp3 5
  python autoloop.py video.mp4 10

📦 Dependencias opcionales:
  pip install librosa numpy  # Para detección avanzada
        """)
        sys.exit(1)
    
    archivo = sys.argv[1]
    
    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        sys.exit(1)
    
    minutos = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    looper = AudioLooper(archivo, minutos)
    looper.ejecutar()

if __name__ == "__main__":
    main()