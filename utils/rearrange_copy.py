import json
from pathlib import Path

# Cartella in cui DeepfakeBench legge i file JSON dei dataset
json_dir = Path("/app/preprocessing/dataset_json")
orig_json_path = json_dir / "Celeb-DF-v2.json"

# Carica il JSON originale in memoria
with open(orig_json_path, "r") as f:
    orig_data = json.load(f)

# Converte in stringa per sostituire in blocco tutti i riferimenti al dataset originale
raw_text = json.dumps(orig_data)

for crf in [23, 40]:
    new_name = f"Celeb-DF-v2_crf{crf}"
    
    # Sostituisce sia la chiave principale ("Celeb-DF-v2") sia i percorsi interni dei frame
    # (es. "Celeb-DF-v2/Celeb-real/frames/..." -> "Celeb-DF-v2_crf23/Celeb-real/frames/...")
    updated_text = raw_text.replace("Celeb-DF-v2", new_name)
    updated_data = json.loads(updated_text)
    
    out_path = json_dir / f"{new_name}.json"
    with open(out_path, "w") as f:
        json.dump(updated_data, f, indent=4)
        
    print(f"Generato: {out_path}")