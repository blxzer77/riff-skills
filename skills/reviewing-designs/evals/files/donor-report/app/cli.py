import sqlite3
from datetime import date
from pathlib import Path

import click

from . import db


def register(app) -> None:
    @app.cli.command("backup")
    @click.argument("dest", type=click.Path(file_okay=False))
    def backup(dest: str) -> None:
        """Copy the database to DEST/pantry-YYYY-MM-DD.db with SQLite's online backup."""
        target = Path(dest) / f"pantry-{date.today().isoformat()}.db"
        with sqlite3.connect(db.path()) as src, sqlite3.connect(target) as out:
            src.backup(out)
        click.echo(f"backed up to {target}")
