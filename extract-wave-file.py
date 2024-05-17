import subprocess

# Caminho do vídeo original
video_path = "C:/py-projects/whisper-transcription/files/RationalTeamConcert_CCM.mp4"
# Caminho para salvar o áudio extraído
audio_path = "C:/py-projects/whisper-transcription/files/RationalTeamConcert_CCM_audio.wav"

# Comando FFmpeg para extrair os primeiros 60 segundos de áudio
subprocess.run([
    "ffmpeg", "-i", video_path, "-t", "60", "-q:a", "0", "-map", "a", audio_path
])
