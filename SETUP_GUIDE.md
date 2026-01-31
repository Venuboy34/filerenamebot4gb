# Complete Setup Guide for 4GB Rename Bot

## Step-by-Step Setup

### Step 1: Get Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "My Rename Bot")
4. Choose a username for your bot (must end with 'bot', e.g., "myrenamebot")
5. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get API ID and API Hash

1. Go to https://my.telegram.org
2. Log in with your Telegram phone number
3. Click on "API Development Tools"
4. Fill in the application details:
   - App title: Any name
   - Short name: Any short name
   - Platform: Other
   - Description: Optional
5. Click "Create application"
6. Copy your `API ID` (a number) and `API Hash` (a string)

### Step 3: Setup MongoDB Database

#### Option A: MongoDB Atlas (Free Cloud Database)

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Sign up for a free account
3. Create a new cluster (select the free M0 tier)
4. Wait for the cluster to be created (takes 3-5 minutes)
5. Click "Connect" button
6. Add your current IP address or use `0.0.0.0/0` for access from anywhere
7. Create a database user with username and password
8. Choose "Connect your application"
9. Copy the connection string (looks like: `mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`)
10. Replace `<password>` with your database password

#### Option B: Local MongoDB

```bash
# Install MongoDB on Ubuntu/Debian
sudo apt-get install mongodb

# Start MongoDB service
sudo systemctl start mongodb

# Your connection string will be:
mongodb://localhost:27017/
```

### Step 4: Get Your Telegram User ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start the bot and it will show your user ID
3. Copy this ID (it's a number, e.g., 123456789)

### Step 5: Setup Premium Logs Channel (Optional)

1. Create a new Telegram channel
2. Add your bot as admin to the channel
3. Get the channel ID:
   - Forward any message from the channel to [@userinfobot](https://t.me/userinfobot)
   - Copy the channel ID (it will be negative, e.g., -1001234567890)

### Step 6: Install the Bot

#### For VPS/Server:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3 and pip
sudo apt-get install python3 python3-pip -y

# Install git (if not installed)
sudo apt-get install git -y

# Create a directory for the bot
mkdir ~/rename_bot
cd ~/rename_bot

# Copy all bot files to this directory
# Then install requirements
pip3 install -r requirements.txt
```

#### For Local Computer:

```bash
# Make sure Python 3.8+ is installed
python --version

# Navigate to bot directory
cd path/to/rename_bot

# Install requirements
pip install -r requirements.txt
```

### Step 7: Configure the Bot

1. Create a `.env` file in the bot directory:

```bash
nano .env
```

2. Add your configuration (replace with your actual values):

```env
# Bot Configuration
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890

# Database
MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority

# Admin User IDs (space separated, can add multiple)
ADMINS=123456789 987654321

# Premium Logs Channel ID (optional, set to 0 if not using)
PREMIUM_LOGS=-1001234567890
```

3. Save the file:
   - Press `Ctrl + X`
   - Press `Y`
   - Press `Enter`

### Step 8: Run the Bot

#### For Testing:

```bash
python3 main.py
```

#### For Production (Using Screen):

```bash
# Install screen
sudo apt-get install screen -y

# Create a new screen session
screen -S renamebot

# Run the bot
python3 main.py

# Detach from screen (bot will keep running)
# Press Ctrl + A, then D

# To re-attach to the screen later:
screen -r renamebot
```

#### For Production (Using PM2):

```bash
# Install Node.js and npm
sudo apt-get install nodejs npm -y

# Install PM2
sudo npm install -g pm2

# Start the bot with PM2
pm2 start main.py --name renamebot --interpreter python3

# Make PM2 start on system boot
pm2 startup
pm2 save

# View logs
pm2 logs renamebot

# Stop the bot
pm2 stop renamebot

# Restart the bot
pm2 restart renamebot
```

### Step 9: Test the Bot

1. Open Telegram and search for your bot username
2. Start the bot with `/start` command
3. You should see the welcome message with animation
4. Try sending a file to test renaming

### Step 10: Deploy to Heroku (Optional)

1. Create a Heroku account at https://heroku.com
2. Install Heroku CLI
3. Run these commands:

```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set MONGODB_URL=your_mongodb_url
heroku config:set ADMINS=your_user_id
heroku config:set PREMIUM_LOGS=0

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku master

# Scale the worker
heroku ps:scale worker=1
```

## Troubleshooting

### Bot doesn't respond
- Check if the bot is running
- Verify BOT_TOKEN is correct
- Check MongoDB connection

### File upload fails
- Check file size limits
- Verify user has premium if file > 2GB
- Check server disk space

### Force subscribe not working
- Make sure bot is admin in the channels
- Verify channel usernames in config.py

### Database errors
- Check MongoDB connection string
- Verify database user has read/write permissions
- Check if MongoDB service is running

## Admin Commands Usage

### Add Premium to User
```
/add_premium 123456789 1 month
/add_premium 123456789 3 months
/add_premium 123456789 1 year
```

### Broadcast Message
1. Reply to a message with `/broadcast`
2. Choose whether to pin the message

### Check Premium Users
```
/premium_users
```

## Support

If you face any issues, contact [@Venuboyy](https://t.me/Venuboyy)
