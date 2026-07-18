#!/usr/bin/env bash
# build_gui.sh - Build Re-Gen GUI portable binary + .deb package
# Usage: ./build_gui.sh
#
# Requires: pip install pyinstaller PyQt5 scipy
# For .deb: sudo apt install dpkg-dev

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "==========================================="
echo "  Re-Gen v3.0.0 - Build Script"
echo "==========================================="
echo ""

# --- deps check ---
python3 -c "import PyQt5" 2>/dev/null || { echo "Run: pip install PyQt5"; exit 1; }
python3 -c "import PyInstaller" 2>/dev/null || { echo "Run: pip install pyinstaller"; exit 1; }

# --- clean ---
rm -rf build/ dist/

# --- build onefile binary ---
echo "[1/3] Building onefile binary..."
python3 -m PyInstaller \
    --onefile \
    --name "re-gen" \
    --windowed \
    --noconfirm \
    --clean \
    --noupx \
    --collect-all re_gen \
    --collect-submodules re_gen \
    src/re_gen/gui/app.py \
    2>&1 | grep -v "INFO:" || true

if [ ! -f "dist/re-gen" ]; then
    echo "ERROR: Build failed"
    exit 1
fi
echo "  OK: dist/re-gen ($(du -h dist/re-gen | cut -f1))"

# --- package as .deb ---
echo "[2/3] Packaging .deb..."
DEB_NAME="re-gen_3.0.0_amd64"
DEB_DIR="dist/$DEB_NAME"

mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"

cp dist/re-gen "$DEB_DIR/usr/bin/re-gen"
chmod 755 "$DEB_DIR/usr/bin/re-gen"

cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: re-gen
Version: 3.0.0
Section: science
Priority: optional
Architecture: amd64
Depends: libc6, libglib2.0-0, libx11-6, libgl1, libegl1, libfontconfig1, libfreetype6
Installed-Size: $(du -sk "$DEB_DIR" | cut -f1)
Maintainer: Re-Gen Contributors
Homepage: https://github.com/re-gen/re-gen
Description: Paleontological Genome Reconstruction GUI
 Re-Gen is a genome reconstruction pipeline for de-extinction research.
 Features CRISPR gRNA design, ancestral sequence reconstruction,
 phylogenetic bracketing, and hardware device simulation/control.
 Includes a database of 530+ dinosaur species.
EOF

cat > "$DEB_DIR/usr/share/applications/re-gen.desktop" << EOF
[Desktop Entry]
Name=Re-Gen
Comment=Paleontological Genome Reconstruction
Exec=/usr/bin/re-gen
Icon=re-gen
Terminal=false
Type=Application
Categories=Science;Education;
Keywords=genome;crispr;palaeontology;dinosaur;bioinformatics;
EOF

# Build .deb
dpkg-deb --build "$DEB_DIR" "dist/${DEB_NAME}.deb" 2>/dev/null || {
    echo "  dpkg-deb not available, skipping .deb (install dpkg-dev)"
    echo "  Manual: sudo dpkg-deb -B $DEB_DIR dist/re-gen.deb"
}
rm -rf "$DEB_DIR"

# --- summary ---
echo "[3/3] Done!"
echo ""
echo "==========================================="
echo "  BUILD COMPLETE"
echo "==========================================="
ls -lh dist/re-gen dist/*.deb 2>/dev/null || ls -lh dist/re-gen
echo ""
echo "  Linux binary:  dist/re-gen"
echo "  Linux .deb:    dist/${DEB_NAME}.deb"
echo ""
echo "  Install .deb:  sudo dpkg -i dist/${DEB_NAME}.deb"
echo "  Run binary:    ./dist/re-gen"
