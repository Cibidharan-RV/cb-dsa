import os
import sys
import json
import re
import datetime
import subprocess

from cb_dsa.core.utils import (
    LANG_EXTENSIONS, get_session_cookie, get_csrf_token, fetch_problem_data, 
    fetch_submission_details, get_slug_from_id, get_last_category, save_last_category,
    get_switch_topic, reset_switch_topic, get_metadata, clean_code, multiline_input
)

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import print as rprint

console = Console()

def get_clipboard_text():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        clip = root.clipboard_get()
        root.destroy()
        return clip
    except Exception:
        return ""

def create_problem():
    base_dir = os.getcwd()
    console.print(Panel.fit(" [bold blue]Create New DSA Problem[/bold blue] ", border_style="blue"))
    
    categories = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')]
    category_map = {c.lower(): c for c in categories}
    category_map['array'] = 'Arrays'
    category_map['hash table'] = 'HashMaps'
    category_map['dynamic programming'] = 'DP'
    
    clip_text = get_clipboard_text().strip()
    match = re.search(r'leetcode\.com/problems/([a-zA-Z0-9\-]+)', clip_text)
    
    lc_data = None
    num = None
    submission_link = ""
    custom_code = ""
    question_link = ""
    lang_ext = ".cpp"
    
    if match:
        slug = match.group(1)
        console.print(f"[bold green]✓[/bold green] Detected LeetCode URL for [bold cyan]'{slug}'[/bold cyan] in clipboard!")
        if '/submissions/' in clip_text:
            submission_link = clip_text
            console.print("[bold green]✓[/bold green] Detected submission link in clipboard!")
            
        with console.status(f"[bold cyan]Fetching data for '{slug}'...[/bold cyan]", spinner="dots"):
            lc_data = fetch_problem_data(slug)
        if lc_data:
            num = lc_data['questionFrontendId']
            console.print(f"[bold green]✓[/bold green] Fetched data for problem: [bold white]{num}. {lc_data['title']}[/bold white]")
    
    if not lc_data:
        console.print("\n[yellow]⚠ No valid LeetCode link in clipboard.[/yellow]")
        console.print("1. LeetCode (Input ID)")
        console.print("2. Other Platform")
        choice = Prompt.ask("[bold cyan]Choose option[/bold cyan]", choices=["1", "2"], default="1")
        
        if choice == "1":
            while True:
                num_input = Prompt.ask("[bold cyan]Problem number[/bold cyan]").strip()
                if num_input:
                    num = num_input
                    break
            slug = get_slug_from_id(num)
            if slug:
                with console.status(f"[bold cyan]Fetching data for problem {num}...[/bold cyan]", spinner="dots"):
                    lc_data = fetch_problem_data(slug)
            
    # Process problem data
    category = None
    if lc_data:
        title = lc_data['title']
        slug = lc_data['titleSlug']
        difficulty = lc_data['difficulty']
        
        try:
            similar_questions_list = json.loads(lc_data['similarQuestions'])
            similar_problems = [(q['title'], q['titleSlug']) for q in similar_questions_list]
        except:
            similar_problems = []
            
        tags = []
        if 'topicTags' in lc_data and lc_data['topicTags']:
            for tag in lc_data['topicTags']:
                name = tag['name']
                if 'contest' not in name.lower():
                    tags.append(name)
        lc_data['filtered_tags'] = tags
        
        if tags:
            switch_topic = get_switch_topic(base_dir)
            if not switch_topic:
                last_category = get_last_category(base_dir)
                
                # Check if any tag matches the last category
                if last_category:
                    for tag in tags:
                        tag_lower = tag.lower()
                        mapped_category = category_map.get(tag_lower, category_map.get(tag_lower + 's', tag_lower))
                        if mapped_category.lower() == last_category.lower() or tag_lower == last_category.lower():
                            category = last_category
                            break
                            
                # Fallback to primary tag if no match with last_category
                if not category:
                    primary_tag = tags[0].lower()
                    if primary_tag in category_map:
                        category = category_map[primary_tag]
                    elif primary_tag + 's' in category_map:
                        category = category_map[primary_tag + 's']
                        
                    # Enforce topic-grinding mode: auto-map ONLY if it matches the last category you worked on
                    if last_category and category and category.lower() != last_category.lower():
                        category = None
                
        name = title
    else:
        console.print("\n[yellow]⚠ Manual Problem Setup[/yellow]")
        while True:
            name = Prompt.ask("[bold cyan]Problem name[/bold cyan]").strip()
            if name:
                break
                
        num_input = Prompt.ask("[bold cyan]Problem number/ID (e.g., 100, CF-123)[/bold cyan]", default="000").strip()
        num = num_input if num_input else "000"
        
        question_link = Prompt.ask("[bold cyan]Question Link[/bold cyan]").strip()
        submission_link = Prompt.ask("[bold cyan]Submission Link (optional)[/bold cyan]").strip()
        
        difficulty = Prompt.ask("[bold cyan]Difficulty[/bold cyan]", choices=["Easy", "Medium", "Hard", "Basic", "School", "Other"], default="Medium").strip()
        
        custom_code = multiline_input("\nPaste your code here")
        
        ext_input = Prompt.ask("[bold cyan]File extension (e.g., .cpp, .py)[/bold cyan]", default=".cpp").strip()
        if ext_input:
            lang_ext = ext_input if ext_input.startswith('.') else '.' + ext_input
            
        similar_problems = []
        tags = []
        slug = name.lower().replace(' ', '-').replace(':', '')
        title = name.title()

    # Get Category if not auto-mapped
    if not category:
        options = list(categories)
        if tags:
            for t in tags:
                # Add tags that don't already perfectly match an existing folder name
                if not any(t.lower() == existing.lower() for existing in options):
                    options.append(t)
                    
        console.print("\n[bold yellow]Could not auto-map category. Where should this problem go?[/bold yellow]")
        
        table = Table(show_header=False, box=None)
        table.add_column("Index", style="cyan")
        table.add_column("Category")
        for i, opt in enumerate(options):
            table.add_row(f"{i + 1}.", opt)
        table.add_row(f"{len(options) + 1}.", "[bold]Create a new category folder[/bold]")
        console.print(table)
        
        while True:
            category_input = Prompt.ask(f"[bold cyan]Choose one option (1-{len(options) + 1})[/bold cyan]").strip()
            if category_input.isdigit():
                idx = int(category_input)
                if 1 <= idx <= len(options):
                    category = options[idx - 1]
                    break
                elif idx == len(options) + 1:
                    category = Prompt.ask("[bold cyan]Enter new category name[/bold cyan]").strip()
                    if category: break
            elif category_input:
                category = category_input
                break
                
    save_last_category(base_dir, category)
    reset_switch_topic(base_dir)
                
    category_path = os.path.join(base_dir, category)
    if not os.path.exists(category_path):
        os.makedirs(category_path)
        console.print(f"[bold green]✓ Created new category folder:[/bold green] [cyan]{category}[/cyan]")
        
    if not submission_link and lc_data:
        submission_link = Prompt.ask("[bold cyan]Submission link (optional, press Enter to skip)[/bold cyan]", default="").strip()
            
    clean_name = re.sub(r'[^a-zA-Z0-9\s\-]', '', name)
    formatted_name = clean_name.lower().replace(' ', '_').replace('-', '_')
    folder_name = f"{num}_{formatted_name}"
    folder_path = os.path.join(category_path, folder_name)
    
    if lc_data:
        question_link = f"https://leetcode.com/problems/{slug}/"
    elif not question_link:
        question_link = f"https://example.com/problems/{slug}/"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    # Attempt to fetch code if submission link is provided
    code_content = custom_code if not lc_data else ""
    if lc_data and submission_link:
        sub_id_match = re.search(r'submissions/(?:detail/)?(\d+)', submission_link)
        if sub_id_match:
            sub_id = sub_id_match.group(1)
            session_cookie = get_session_cookie(base_dir, prompt_if_missing=True)
            
            if session_cookie:
                with console.status(f"[bold cyan]Fetching code for submission {sub_id}...[/bold cyan]", spinner="dots"):
                    csrf_token = get_csrf_token(session_cookie)
                    details = fetch_submission_details(sub_id, session_cookie, csrf_token)
                if details:
                    code_content = details.get('code', '')
                    lang_name = details.get('lang', {}).get('name', '')
                    lang_ext = LANG_EXTENSIONS.get(lang_name, f".{lang_name}")
                    console.print(f"[bold green]✓ Successfully fetched {lang_name} code![/bold green]")
                else:
                    console.print("[bold red]✗ Could not retrieve submission code (possibly expired or invalid cookie).[/bold red]")
                    
    if not code_content:
        if lang_ext in ['.py', '.rb']:
            code_content = f"# {num}. {title}\n\n"
        else:
            code_content = f"// {num}. {title}\n\n"
            
    meta = get_metadata(code_content, interactive=True)
    code_content = clean_code(code_content)
            
    suffix = ""
    counter = 1
    while True:
        code_file_name = f"{folder_name}_soln{suffix}{lang_ext}"
        code_file_path = os.path.join(folder_path, code_file_name)
        
        md_file_name = f"{folder_name}_doc{suffix}.md"
        md_file_path = os.path.join(folder_path, md_file_name)
        
        if not os.path.exists(code_file_path) and not os.path.exists(md_file_path):
            break
            
        suffix = str(counter)
        counter += 1
        
    with open(code_file_path, 'w', encoding='utf-8') as f:
        f.write(code_content)
    
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    md_content = f"# [{num}. {title}]({question_link})\n\n"
    md_content += f"## Date\n{current_date}\n\n"
    md_content += f"## Difficulty\n{difficulty}\n\n"
    
    md_content += f"## Topics\n"
    if tags:
        for t in tags:
            md_content += f"- {t}\n"
    else:
        md_content += f"- {category}\n"
    md_content += f"\n---\n\n"
    
    md_content += f"## Idea\n\n"
    if submission_link:
        if lc_data:
            md_content += f"[View Submission on LeetCode]({submission_link})\n\n"
        else:
            md_content += f"[View Submission]({submission_link})\n\n"
        
    if meta.get('idea'):
        md_content += f"{meta['idea']}\n\n"
        
    md_content += f"---\n\n"
    md_content += f"## Time Complexity\n\n{meta['time']}\n\n## Space Complexity\n\n{meta['space']}\n\n---\n\n"
    
    if meta.get('learning'):
        md_content += f"## Key Learning\n\n{meta['learning']}\n\n---\n\n"
        
    if meta.get('mistakes'):
        md_content += f"## Mistakes Made\n\n{meta['mistakes']}\n\n---\n\n"
    
    if similar_problems:
        md_content += f"## Similar Problems\n\n"
        for sp_title, sp_slug in similar_problems:
            md_content += f"- [{sp_title}](https://leetcode.com/problems/{sp_slug}/)\n"
    else:
        md_content += f"## Similar Problems\n\n- \n"
        
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    console.print("\n")
    success_panel = Panel(
        f"[bold]Folder:[/bold] {os.path.relpath(folder_path, base_dir)}\n"
        f"[bold]Code:[/bold]   {os.path.relpath(code_file_path, base_dir)}\n"
        f"[bold]Doc:[/bold]    {os.path.relpath(md_file_path, base_dir)}",
        title="[bold green]Success! Created Files[/bold green]",
        border_style="green",
        expand=False
    )
    console.print(success_panel)
    
    with console.status("[bold cyan]Updating README statistics...[/bold cyan]", spinner="dots"):
        from cb_dsa.commands.generate import update_readme
        update_readme()
        console.print("[bold green]✓ README updated![/bold green]")

    console.print("\n[bold magenta]" + "="*40 + "[/bold magenta]")
    console.print("[bold white]Files have been generated and README updated![/bold white]")
    
    ans = Prompt.ask("\n[bold cyan]Press Enter to commit and push, or type any character to skip[/bold cyan]", default="")
    if ans == '':
        try:
            with console.status("[bold cyan]Committing to Git...[/bold cyan]", spinner="dots"):
                subprocess.run(["git", "add", folder_path, "README.md", "docs/data.js", "docs/index.html"], check=True, capture_output=True)
                commit_message = f"{num}. {title}"
                subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)
                console.print(f"[bold green]✓ Successfully committed to Git:[/bold green] '{commit_message}'")
                
            console.print("[bold cyan]Pushing to GitHub...[/bold cyan]")
            subprocess.run(["git", "push", "origin", "main"], check=True)
            console.print("[bold green]✓ Successfully pushed to GitHub![/bold green]")
        except Exception as e:
            console.print(f"[bold red]✗ Failed to auto-commit or push:[/bold red] {e}")
    else:
        console.print("[yellow]Skipped commit and push.[/yellow]")

if __name__ == "__main__":
    create_problem()
