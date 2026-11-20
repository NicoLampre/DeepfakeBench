import argparse
from pathlib import Path

def generate_test_list(dataset_dir: str, output_filename: str = "List_of_testing_videos.txt"):
    root = Path(dataset_dir)
    if not root.exists():
        raise FileNotFoundError(f"La cartella del dataset non esiste: {root.resolve()}")

    entries = []

    # 1. Video Reali -> Etichetta 1
    real_subdirs = ["Celeb-real/videos", "YouTube-real/videos"]
    real_count = 0
    for subdir in real_subdirs:
        folder = root / subdir
        if folder.exists():
            for file_path in sorted(folder.glob("*.mp4")):
                rel_path = f"{subdir}/{file_path.name}"
                entries.append(f"1 {rel_path}")
                real_count += 1

    # 2. Video Fake -> Etichetta 0
    fake_subdir = "Celeb-synthesis/videos"
    fake_folder = root / fake_subdir
    fake_count = 0
    if fake_folder.exists():
        for file_path in sorted(fake_folder.glob("*.mp4")):
            rel_path = f"{fake_subdir}/{file_path.name}"
            entries.append(f"0 {rel_path}")
            fake_count += 1

    if not entries:
        raise RuntimeError(f"Nessun file .mp4 trovato nelle sottocartelle di {root.resolve()}")

    output_path = root / output_filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries) + "\n")

    print(f"File generato con successo: {output_path.resolve()}")
    print(f"  - Video Reali (1): {real_count}")
    print(f"  - Video Fake  (0): {fake_count}")
    print(f"  - Totale video:    {len(entries)}")
    if real_count != fake_count:
        print("ATTENZIONE: Il numero di video reali e fake non è bilanciato!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genera List_of_testing_videos.txt (da eseguire dentro /app/utils)."
    )
    parser.add_argument(
        "--dataset_dir",
        type=str,
        default="../datasets/Celeb-DF-v2",
        help="Percorso relativo da utils/ (default: ../datasets/Celeb-DF-v2)"
    )
    args = parser.parse_args()
    generate_test_list(args.dataset_dir)
