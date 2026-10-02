import os
import re
import datetime
import json
import urllib.parse
from rich.console import Console

console = Console()

def normalize_topic(topic):
    mapping = {
        'arrays': 'Array',
        'hashmaps': 'Hash Table',
        'hash map': 'Hash Table',
        'dp': 'Dynamic Programming'
    }
    return mapping.get(topic.lower().strip(), topic.strip())

def parse_doc_file(filepath, category):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Title and Link
    title_match = re.search(r'# \[([a-zA-Z0-9\-]+)\.\s+(.*?)\]\((.*?)\)', content)
    if not title_match:
        title_match = re.search(r'# ([a-zA-Z0-9\-]+)\.\s+(.*)', content)
        if title_match:
            num = title_match.group(1)
            title = title_match.group(2).strip()
            link = ""
        else:
            return None
    else:
        num = title_match.group(1)
        title = title_match.group(2).strip()
        link = title_match.group(3).strip()

    # Extract Difficulty
    difficulty_match = re.search(r'## Difficulty\s*\n\s*(Easy|Medium|Hard)', content, re.IGNORECASE)
    difficulty = difficulty_match.group(1).capitalize() if difficulty_match else "Unknown"

    # Extract Date
    date_match = re.search(r'## Date\s*\n\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        date_solved = date_match.group(1)
    else:
        ctime = os.path.getctime(filepath)
        date_solved = datetime.datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")

    # Extract Topics
    topics_match = re.search(r'## Topics\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    topics = []
    if topics_match:
        for line in topics_match.group(1).split('\n'):
            line = line.strip()
            if line.startswith('- '):
                topic = line[2:].strip()
                if topic:
                    norm_topic = normalize_topic(topic)
                    if norm_topic not in topics:
                        topics.append(norm_topic)
    if not topics:
        topics.append(normalize_topic(category))

    return {
        'num': num,
        'title': title,
        'link': link,
        'difficulty': difficulty,
        'category': category,
        'topics': topics,
        'date': date_solved,
        'folder_path': os.path.dirname(filepath)
    }

def update_readme():
    base_dir = os.getcwd()
    problems = []
    
    categories = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.') and d not in ['cb-dsa', 'docs', '__pycache__']]
    
    for category in categories:
        category_path = os.path.join(base_dir, category)
        
        for item in os.listdir(category_path):
            item_path = os.path.join(category_path, item)
            if not os.path.isdir(item_path):
                continue
                
            doc_files = [f for f in os.listdir(item_path) if f.endswith('_doc.md') or f.endswith('_doc1.md') or '_doc' in f and f.endswith('.md')]
            
            if not doc_files:
                continue
                
            doc_file = doc_files[0]
            doc_path = os.path.join(item_path, doc_file)
            
            problem_data = parse_doc_file(doc_path, category)
            if problem_data:
                problems.append(problem_data)

    def sort_key(x):
        num_str = str(x['num'])
        m = re.match(r'(\d+)(.*)', num_str)
        if m:
            return (int(m.group(1)), m.group(2))
        return (float('inf'), num_str)
        
    problems.sort(key=sort_key)

    total_problems = len(problems)
    difficulty_counts = {'Easy': 0, 'Medium': 0, 'Hard': 0, 'Unknown': 0}
    category_stats = {}
    topic_stats = {}

    for p in problems:
        diff = p['difficulty']
        cat = p['category']
        
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        if cat not in category_stats:
            category_stats[cat] = {'Total': 0, 'Easy': 0, 'Medium': 0, 'Hard': 0, 'Unknown': 0}
        
        category_stats[cat]['Total'] += 1
        if diff in category_stats[cat]:
            category_stats[cat][diff] += 1
        else:
            category_stats[cat]['Unknown'] += 1
            
        for t in p['topics']:
            if t not in topic_stats:
                topic_stats[t] = 0
            topic_stats[t] += 1

    def get_bar(count, total, length=20):
        if total == 0: return '░' * length
        filled = int(round((count / total) * length))
        return '█' * filled + '░' * (length - filled)

    easy_count = difficulty_counts.get('Easy', 0)
    medium_count = difficulty_counts.get('Medium', 0)
    hard_count = difficulty_counts.get('Hard', 0)
    
    easy_pct = (easy_count / total_problems * 100) if total_problems else 0
    medium_pct = (medium_count / total_problems * 100) if total_problems else 0
    hard_pct = (hard_count / total_problems * 100) if total_problems else 0

    stats_content = f"**Total Problems Solved:** {total_problems}\n\n"
    stats_content += "### Difficulty Breakdown\n"
    stats_content += f"- 🟢 **Easy** ({easy_pct:.1f}%): `{get_bar(easy_count, total_problems)}` ({easy_count})\n"
    stats_content += f"- 🟡 **Medium** ({medium_pct:.1f}%): `{get_bar(medium_count, total_problems)}` ({medium_count})\n"
    stats_content += f"- 🔴 **Hard** ({hard_pct:.1f}%): `{get_bar(hard_count, total_problems)}` ({hard_count})\n\n"
    
    stats_content += "### Topic Breakdown\n\n"
    stats_content += "| Topic | Total | 🟢 Easy | 🟡 Medium | 🔴 Hard |\n"
    stats_content += "|---|---|---|---|---|\n"
    
    for cat, stats in sorted(category_stats.items(), key=lambda item: item[1]['Total'], reverse=True):
        stats_content += f"| **{cat}** | {stats['Total']} | {stats['Easy']} | {stats['Medium']} | {stats['Hard']} |\n"

    table_content = "| # | Title | Difficulty | Topic | Solution |\n"
    table_content += "|---|---|---|---|---|\n"
    
    for p in problems:
        rel_folder = os.path.relpath(p['folder_path'], base_dir).replace('\\', '/')
        encoded_folder = urllib.parse.quote(rel_folder)
        
        p['rel_folder'] = rel_folder
        p['encoded_folder'] = encoded_folder
        
        title_link = f"[{p['title']}]({p['link']})" if p['link'] else p['title']
        
        diff_emoji = ""
        if p['difficulty'] == 'Easy': diff_emoji = "🟢 Easy"
        elif p['difficulty'] == 'Medium': diff_emoji = "🟡 Medium"
        elif p['difficulty'] == 'Hard': diff_emoji = "🔴 Hard"
        else: diff_emoji = p['difficulty']
        
        folder_link = f"[Code & Doc](./{encoded_folder})"
        
        table_content += f"| {p['num']} | {title_link} | {diff_emoji} | {p['category']} | {folder_link} |\n"

    readme_path = os.path.join(base_dir, "README.md")
    
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_text = f.read()
    else:
        readme_text = "# DSA Practice Repository\n\n## 📊 Statistics\n\n<!-- STATS:START -->\n<!-- STATS:END -->\n\n---\n\n## 📝 Problem Index\n\n<!-- TABLE:START -->\n<!-- TABLE:END -->\n"

    stats_pattern = r'<!-- STATS:START -->.*?<!-- STATS:END -->'
    stats_replacement = f"<!-- STATS:START -->\n{stats_content}\n<!-- STATS:END -->"
    if re.search(stats_pattern, readme_text, re.DOTALL):
        readme_text = re.sub(stats_pattern, stats_replacement, readme_text, flags=re.DOTALL)
    else:
        readme_text += f"\n\n## 📊 Statistics\n\n{stats_replacement}"
        
    table_pattern = r'<!-- TABLE:START -->.*?<!-- TABLE:END -->'
    table_replacement = f"<!-- TABLE:START -->\n{table_content}\n<!-- TABLE:END -->"
    if re.search(table_pattern, readme_text, re.DOTALL):
        readme_text = re.sub(table_pattern, table_replacement, readme_text, flags=re.DOTALL)
    else:
        readme_text += f"\n\n## 📝 Problem Index\n\n{table_replacement}"

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_text)
        
    docs_dir = os.path.join(base_dir, "docs")
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        
    dashboard_data = {
        'total': total_problems,
        'difficulty': difficulty_counts,
        'categories': category_stats,
        'topic_stats': topic_stats,
        'problems': problems
    }
    
    js_content = f"const dsaData = {json.dumps(dashboard_data, indent=2)};"
    with open(os.path.join(docs_dir, "data.js"), 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    import time
    index_path = os.path.join(docs_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        timestamp = int(time.time())
        index_content = re.sub(r'data\.js(\?v=\d+)?', f'data.js?v={timestamp}', index_content)
        index_content = re.sub(r'app\.js(\?v=\d+)?', f'app.js?v={timestamp}', index_content)
        index_content = re.sub(r'styles\.css(\?v=\d+)?', f'styles.css?v={timestamp}', index_content)
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
            
    console.print(f"[bold green]✓ Successfully updated README.md and docs/data.js with {total_problems} problems.[/bold green]")

if __name__ == "__main__":
    update_readme()
