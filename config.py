import os

def get_config():
    config = {
        'api_key': os.getenv('API_KEY'),
        'from_email': os.getenv('FROM_EMAIL'),
        'from_password': os.getenv('FROM_PASSWORD'),
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', 587))
    }
    
    for key, value in config.items():
        if value is None:
            raise EnvironmentError(f"Environment variable {key.upper()} not defined.")
    
    return config
