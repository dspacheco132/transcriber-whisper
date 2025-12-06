# Transcriber - Voice to Text Transcription API

REST API developed in Python using FastAPI and OpenAI Whisper for audio-to-text transcription.

## 🚀 Features

- Transcribes audio to text using Whisper models
- Supports multiple audio formats (mp3, wav, m4a, flac, ogg, webm, etc.)
- Simple and easy-to-use REST API
- Containerized with Docker
- Automatic language detection or manual specification
- Supports transcription and translation

## 📋 Requirements

- Docker and Docker Compose installed
- (Optional) Python 3.11+ if you want to run locally

## 🛠️ Installation and Usage

### Using Docker Compose (Recommended)

1. Clone or navigate to the project directory:
```bash
cd transcriber
```

2. Build and start the container:
```bash
docker compose up --build
```

3. The API will be available at `http://localhost:8484`

### Using Docker directly

1. Build the image:
```bash
docker build -t transcriber .
```

2. Run the container:
```bash
docker run -p 8484:8484 -e WHISPER_MODEL=base transcriber
```

### Running locally (without Docker)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have FFmpeg installed:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

3. Run the application:
```bash
python app.py
```

## 📖 API Usage

### Endpoints

#### GET `/`
Returns information about the API and available endpoints.

#### GET `/health`
Checks the API status and whether the model is loaded.

#### POST `/transcribe`
Transcribes an audio file to text.

**Parameters:**
- `file` (required): Audio file to transcribe
- `language` (optional): Language code (e.g., 'pt', 'en', 'es'). If not specified, the model detects automatically.
- `task` (optional): 'transcribe' (default) or 'translate' (translates to English)

**Example using curl:**
```bash
curl -X POST "http://localhost:8484/transcribe" \
  -F "file=@your_file.mp3" \
  -F "language=pt"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8484/transcribe"
files = {"file": open("audio.mp3", "rb")}
data = {"language": "pt"}

response = requests.post(url, files=files, data=data)
result = response.json()
print(result["text"])
```

#### POST `/transcribe-url`
Transcribes an audio file from a URL (useful for Telegram, N8N, etc.).

**Parameters (JSON body):**
- `url` (required): URL of the audio file
- `language` (optional): Language code (e.g., 'pt', 'en', 'es')
- `task` (optional): 'transcribe' (default) or 'translate'

**Example using curl:**
```bash
curl -X POST "http://localhost:8484/transcribe-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.telegram.org/file/botTOKEN/path/to/file.ogg", "language": "pt"}'
```

**Example response:**
```json
{
  "text": "Hello, this is an example of audio transcription.",
  "language": "en",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "Hello, this is an example of audio transcription."
    }
  ],
  "url": "https://api.telegram.org/file/botTOKEN/path/to/file.ogg"
}
```

## ⚙️ Configuration

### Whisper Models

You can choose different Whisper models by changing the `WHISPER_MODEL` environment variable:

- `tiny`: Fastest, less accurate (~39M parameters)
- `base`: Balance between speed and accuracy (~74M parameters) - **default**
- `small`: Better accuracy (~244M parameters)
- `medium`: High accuracy (~769M parameters)
- `large`: Maximum accuracy (~1550M parameters)

**Example in docker-compose.yml:**
```yaml
environment:
  - WHISPER_MODEL=small
```

**Note:** Larger models are more accurate but require more memory and are slower.

## 🔗 Integrations

### N8N and Telegram

This API can be easily integrated with N8N workflows to transcribe audio messages from Telegram.

**Quick start:**
1. **Create Telegram Bot**: See [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md) for step-by-step instructions
2. **Import workflow**: Import `n8n-workflow.json` into N8N
3. **Configure**: See [N8N_WORKFLOW_SETUP.md](N8N_WORKFLOW_SETUP.md) for import and configuration instructions
4. **Advanced**: For detailed integration guide, see [N8N_INTEGRATION.md](N8N_INTEGRATION.md)

**Manual setup:**
1. Configure Telegram trigger in N8N
2. Get file URL from Telegram API
3. Call `/transcribe-url` endpoint with the file URL
4. Send transcription result back to Telegram

## 📁 Project Structure

```
transcriber/
├── app.py                  # Main FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Files ignored in Docker build
├── n8n-workflow.json       # Ready-to-use N8N workflow
├── TELEGRAM_BOT_SETUP.md   # How to create and configure Telegram bot
├── N8N_WORKFLOW_SETUP.md   # N8N workflow setup guide
├── N8N_INTEGRATION.md      # N8N and Telegram integration guide
└── README.md               # This file
```

## 🔧 Troubleshooting

### Error loading model
- Check if there is enough disk space (models can be large)
- Try using a smaller model (e.g., `tiny` or `base`)

### Error processing audio file
- Check if the file format is supported
- Make sure the file is not corrupted

### Container won't start
- Check logs: `docker compose logs`
- Make sure port 8484 is not in use

## 📝 Notes

- The first model load may take a few minutes
- Large audio files may take longer to process
- The API temporarily saves files during processing and removes them automatically

## 📄 License

This project uses OpenAI's Whisper model, which is open-source.
