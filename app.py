from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import whisper
import tempfile
import os
from typing import Optional
import httpx
from pydantic import BaseModel

app = FastAPI(title="Transcriber API", description="API para transcrição de voz para texto")

# Carregar o modelo Whisper (pode ser: tiny, base, small, medium, large)
model = None

def load_model(model_name: str = "base"):
    """Carrega o modelo Whisper"""
    global model
    if model is None:
        print(f"Carregando modelo Whisper: {model_name}")
        model = whisper.load_model(model_name)
        print("Modelo carregado com sucesso!")
    return model

@app.on_event("startup")
async def startup_event():
    """Carrega o modelo na inicialização"""
    model_name = os.getenv("WHISPER_MODEL", "base")
    load_model(model_name)

class TranscribeURLRequest(BaseModel):
    url: str
    language: Optional[str] = None
    task: str = "transcribe"

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "API de Transcrição de Voz para Texto",
        "endpoints": {
            "transcribe": "/transcribe (POST) - Envie um arquivo de áudio",
            "transcribe-url": "/transcribe-url (POST) - Envie uma URL de arquivo de áudio",
            "health": "/health (GET) - Status da API"
        }
    }

@app.get("/health")
async def health():
    """Verifica o status da API"""
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    task: str = "transcribe"
):
    """
    Transcreve um arquivo de áudio para texto
    
    Args:
        file: Arquivo de áudio (suporta: mp3, wav, m4a, flac, etc.)
        language: Código do idioma (opcional, ex: 'pt', 'en', 'es')
        task: 'transcribe' ou 'translate' (padrão: 'transcribe')
    
    Returns:
        JSON com o texto transcrito e informações adicionais
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado")
    
    # Validar tipo de arquivo
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm', '.mp4', '.mpeg', '.mpga', '.wma'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de arquivo não suportado. Formatos permitidos: {', '.join(allowed_extensions)}"
        )
    
    # Salvar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        try:
            # Salvar conteúdo do arquivo
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
            # Transcrever áudio
            print(f"Transcrevendo arquivo: {file.filename}")
            
            transcribe_options = {
                "task": task,
                "verbose": False
            }
            
            if language:
                transcribe_options["language"] = language
            
            result = model.transcribe(tmp_file_path, **transcribe_options)
            
            return JSONResponse({
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "segments": [
                    {
                        "id": seg.get("id"),
                        "start": seg.get("start"),
                        "end": seg.get("end"),
                        "text": seg.get("text")
                    }
                    for seg in result.get("segments", [])
                ],
                "filename": file.filename
            })
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao transcrever áudio: {str(e)}")
        
        finally:
            # Remover arquivo temporário
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

@app.post("/transcribe-url")
async def transcribe_audio_from_url(request: TranscribeURLRequest):
    """
    Transcreve um arquivo de áudio a partir de uma URL (útil para Telegram, etc.)
    
    Args:
        url: URL do arquivo de áudio
        language: Código do idioma (opcional, ex: 'pt', 'en', 'es')
        task: 'transcribe' ou 'translate' (padrão: 'transcribe')
    
    Returns:
        JSON com o texto transcrito e informações adicionais
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado")
    
    # Baixar arquivo da URL
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.get(request.url)
            response.raise_for_status()
            file_content = response.content
            
            # Detectar extensão do arquivo
            content_type = response.headers.get("content-type", "")
            file_ext = None
            
            # Tentar detectar extensão pela URL
            url_lower = request.url.lower()
            for ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm', '.mp4', '.mpeg', '.mpga', '.wma']:
                if ext in url_lower:
                    file_ext = ext
                    break
            
            # Se não encontrou na URL, tentar pelo content-type
            if not file_ext:
                content_type_map = {
                    'audio/mpeg': '.mp3',
                    'audio/wav': '.wav',
                    'audio/x-m4a': '.m4a',
                    'audio/flac': '.flac',
                    'audio/ogg': '.ogg',
                    'audio/webm': '.webm',
                    'audio/mp4': '.m4a',
                }
                file_ext = content_type_map.get(content_type, '.mp3')  # default para mp3
            
            # Validar tipo de arquivo
            allowed_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm', '.mp4', '.mpeg', '.mpga', '.wma'}
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de arquivo não suportado. Formatos permitidos: {', '.join(allowed_extensions)}"
                )
            
            # Salvar arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            # Transcrever áudio
            print(f"Transcrevendo arquivo da URL: {request.url}")
            
            transcribe_options = {
                "task": request.task,
                "verbose": False
            }
            
            if request.language:
                transcribe_options["language"] = request.language
            
            result = model.transcribe(tmp_file_path, **transcribe_options)
            
            # Remover arquivo temporário
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            
            return JSONResponse({
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "segments": [
                    {
                        "id": seg.get("id"),
                        "start": seg.get("start"),
                        "end": seg.get("end"),
                        "text": seg.get("text")
                    }
                    for seg in result.get("segments", [])
                ],
                "url": request.url
            })
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Erro ao baixar arquivo da URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao transcrever áudio: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8484))
    uvicorn.run(app, host="0.0.0.0", port=port)

