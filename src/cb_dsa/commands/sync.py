import os
import sys
import json
import re
import time
import datetime
from rich.console import Console

from cb_dsa.core.utils import (
    LANG_EXTENSIONS, get_session_cookie, get_csrf_token,
    fetch_problem_data, fetch_submission_details, fetch_submissions,
    get_metadata, clean_code
)
from cb_dsa.commands.generate import update_readme

console = Console()

def sync_leetcode():
    base_dir = os.getcwd()
    console.print("[bold blue]=== LeetCode Sync ===[/bold blue]")
    console.print("This script will download your past Accepted submissions.")
    
    session_cookie = get_session_cookie(base_dir, prompt_if_missing=True)
    if not session_cookie:
        console.print("[bold red]Session cookie is required. Exiting.[/bold red]")
        return
        
    console.print("\nFetching CSRF token...")
    csrf_token = get_csrf_token(session_cookie)
    
    console.print("Fetching submissions (this may take a minute)...")
    offset = 0
    limit = 40
    
    # slug -> { lang: submission_id }
    accepted_problems = {} 
    
    while True:
        data = fetch_submissions(session_cookie, offset, limit)
        if not data:
            break
            
        submissions = data.get('submissions_dump', [])
        if not submissions:
            break
            
        for sub in submissions:
            if sub['status_display'] == "Accepted":
                slug = sub['title_slug']
                lang = sub['lang']
                if slug not in accepted_problems:
                    accepted_problems[slug] = {}
                # Only keep the most recent per language
                if lang not in accepted_problems[slug]:
                    accepted_problems[slug][lang] = {'id': sub['id'], 'timestamp': sub.get('timestamp', time.time())}
                    
        if not data.get('has_next'):
            break
            
        offset += limit
        console.print(f"Scanned {offset} total submissions...")
        time.sleep(2.5) # Rate limit protection
        
    console.print(f"\n[bold green]Found {len(accepted_problems)} unique accepted problems.[/bold green]")
    
    if not accepted_problems:
        console.print("No accepted submissions found. Exiting.")
        return
        
    categories = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.') and d not in ['cb-dsa', 'docs', '__pycache__']]
    category_map = {c.lower(): c for c in categories}
    category_map['array'] = 'Arrays'
    category_map['hash table'] = 'HashMaps'
    category_map['dynamic programming'] = 'DP'
    
    success_count = 0
    
    for slug, langs_dict in accepted_problems.items():
        console.print(f"\nProcessing '{slug}'...")
        lc_data = fetch_problem_data(slug, session_cookie, csrf_token)
        if not lc_data:
            console.print(f"[bold red]Failed to fetch problem metadata for {slug}. Skipping.[/bold red]")
            continue
            
        num = lc_data['questionFrontendId']
        title = lc_data['title']
        difficulty = lc_data['difficulty']
        
        # Tags logic
        tags = []
        if 'topicTags' in lc_data and lc_data['topicTags']:
            for tag in lc_data['topicTags']:
                name = tag['name']
                if 'contest' not in name.lower():
                    tags.append(name)
                    
        category = "Other"
        if tags:
            primary_tag = tags[0].lower()
            if primary_tag in category_map:
                category = category_map[primary_tag]
            elif primary_tag + 's' in category_map:
                category = category_map[primary_tag + 's']
                
        category_path = os.path.join(base_dir, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
            
        clean_name = re.sub(r'[^a-zA-Z0-9\s\-]', '', title)
        formatted_name = clean_name.lower().replace(' ', '_').replace('-', '_')
        folder_name = f"{num}_{formatted_name}"
        folder_path = os.path.join(category_path, folder_name)
        
        # If problem already exists locally, patch it instead of skipping
        exists = False
        existing_folder_path = None
        for cat in os.listdir(base_dir):
            if os.path.isdir(os.path.join(base_dir, cat)) and not cat.startswith('.'):
                if os.path.exists(os.path.join(base_dir, cat, folder_name)):
                    exists = True
                    existing_folder_path = os.path.join(base_dir, cat, folder_name)
                    break
        
        most_recent_timestamp = max([info['timestamp'] for info in langs_dict.values()])
        most_recent_sub_id = [info['id'] for info in langs_dict.values() if info['timestamp'] == most_recent_timestamp][0]
        true_date = datetime.datetime.fromtimestamp(most_recent_timestamp).strftime("%Y-%m-%d")
        sub_link_md = f"[View Submission on LeetCode](https://leetcode.com/submissions/detail/{most_recent_sub_id}/)"
        
        if exists:
            # Patch existing file
            doc_files = [f for f in os.listdir(existing_folder_path) if f.endswith('.md')]
            if doc_files:
                doc_path = os.path.join(existing_folder_path, doc_files[0])
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update Date
                if re.search(r'## Date\s*\n\s*\d{4}-\d{2}-\d{2}', content):
                    content = re.sub(r'## Date\s*\n\s*\d{4}-\d{2}-\d{2}', f'## Date\n{true_date}', content)
                else:
                    content += f'\n\n## Date\n{true_date}\n'
                
                # Add submission link if not present
                if 'leetcode.com/submissions/detail' not in content:
                    if '## Idea\n' in content:
                        content = content.replace('## Idea\n', f'## Idea\n\n{sub_link_md}\n')
                    else:
                        content += f'\n\n## Submission\n{sub_link_md}\n'
                        
                # Clean up the old submission link format if the new one exists
                if 'View Submission on LeetCode' in content and 'Click here to see the submission' in content:
                    content = re.sub(r'\[Click here to see the submission\]\(.*?\)\s*\n?', '', content)
                        
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            console.print(f"[bold yellow]Problem {num} already exists. Patched true date and submission link.[/bold yellow]")
            success_count += 1
            continue
            
        os.makedirs(folder_path)
        
        # Fetch actual code for each language
        console.print(f"Fetching source code for {len(langs_dict)} language(s)...")
        meta = {'idea': '', 'time': 'O(?)', 'space': 'O(?)'}
        for lang, sub_info in langs_dict.items():
            sub_id = sub_info['id']
            details = fetch_submission_details(sub_id, session_cookie, csrf_token)
            code = details.get('code') if details else None
            
            if not code:
                code = f"// Failed to fetch code automatically."
                
            ext = LANG_EXTENSIONS.get(lang, f".{lang}")
            file_name = f"{folder_name}_soln{ext}"
            
            # Format header appropriately depending on language extension
            if ext in ['.py', '.rb']:
                header = f"# {num}. {title}\n\n"
            else:
                header = f"// {num}. {title}\n\n"
                
            code = clean_code(code)
            with open(os.path.join(folder_path, file_name), 'w', encoding='utf-8') as f:
                f.write(header + code + "\n")
                
            if sub_id == most_recent_sub_id:
                meta = get_metadata(code, interactive=False)
            
        # Write doc
        md_file_name = f"{folder_name}_doc.md"
        leet_link = f"https://leetcode.com/problems/{slug}/"
        
        md_content = f"# [{num}. {title}]({leet_link})\n\n"
        md_content += f"## Date\n{true_date}\n\n"
        md_content += f"## Difficulty\n{difficulty}\n\n"
        md_content += f"## Topics\n"
        if tags:
            for t in tags: md_content += f"- {t}\n"
        else:
            md_content += f"- {category}\n"
        md_content += f"\n---\n\n## Idea\n\n{sub_link_md}\n\n"
        if meta.get('idea'):
            md_content += f"{meta['idea']}\n\n"
        md_content += f"---\n\n"
        md_content += f"## Time Complexity\n\n{meta.get('time', 'O(?)')}\n\n## Space Complexity\n\n{meta.get('space', 'O(?)')}\n\n---\n\n"
        md_content += f"## Key Learning\n\n\n\n---\n\n## Mistakes Made\n\n\n\n---\n\n"
        
        try:
            similar_questions_list = json.loads(lc_data['similarQuestions'])
            similar_problems = [q['title'] for q in similar_questions_list]
        except:
            similar_problems = []
            
        md_content += f"## Similar Problems\n\n"
        if similar_problems:
            for sp in similar_problems: md_content += f"- {sp}\n"
        else:
            md_content += f"- \n"
            
        with open(os.path.join(folder_path, md_file_name), 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        success_count += 1
        time.sleep(1) # Protect against rate limiting
        
    console.print(f"\n[bold green]Done! Successfully imported {success_count} problems.[/bold green]")
    if success_count > 0:
        console.print("Updating README statistics...")
        update_readme()

if __name__ == "__main__":
    sync_leetcode()
