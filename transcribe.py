#!/usr/bin/env python3
"""
Script para transcrever arquivos de áudio usando a API
"""
import requests
import sys
import os
import json

def transcribe_audio(file_path, language=None, api_url="http://localhost:8484/transcribe"):
    """
    Transcreve um arquivo de áudio
    
    Args:
        file_path: Caminho para o arquivo de áudio
        language: Código do idioma (opcional, ex: 'pt', 'en', 'es')
        api_url: URL da API de transcrição
    """
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo não encontrado: {file_path}")
        return None
    
    print(f"Transcrevendo: {file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {}
        
        if language:
            data['language'] = language
        
        try:
            response = requests.post(api_url, files=files, data=data)
            response.raise_for_status()
            
            result = response.json()
            
            print("\n" + "="*60)
            print("TRANSCRIÇÃO CONCLUÍDA")
            print("="*60)
            print(f"\nIdioma detectado: {result.get('language', 'unknown')}")
            print(f"\nTexto transcrito:\n")
            print(result['text'])
            print("\n" + "="*60)
            
            # Salvar resultado em arquivo JSON
            output_file = os.path.splitext(file_path)[0] + "_transcription.json"
            with open(output_file, 'w', encoding='utf-8') as out:
                json.dump(result, out, indent=2, ensure_ascii=False)
            print(f"\nResultado completo salvo em: {output_file}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer requisição: {e}")
            if hasattr(e.response, 'text'):
                print(f"Resposta do servidor: {e.response.text}")
            return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python transcribe.py <arquivo_audio> [idioma]")
        print("Exemplo: python transcribe.py audio.mp3 en")
        print("Exemplo: python transcribe.py audio.mp3 pt")
        sys.exit(1)
    
    file_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else None
    
    transcribe_audio(file_path, language)

