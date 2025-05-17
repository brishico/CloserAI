import click
from .audio import listen

@click.group()
def cli():
    """CloserAI command‐line interface."""
    pass

@cli.command()
@click.option(
    "--no-gpt",
    is_flag=True,
    help="Disable dynamic ChatGPT suggestions"
)
def listen_cmd(no_gpt):
    """
    Start listening on mic + loopback.
    Pass --no-gpt to suppress GPT suggestions.
    """
    listen(disable_gpt=no_gpt)

if __name__ == "__main__":
    cli()
