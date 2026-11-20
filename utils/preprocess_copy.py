import sys
import cv2
import dlib
from pathlib import Path

# Aggiunge la cartella preprocessing di DeepfakeBench al path di Python
# per poter importare direttamente le funzioni native senza duplicare codice
sys.path.append("/app/preprocessing")
from preprocess import extract_aligned_face_dlib

# Inizializza il rilevatore di volti HOG e il predittore degli 81 landmark facciali di Dlib
face_detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("/app/preprocessing/dlib_tools/shape_predictor_81_face_landmarks.dat")

# Definisce il dataset originale (da cui ricavare le coordinate esatte di ritaglio)
# e i dataset compressi (da cui estrarre i pixel degradati da H.264)
orig_root = Path("/app/datasets/Celeb-DF-v2")
comp_roots = [
    Path("/app/datasets/Celeb-DF-v2_crf23"),
    Path("/app/datasets/Celeb-DF-v2_crf40"),
]

# Tutte e tre le sottocartelle standard di Celeb-DF-v2 (reali e sintetici)
SUBDIRS = ["Celeb-real", "Celeb-synthesis", "YouTube-real"]

for sub in SUBDIRS:
    landmarks_base = orig_root / sub / "landmarks"
    # Salta la sottocartella se non è presente nel campione bilanciato
    if not landmarks_base.exists():
        print(f"Salto {sub}: cartella landmarks non trovata")
        continue

    # Elenca in ordine alfabetico tutte le cartelle video già processate nell'originale
    video_dirs = sorted([d for d in landmarks_base.iterdir() if d.is_dir()])

    for i, vid_land_dir in enumerate(video_dirs, 1):
        vid_name = vid_land_dir.name
        
        # Ricava gli esatti indici temporali (es. [0, 14, 28...]) dai nomi dei file .npy originali
        # In questo modo si mantengono gli stessi identici frame della baseline
        target_indices = sorted([int(p.stem) for p in vid_land_dir.glob("*.npy")])
        if not target_indices:
            continue

        # Apre contemporaneamente il video originale e i corrispondenti video compressi
        cap_orig = cv2.VideoCapture(str(orig_root / sub / "videos" / f"{vid_name}.mp4"))
        caps_comp = {c: cv2.VideoCapture(str(c / sub / "videos" / f"{vid_name}.mp4")) for c in comp_roots}

        # Crea le cartelle di destinazione per salvare i ritagli PNG dei video compressi
        for c in comp_roots:
            (c / sub / "frames" / vid_name).mkdir(parents=True, exist_ok=True)

        # Usa un set per verificare in O(1) se il frame corrente va estratto
        target_set = set(target_indices)
        
        # Legge i video sequenzialmente frame per frame fino all'ultimo frame utile:
        # la lettura sequenziale garantisce sincronia perfetta tra stream originale e compressi
        for frame_idx in range(target_indices[-1] + 1):
            ret_o, frame_o = cap_orig.read()
            frames_c = {c: cap.read() for c, cap in caps_comp.items()}

            # Interrompe se il video originale termina prima del previsto
            if not ret_o:
                break
            # Ignora i frame non selezionati nel campionamento originale
            if frame_idx not in target_set:
                continue

            # Applica l'allineamento di DeepfakeBench per ciascun livello di compressione:
            # - Dlib rileva il volto e calcola la matrice affine M sul frame ORIGINALE (frame_o)
            # - Passando frame_c nel parametro 'mask', quella stessa identica matrice M viene
            #   applicata ai pixel del frame COMPRESSO, garantendo allineamento identico al pixel
            for c_root, (ret_c, frame_c) in frames_c.items():
                if ret_c:
                    _, _, cropped_c = extract_aligned_face_dlib(face_detector, predictor, frame_o, mask=frame_c)
                    if cropped_c is not None:
                        # Salva il volto ritagliato 256x256 in formato PNG senza perdita (lossless)
                        cv2.imwrite(str(c_root / sub / "frames" / vid_name / f"{frame_idx:03d}.png"), cropped_c)

        # Chiude gli stream video per liberare i descrittori di file
        cap_orig.release()
        for cap in caps_comp.values():
            cap.release()

        # Stampa un aggiornamento periodico ogni 25 video elaborati
        if i % 25 == 0 or i == len(video_dirs):
            print(f"[{sub}] {i}/{len(video_dirs)} video completati")

print("Estrazione completata su tutte le sottocartelle!")