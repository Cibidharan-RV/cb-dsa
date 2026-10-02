import os
import urllib.request
import json
import ssl
import time

from rich.console import Console
from rich.prompt import Prompt

console = Console()

LANG_EXTENSIONS = {
    'cpp': '.cpp', 'python': '.py', 'python3': '.py', 'java': '.java',
    'c': '.c', 'csharp': '.cs', 'javascript': '.js', 'typescript': '.ts',
    'golang': '.go', 'rust': '.rs', 'ruby': '.rb', 'swift': '.swift',
    'kotlin': '.kt', 'php': '.php'
}

def get_session_cookie(base_dir, prompt_if_missing=True):
    env_path = os.path.join(base_dir, ".env")
    session_cookie = ""
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("LEETCODE_SESSION="):
                    session_cookie = line.strip().split('=', 1)[1]
    
    if not session_cookie and prompt_if_missing:
        session_cookie = Prompt.ask("\n[bold cyan]Paste your LEETCODE_SESSION cookie (will be saved to .env)[/bold cyan]").strip()
        if session_cookie:
            with open(env_path, 'a', encoding='utf-8') as f:
                f.write(f"LEETCODE_SESSION={session_cookie}\n")
    return session_cookie

def get_last_category(base_dir):
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("LAST_CATEGORY="):
                    return line.strip().split('=', 1)[1]
    return None

