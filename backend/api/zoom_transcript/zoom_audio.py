import requests

def download_zoom_audio(download_url, token, out_file):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(download_url)
    with open(out_file, "wb") as f:
        f.write(r.content)
