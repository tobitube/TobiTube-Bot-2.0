from flask import Flask, request, send_file, Response, abort
from pymongo import MongoClient
from pyrogram import Client
import os
import logging
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
MONGO_URI = os.getenv('MONGO_URI')
BASE_URL = os.getenv('BASE_URL')

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.file_bot
files_collection = db.files

# Initialize Pyrogram client for file downloads
telegram_client = Client(
    "file_downloader",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    no_updates=True
)

@app.route('/')
def home():
    return {
        "status": "online",
        "service": "Telegram File Bot",
        "endpoints": {
            "download": "/download/<unique_key>"
        }
    }

@app.route('/download/<unique_key>')
async def download_file(unique_key):
    """Handle file downloads"""
    try:
        # Find file in database
        file_data = files_collection.find_one({"unique_key": unique_key})
        
        if not file_data:
            abort(404, description="File not found")
        
        file_id = file_data['file_id']
        file_name = file_data['file_name']
        file_type = file_data['file_type']
        
        # Start Telegram client if not already running
        if not telegram_client.is_connected:
            await telegram_client.start()
        
        # Download file from Telegram
        download_path = await telegram_client.download_media(file_id, in_memory=True)
        
        if not download_path:
            abort(404, description="File not found on Telegram")
        
        # Determine MIME type
        mime_types = {
            "document": "application/octet-stream",
            "video": "video/mp4",
            "audio": "audio/mpeg",
            "photo": "image/jpeg"
        }
        
        mime_type = mime_types.get(file_type, "application/octet-stream")
        
        # Create response
        if isinstance(download_path, bytes):
            file_data_bytes = download_path
        else:
            with open(download_path, 'rb') as f:
                file_data_bytes = f.read()
        
        response = Response(
            file_data_bytes,
            mimetype=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={file_name}",
                "Content-Type": mime_type
            }
        )
        
        logger.info(f"File downloaded: {file_name} via key: {unique_key}")
        return response
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        abort(500, description="Internal server error")

@app.route('/health')
def health_check():
    return {"status": "healthy"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
