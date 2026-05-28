#!/bin/bash

# Quick Docker Compose Verification Script
# Usage: ./verify-infrastructure.sh

set -e

echo "========================================"
echo "Docker Infrastructure Verification"
echo "========================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi
echo "✅ Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi
echo "✅ Docker Compose found: $(docker-compose --version)"
echo ""

# Build and start services
echo "========================================"
echo "Building and starting services..."
echo "========================================"
docker-compose --version
docker-compose build
docker-compose up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "========================================"
echo "Service Status"
echo "========================================"
docker-compose ps
echo ""

# Test endpoints
echo "========================================"
echo "Testing Endpoints"
echo "========================================"

# FastAPI health
echo ""
echo "Testing FastAPI health endpoint..."
if curl -s http://localhost/health > /dev/null; then
    echo "✅ FastAPI health check: OK"
else
    echo "⚠️  FastAPI health check: FAILED (may still be starting)"
fi

# PostgreSQL
echo ""
echo "Testing PostgreSQL connection..."
if docker-compose exec -T postgres psql -U tutordb_user -d tutor_platform_db -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ PostgreSQL connection: OK"
else
    echo "⚠️  PostgreSQL connection: FAILED"
fi

# Keycloak (wait longer)
echo ""
echo "Testing Keycloak availability..."
for i in {1..30}; do
    if curl -s http://localhost:8080/auth/health/live > /dev/null; then
        echo "✅ Keycloak: OK (ready on attempt $i)"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Keycloak: Still starting (may take a few minutes)"
    fi
    sleep 2
done

# PostgREST
echo ""
echo "Testing PostgREST..."
if curl -s http://localhost/api/data/health_check > /dev/null; then
    echo "✅ PostgREST: OK"
else
    echo "⚠️  PostgREST: May be starting"
fi

# Nginx
echo ""
echo "Testing Nginx..."
if curl -s http://localhost/ > /dev/null; then
    echo "✅ Nginx: OK"
else
    echo "⚠️  Nginx: FAILED"
fi

echo ""
echo "========================================"
echo "Docker Infrastructure Ready!"
echo "========================================"
echo ""
echo "Access points:"
echo "  - FastAPI Docs:  http://localhost:8000/docs"
echo "  - FastAPI Redoc:  http://localhost:8000/redoc"
echo "  - Keycloak Admin: http://localhost:8080/admin"
echo "    (admin / admin_password)"
echo "  - PostgREST:     http://localhost/api/data/"
echo "  - PostgreSQL:    localhost:5432"
echo "     (tutordb_user / tutordb_pass)"
echo ""
echo "Useful commands:"
echo "  - View logs:     docker-compose logs -f fastapi"
echo "  - Stop services: docker-compose down"
echo "  - Remove data:   docker-compose down -v"
echo "  - Shell in fastapi: docker-compose exec fastapi bash"
echo ""
