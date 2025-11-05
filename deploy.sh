#!/bin/bash

# Deployment script for Student Attendance Tracker
# This script helps deploy the application to production

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}❌ Please edit .env file and set SECRET_KEY before deploying!${NC}"
    echo -e "${YELLOW}Generate a secret key: python -c 'import secrets; print(secrets.token_hex(32))'${NC}"
    exit 1
fi

# Check if SECRET_KEY is set and not default
if grep -q "change-this-secret-key-in-production" .env || grep -q "your-secret-key-change-this" .env; then
    echo -e "${RED}❌ Please set a secure SECRET_KEY in .env file!${NC}"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Create necessary directories
mkdir -p instance logs

# Deployment method selection
echo ""
echo "Select deployment method:"
echo "1) Docker Compose (Recommended)"
echo "2) Gunicorn (Direct)"
echo "3) Docker (Standalone)"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo -e "${GREEN}📦 Deploying with Docker Compose...${NC}"
        
        # Build and start containers
        docker-compose down
        docker-compose build
        docker-compose up -d
        
        echo -e "${GREEN}✅ Deployment complete!${NC}"
        echo -e "${GREEN}Application is running at http://localhost:5000${NC}"
        echo -e "${YELLOW}View logs: docker-compose logs -f${NC}"
        ;;
        
    2)
        echo -e "${GREEN}📦 Deploying with Gunicorn...${NC}"
        
        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment
        source venv/bin/activate
        
        # Install dependencies
        pip install -r requirements.txt
        
        # Initialize database
        python -c "from app import init_db; init_db()"
        
        # Start Gunicorn
        echo -e "${GREEN}Starting Gunicorn server...${NC}"
        gunicorn -c gunicorn_config.py app:app
        
        ;;
        
    3)
        echo -e "${GREEN}📦 Building Docker image...${NC}"
        
        # Build Docker image
        docker build -t student-tracker:latest .
        
        # Run container
        docker run -d \
            --name student_tracker \
            -p 5000:5000 \
            --env-file .env \
            -v $(pwd)/instance:/app/instance \
            -v $(pwd)/logs:/app/logs \
            --restart unless-stopped \
            student-tracker:latest
        
        echo -e "${GREEN}✅ Deployment complete!${NC}"
        echo -e "${GREEN}Application is running at http://localhost:5000${NC}"
        echo -e "${YELLOW}View logs: docker logs -f student_tracker${NC}"
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Deployment successful!${NC}"

