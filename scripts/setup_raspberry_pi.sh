#!/bin/bash
# Raspberry Pi setup script
# Sets up Teddy AI development infrastructure on Raspberry Pi

set -e

echo "🧸 Setting up Teddy AI Infrastructure on Raspberry Pi..."
echo ""

# Check if running on Raspberry Pi
if ! grep -q "arm" /proc/cpuinfo; then
    echo "⚠️  This script is designed for Raspberry Pi (ARM processor)"
    echo "  Continuing anyway..."
fi

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
sudo apt-get install -y \
    git \
    curl \
    wget \
    vim \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    docker.io \
    docker-compose

# Enable Docker
echo "🐳 Configuring Docker..."
sudo systemctl enable docker
sudo usermod -aG docker $USER
echo "  (You may need to log out and back in for group changes to take effect)"

# Create app directory
APP_DIR="/home/$USER/teddy-ai"
echo "📁 Creating application directory: $APP_DIR"
mkdir -p $APP_DIR

# Clone or setup repository
if [ ! -d "$APP_DIR/.git" ]; then
    echo "📖 Cloning Teddy AI repository..."
    # This would be the actual clone command
    echo "  To clone: git clone <repo-url> $APP_DIR"
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p $APP_DIR/data
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/backups

# Install Docker containers for services
echo "🐳 Setting up Docker services..."
cat > "$APP_DIR/docker-compose.yml" << 'EOF'
version: '3'
services:
  # Gitea - Git server
  gitea:
    image: gitea/gitea:latest
    ports:
      - "3000:3000"
      - "222:22"
    volumes:
      - ./data/gitea:/data
    environment:
      - USER_UID=1000
      - USER_GID=1000
  
  # SQLite with web interface (optional)
  sqlite-web:
    image: coleifer/sqlite-web:latest
    ports:
      - "8080:8080"
    volumes:
      - ./data:/data
    command: /data/teddy.db
    depends_on:
      - gitea
EOF

echo "  docker-compose.yml created"

# Setup SSH
echo "🔐 Configuring SSH..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "  SSH home directory ready. Add your public key to ~/.ssh/authorized_keys"

# Setup Tailscale (optional)
echo "🌐 Installing Tailscale (optional - press Ctrl+C to skip)..."
sleep 2
if timeout 5 curl -fsSL https://tailscale.com/install.sh > /tmp/tailscale-setup.sh; then
    chmod +x /tmp/tailscale-setup.sh
    sudo /tmp/tailscale-setup.sh
    echo "  Tailscale installed. Run 'sudo tailscale up' to connect."
else
    echo "  Skipping Tailscale installation."
fi

# Create systemd service (optional)
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/teddy-docker.service > /dev/null << EOF
[Unit]
Description=Teddy AI Docker Services
After=network.target
Wants=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo "  Service installed. Enable with: sudo systemctl enable teddy-docker"

echo ""
echo "✅ Raspberry Pi setup complete!"
echo ""
echo "Next steps:"
echo "1. (Optional) Enable Docker service: sudo systemctl enable teddy-docker"
echo "2. (Optional) Setup Tailscale: sudo tailscale up"
echo "3. Start services: cd $APP_DIR && docker-compose up -d"
echo "4. Check Gitea: http://localhost:3000"
echo ""
