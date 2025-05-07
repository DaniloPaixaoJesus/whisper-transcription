# Whisper Transcription

Whisper Transcription é uma aplicação em Python com FastAPI que permite **transcrever áudios a partir de vídeos enviados via upload**. A transcrição é processada em **segundo plano** e armazenada localmente na pasta `src/results`.

## ✅ Funcionalidades

- Upload de arquivos de vídeo para transcrição
- Extração de áudio com FFmpeg
- Transcrição automática usando OpenAI Whisper
- Processamento assíncrono (retorna HTTP 202 Accepted)
- Geração do arquivo `.txt` com o conteúdo transcrito
- Código simples, sem dependência de mensageria ou serviços externos

---

## 📁 Estrutura Atual do Projeto

```
whisper-transcription/
├── src/
│   ├── controllers/             # Endpoints da API (FastAPI)
│   ├── services/                # Lógica de transcrição e utilitários
│   ├── main_uvicorn.py         # Inicialização do FastAPI
│   └── tmp/                    # Arquivos temporários
│   └── results/                # Resultados das transcrições geradas
├── requirements.txt            # Dependências do projeto
├── Dockerfile                  # Docker da aplicação
├── docker-compose.yml          # Orquestração do container
└── README.md                   # Este documento
```

---

## 🚀 Como Executar

### Pré-requisitos

- Docker + Docker Compose
- Python 3.9+ (caso deseje rodar fora do container)
- FFmpeg instalado no container (já incluso no Dockerfile)

### Subindo com Docker

```bash
docker-compose up --build
```

A aplicação ficará acessível em:  
📡 `http://localhost:8000`

---

## 🧪 Como Testar

### Via `curl` (linha de comando)

```bash
curl --location 'http://localhost:8000/transcription/upload' \
--form 'file=@"caminho/do/seu/video.mp4"'
```

📨 A resposta será:

```json
{
  "message": "Arquivo recebido. A transcrição será processada em segundo plano."
}
```

📂 Após o processamento, o arquivo `.txt` estará em:

```
src/results/NOME_DO_VIDEO_transcription_UUID.txt
```

---

## 📦 Instalação manual (sem Docker)

> Recomendado apenas para testes locais

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main_uvicorn:app --reload
```

---

## ❌ O que foi removido

- Integração com AWS (S3, SNS, SQS)
- Dependência do LocalStack
- Envio de e-mail com links
- Resumo com GPT-4

---

## ✨ To Do (opcional)

- Adicionar barra de progresso
- Interface web com upload
- Persistência em banco (SQLite ou Mongo)
- Monitoramento do status das transcrições

---

## 📄 Licença

Este projeto é livre para fins educacionais e pode ser customizado à vontade.
