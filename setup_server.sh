#!/bin/bash

# LearnSphere Server Setup Script
# Run this on a fresh Ubuntu server

echo "Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

echo "Installing prerequisites..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common git ufw

echo "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "Setting up Firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "System ready! Please log out and back in to use docker without sudo."
sudo usermod -aG docker $USER

echo "------------------------------------------------"
echo "Setup Complete. Now clone your repo and run deploy_prod.sh"
