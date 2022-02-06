from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from config import config as config_bot
from database.accessor import PostgresAccessor
from database.models import db

config = context.config
fileConfig(config.config_file_name)
target_metadata = db


def run_migrations_online():
    # Alembic видит только те модели, которые импортированы в момент генерации миграции.
    # PostgresAccessor инстанцируется и импортит все нужные модели, тем самым позволяя автогенерировать миграции
    PostgresAccessor()
    connectable = create_engine(config_bot["database_url"])
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()