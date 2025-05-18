import subprocess
from pathlib import Path
from PIL import Image
from datetime import datetime
import shutil
import logging
from typing import Optional, Callable, Awaitable

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class MediaProcessor:
    def __init__(self, base_temp_dir: Optional[str] = None):
        if base_temp_dir is None:
            from stickers.config import load_config
            config = load_config()
            base_temp_dir = str(config.media.temp_media_dir)

        self.base_temp_dir = Path(base_temp_dir)
        self.base_temp_dir.mkdir(parents=True, exist_ok=True)

    async def crop_image_to_tiles(
            self,
            image_path: str,
            total_width: int,
            total_height: int,
            progress_callback: Optional[Callable[[int, int, int, int], Awaitable[None]]] = None
    ) -> str:
        try:
            image = Image.open(image_path).convert("RGBA")
            resized = image.resize((total_width, total_height), resample=Image.Resampling.LANCZOS)

            tile_size = 100
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder = self.base_temp_dir / f"input_img_{timestamp}"
            folder.mkdir(exist_ok=True)

            index = 0
            total_tiles = (total_width // tile_size) * (total_height // tile_size)

            for y in range(0, total_height, tile_size):
                for x in range(0, total_width, tile_size):
                    tile = resized.crop((x, y, x + tile_size, y + tile_size))
                    tile_path = folder / f"tile_{index:03}.png"
                    tile.save(tile_path)

                    if progress_callback:
                        await progress_callback(index + 1, total_tiles, 0, 1)

                    index += 1

            logging.info(f"Фото нарезано в папку: {folder}")
            return str(folder)

        except Exception as e:
            logging.error(f"Ошибка в crop_image_to_tiles: {e}")
            raise

    async def crop_video_to_webm_tiles(
        self,
        video_path: str,
        total_width: int,
        total_height: int,
        progress_callback: Optional[Callable[[int, int, int, int], Awaitable[None]]] = None
    ) -> str:
        tile_size = 100
        output_dir = self.base_temp_dir / f"webm_{Path(video_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir.mkdir(parents=True, exist_ok=True)

        resized_path = output_dir / "resized_temp.mp4"

        speedup_cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", f"scale={total_width}:{total_height},setpts=PTS*0.1",
            "-an",
            "-t", "3",
            str(resized_path)
        ]
        subprocess.run(speedup_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        rows = total_height // tile_size
        cols = total_width // tile_size
        total_tiles = rows * cols
        count = 0

        for row in range(rows):
            for col in range(cols):
                x = col * tile_size
                y = row * tile_size
                out_path = output_dir / f"tile_{count:03}.webm"

                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(resized_path),
                    "-vf", f"crop={tile_size}:{tile_size}:{x}:{y}",
                    "-c:v", "libvpx-vp9",
                    "-b:v", "140k",
                    "-crf", "32",
                    "-deadline", "realtime",
                    "-cpu-used", "5",
                    "-an",
                    str(out_path)
                ]

                logging.info(f"🎬 Рендеринг: {out_path.name}")
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                size_kb = out_path.stat().st_size / 1024
                if size_kb > 64:
                    logging.warning(f"⚠️ {out_path.name} превышает 64 KB ({size_kb:.1f} KB)")

                if progress_callback:
                    await progress_callback(count + 1, total_tiles, count + 1, 1)
                count += 1

        return str(output_dir)

    def cleanup_media(self, folder_path: str):
        try:
            folder = Path(folder_path)
            if folder.exists() and folder.is_dir():
                shutil.rmtree(folder)
                logging.info(f"Временная папка {folder} удалена")
        except Exception as e:
            logging.error(f"Ошибка удаления папки {folder_path}: {e}")