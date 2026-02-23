#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Typenschild-Scanner – VPS Deployment-Skript
# Hostinger VPS: srv1356442.hstgr.cloud (76.13.155.137)
# Dashboard: https://scanner.christianradden.de
# ═══════════════════════════════════════════════════════════════
set -e

APP_DIR="/opt/typenschild-scanner"
DOMAIN="scanner.christianradden.de"

echo "═══════════════════════════════════════════════"
echo "  Typenschild-Scanner – Deployment"
echo "═══════════════════════════════════════════════"

# ─── 1. System-Updates & Docker installieren ──────────────────
echo ""
echo "▶ [1/6] System-Pakete & Docker..."

apt-get update -qq
apt-get install -y -qq git curl nginx certbot python3-certbot-nginx > /dev/null

# Docker installieren (falls nicht vorhanden)
if ! command -v docker &> /dev/null; then
    echo "  → Docker wird installiert..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "  ✅ Docker installiert"
else
    echo "  ✅ Docker bereits vorhanden"
fi

# Docker Compose Plugin prüfen
if ! docker compose version &> /dev/null; then
    echo "  → Docker Compose Plugin wird installiert..."
    apt-get install -y -qq docker-compose-plugin > /dev/null
fi

# ─── 2. Repository klonen ────────────────────────────────────
echo ""
echo "▶ [2/6] Repository klonen..."

if [ -d "$APP_DIR" ]; then
    echo "  → Verzeichnis existiert, aktualisiere..."
    cd "$APP_DIR"
    git pull origin main
else
    git clone https://github.com/chradden/typenschild-scanner.git "$APP_DIR"
    cd "$APP_DIR"
fi
echo "  ✅ Code bereit in $APP_DIR"

# ─── 3. Umgebungsvariablen ────────────────────────────────────
echo ""
echo "▶ [3/6] Konfiguration (.env)..."

if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo ""
    echo "  ⚠️  WICHTIG: Bitte .env bearbeiten!"
    echo "  nano $APP_DIR/.env"
    echo ""
    echo "  Dort eintragen:"
    echo "    TELEGRAM_BOT_TOKEN=dein-token"
    echo "    OPENAI_API_KEY=sk-dein-key"
    echo "    BOT_AKTIV=true"
    echo ""
    read -p "  .env jetzt bearbeiten? (j/n): " edit_env
    if [[ "$edit_env" == "j" ]]; then
        nano "$APP_DIR/.env"
    fi
else
    echo "  ✅ .env existiert bereits"
fi

# ─── 4. Docker Container bauen & starten ─────────────────────
echo ""
echo "▶ [4/6] Docker Container bauen & starten..."

cd "$APP_DIR"
docker compose down 2>/dev/null || true
docker compose build --quiet
docker compose up -d

echo "  ✅ Container läuft auf Port 8091"

# Warten bis Container bereit ist
echo "  → Warte auf Startup..."
sleep 5

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8091 | grep -q "200\|401"; then
    echo "  ✅ Dashboard antwortet auf http://localhost:8091"
else
    echo "  ⚠️  Dashboard noch nicht bereit, prüfe Logs:"
    echo "      docker compose -f $APP_DIR/docker-compose.yml logs --tail=20"
fi

# ─── 5. Nginx Reverse Proxy ──────────────────────────────────
echo ""
echo "▶ [5/6] Nginx Reverse Proxy für $DOMAIN..."

cp "$APP_DIR/deploy/nginx-scanner.conf" "/etc/nginx/sites-available/scanner"

if [ ! -L "/etc/nginx/sites-enabled/scanner" ]; then
    ln -sf /etc/nginx/sites-available/scanner /etc/nginx/sites-enabled/scanner
fi

# Nginx testen & neuladen
nginx -t && systemctl reload nginx
echo "  ✅ Nginx konfiguriert → http://$DOMAIN"

# ─── 6. SSL-Zertifikat (Let's Encrypt) ───────────────────────
echo ""
echo "▶ [6/6] SSL-Zertifikat..."

# Prüfen ob Domain schon auf diesen Server zeigt
DOMAIN_IP=$(getent hosts "$DOMAIN" 2>/dev/null | awk '{print $1}' | head -1)
SERVER_IP=$(curl -s -4 ifconfig.me 2>/dev/null || echo "unbekannt")

if [[ "$DOMAIN_IP" == "$SERVER_IP" ]]; then
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos \
        --email admin@christianradden.de --redirect 2>/dev/null \
        && echo "  ✅ SSL aktiv → https://$DOMAIN" \
        || echo "  ⚠️  SSL fehlgeschlagen, manuell: certbot --nginx -d $DOMAIN"
else
    echo "  ⚠️  DNS-Eintrag fehlt noch!"
    echo "     Domain '$DOMAIN' zeigt auf: ${DOMAIN_IP:-nichts}"
    echo "     Server-IP: $SERVER_IP"
    echo ""
    echo "  → Erstelle einen A-Record bei deinem DNS-Provider:"
    echo "     scanner.christianradden.de  →  A  →  $SERVER_IP"
    echo ""
    echo "  Danach SSL aktivieren mit:"
    echo "     certbot --nginx -d $DOMAIN"
fi

# ─── Fertig ───────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ Deployment abgeschlossen!"
echo "═══════════════════════════════════════════════"
echo ""
echo "  📍 Dashboard: http://$DOMAIN (→ https nach SSL)"
echo "  🔧 Logs:      cd $APP_DIR && docker compose logs -f"
echo "  🔄 Neustart:  cd $APP_DIR && docker compose restart"
echo "  📦 Update:    cd $APP_DIR && git pull && docker compose up -d --build"
echo ""
