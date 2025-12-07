
import requests

def upload(file_path: str, time: str = "24h"):
    with open(file_path, "rb") as f:
        res = requests.post(
            "https://litterbox.catbox.moe/resources/internals/api.php",
            data={"reqtype": "fileupload", "time": time},
            files={"fileToUpload": f},
        )
    if res.status_code != 200:
        raise Exception(f"Litterbox error {res.status_code}: {res.text}")
    return res.text.strip()
