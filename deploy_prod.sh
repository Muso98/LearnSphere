#!/bin/bash

# LearnSphere Production Deployment Script

echo "🚀 Starting deployment..."

# Build and start containers
echo "📦 Building and starting containers..."
docker-compose up -d --build

# Run migrations (already in docker-compose command, but safe to run again)
echo "⚙️ Running database migrations..."
docker-compose exec web python manage.py migrate

# Clean up
echo "🧹 Cleaning up unused Docker images..."
docker image prune -f

echo "✅ LearnSphere is live!"
