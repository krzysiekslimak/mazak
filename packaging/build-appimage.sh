#!/usr/bin/env bash
# Buduje samodzielny plik .AppImage dla Mazaka (z wlasnym PySide6 w srodku,
# dziala na dowolnej dystrybucji Linuksa bez instalacji).
set -euo pipefail

VERSION="${1:-0.1.0}"
ARCH="x86_64"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APPDIR="$SCRIPT_DIR/AppDir"
BUILD_VENV="$SCRIPT_DIR/build-venv"
DIST_DIR="$PROJECT_ROOT/dist"
TOOLS_DIR="$SCRIPT_DIR/tools"
APPIMAGETOOL="$TOOLS_DIR/appimagetool"

echo "==> Czyszczenie poprzedniego builda"
rm -rf "$APPDIR" "$BUILD_VENV"
mkdir -p "$DIST_DIR" "$TOOLS_DIR"

if [ ! -x "$APPIMAGETOOL" ]; then
    echo "==> Pobieranie appimagetool"
    curl -fL -o "$APPIMAGETOOL" "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

echo "==> Budowanie samodzielnego venv z PySide6-Essentials"
python3 -m venv "$BUILD_VENV"
"$BUILD_VENV/bin/python" -m pip install --quiet --upgrade pip
"$BUILD_VENV/bin/python" -m pip install --quiet -r "$PROJECT_ROOT/requirements.txt"

echo "==> Przygotowanie struktury AppDir"
mkdir -p "$APPDIR/opt/mazak"

cp -r "$PROJECT_ROOT/mazak" "$APPDIR/opt/mazak/"
cp "$PROJECT_ROOT/main.py" "$APPDIR/opt/mazak/"
find "$APPDIR/opt/mazak" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

cp -r "$BUILD_VENV" "$APPDIR/opt/mazak/venv"
find "$APPDIR/opt/mazak/venv" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

cp "$PROJECT_ROOT/mazak_icon.png" "$APPDIR/mazak.png"

mkdir -p "$APPDIR/usr/share/applications"
cat > "$APPDIR/mazak.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Mazak
Comment=Screenshot annotation editor - arrows, speech bubbles, text, frames, stickers
Exec=mazak
Icon=mazak
Terminal=false
Categories=Graphics;2DGraphics;RasterGraphics;
EOF
cp "$APPDIR/mazak.desktop" "$APPDIR/usr/share/applications/mazak.desktop"

mkdir -p "$APPDIR/usr/share/metainfo"
cat > "$APPDIR/usr/share/metainfo/io.github.krzysiekslimak.Mazak.appdata.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>io.github.krzysiekslimak.Mazak</id>
  <name>Mazak</name>
  <summary>Screenshot annotation editor</summary>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <description>
    <p>
      Mazak is a lightweight screenshot annotation editor for Linux - arrows,
      speech bubbles, text, frames, stickers, blur/pixelate, and crop tools,
      each with a live properties panel that floats over the canvas.
    </p>
  </description>
  <launchable type="desktop-id">mazak.desktop</launchable>
  <url type="homepage">https://github.com/krzysiekslimak/mazak</url>
  <developer id="io.github.krzysiekslimak">
    <name>Krzysztof Ślimak</name>
  </developer>
  <provides>
    <binary>mazak</binary>
  </provides>
  <releases>
    <release version="$VERSION" date="$(date +%Y-%m-%d)"/>
  </releases>
  <content_rating type="oars-1.1"/>
</component>
EOF

cat > "$APPDIR/AppRun" << 'EOF'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "$HERE/opt/mazak/venv/bin/python" "$HERE/opt/mazak/main.py" "$@"
EOF
chmod +x "$APPDIR/AppRun"

echo "==> Walidacja pliku .desktop i metainfo"
desktop-file-validate "$APPDIR/mazak.desktop"
appstreamcli validate --no-net "$APPDIR/usr/share/metainfo/io.github.krzysiekslimak.Mazak.appdata.xml" || true

APPIMAGE_FILE="$DIST_DIR/mazak-${VERSION}-${ARCH}.AppImage"
echo "==> Budowanie $APPIMAGE_FILE"
ARCH="$ARCH" "$APPIMAGETOOL" "$APPDIR" "$APPIMAGE_FILE"

echo "==> Gotowe: $APPIMAGE_FILE"
du -h "$APPIMAGE_FILE"
