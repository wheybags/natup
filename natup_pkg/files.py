import requests
import shutil


def get(url: str, save_path: str):
    if url.startswith("file://"):
        shutil.copyfile(url[len("file://"):], save_path)
    else:
        r = requests.get(url, stream=True)
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
