#!/usr/bin/env bash
# Buduje samodzielny pakiet .deb dla Mazaka (z wlasnym PySide6 w srodku,
# bo Ubuntu 24.04 nie ma PySide6 w apt - tylko PySide2).
set -euo pipefail

VERSION="${1:-0.1.0}"
ARCH="amd64"
PKG_NAME="mazak"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PKG_ROOT="$SCRIPT_DIR/mazak_pkgroot"
BUILD_VENV="$SCRIPT_DIR/build-venv"
DIST_DIR="$PROJECT_ROOT/dist"

echo "==> Czyszczenie poprzedniego builda"
rm -rf "$PKG_ROOT" "$BUILD_VENV"
mkdir -p "$DIST_DIR"

echo "==> Budowanie samodzielnego venv z PySide6-Essentials"
python3 -m venv "$BUILD_VENV"
"$BUILD_VENV/bin/pip" install --quiet --upgrade pip
"$BUILD_VENV/bin/pip" install --quiet -r "$PROJECT_ROOT/requirements.txt"

echo "==> Przygotowanie struktury pakietu"
mkdir -p "$PKG_ROOT/DEBIAN"
mkdir -p "$PKG_ROOT/opt/mazak"
mkdir -p "$PKG_ROOT/usr/bin"
mkdir -p "$PKG_ROOT/usr/share/applications"
mkdir -p "$PKG_ROOT/usr/share/icons/hicolor/256x256/apps"

cp -r "$PROJECT_ROOT/mazak" "$PKG_ROOT/opt/mazak/"
cp "$PROJECT_ROOT/main.py" "$PKG_ROOT/opt/mazak/"
find "$PKG_ROOT/opt/mazak" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

cp -r "$BUILD_VENV" "$PKG_ROOT/opt/mazak/venv"
# usun cache pip z zapakowanego venv, zeby nie pompowac rozmiaru na darmo
rm -rf "$PKG_ROOT/opt/mazak/venv/pip-selfcheck.json" 2>/dev/null || true
find "$PKG_ROOT/opt/mazak/venv" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

cp "$PROJECT_ROOT/mazak_icon.png" "$PKG_ROOT/usr/share/icons/hicolor/256x256/apps/mazak.png"

cat > "$PKG_ROOT/usr/share/applications/mazak.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Mazak
Comment=Adnotacje na screenshotach - strzałki, dymki, opisy
Exec=/usr/bin/mazak
Icon=mazak
Terminal=false
Categories=Graphics;2DGraphics;RasterGraphics;
EOF

cat > "$PKG_ROOT/usr/bin/mazak" << 'EOF'
#!/usr/bin/env bash
# nie polegamy na tym, ze venv/bin/python (symlink) sam wykryje swoj
# venv na obcej maszynie - jawnie dokladamy site-packages do PYTHONPATH
for d in /opt/mazak/venv/lib/python3.*/site-packages; do
    export PYTHONPATH="$d${PYTHONPATH:+:$PYTHONPATH}"
    break
done
unset PYTHONHOME
exec /opt/mazak/venv/bin/python3 /opt/mazak/main.py "$@"
EOF
chmod +x "$PKG_ROOT/usr/bin/mazak"

INSTALLED_SIZE_KB=$(du -sk "$PKG_ROOT" | cut -f1)

cat > "$PKG_ROOT/DEBIAN/control" << EOF
Package: $PKG_NAME
Version: $VERSION
Section: graphics
Priority: optional
Architecture: $ARCH
Installed-Size: $INSTALLED_SIZE_KB
Depends: python3 (>= 3.10), libxcb-cursor0, libqt6gui6t64 | libqt6gui6
Maintainer: Krzysztof Ślimak <krzysztof.slimak@outlook.com>
Homepage: https://github.com/krzysiekslimak/mazak
Description: Narzędzie do adnotowania zrzutów ekranu
 Mazak to lekki edytor PNG do nanoszenia strzałek, dymków, tekstu,
 ramek i naklejek na już zrobione zrzuty ekranu. Zawiera własny,
 samodzielny zestaw PySide6 (Qt6) - nie wymaga niczego dodatkowego
 z internetu podczas instalacji.
EOF

cat > "$PKG_ROOT/DEBIAN/postinst" << 'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod +x "$PKG_ROOT/DEBIAN/postinst"

DEB_FILE="$DIST_DIR/${PKG_NAME}_${VERSION}_${ARCH}.deb"
echo "==> Budowanie $DEB_FILE"
dpkg-deb --build --root-owner-group "$PKG_ROOT" "$DEB_FILE"

echo "==> Gotowe: $DEB_FILE"
du -h "$DEB_FILE"
