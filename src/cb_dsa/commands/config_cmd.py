import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from cb_dsa.config import load_config, save_config
from cb_dsa.commands.generate import update_readme
from cb_dsa.core.utils import get_session_cookie

console = Console()

def config_command():
    """
    Modify configuration options for cb-dsa.
    """
    base_dir = os.getcwd()
    console.print(Panel.fit(" [bold blue]cb-dsa Configuration[/bold blue] ", border_style="blue"))
    config = load_config(base_dir)

    while True:
        console.print("\n[bold cyan]What would you like to configure?[/bold cyan]")
        console.print("1. Dashboard Appearance (Title, Subtitle, Theme)")
        console.print("2. Workflow & Defaults (Language, Auto-commit)")
        console.print("3. Personal & Social Links")
        console.print("4. GitHub Repository URL")
        console.print("5. Update LeetCode Session Cookie")
        console.print("0. Exit")
        
        choice = Prompt.ask("Select an option", choices=["0", "1", "2", "3", "4", "5"], default="0")
        
        if choice == "0":
            console.print("[green]Exiting configuration menu.[/green]")
            break
            
        elif choice == "1":
            config["dashboard_title"] = Prompt.ask("Dashboard Title", default=config.get("dashboard_title"))
            config["dashboard_subtitle"] = Prompt.ask("Dashboard Subtitle", default=config.get("dashboard_subtitle"))
            config["dashboard_theme"] = Prompt.ask("Default Theme (dark/pink)", choices=["dark", "pink"], default=config.get("dashboard_theme", "dark"))
            save_config(base_dir, config)
            console.print("[green]Dashboard settings updated! Regenerating dashboard...[/green]")
            update_readme()
            
        elif choice == "2":
            config["default_language"] = Prompt.ask("Default Programming Language Extension", default=config.get("default_language", ".py"))
            config["auto_commit"] = Confirm.ask("Auto-commit and push to GitHub after creating a problem?", default=config.get("auto_commit", False))
            save_config(base_dir, config)
            console.print("[green]Workflow settings updated![/green]")
            
        elif choice == "3":
            config["author_name"] = Prompt.ask("Your Name", default=config.get("author_name"))
            config["github_username"] = Prompt.ask("GitHub Username", default=config.get("github_username"))
            config["github_url"] = Prompt.ask("GitHub Profile URL", default=config.get("github_url"))
            config["linkedin_url"] = Prompt.ask("LinkedIn Profile URL", default=config.get("linkedin_url"))
            config["twitter_url"] = Prompt.ask("X (Twitter) Profile URL", default=config.get("twitter_url"))
            config["leetcode_url"] = Prompt.ask("LeetCode Profile URL", default=config.get("leetcode_url"))
            save_config(base_dir, config)
            console.print("[green]Personal & social details updated! Regenerating dashboard...[/green]")
            update_readme()
            
        elif choice == "4":
            config["github_repo_url"] = Prompt.ask("GitHub Repository URL", default=config.get("github_repo_url"))
            save_config(base_dir, config)
            console.print("[green]GitHub Repository URL updated! Regenerating dashboard...[/green]")
            update_readme()
            
        elif choice == "5":
            get_session_cookie(base_dir, force_prompt=True)
            console.print("[green]LeetCode session updated successfully![/green]")
