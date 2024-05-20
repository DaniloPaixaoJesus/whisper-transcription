import requests

def download_video(url, video_path):
    """Downloads a video from a URL."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(video_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
    else:
        raise Exception(f"Failed to download video from {url}")
