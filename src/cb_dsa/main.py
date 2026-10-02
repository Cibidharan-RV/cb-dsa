import typer
from rich.console import Console

from cb_dsa.commands.create import create_problem
from cb_dsa.commands.generate import update_readme
from cb_dsa.commands.sync import sync_leetcode

app = typer.Typer(help="cb-dsa: A CLI to automate your LeetCode and DSA workflow.")
console = Console()

@app.command()
def init():
    """
    Initialize cb-dsa configuration in the current directory.
    """
    console.print("[bold green]Initializing cb-dsa...[/bold green]")
    # TODO: Implement config generation

app.command(name="create")(create_problem)
app.command(name="generate")(update_readme)
app.command(name="sync")(sync_leetcode)

if __name__ == "__main__":
    app()
