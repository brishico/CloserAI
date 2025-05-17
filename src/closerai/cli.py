import click
import subprocess
from pathlib import Path

@click.group()
def cli(): 
    ...

@cli.command("edit-triggers")
def edit_triggers():
    """
    Open the trigger-config JSON in your default editor so managers
    can add/remove keywords and tips without editing code.
    """
    cfg = Path("config/triggers.json").resolve()
    if not cfg.exists():
        cfg.parent.mkdir(exist_ok=True, parents=True)
        cfg.write_text("{}")
    # On Windows this will open in Notepad; on macOS/Linux it'll pick $EDITOR
    subprocess.run(["${EDITOR:-notepad}", str(cfg)], shell=True)

@cli.command("run-web-gui")
@click.option("--host", default="127.0.0.1", help="Host to bind")
@click.option("--port", default=5000, help="Port to listen on")
def run_web_gui(host, port):
    """
    Launch the browser-based trigger editor.
    """
    from .webgui import create_app
    app = create_app()
    app.run(host=host, port=port)