import sys
import os
import subprocess

def crear_loop(archivo_entrada, duracion_minutos=10):
    print(f"🎵 Analizando: {archivo_entrada}")
    
    # Comprobar si el archivo existe
    if not os.path.exists(archivo_entrada):
        print("❌ ¡El archivo no existe!")
        return

    # Nombre del archivo de salida
    nombre, ext = os.path.splitext(archivo_entrada)
    archivo_salida = f"{nombre}_looped{ext}"

    # 1. Obtenemos la duración total del archivo original usando FFprobe
    cmd_duracion = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 '{archivo_entrada}'"
    duracion_original = float(subprocess.check_output(cmd_duracion, shell=True).strip())
    
    # 2. Truco para Termux: En lugar de analizar ondas complejas, 
    # asumimos un punto de loop estándar (por ejemplo, el estribillo).
    # ¡Vamos a cortar la intro y repetir el cuerpo del audio/video!
    punto_a = duracion_original * 0.2  # El 20% del archivo (ej. cuando ya empezó el ritmo)
    punto_b = duracion_original * 0.9  # El 90% del archivo (antes de que baje el volumen al final)
    
    duracion_loop = punto_b - punto_a
    veces_a_repetir = int((duracion_minutos * 60) // duracion_loop)

    print(f"⏱️ Duración original: {duracion_original:.2f}s")
    print(f"✂️ Punto de Loop: desde {punto_a:.2f}s hasta {punto_b:.2f}s")
    print(f"🔁 Se repetirá {veces_a_repetir} veces para alcanzar los {duracion_minutos} minutos.")

    # 3. Construimos el mega comando de FFmpeg (sirve para MP3 y MP4 de video)
    # Corta la intro, luego clona el fragmento central X veces, y los une.
    
    # Creamos un archivo temporal con la lista de videos/audios a unir
    with open("lista.txt", "w") as f:
        # Primero la intro más la primera vuelta
        f.write(f"file '{archivo_entrada}'\ninpoint 0\noutpoint {punto_b}\n")
        # Luego las repeticiones del bucle
        for _ in range(veces_a_repetir):
            f.write(f"file '{archivo_entrada}'\ninpoint {punto_a}\noutpoint {punto_b}\n")

    # Ejecutamos FFmpeg para concatenar de forma nativa (ultra rápido y sin perder calidad)
    print("🎬 Generando archivo final con FFmpeg...")
    cmd_ffmpeg = f"ffmpeg -y -f concat -safe 0 -i lista.txt -c copy '{archivo_salida}'"
    
    subprocess.run(cmd_ffmpeg, shell=True)
    
    # Limpiamos el archivo temporal
    if os.path.exists("lista.txt"):
        os.remove("lista.txt")
        
    print(f"✅ ¡Listo! Archivo guardado como: {archivo_salida}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python autoloop.py <archivo> <minutos>")
    else:
        archivo = sys.argv[1]
        minutos = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        crear_loop(archivo, minutos)

