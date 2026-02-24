#!/bin/bash
# Build Casaluce mod for Assetto Corsa (Linux)
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BLEND_FILE="$ROOT_DIR/casaluce.blend"

# --- Verifica requisiti ---
if [ ! -f "$BLEND_FILE" ]; then
    echo "Errore: casaluce.blend non trovato."
    echo "Esegui prima il generatore:"
    echo "  blender --python scripts/create_track.py"
    exit 1
fi

if [ ! -d "textures" ] || [ -z "$(ls textures/*.png 2>/dev/null)" ]; then
    echo "Errore: cartella textures/ vuota o mancante."
    echo "Inserisci le textures (asphalt.png, grass.png, curb_rw.png, barrier.png, startline.png)"
    exit 1
fi

# Find Blender
BLENDER="/snap/bin/blender"
if ! command -v "$BLENDER" &>/dev/null; then
    BLENDER="blender"
    if ! command -v "$BLENDER" &>/dev/null; then
        echo "Errore: Blender non trovato. Installa con: sudo snap install blender --classic"
        exit 1
    fi
fi
echo "Blender: $BLENDER"

# Virtualenv
if [ ! -d ".venv" ]; then
    echo "Creo virtualenv..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# Controlla dipendenze Python
python3 -c "import numpy, PIL" 2>/dev/null || {
    echo "Installo dipendenze Python..."
    pip install -q -r requirements.txt
}
echo ""

echo "=== Casaluce - Build mod ==="
echo

# --- Step 1: Esportazione KN5 (default CW) ---
echo "[1/6] Esportazione KN5 da Blender..."
"$BLENDER" --background "$BLEND_FILE" --python "$ROOT_DIR/scripts/export_kn5.py" 2>&1 | grep -E "^(  |Done|=)"
echo ""

# --- Step 2: Setup struttura mod (default + reverse layout) ---
echo "[2/6] Creazione struttura mod..."
python3 "$ROOT_DIR/scripts/setup_mod_folder.py"
echo ""

# --- Step 3: Generazione AI line (default CW) ---
echo "[3/6] Generazione AI line CW..."
"$BLENDER" --background "$BLEND_FILE" --python "$ROOT_DIR/scripts/generate_ai_line.py" 2>&1 | grep -E "^(  |Done|=|Gen|Writ)"
echo ""

# --- Step 4: Creazione reverse .blend (empties ruotati 180°) ---
echo "[4/6] Creazione reverse blend..."
"$BLENDER" --background "$BLEND_FILE" --python "$ROOT_DIR/scripts/create_reverse_blend.py" 2>&1 | grep -E "^(  |Done|=|Sav|Flip)"
REVERSE_BLEND="$ROOT_DIR/casaluce_reverse.blend"
echo ""

# --- Step 5: Esportazione KN5 reverse ---
echo "[5/6] Esportazione KN5 reverse..."
TRACK_REVERSE=1 "$BLENDER" --background "$REVERSE_BLEND" --python "$ROOT_DIR/scripts/export_kn5.py" 2>&1 | grep -E "^(  |Done|=)"
echo ""

# --- Step 6: Generazione AI line reverse (CCW) ---
echo "[6/6] Generazione AI line CCW (reverse)..."
TRACK_REVERSE=1 "$BLENDER" --background "$REVERSE_BLEND" --python "$ROOT_DIR/scripts/generate_ai_line.py" 2>&1 | grep -E "^(  |Done|=|Gen|Writ)"
echo ""

# --- Copia KN5 nel mod ---
echo "Copia KN5 nella cartella mod..."
cp "$ROOT_DIR/casaluce.kn5" "$ROOT_DIR/mod/casaluce/casaluce.kn5"
cp "$ROOT_DIR/casaluce_reverse.kn5" "$ROOT_DIR/mod/casaluce/casaluce_reverse.kn5"
echo

# --- Creazione zip distribuibile ---
echo "Creazione zip distribuibile..."
mkdir -p "$ROOT_DIR/builds"
(cd "$ROOT_DIR/mod" && zip -r -q ../builds/casaluce.zip casaluce/)
echo "  builds/casaluce.zip  $(du -h "$ROOT_DIR/builds/casaluce.zip" | cut -f1)"
echo

# --- Riepilogo ---
echo "=== Build completata! ==="
echo ""
echo "File generati:"
echo "  casaluce.kn5         $(du -h "$ROOT_DIR/casaluce.kn5" | cut -f1)"
echo "  casaluce_reverse.kn5 $(du -h "$ROOT_DIR/casaluce_reverse.kn5" | cut -f1)"
echo "  mod/casaluce/        $(du -sh "$ROOT_DIR/mod/casaluce/" | cut -f1) totale"
echo "  builds/casaluce.zip  $(du -h "$ROOT_DIR/builds/casaluce.zip" | cut -f1) (distribuibile)"
echo ""
echo "Layout inclusi:"
echo "  default  -> clockwise (orario)"
echo "  reverse  -> counter-clockwise (antiorario)"
echo ""
echo "Per installare in Assetto Corsa:"
echo "  bash install.sh"
echo ""
echo "Per condividere la mod:"
echo "  Invia builds/casaluce.zip"
echo "  Estrarre in: assettocorsa/content/tracks/"
