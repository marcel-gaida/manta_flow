#!/bin/bash

set -e

echo "-----------------------------------------------------"
echo " Metabase Installer for Raspberry Pi 4"
echo "-----------------------------------------------------"
echo "This script will:"
echo "1. Update your system"
echo "2. Install OpenJDK 21 from Adoptium (Temurin)"
echo "3. Configure GPU memory to 16MB (needs reboot)"
echo "4. Create a secure 'metabase' user"
echo "5. Download Metabase and configure it as a service"
echo ""

read -p "Do you want to continue with the installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

# --- Step 1: System Update ---
echo ""
echo " Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y
echo "System packages updated."

# --- Step 2: Install OpenJDK 21 from Adoptium (Temurin) ---
echo ""
echo " Installing OpenJDK 21 (Temurin)..."
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" ]]; then
    echo "This script is intended for 64-bit Raspberry Pi OS only."
    exit 1
fi

# Download and extract the JDK
JDK_URL="https://github.com/adoptium/temurin21-binaries/releases/latest/download/OpenJDK21U-jdk_aarch64_linux_hotspot_21.0.7_6.tar.gz"
JDK_DIR="/opt/temurin"
sudo mkdir -p "$JDK_DIR"
sudo wget -q -O - "$JDK_URL" | sudo tar xz -C "$JDK_DIR" --strip-components=1

# Make sure it's in PATH for this script
export PATH="$JDK_DIR/bin:$PATH"
JAVA_PATH="$JDK_DIR/bin/java"

echo "Java installed at $JAVA_PATH"
"$JAVA_PATH" -version

# --- Step 3: Optimize GPU Memory ---
echo ""
echo " Configuring GPU memory..."
CONFIG_FILE="/boot/firmware/config.txt"
if grep -q "^gpu_mem=" "$CONFIG_FILE"; then
    echo "GPU memory already configured. Skipping."
else
    echo "Setting GPU memory to 16MB..."
    echo "" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "# Reduce GPU memory for server workloads" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "gpu_mem=16" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "GPU memory set. A reboot will apply the change."
fi

# --- Step 4: Create Metabase User and Directory ---
echo ""
echo " Creating user and directory for Metabase..."
if id "metabase" &>/dev/null; then
    echo "User 'metabase' already exists."
else
    sudo groupadd metabase
    sudo useradd -r -s /bin/false -g metabase metabase
    echo "User 'metabase' created."
fi

sudo mkdir -p /opt/metabase
sudo chown metabase:metabase /opt/metabase
echo "Directory /opt/metabase ready."

# --- Step 5: Download Metabase ---
echo ""
echo " Downloading latest Metabase..."
sudo wget -q -O /opt/metabase/metabase.jar https://downloads.metabase.com/latest/metabase.jar
sudo chown metabase:metabase /opt/metabase/metabase.jar
echo "Metabase downloaded."

# --- Step 6: Create systemd Service ---
echo ""
echo " Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/metabase.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Metabase Analytics Application
After=network.target

[Service]
User=metabase
Group=metabase
WorkingDirectory=/opt/metabase
ExecStart=$JAVA_PATH --add-opens java.base/java.nio=ALL-UNNAMED -jar metabase.jar
Environment="MB_JETTY_PORT=3000"
Environment="JAVA_TOOL_OPTIONS=-Xmx2560m"
SuccessExitStatus=143
Restart=on-failure
RestartSec=10
ProtectSystem=full
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable metabase.service
sudo systemctl start metabase.service
echo "Metabase service installed and started."

# --- Final Instructions ---
echo ""
echo "-----------------------------------------------------"
echo " ? Metabase Installation Complete!"
echo "-----------------------------------------------------"
echo ""
echo "Access Metabase in your browser after a few minutes:"
echo "1. Get your Raspberry Pi's IP:"
echo "   hostname -I"
echo "2. Open:"
echo "   http://<YOUR_PI_IP>:3000"
echo ""
echo "To check the service status:"
echo "   sudo systemctl status metabase"
echo ""
echo "??  To apply GPU memory change, reboot:"
echo "   sudo reboot"
echo ""
