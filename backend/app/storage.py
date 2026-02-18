import os
from pathlib import Path

import aiofiles

from app.config import settings


class LocalStorage:
    def __init__(self, base_path: str = "/app/uploads"):
        self.base_path = Path(base_path)

    async def upload(self, key: str, data: bytes) -> str:
        file_path = self.base_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)
        return str(file_path)

    async def delete(self, key: str) -> None:
        file_path = self.base_path / key
        if file_path.exists():
            os.remove(file_path)


def get_storage() -> LocalStorage:
    return LocalStorage()
