# src/closerai/cli.py
import click
from .audio import listen

@click.group()
def cli():
    """CloserAI: real-time coaching for sales calls."""
    pass

@cli.command()
def greet():
    """Show welcome message."""
    click.echo("👋 Welcome to CloserAI!")

@cli.command()
@click.option("--keyword", "-k", multiple=True,
              help="Additional keywords to watch for.")
def listen_cmd(keyword):
    """Start listening on your mic and suggest talking points."""
    listen(keywords=list(keyword))

if __name__ == "__main__":
    cli()
