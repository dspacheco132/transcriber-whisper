from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import whisper
import tempfile
import os
from typing import Optional

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

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "API de Transcrição de Voz para Texto",
        "endpoints": {
            "transcribe": "/transcribe (POST) - Envie um arquivo de áudio",
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8484))
    uvicorn.run(app, host="0.0.0.0", port=port)

