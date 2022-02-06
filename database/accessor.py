from config import config
from database.models import db
class PostgresAccessor:
    def __init__(self) -> None:
        self.config = config
        self.db = None

    async def _on_connect(self):
        await db.set_bind(self.config["database_url"])
        self.db = db

    async def _on_disconnect(self) -> None:
        if self.db is not None:
            await self.db.pop_bind().close()