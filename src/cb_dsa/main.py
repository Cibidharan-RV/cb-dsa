import typer
from rich.console import Console

from cb_dsa.commands.create import create_problem
from cb_dsa.commands.generate import update_readme
from cb_dsa.commands.sync import sync_leetcode

app = typer.Typer(help="cb-dsa: A CLI to automate your LeetCode and DSA workflow.")
console = Console()

from cb_dsa.commands.init import init_command
from cb_dsa.commands.config_cmd import config_command

app.command(name="init")(init_command)
app.command(name="config")(config_command)
app.command(name="create")(create_problem)
app.command(name="generate")(update_readme)
app.command(name="sync")(sync_leetcode)

if __name__ == "__main__":
    app()
