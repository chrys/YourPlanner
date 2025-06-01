#!/bin/bash
# Deployment script for YourPlanner

set -e  # Exit immediately if a command exits with a non-zero status

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if we're in production mode
if [ "$DJANGO_SETTINGS_MODULE" != "YourPlanner.settings.production" ]; then
    echo "Warning: Not using production settings. Set DJANGO_SETTINGS_MODULE=YourPlanner.settings.production"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update code from repository
echo "Updating code from repository..."
git pull

# Install or update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p media/item_images
mkdir -p staticfiles

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Optimize database
echo "Optimizing database..."
python manage.py optimize_db --all

# Restart services
echo "Restarting services..."
if command -v systemctl &> /dev/null; then
    # If using systemd
    sudo systemctl restart yourplanner.service
    sudo systemctl restart nginx
elif command -v supervisorctl &> /dev/null; then
    # If using supervisor
    sudo supervisorctl restart yourplanner
    sudo service nginx restart
else
    echo "Warning: Could not automatically restart services. Please restart manually."
fi

echo "Deployment completed successfully!"