def save_last_category(base_dir, category):
    env_path = os.path.join(base_dir, ".env")
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
    with open(env_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith("LAST_CATEGORY="):
                f.write(f"LAST_CATEGORY={category}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"LAST_CATEGORY={category}\n")

def get_switch_topic(base_dir):
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("SWITCH_TOPIC="):
                    return line.strip().split('=', 1)[1].lower() == 'true'
    return False

def reset_switch_topic(base_dir):
    env_path = os.path.join(base_dir, ".env")
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
    with open(env_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith("SWITCH_TOPIC="):
                f.write("SWITCH_TOPIC=false\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write("SWITCH_TOPIC=false\n")

def get_csrf_token(session_cookie):
    context = ssl._create_unverified_context()
    req = urllib.request.Request("https://leetcode.com/", headers={'Cookie': f'LEETCODE_SESSION={session_cookie}', 'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req, context=context)
        for header, value in response.getheaders():
            if header.lower() == 'set-cookie' and 'csrftoken' in value:
                return value.split('csrftoken=')[1].split(';')[0]
    except:
        pass
    return "csrftoken_placeholder"

def fetch_graphql(query, variables, session_cookie=None, csrf_token=None, retries=3):
    context = ssl._create_unverified_context()
    graphql_url = "https://leetcode.com/graphql/"
    payload = {"query": query, "variables": variables}
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    if session_cookie and csrf_token:
        headers['Cookie'] = f'LEETCODE_SESSION={session_cookie}; csrftoken={csrf_token}'
        headers['X-CSRFToken'] = csrf_token
        
    req = urllib.request.Request(graphql_url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    
    for attempt in range(retries):
        try:
            response = urllib.request.urlopen(req, context=context, timeout=10)
            return json.loads(response.read())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                console.print(f"[bold red]GraphQL request failed after {retries} attempts: {e}[/bold red]")
                return None

def fetch_problem_data(slug, session_cookie=None, csrf_token=None):
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
        questionFrontendId
        title
        titleSlug
        difficulty
        similarQuestions
        note
        topicTags {
          name
        }
      }
    }
    """
    res = fetch_graphql(query, {"titleSlug": slug}, session_cookie, csrf_token)
    if res and 'data' in res:
        return res['data'].get('question')
    return None

def fetch_submission_details(submission_id, session_cookie, csrf_token):
    query = """
    query submissionDetails($submissionId: Int!) {
      submissionDetails(submissionId: $submissionId) {
        code
        lang {
          name
        }
      }
    }
    """
    res = fetch_graphql(query, {"submissionId": int(submission_id)}, session_cookie, csrf_token)
    if res and 'data' in res and res['data'].get('submissionDetails'):
        return res['data']['submissionDetails']
    return None

def fetch_submissions(session_cookie, offset, limit, retries=5):
    context = ssl._create_unverified_context()
    url = f"https://leetcode.com/api/submissions/?offset={offset}&limit={limit}"
    req = urllib.request.Request(url, headers={'Cookie': f'LEETCODE_SESSION={session_cookie}', 'User-Agent': 'Mozilla/5.0'})
    for attempt in range(retries):
        try:
            response = urllib.request.urlopen(req, context=context, timeout=30)
            return json.loads(response.read())
        except Exception as e:
            if attempt < retries - 1:
                console.print(f"[yellow]Timeout at offset {offset}. Retrying ({attempt+1}/{retries})...[/yellow]")
                time.sleep(5)
            else:
                console.print(f"[bold red]Failed to fetch submissions at offset {offset}: {e}[/bold red]")
                return None

def get_slug_from_id(question_id):
    context = ssl._create_unverified_context()
    all_url = "https://leetcode.com/api/problems/all/"
    req = urllib.request.Request(all_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req, context=context)
        data = json.loads(response.read())
    except Exception as e:
        console.print(f"[bold red]Failed to fetch problems list: {e}[/bold red]")
        return None
        
    for p in data.get('stat_status_pairs', []):
        if str(p['stat']['frontend_question_id']) == str(question_id):
            return p['stat']['question__title_slug']
            
    console.print(f"[bold yellow]Could not find a problem with ID {question_id}[/bold yellow]")
    return None

import re

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

def extract_metadata(code_content):
    """
    Extracts idea, time, space, learning, and mistakes from code comments.
    Supports both old format ($t: <time>) and new block format ($t <time> $$).
    """
    if code_content is None:
        code_content = ""
        
    metadata = {'idea': None, 'time': None, 'space': None, 'learning': None, 'mistakes': None}
    
    def extract_block(tag):
        # Look for $tag ... $$
        pattern = r'\$' + tag + r'\s*(.*?)\$\$'
        match = re.search(pattern, code_content, re.DOTALL | re.IGNORECASE)
        if match:
            raw_text = match.group(1)
            cleaned_lines = []
            for line in raw_text.split('\n'):
                # remove leading comment chars
                clean = re.sub(r'^(\s*\*\s*|\s*//\s*|\s*#\s*)', '', line)
                cleaned_lines.append(clean)
            return '\n'.join(cleaned_lines).strip()
        return None

    metadata['idea'] = extract_block('i')
    metadata['time'] = extract_block('t')
    metadata['space'] = extract_block('s')
    metadata['learning'] = extract_block('l')
    metadata['mistakes'] = extract_block('m')
    
    # Fallback for old format if $$ block not found
    if not metadata['idea']:
        idea_match = re.search(r'\$i\s*\n(.*?)(?=\$t:|\$s:|\*/|\Z)', code_content, re.DOTALL | re.IGNORECASE)
        if idea_match:
            raw_idea = idea_match.group(1)
            cleaned_lines = []
            for line in raw_idea.split('\n'):
                clean = re.sub(r'^(\s*\*\s*|\s*//\s*|\s*#\s*)', '', line)
                cleaned_lines.append(clean)
            metadata['idea'] = '\n'.join(cleaned_lines).strip()
            
    if not metadata['time']:
        time_match = re.search(r'\$t:\s*(.*)', code_content, re.IGNORECASE)
        if time_match:
            metadata['time'] = time_match.group(1).strip()
            
    if not metadata['space']:
        space_match = re.search(r'\$s:\s*(.*)', code_content, re.IGNORECASE)
        if space_match:
            metadata['space'] = space_match.group(1).strip()
            
    return metadata

def multiline_input(prompt):
    console.print(f"[bold cyan]{prompt}[/bold cyan]")
    console.print("[dim](Press ENTER twice on an empty line to finish)[/dim]")
    lines = []
    consecutive_empty = 0
    
    while True:
        try:
            line = input()
        except EOFError:
            break
            
        if line == "":
            consecutive_empty += 1
            if consecutive_empty >= 2:
                ans = Prompt.ask("[bold cyan]Continue typing?[/bold cyan]", choices=["y", "n", ""], default="").strip().lower()
                if ans == 'y':
                    consecutive_empty = 0
                    continue
                else:
                    break
        else:
            consecutive_empty = 0
            
        lines.append(line)
        
    return '\n'.join(lines).strip()

def get_metadata(code_content, interactive=True):
    meta = extract_metadata(code_content)
    
    if interactive:
        if not meta.get('idea'):
            console.print("\n[bold yellow]Idea not found in code comments.[/bold yellow]")
            console.print("1. Read docs block from clipboard")
            console.print("2. Paste docs block manually")
            console.print("3. Skip / Default")
            choice = Prompt.ask("[bold cyan]Choose option[/bold cyan]", choices=["1", "2", "3"], default="1")
            
            raw_docs = ""
            if choice == "1":
                raw_docs = get_clipboard_text()
                if raw_docs:
                    console.print("[bold green]✓ Read docs from clipboard![/bold green]")
                else:
                    console.print("[bold red]✗ Could not read from clipboard or clipboard is empty.[/bold red]")
                    raw_docs = multiline_input("\nPaste your docs block here")
            elif choice == "2":
                raw_docs = multiline_input("\nPaste your docs block here")
                
            if raw_docs:
                new_meta = extract_metadata(raw_docs)
                for k, v in new_meta.items():
                    if v:
                        meta[k] = v

        if not meta.get('time'):
            meta['time'] = Prompt.ask("[bold cyan]Enter Time Complexity (e.g., O(n))[/bold cyan]", default="O(n)").strip()
        if not meta.get('space'):
            meta['space'] = Prompt.ask("[bold cyan]Enter Space Complexity (e.g., O(1))[/bold cyan]", default="O(n)").strip()
            
    if not meta.get('idea'): meta['idea'] = ""
    if not meta.get('time'): meta['time'] = "O(n)"
    if not meta.get('space'): meta['space'] = "O(n)"
    
    return meta

def clean_code(code_content):
    # Strip C++/Java/JS block comments
    code_content = re.sub(r'/\*\s*\$i.*?\*/\s*', '', code_content, flags=re.DOTALL | re.IGNORECASE)
    # Strip Python block strings
    code_content = re.sub(r'\"\"\"\s*\$i.*?\"\"\"\s*', '', code_content, flags=re.DOTALL | re.IGNORECASE)
    code_content = re.sub(r"'''\s*\$i.*?'''\s*", '', code_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Strip contiguous Python '#' comments if one contains $i
    lines = code_content.split('\n')
    cleaned_lines = []
    in_idea_block = False
    for line in lines:
        is_comment = bool(re.match(r'^\s*#', line))
        if is_comment and '$i' in line.lower():
            in_idea_block = True
            continue
        if in_idea_block:
            if is_comment:
                continue # Skip all contiguous comment lines
            else:
                in_idea_block = False # Block ended
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines).strip()
