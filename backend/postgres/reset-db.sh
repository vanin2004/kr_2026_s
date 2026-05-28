#!/bin/bash
# Database Reset Script
# Use this to completely reset the databases and reinitialize them

set -e

echo "🔄 Resetting PostgreSQL databases..."

# Remove PostgreSQL volume if it exists
if docker volume ls | grep -q postgres_data; then
    echo "⚠️  Removing postgres_data volume..."
    docker volume rm postgres_data || true
fi

# Remove Keycloak volume if it exists
if docker volume ls | grep -q keycloak_data; then
    echo "⚠️  Removing keycloak_data volume..."
    docker volume rm keycloak_data || true
fi

# Restart PostgreSQL container
echo "🔄 Restarting PostgreSQL container..."
docker-compose down postgres || true
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to initialize..."
sleep 10

# Check if database is ready
max_attempts=30
attempt=0
while ! docker-compose exec -T postgres pg_isready -U tutordb_user -d tutor_platform_db > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ PostgreSQL did not become ready in time"
        exit 1
    fi
    echo "⏳ Waiting for PostgreSQL to be ready... ($attempt/$max_attempts)"
    sleep 1
done

echo "✅ PostgreSQL is ready"

# Show migration tables status
echo ""
echo "📊 Checking migration tables..."
docker-compose exec -T postgres psql -U tutordb_user -d tutor_platform_db -c "
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%migration%' OR table_name LIKE '%changelog%';"

echo ""
echo "✅ Database reset complete!"
echo ""
echo "Next steps:"
echo "  1. Restart all services: docker-compose restart"
echo "  2. Run API tests: python api_client.py full"
