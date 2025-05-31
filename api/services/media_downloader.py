import os
import logging
import requests

from pathlib import Path
from datetime import datetime

from ..config import load_config

class MediaDownloader:
    def __init__(self, base_dir: str = "/tmp/media"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Загружаем конфиг
        self.config = load_config()
        self.bot_token = self.config.telegram_api.token
        self.api_url = f"https://api.telegram.org/file/bot{self.bot_token}"

    async def download(self, file_id: str) -> str:
        """
        Скачивает файл по file_id через Telegram Bot API
        """
        logging.info(f"[MediaDownloader] Запрос file_path по file_id={file_id}...")

        # Получаем путь к файлу от Telegram
        resp = requests.get(
            f"https://api.telegram.org/bot{self.bot_token}/getFile",
            params={"file_id": file_id},
            timeout=10
        )
        if not resp.ok or "result" not in resp.json():
            raise RuntimeError(f"Не удалось получить file_path: {resp.text}")

        file_path = resp.json()["result"]["file_path"]
        download_url = f"{self.api_url}/{file_path}"

        extension = Path(file_path).suffix or ".bin"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.base_dir / f"{file_id}_{timestamp}{extension}"

        logging.info(f"[MediaDownloader] Скачивание файла с {download_url}")

        response = requests.get(download_url, stream=True, timeout=20)
        if not response.ok:
            raise RuntimeError(f"Ошибка при скачивании файла: {response.status_code}")

        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logging.info(f"[MediaDownloader] Успешно скачано: {output_file}")
        return str(output_file)

    def cleanup(self, path: str):
        try:
            os.remove(path)
            logging.info(f"[MediaDownloader] Удалён временный файл: {path}")
        except Exception as e:
            logging.warning(f"[MediaDownloader] Ошибка удаления: {e}")