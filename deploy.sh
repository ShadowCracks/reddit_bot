#!/bin/bash

# Heroku deployment script

echo "Setting up Heroku deployment..."

# Make sure you're in the project directory
cd /home/shadow-crack/reddit_bot

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for Heroku deployment"

# Create Heroku app (replace 'your-bot-name' with your desired app name)
heroku create your-reddit-bot-name

# Set environment variables on Heroku
echo "Setting environment variables..."
heroku config:set OPENAI_API_KEY="$(grep OPENAI_API_KEY .env | cut -d '=' -f2)"
heroku config:set OPENAI_MODEL="gpt-4o-mini"
heroku config:set REDDIT_CLIENT_ID="your_reddit_client_id"
heroku config:set REDDIT_CLIENT_SECRET="your_reddit_client_secret"
heroku config:set REDDIT_USER_AGENT="HiringBot/1.0 by YourUsername"
heroku config:set REDDIT_USERNAME="your_reddit_username"
heroku config:set REDDIT_PASSWORD="your_reddit_password"

# Deploy to Heroku
git push heroku main

echo "Deployment complete!"
echo "Check your app logs with: heroku logs --tail"
