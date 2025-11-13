# Private Telegram File Bot

A private Telegram bot that generates permanent download links for files.

## Features
- Admin-only file uploads
- Automatic forwarding to private channel
- Permanent download links
- MongoDB storage
- Render deployment

## Setup Instructions

1. **Create Telegram Bot**
   - Message @BotFather on Telegram
   - Create new bot and get `BOT_TOKEN`

2. **Get API Credentials**
   - Visit https://my.telegram.org
   - Create application and get `API_ID` & `API_HASH`

3. **Create Private Channel**
   - Create Telegram channel
   - Add bot as admin
   - Get `BIN_CHANNEL_ID` (add -100 prefix)

4. **Get Your User ID**
   - Message @userinfobot on Telegram
   - Get your `ADMIN_USER_ID`

5. **MongoDB Database**
   - Create MongoDB database (MongoDB Atlas recommended)
   - Get `MONGO_URI`

6. **Deploy to Render**
   - Fork this repository
   - Connect GitHub to Render
   - Set all environment variables
   - Deploy

## Environment Variables
- `BOT_TOKEN`: Telegram bot token
- `API_ID`: Telegram API ID
- `API_HASH`: Telegram API hash
- `BIN_CHANNEL_ID`: Private channel ID
- `ADMIN_USER_ID`: Your Telegram user ID
- `MONGO_URI`: MongoDB connection string
- `BASE_URL`: Your Render app URL

## Usage
1. Start your bot on Telegram
2. Send any file to the bot
3. Receive permanent download link
4. Share link publicly
