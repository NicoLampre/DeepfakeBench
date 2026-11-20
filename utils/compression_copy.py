import subprocess
from pathlib import Path
import imageio_ffmpeg

# Recupera il percorso dell'eseguibile ffmpeg incluso nella libreria imageio-ffmpeg
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

# Cartella radice del dataset originale (già strutturato per DeepfakeBench)
src_root = Path("/app/datasets/Celeb-DF-v2")

# Cicla sui due livelli di compressione H.264 previsti per l'esperimento
for crf in [23, 40]:
    # Cartella di destinazione per il livello di compressione corrente
    dst_root = Path(f"/app/datasets/Celeb-DF-v2_crf{crf}")
    
    # Elabora sia i video reali sia quelli manipolati
    for sub in ["Celeb-real/videos", "Celeb-synthesis/videos", "YouTube-real/videos"]:
        out_dir = dst_root / sub
        # Crea la cartella di output (e le eventuali sottocartelle mancanti)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Itera in ordine alfabetico su tutti i file .mp4 della cartella sorgente
        for video in sorted((src_root / sub).glob("*.mp4")):
            out_file = out_dir / video.name
            
            # Esegue ffmpeg per ricodificare il video:
            # -y: sovrascrive l'output se già presente
            # -loglevel error: mostra a schermo solo eventuali errori
            # -c:v libx264: usa il codec video H.264
            # -crf: imposta la qualità/compressione (23 = media, 40 = alta compressione)
            # -pix_fmt yuv420p: uniforma lo spazio colore per reali e fake
            subprocess.run([
                ffmpeg, "-y", "-loglevel", "warning",
                "-i", str(video),
                "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p",
                str(out_file)
            ], check=True)
            
    print(f"Finito CRF {crf}")