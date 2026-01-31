# 4GB File Renamer Telegram Bot

A powerful Telegram bot to rename files up to 4GB with premium subscription features.

## Features

### Free Users (2GB Limit)
- ✅ Rename files up to 2GB
- ✅ Custom thumbnail support
- ✅ Upload as document or video
- ✅ Fast and secure

### Premium Users (4GB Limit)
- ✅ Rename files up to 4GB
- ✅ All free features
- ✅ Priority processing
- ✅ No ads

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- MongoDB database
- Telegram Bot Token
- Telegram API ID and API Hash

### 2. Installation

```bash
# Clone or download the repository
cd rename_bot

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:
```env
BOT_TOKEN=your_bot_token_from_botfather
API_ID=your_api_id_from_my.telegram.org
API_HASH=your_api_hash_from_my.telegram.org
MONGODB_URL=your_mongodb_connection_string
ADMINS=your_telegram_user_id
PREMIUM_LOGS=channel_id_for_premium_logs (optional)
```

### 4. Getting Required Credentials

#### Bot Token
1. Go to [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Follow the instructions
4. Copy the bot token

#### API ID and API Hash
1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click on "API Development Tools"
4. Create a new application
5. Copy API ID and API Hash

#### MongoDB URL
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get the connection string
4. Replace `<password>` with your database password

### 5. Running the Bot

```bash
python main.py
```

## Bot Commands

### User Commands
- `/start` - Start the bot
- `/help` - Get help
- `/about` - About the bot
- `/plan` - View premium plans
- `/myplan` - Check your current plan
- `/addthumb` - Add custom thumbnail
- `/viewthumb` - View your thumbnail
- `/deletethumb` - Delete your thumbnail

### Admin Commands
- `/add_premium <user_id> <time>` - Add premium to a user
  - Example: `/add_premium 123456789 1 month`
- `/remove_premium <user_id>` - Remove premium from a user
- `/get_premium <user_id>` - Get premium details of a user
- `/premium_users` - List all premium users
- `/broadcast` - Broadcast message to all users
- `/grp_broadcast` - Broadcast message to all groups
- `/clear_junk` - Remove inactive users
- `/clear_junk_group` - Remove inactive groups

## Premium Subscription

Users can purchase premium using Telegram Stars:

- **1 Month** - 50⭐
- **3 Months** - 150⭐
- **6 Months** - 250⭐
- **1 Year** - 450⭐

## Force Subscribe Channels

The bot requires users to join these channels:
- [@zerodev2](https://t.me/zerodev2)
- [@mvxyoffcail](https://t.me/mvxyoffcail)

You can modify these in `config.py`.

## File Structure

```
rename_bot/
├── main.py                 # Main bot file
├── config.py              # Configuration
├── database.py            # Database operations
├── script.py              # Bot messages
├── utils.py               # Helper functions
├── requirements.txt       # Dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── plugins/              # Plugin modules
    ├── start.py          # Start command & callbacks
    ├── rename.py         # File renaming
    ├── thumbnail.py      # Thumbnail management
    ├── premium.py        # Premium features
    └── broadcast.py      # Admin broadcast
```

## Developer

**ZeroDev** - [@Venuboyy](https://t.me/Venuboyy)

## Credits

- Built with [Pyrogram](https://docs.pyrogram.org/)
- Database: [MongoDB](https://www.mongodb.com/)

## Support

For support, contact [@Venuboyy](https://t.me/Venuboyy)

## License

This project is for educational purposes only.
