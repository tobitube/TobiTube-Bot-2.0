import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
import secrets
import string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BIN_CHANNEL_ID = int(os.getenv('BIN_CHANNEL_ID'))
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))
MONGO_URI = os.getenv('MONGO_URI')
BASE_URL = os.getenv('BASE_URL')

# Initialize MongoDB client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.file_bot
files_collection = db.files

# Create Pyrogram client
app = Client(
    "file_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def generate_unique_key(length=12):
    """Generate a unique key for the file"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_USER_ID

@app.on_message(filters.private & filters.command("start"))
async def start_command(client, message: Message):
    """Handle /start command"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized access. This bot is private.")
        return
    
    await message.reply_text(
        "🤖 **Admin File Bot**\n\n"
        "Send me any file and I'll generate a permanent download link for it.\n\n"
        "**Supported files:** Documents, Videos, Audio, Photos"
    )

@app.on_message(filters.private & filters.document | filters.video | filters.audio | filters.photo)
async def handle_file_upload(client, message: Message):
    """Handle file uploads from admin"""
    
    # Check if user is admin
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized access. This bot is private.")
        return
    
    try:
        # Generate unique key
        unique_key = generate_unique_key()
        
        # Forward file to bin channel
        if message.document:
            file_attr = message.document
            file_type = "document"
        elif message.video:
            file_attr = message.video
            file_type = "video"
        elif message.audio:
            file_attr = message.audio
            file_type = "audio"
        elif message.photo:
            file_attr = message.photo
            file_type = "photo"
        else:
            await message.reply_text("❌ Unsupported file type.")
            return
        
        # Get file info
        file_id = file_attr.file_id
        file_name = getattr(file_attr, 'file_name', f'{unique_key}.{file_type}')
        file_size = file_attr.file_size
        
        # Forward to bin channel
        forwarded_msg = await message.forward(BIN_CHANNEL_ID)
        
        # Store in MongoDB
        file_data = {
            "unique_key": unique_key,
            "file_id": file_id,
            "message_id": forwarded_msg.id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,
            "admin_id": ADMIN_USER_ID,
            "timestamp": message.date
        }
        
        files_collection.insert_one(file_data)
        
        # Generate download link
        download_link = f"{BASE_URL}/download/{unique_key}"
        
        # Send confirmation to admin
        await message.reply_text(
            f"✅ **File uploaded successfully!**\n\n"
            f"📁 **File:** {file_name}\n"
            f"📊 **Size:** {file_size} bytes\n"
            f"🔗 **Download Link:**\n`{download_link}`\n\n"
            f"**Share this link for public access.**"
        )
        
        logger.info(f"File uploaded: {file_name} -> Key: {unique_key}")
        
    except Exception as e:
        logger.error(f"Error handling file upload: {e}")
        await message.reply_text("❌ Error processing file. Please try again.")

@app.on_message(filters.private)
async def handle_other_messages(client, message: Message):
    """Handle other messages"""
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ Unauthorized access. This bot is private.")
        return
    
    await message.reply_text(
        "Please send a file (document, video, audio, or photo) to generate a download link."
    )

if __name__ == "__main__":
    logger.info("Starting Telegram File Bot...")
    app.run()
