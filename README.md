# Transcrição e Resumo de Vídeos com Whisper e ChatGPT

Este projeto tem como objetivo extrair o áudio de um vídeo, transcrever o áudio em texto utilizando o modelo Whisper, e gerar uma versão resumida do texto transcrito usando a API do OpenAI (ChatGPT). O texto transcrito e o resumo são salvos em arquivos separados.

## Descrição

- **Transcrição**: Utiliza o modelo Whisper para converter o áudio do vídeo em texto.
- **Resumo**: Usa a API do OpenAI para resumir o texto transcrito.

## Instalação

### Pré-requisitos

- Python 3.6 ou superior
- FFmpeg instalado e configurado no PATH do sistema


### Dependências necessárias
- openai
- whisper


### Passos de Instalação

- pip install -r requirements.txt
- python -m venv venv
source venv/bin/activate  # No Windows, use: venv\Scripts\activate

### Execucao
linux - python main.py some-token-open-api-code
win - py main.py some-token-open-api-code

### Bibliotecas Utilizadas
 - subprocess: Usada para chamar comandos do sistema (neste caso, para executar o FFmpeg).
 - whisper: Biblioteca usada para carregar e usar o modelo Whisper para transcrição de áudio.
 - os: Usada para manipulação de caminhos de arquivos e remoção de arquivos temporários.
 - openai: Biblioteca da OpenAI usada para interagir com a API do ChatGPT e gerar resumos.

### Motivo do Uso das Bibliotecas
 - subprocess: Necessária para executar comandos do sistema diretamente do script Python, como a extração de áudio com o FFmpeg.
 - whisper: Fornece os modelos de transcrição de áudio de última geração da OpenAI, facilitando a conversão de áudio em texto.
 - os: Permite manipulações de sistema de arquivos, como salvar e remover arquivos.
 - openai: Permite a integração com a API da OpenAI, facilitando a geração de resumos do texto transcrito usando o modelo GPT-3.5.