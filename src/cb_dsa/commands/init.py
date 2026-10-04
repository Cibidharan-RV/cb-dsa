import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from cb_dsa.config import load_config, save_config
from cb_dsa.commands.generate import update_readme

console = Console()

def init_command():
    base_dir = os.getcwd()
    console.print(Panel.fit(" [bold blue]Initialize cb-dsa Repository[/bold blue] ", border_style="blue"))
    
    config = load_config(base_dir)
    
    # 1. Customization
    console.print("[bold yellow]1. Dashboard Customization[/bold yellow]")
    config["dashboard_title"] = Prompt.ask("Dashboard Title", default=config.get("dashboard_title"))
    config["dashboard_subtitle"] = Prompt.ask("Dashboard Subtitle", default=config.get("dashboard_subtitle"))
    
    theme = Prompt.ask("Default Theme (dark/pink)", choices=["dark", "pink"], default=config.get("dashboard_theme", "dark"))
    config["dashboard_theme"] = theme
    
    # 2. Workflow & Socials
    console.print("\n[bold yellow]2. Workflow & Social Links[/bold yellow]")
    config["author_name"] = Prompt.ask("Your Name", default=config.get("author_name"))
    config["default_language"] = Prompt.ask("Default Programming Language Extension", default=config.get("default_language", ".py"))
    config["auto_commit"] = Confirm.ask("Auto-commit and push to GitHub after creating a problem?", default=config.get("auto_commit", False))
    
    config["github_repo_url"] = Prompt.ask("GitHub Repository URL (e.g., https://github.com/username/dsa-repo)", default=config.get("github_repo_url", ""))
    config["github_username"] = Prompt.ask("GitHub Username", default=config.get("github_username"))
    config["github_url"] = Prompt.ask("GitHub Profile URL", default=f"https://github.com/{config['github_username']}" if config['github_username'] and config['github_username'] != "your-username" else config.get("github_url"))
    config["linkedin_url"] = Prompt.ask("LinkedIn Profile URL", default=config.get("linkedin_url", "#"))
    config["twitter_url"] = Prompt.ask("X (Twitter) Profile URL", default=config.get("twitter_url", "#"))
    config["leetcode_url"] = Prompt.ask("LeetCode Profile URL", default=config.get("leetcode_url", "#"))

    # 3. LeetCode Session (optional)
    console.print("\n[bold yellow]3. LeetCode Setup (Optional)[/bold yellow]")
    console.print("To fetch problem details automatically, we need your LEETCODE_SESSION cookie.")
    console.print("You can find this in your browser's Developer Tools -> Application -> Cookies -> leetcode.com")
    leetcode_session = Prompt.ask("LEETCODE_SESSION cookie (leave blank to skip for now)", default="")
    if leetcode_session:
        env_path = os.path.join(base_dir, ".env")
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"LEETCODE_SESSION={leetcode_session}\n")
        
    save_config(base_dir, config)
    
    # 4. Repo Setup
    console.print("\n[bold yellow]4. Repository Setup[/bold yellow]")
    
    # .gitignore
    gitignore_path = os.path.join(base_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("dsa-config.json\n__pycache__/\n.env\n*.pyc\n")
        console.print("[green]Created .gitignore[/green]")
        
    # Default folders
    create_folders = Confirm.ask("Create default categorization folders (Arrays, HashMaps, DP, Trees)?", default=True)
    if create_folders:
        for folder in ["Arrays", "HashMaps", "DP", "Trees"]:
            os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
        console.print("[green]Created default folders[/green]")

    # 5. Git Init and Push
    if not os.path.exists(os.path.join(base_dir, ".git")):
        subprocess.run(["git", "init"], check=False)
        console.print("[green]Initialized empty Git repository[/green]")
        
    # Generate Dashboard
    console.print("\n[bold yellow]Generating Dashboard...[/bold yellow]")
    update_readme()
    
    # Git Commit and Push
    if config["github_repo_url"]:
        do_push = Confirm.ask(f"Commit and push to {config['github_repo_url']}?", default=True)
        if do_push:
            try:
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit via cb-dsa init"], check=True)
                subprocess.run(["git", "branch", "-M", "main"], check=True)
                
                # Check if remote origin already exists
                remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout
                if "origin" not in remotes:
                    subprocess.run(["git", "remote", "add", "origin", config["github_repo_url"]], check=True)
                else:
                    subprocess.run(["git", "remote", "set-url", "origin", config["github_repo_url"]], check=True)
                    
                subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
                console.print("[bold green]Successfully pushed to GitHub![/bold green]")
                
                console.print(Panel.fit(
                    "[bold magenta]GitHub Pages Setup Instructions:[/bold magenta]\n"
                    "1. Go to your repository on GitHub.\n"
                    "2. Click on [bold]Settings[/bold] -> [bold]Pages[/bold] (left sidebar).\n"
                    "3. Under 'Build and deployment', set Source to [bold]'Deploy from a branch'[/bold].\n"
                    "4. Under 'Branch', select [bold]'main'[/bold] and folder [bold]'/docs'[/bold].\n"
                    "5. Click Save. Your dashboard will be live in a few minutes!",
                    border_style="magenta"
                ))
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]Git operation failed: {e}[/bold red]")
