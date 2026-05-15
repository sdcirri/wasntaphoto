from alembic.config import Config
from alembic import command
from subprocess import run
from pathlib import Path
from time import sleep
import uvicorn

import os

os.environ['DATABASE_URL'] = 'postgresql+psycopg://wasntaphoto:wasntaphoto@localhost/wasntaphoto'
os.environ['DATABASE_URL_MIGRATIONS'] = 'postgresql+psycopg://wasntaphoto:wasntaphoto@localhost/wasntaphoto'
os.environ['WASA_STORAGE_ROOT'] = '/tmp/wasntaphoto'

from app import app


def start_demo_db() -> None:
    # capture_output=True hides annoying output from Docker
    run([
        'docker', 'run', '-d',
        '--name', 'wasntaphoto-dev-db',
        '-e', 'POSTGRES_USER=wasntaphoto',
        '-e', 'POSTGRES_PASSWORD=wasntaphoto',
        '-e', 'POSTGRES_DB=wasntaphoto',
        '-p', '5432:5432',
        '-v', f'{Path(__file__).parent}/initdb:/docker-entrypoint-initdb.d:ro',
        'postgres:18'
    ], capture_output=True, check=False)

    print('Waiting for DB...')

    while True:
        result = run(
            ['docker', 'exec', 'wasntaphoto-dev-db', 'pg_isready', '-U', 'wasntaphoto'],
            capture_output=True
        )
        if result.returncode == 0:
            print("DB ready.")
            return
        sleep(1)


def stop_demo_db() -> None:
    print('Stopping DB...')
    run(['docker', 'rm', '-f', 'wasntaphoto-dev-db'], capture_output=True)


def setup_fs() -> None:
    os.makedirs('/tmp/wasntaphoto/propics', exist_ok=True)
    os.makedirs('/tmp/wasntaphoto/posts', exist_ok=True)
    with open(Path(__file__).parent / 'assets' / 'propic_default.jpg', 'rb') as i:
        with open('/tmp/wasntaphoto/propics/default.jpg', 'wb') as o:
            o.write(i.read())


def run_migrations() -> None:
    cfg = Config('alembic.ini')
    cfg.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL_MIGRATIONS'])
    command.upgrade(cfg, 'head')


def main() -> None:
    start_demo_db()
    setup_fs()
    run_migrations()
    uvicorn.run(app, host="0.0.0.0", port=8000)
    stop_demo_db()


if __name__ == '__main__':
    main()
