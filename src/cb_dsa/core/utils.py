import os
import urllib.request
import urllib.error
import json
import ssl
import time
import re

from rich.console import Console
from rich.prompt import Prompt

console = Console()

LANG_EXTENSIONS = {
    'cpp': '.cpp', 'python': '.py', 'python3': '.py', 'java': '.java',
    'c': '.c', 'csharp': '.cs', 'javascript': '.js', 'typescript': '.ts',
    'golang': '.go', 'rust': '.rs', 'ruby': '.rb', 'swift': '.swift',
    'kotlin': '.kt', 'php': '.php'
}

IGNORED_DIRS = {
    'cb-dsa', 'docs', 'dist', 'src', 'build', '__pycache__',
    '.venv', 'venv', 'node_modules', '.git', '.idea', '.vscode'
}

def get_category_folders(base_dir):
    """
    Returns valid category directories, excluding tool and system directories.
    """
    base_dir = find_repo_root(base_dir)
    if not os.path.exists(base_dir):
        return []
    return [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
        and not d.startswith('.')
        and d.lower() not in IGNORED_DIRS
        and not d.endswith('.egg-info')
    ]

def find_repo_root(start_dir=None):
    """
    Find the root directory of the cb-dsa repository by looking for dsa-config.json or .git.
    Falls back to start_dir or current working directory.
    """
    if not start_dir:
        start_dir = os.getcwd()
    cur = os.path.abspath(start_dir)
    while True:
        if os.path.exists(os.path.join(cur, "dsa-config.json")) or os.path.exists(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return os.path.abspath(start_dir)
        cur = parent

def sanitize_cookie(raw_cookie):
    """
    Strips whitespace, quotes, and common prefix wrappers like LEETCODE_SESSION= or Cookie:.
    """
    if not raw_cookie:
        return ""
    c = str(raw_cookie).strip()
    if c.lower().startswith("cookie:"):
        c = c[7:].strip()
    if "leetcode_session=" in c.lower():
        m = re.search(r'leetcode_session=([^;\s]+)', c, re.IGNORECASE)
        if m:
            c = m.group(1)
        else:
            c = re.sub(r'(?i)leetcode_session=', '', c).strip()
    c = c.split(';')[0].strip()
    c = c.strip("'\"")
    return c

def read_env_file(base_dir):
    """
    Reads .env file returning a dict of key-values without trailing quotes/whitespace.
    """
    base_dir = find_repo_root(base_dir)
    env_path = os.path.join(base_dir, ".env")
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_str = line.strip()
                if not line_str or line_str.startswith('#') or '=' not in line_str:
                    continue
                k, v = line_str.split('=', 1)
                env_vars[k.strip()] = v.strip().strip("'\"")
    return env_vars

def write_env_var(base_dir, key, value):
    """
    Writes or updates a key in .env, deduplicating any repeated keys.
    """
    base_dir = find_repo_root(base_dir)
    env_path = os.path.join(base_dir, ".env")
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
    new_lines = []
    found = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
            if not found:
                new_lines.append(f"{key}={value}\n")
                found = True
            # Skip any duplicate lines with the same key
        else:
            new_lines.append(line)
            
    if not found:
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'
        new_lines.append(f"{key}={value}\n")
        
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def validate_session_cookie(cookie):
    """
    Checks if a LEETCODE_SESSION cookie is currently authenticated via LeetCode's userStatus query.
    Returns (is_valid: bool, username: str).
    """
    if not cookie:
        return False, ""
    cleaned = sanitize_cookie(cookie)
    if not cleaned:
        return False, ""
    context = ssl._create_unverified_context()
    graphql_url = "https://leetcode.com/graphql/"
    payload = {"query": "query globalData { userStatus { isSignedIn username } }"}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
        'Cookie': f'LEETCODE_SESSION={cleaned}'
    }
    req = urllib.request.Request(graphql_url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    try:
        response = urllib.request.urlopen(req, context=context, timeout=8)
        data = json.loads(response.read())
        user_status = data.get('data', {}).get('userStatus', {})
        if user_status.get('isSignedIn'):
            return True, user_status.get('username', '')
    except Exception:
        pass
    return False, ""

def get_session_cookie(base_dir, prompt_if_missing=True, force_prompt=False):
    base_dir = find_repo_root(base_dir)
    env_vars = read_env_file(base_dir)
    session_cookie = sanitize_cookie(env_vars.get("LEETCODE_SESSION", ""))
    
    if force_prompt or (not session_cookie and prompt_if_missing):
        if force_prompt:
            console.print("\n[bold yellow]Your LeetCode session seems to be expired or invalid.[/bold yellow]")
            console.print("Instructions: Open leetcode.com, open Developer Tools (F12) -> Application -> Cookies -> Copy the value of LEETCODE_SESSION.")
            
        while True:
            raw_cookie = Prompt.ask("\n[bold cyan]Paste your LEETCODE_SESSION cookie (will be saved to .env)[/bold cyan]").strip()
            if not raw_cookie:
                break
            candidate = sanitize_cookie(raw_cookie)
            with console.status("[bold cyan]Validating session cookie with LeetCode...[/bold cyan]", spinner="dots"):
                is_valid, username = validate_session_cookie(candidate)
            if is_valid:
                session_cookie = candidate
                write_env_var(base_dir, "LEETCODE_SESSION", session_cookie)
                console.print(f"[bold green]✓ Authenticated as '{username}'! Session cookie saved to .env.[/bold green]")
                break
            else:
                console.print("[bold red]✗ Invalid or expired session cookie. LeetCode reported you are not signed in.[/bold red]")
                retry = Prompt.ask("[bold yellow]Try pasting again?[/bold yellow]", choices=["y", "n"], default="y")
                if retry.lower() != 'y':
                    if candidate:
                        session_cookie = candidate
                        write_env_var(base_dir, "LEETCODE_SESSION", session_cookie)
                        console.print("[yellow]Cookie saved without verification.[/yellow]")
                    break
                
    return session_cookie

def ensure_valid_session(base_dir, current_cookie=None):
    """
    Verifies that the session cookie is valid. If missing or invalid, prompts in place,
    saves the valid cookie to .env immediately, and returns (new_cookie, new_csrf).
    """
    base_dir = find_repo_root(base_dir)
    if not current_cookie:
        env_vars = read_env_file(base_dir)
        current_cookie = sanitize_cookie(env_vars.get("LEETCODE_SESSION", ""))
        
    is_valid, username = validate_session_cookie(current_cookie)
    if is_valid:
        csrf = get_csrf_token(current_cookie)
        return current_cookie, csrf
        
    console.print("\n[bold yellow]⚠ LeetCode session cookie is missing, expired, or invalid.[/bold yellow]")
    console.print("LeetCode requires an active login session to fetch private submission code.")
    console.print("[dim]Instructions: Open leetcode.com -> F12 -> Application -> Cookies -> Copy LEETCODE_SESSION[/dim]")
    
    new_cookie = get_session_cookie(base_dir, force_prompt=True)
    if new_cookie:
        new_csrf = get_csrf_token(new_cookie)
        return new_cookie, new_csrf
    return current_cookie, get_csrf_token(current_cookie)

def get_last_category(base_dir):
    base_dir = find_repo_root(base_dir)
    return read_env_file(base_dir).get("LAST_CATEGORY")

def save_last_category(base_dir, category):
    base_dir = find_repo_root(base_dir)
    write_env_var(base_dir, "LAST_CATEGORY", category)

def get_switch_topic(base_dir):
    base_dir = find_repo_root(base_dir)
    return read_env_file(base_dir).get("SWITCH_TOPIC", "").lower() == 'true'

def reset_switch_topic(base_dir):
    base_dir = find_repo_root(base_dir)
    write_env_var(base_dir, "SWITCH_TOPIC", "false")

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
            data = json.loads(response.read())
            
            if 'errors' in data and any('permission denied' in str(err).lower() or 'anonymous' in str(err).lower() for err in data['errors']):
                raise urllib.error.HTTPError(graphql_url, 401, "Unauthorized in body", req.headers, None)
                
            return data
            
        except urllib.error.HTTPError as e:
            if e.code in (401, 403) and attempt == 0:
                base_dir = find_repo_root()
                new_cookie = get_session_cookie(base_dir, force_prompt=True)
                new_csrf = get_csrf_token(new_cookie)
                
                req.headers['Cookie'] = f'LEETCODE_SESSION={new_cookie}; csrftoken={new_csrf}'
                req.headers['X-CSRFToken'] = new_csrf
                
                if hasattr(req, 'unredirected_hdrs'):
                    req.unredirected_hdrs['Cookie'] = f'LEETCODE_SESSION={new_cookie}; csrftoken={new_csrf}'
                    req.unredirected_hdrs['X-CSRFToken'] = new_csrf
                continue
                
            elif attempt < retries - 1:
                time.sleep(2)
            else:
                console.print(f"[bold red]GraphQL request failed: {e}[/bold red]")
                return None
                
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

def fetch_submission_details(submission_id, session_cookie, csrf_token, base_dir=None):
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
    details = res.get('data', {}).get('submissionDetails') if res and 'data' in res else None
    if details and details.get('code'):
        return details
        
    # If code was not returned, session may be invalid or expired
    if base_dir:
        base_dir = find_repo_root(base_dir)
        console.print("[yellow]Could not retrieve submission code with current session cookie. Checking session...[/yellow]")
        new_cookie, new_csrf = ensure_valid_session(base_dir, session_cookie)
        if new_cookie and new_cookie != session_cookie:
            res = fetch_graphql(query, {"submissionId": int(submission_id)}, new_cookie, new_csrf)
            details = res.get('data', {}).get('submissionDetails') if res and 'data' in res else None
            if details and details.get('code'):
                return details
                
    return None

def fetch_submissions(session_cookie, offset, limit, retries=5, base_dir=None):
    context = ssl._create_unverified_context()
    url = f"https://leetcode.com/api/submissions/?offset={offset}&limit={limit}"
    req = urllib.request.Request(url, headers={'Cookie': f'LEETCODE_SESSION={session_cookie}', 'User-Agent': 'Mozilla/5.0'})
    for attempt in range(retries):
        try:
            response = urllib.request.urlopen(req, context=context, timeout=30)
            data = json.loads(response.read())
            if isinstance(data, dict) and ('detail' in data or 'error' in data):
                raise urllib.error.HTTPError(url, 401, str(data.get('detail', data.get('error'))), req.headers, None)
            return data
        except urllib.error.HTTPError as e:
            if e.code in (401, 403) and attempt == 0:
                root_dir = find_repo_root(base_dir)
                new_cookie = get_session_cookie(root_dir, force_prompt=True)
                
                req.headers['Cookie'] = f'LEETCODE_SESSION={new_cookie}'
                if hasattr(req, 'unredirected_hdrs'):
                    req.unredirected_hdrs['Cookie'] = f'LEETCODE_SESSION={new_cookie}'
                continue
                
            elif attempt < retries - 1:
                console.print(f"[yellow]Timeout/Error at offset {offset}. Retrying ({attempt+1}/{retries})...[/yellow]")
                time.sleep(5)
            else:
                console.print(f"[bold red]Failed to fetch submissions at offset {offset}: {e}[/bold red]")
                return None
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
