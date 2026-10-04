HTML_TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>[[TITLE]]</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Fredoka:wght@400;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="styles.css?v=1" />

    <!-- GSAP for Animations -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" />
  </head>
  <body class="[[THEME_CLASS]] flat-ui">
    <!-- Floating Background Elements (kept for aesthetics, but muted in CSS) -->
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>
    <div class="bg-shape shape-3"></div>

    <div class="app-container" id="app-container">
      
      <!-- Left Panel (Sidebar / Analytics) -->
      <aside class="sidebar panel" id="sidebar">
        <div class="sidebar-content-wrapper">
          <div class="sidebar-top-section">
            <div class="sidebar-header">
              <h1 class="glitch-text" style="font-size: 2.2rem; margin-bottom: 0.2rem;">[[TITLE]]</h1>
              <p class="subtitle" style="margin-bottom: 1rem; font-size: 0.9rem;">[[SUBTITLE]]</p>
            </div>
            <div class="stats-and-pie-wrapper">
              <div class="stats-overview-list" id="stats-overview">
                <div class="stat-list-item">
                  <span class="stat-label">Total Solved</span>
                  <span class="stat-value highlight-cyan" id="stat-total">0</span>
                </div>
                <div class="stat-list-item">
                  <span class="stat-label">Current Streak</span>
                  <span class="stat-value" id="stat-streak">0</span>
                </div>
                <div class="stat-list-item">
                  <span class="stat-label">Longest Streak</span>
                  <span class="stat-value" id="stat-max-streak">0</span>
                </div>
                <div class="stat-list-item">
                  <span class="stat-label">Active Days</span>
                  <span class="stat-value" id="stat-active-days">0</span>
                </div>
                <div class="stat-list-item">
                  <span class="stat-label">Avg / Day</span>
                  <span class="stat-value" id="stat-avg-day">0.0</span>
                </div>
              </div>
              <div class="chart-container donut-wrapper" id="donut-chart-container">
                <canvas id="difficultyDonut"></canvas>
              </div>
            </div>
          </div>

          <div class="sidebar-middle-section">
            <!-- Topics Block -->
            <div class="topics-container panel-section" id="topics-panel">
              <h3 class="section-title">Topics</h3>
              <div class="topic-pills-wrapper" id="topic-pills-wrapper">
                <!-- Topic pills will be injected here via JavaScript -->
              </div>
            </div>

            <!-- Detailed Analytics Graph (Hidden by default) -->
            <div class="analytics-section" id="analytics-section">
              <div class="analytics-controls">
                <select id="analytics-range" class="dropdown-select compact">
                  <option value="7">Last 7 Days</option>
                  <option value="30">Last 30 Days</option>
                  <option value="90">Last 3 Months</option>
                  <option value="180">Last 6 Months</option>
                  <option value="365">Last 1 Year</option>
                  <option value="all" selected>All Time</option>
                  <option value="custom">Custom Range</option>
                </select>
                <div id="custom-date-picker" style="display: none; gap: 0.5rem; align-items: center;">
                  <input type="date" id="custom-start" class="dropdown-select compact" />
                  <span style="color: var(--text-secondary); font-size: 0.8rem;">to</span>
                  <input type="date" id="custom-end" class="dropdown-select compact" />
                </div>
                <select id="analytics-agg" class="dropdown-select compact">
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              
              <div class="chart-scroll-wrapper">
                <div class="chart-container bar-wrapper" id="bar-chart-container">
                  <canvas id="analyticsBarChart"></canvas>
                </div>
              </div>
            </div>
          </div>

          <div class="sidebar-bottom-section">
            <button id="toggle-analytics-btn" class="action-btn block-btn" style="margin-bottom: 1rem;">
              <i class="fa-solid fa-chart-line"></i> <span>Detailed Analytics</span>
            </button>

            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div class="social-links" id="sidebar-socials">
                <a href="[[LEETCODE_URL]]" target="_blank" title="LeetCode"><i class="fa-solid fa-code"></i></a>
                <a href="[[GITHUB_URL]]" target="_blank" title="GitHub"><i class="fa-brands fa-github"></i></a>
                <a href="[[LINKEDIN_URL]]" target="_blank" title="LinkedIn"><i class="fa-brands fa-linkedin"></i></a>
                <a href="[[TWITTER_URL]]" target="_blank" title="X (Twitter)"><i class="fa-brands fa-x-twitter"></i></a>
              </div>
              
              <!-- Theme Toggle -->
              <label class="theme-switch" for="theme-toggle" title="Toggle Pink Toy Mode 🦄">
                <input type="checkbox" id="theme-toggle" />
                <span class="slider">
                  <i class="fa-solid fa-moon icon"></i>
                  <i class="fa-solid fa-gamepad icon" style="color: #fff"></i>
                </span>
              </label>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Layout Resizer -->
      <div class="resizer resizer-vertical" id="main-resizer"></div>

      <!-- Right Panel (Explorer) -->
      <main class="main-content panel" id="main-content">
        <!-- Controls Section -->
        <section class="controls panel-section">
          <div class="controls-top">
            <div class="search-wrapper">
              <i class="fa-solid fa-magnifying-glass search-icon"></i>
              <input type="text" id="search-input" placeholder="Search problems..." />
              <button id="clear-search-btn" class="clear-search-btn" style="display: none" title="Clear search">
                <i class="fa-solid fa-times"></i>
              </button>
            </div>
            
            <div class="controls-actions">
              <select id="sort-select" class="dropdown-select">
                <option value="date-desc" selected>Sort: Newest</option>
                <option value="date-asc">Sort: Oldest</option>
                <option value="num-asc">Sort: Number (Asc)</option>
              </select>
              <span id="results-count" class="results-counter">Found: 0</span>
            </div>
          </div>
        </section>

        <!-- Active Filter Indicator -->
        <div id="active-time-filter" class="active-time-filter panel-section" style="display: none;">
            <span id="active-time-filter-text">Showing filtered problems</span>
            <button id="clear-time-filter-btn" class="action-btn small-btn">Clear Filter</button>
        </div>

        <!-- Heatmap -->
        <div class="heatmap-container panel-section" id="heatmap-panel">
          <div class="heatmap-header" style="display: flex; justify-content: center; margin-bottom: 0.5rem;">
            <span id="heatmap-total" class="meta-text" style="font-weight: 600;">0 problems in the last year</span>
          </div>
          <div class="heatmap-scroll-wrapper" style="display: flex; justify-content: center;">
            <div id="heatmap-grid" class="heatmap-months-wrapper" style="display: flex; gap: 15px;"></div>
          </div>
        </div>

        <!-- Explorer Split -->
        <div class="explorer-split">
          <!-- Problem List Pane -->
          <div class="problem-list-pane panel" id="problem-list-pane" style="flex: 1;">
            
            <!-- Revision Section Accordion -->
            <div class="accordion" id="revision-accordion" style="display: none;">
              <div class="accordion-header" id="revision-accordion-header">
                <div class="accordion-title">
                  <i class="fa-solid fa-clock-rotate-left"></i> To Be Revised Today
                  <span class="badge" id="revision-badge">0</span>
                </div>
                <i class="fa-solid fa-chevron-down accordion-icon"></i>
              </div>
              <div class="accordion-content" id="revision-accordion-content">
                <div class="problems-grid list-view" id="revision-grid"></div>
              </div>
            </div>

            <!-- Main Problems Grid -->
            <div class="problems-grid list-view" id="problems-grid">
              <!-- Problem cards injected here -->
            </div>
          </div>
          
          <!-- Explorer Resizer (Hidden when detail pane is hidden) -->
          <div class="resizer resizer-vertical" id="explorer-resizer" style="display: none;"></div>

          <!-- Problem Detail Pane -->
          <div class="problem-detail-pane panel" id="problem-detail-pane" style="display: none; width: 40%;">
            <div class="detail-header-actions">
              <button id="close-detail-btn" class="icon-btn" title="Close Details"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="detail-content" id="detail-content">
              <!-- Injected by JS -->
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Data script generated by Python -->
    <script src="data.js?v=1"></script>
    <!-- App logic -->
    <script src="app.js?v=1"></script>
  </body>
</html>"""

CSS_TEMPLATE = """\
:root {
  /* Dark Theme Variables */
  --bg-color: #121212;
  --panel-bg: #1e1e1e;
  --border-color: #333333;
  --text-primary: #e0e6ed;
  --text-secondary: #8b9bb4;

  --accent-cyan: #00f2fe;
  --accent-blue: #4facfe;

  --color-easy: #00e676;
  --color-medium: #ffea00;
  --color-hard: #ff1744;

  --input-bg: #2d2d2d;
  --hover-bg: #2a2d32;
  --border-radius: 6px;
  
  --resizer-size: 4px;
}

html.pink-mode, body.pink-mode {
  --bg-color: #ffd1dc;
  --panel-bg: #fff0f5;
  --border-color: #ffb6c1;
  --text-primary: #d81b60;
  --text-secondary: #ad1457;
  --accent-cyan: #ff1744;

  --input-bg: #ffe4e1;
  --hover-bg: #ffc0cb;

  font-family: "Fredoka", "Outfit", sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: "Outfit", sans-serif;
  background-color: var(--bg-color);
  color: var(--text-primary);
  overflow: hidden;
  height: 100vh;
}

/* Scrollbars */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }

/* --- APP LAYOUT (FLAT UI) --- */
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  /* Removed padding and gap for a true IDE split look */
}

/* Panels */
#sidebar { flex: 0 0 20%; }
#main-content { flex: 1 1 0; }

.panel {
  background-color: var(--panel-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-section {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}
.panel-section:last-child { border-bottom: none; }

/* Resizer */
.resizer {
  background-color: var(--border-color);
  z-index: 10;
  transition: background-color 0.2s;
}
.resizer:hover, .resizer.resizing {
  background-color: var(--accent-cyan);
}
.resizer-vertical {
  width: var(--resizer-size);
  cursor: col-resize;
  flex-shrink: 0;
}

/* --- SIDEBAR COMPONENTS --- */
.sidebar-content-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
}

.sidebar-top-section {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}
.sidebar-header { margin-bottom: 1.5rem; }
.glitch-text {
  font-weight: 800;
  background: linear-gradient(to right, var(--accent-cyan), var(--accent-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.subtitle { color: var(--text-secondary); }

/* Stats List & Pie Wrapper */
.stats-and-pie-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.stats-overview-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.stat-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
}
.stat-label { color: var(--text-secondary); font-weight: 600; }
.stat-value { font-weight: 800; }
.highlight-cyan { color: var(--accent-cyan); font-size: 1.2rem; }

.sidebar-middle-section {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sidebar-bottom-section {
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.chart-container {
  display: flex; align-items: center; justify-content: center;
}
.donut-wrapper { height: 200px; }

/* Topics */
.section-title { font-size: 1rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 1rem; font-weight: 600; letter-spacing: 1px;}
.topic-pills-wrapper { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.topic-pill {
  background: var(--input-bg); color: var(--text-primary); padding: 0.3rem 0.6rem;
  border-radius: var(--border-radius); font-size: 0.75rem; font-weight: 600;
  display: flex; align-items: center; gap: 0.4rem; cursor: pointer; border: 1px solid var(--border-color);
}
.topic-pill:hover { border-color: var(--accent-cyan); background: var(--hover-bg); }
.topic-pill .count { background: var(--border-color); padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.7rem; }

/* Analytics Section */
#analytics-section { display: none; flex-direction: column; gap: 1rem; flex: 1; }
.analytics-controls { display: flex; gap: 0.5rem; }
.chart-scroll-wrapper { width: 100%; overflow-x: auto; }
.bar-wrapper { height: 250px; min-width: 400px; }

/* --- ANALYTICS MODE --- */
.app-container.analytics-mode .stats-and-pie-wrapper {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.app-container.analytics-mode .stats-overview-list {
  flex: 1;
}
.app-container.analytics-mode .donut-wrapper {
  flex: 1;
  max-width: 50%;
}
.app-container.analytics-mode #analytics-section { display: flex; }
.app-container.analytics-mode #topics-panel { display: none; }

/* --- BUTTONS & INPUTS --- */
.action-btn {
  background: var(--input-bg); border: 1px solid var(--border-color); color: var(--text-primary);
  padding: 0.6rem 1.2rem; cursor: pointer; font-family: inherit; font-weight: 600; border-radius: var(--border-radius);
  transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
}
.action-btn:hover { background: var(--hover-bg); border-color: var(--text-secondary); }
.block-btn { width: 100%; }
.small-btn { padding: 0.3rem 0.8rem; font-size: 0.8rem; }
.icon-btn { background: transparent; border: none; color: var(--text-secondary); cursor: pointer; font-size: 1.2rem; transition: color 0.2s; }
.icon-btn:hover { color: var(--accent-cyan); }

.dropdown-select {
  background: var(--input-bg); border: 1px solid var(--border-color); color: var(--text-primary);
  padding: 0.4rem 0.8rem; font-family: inherit; font-size: 0.85rem; outline: none; cursor: pointer; border-radius: var(--border-radius);
}
.dropdown-select:hover { border-color: var(--text-secondary); }

/* --- SEARCH SECTION --- */
.controls-top { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
.search-wrapper { position: relative; flex: 1; display: flex; align-items: center; max-width: 400px; }
.search-icon { position: absolute; left: 10px; color: var(--text-secondary); font-size: 0.9rem; }
#search-input {
  width: 100%; padding: 0.5rem 2rem 0.5rem 2.2rem; border: 1px solid var(--border-color); background: var(--input-bg);
  color: var(--text-primary); font-family: inherit; outline: none; border-radius: var(--border-radius); font-size: 0.9rem;
}
#search-input:focus { border-color: var(--accent-cyan); }
.clear-search-btn { position: absolute; right: 10px; background: transparent; border: none; color: var(--text-secondary); cursor: pointer; }
.clear-search-btn:hover { color: var(--accent-cyan); }
.controls-actions { display: flex; align-items: center; gap: 1rem; }
.results-counter { font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; }

.active-time-filter { background: var(--hover-bg); display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--accent-cyan); border-left: 4px solid var(--accent-cyan); }
#active-time-filter-text { font-size: 0.85rem; font-weight: 600; }

/* --- HEATMAP --- */
.meta-text { color: var(--text-secondary); font-size: 0.8rem; }
.heatmap-scroll-wrapper { overflow-x: auto; padding-bottom: 0.5rem; }

.month-block { display: flex; flex-direction: column; gap: 5px; }
.month-label { font-size: 0.75rem; color: var(--text-secondary); text-align: center; font-weight: 600; }
.month-grid {
  display: grid; grid-template-rows: repeat(7, 10px); grid-auto-columns: 10px; grid-auto-flow: column; gap: 3px;
}
.heat-box { width: 10px; height: 10px; border-radius: 2px; background: var(--input-bg); position: relative; cursor: pointer; transition: transform 0.1s; }
.heat-box:hover { transform: scale(1.2); z-index: 2; border: 1px solid var(--text-primary);}
.heat-box.empty { background: transparent; cursor: default; }
.heat-box.empty:hover { transform: none; border: none; z-index: 1; }
.heat-box.level-0 { background: var(--input-bg); }
.heat-box.level-1 { background: rgba(0, 242, 254, 0.4); }
.heat-box.level-2 { background: rgba(0, 242, 254, 0.7); }
.heat-box.level-3 { background: rgba(0, 242, 254, 0.9); }
.heat-box.level-4 { background: #fff; }

body.pink-mode .heat-box.level-1 { background: rgba(255, 23, 68, 0.4); }
body.pink-mode .heat-box.level-2 { background: rgba(255, 23, 68, 0.7); }
body.pink-mode .heat-box.level-3 { background: rgba(255, 23, 68, 0.9); }

/* --- EXPLORER SPLIT --- */
.explorer-split { display: flex; flex: 1; min-height: 0; }
.problem-list-pane { overflow-y: auto; display: flex; flex-direction: column; }
.problem-detail-pane { overflow-y: auto; background: var(--bg-color); border-left: 1px solid var(--border-color); }

/* Accordion */
.accordion { border-bottom: 1px solid var(--border-color); }
.accordion-header {
  padding: 0.8rem 1rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center;
  background: var(--hover-bg); transition: background 0.2s;
}
.accordion-header:hover { background: var(--border-color); }
.accordion-title { font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem; color: var(--accent-cyan); }
.badge { background: var(--accent-cyan); color: #000; padding: 0.1rem 0.4rem; border-radius: 10px; font-size: 0.7rem; font-weight: 800; }
.accordion-icon { transition: transform 0.3s; font-size: 0.8rem; color: var(--text-secondary); }
.accordion.open .accordion-icon { transform: rotate(180deg); }
.accordion-content { display: none; padding: 1rem; background: var(--panel-bg); }
.accordion.open .accordion-content { display: block; }

/* Problem List */
.problems-grid { display: flex; flex-direction: column; }
.problem-card {
  padding: 0.8rem 1rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); transition: background 0.1s;
}
.problem-card:hover { background: var(--hover-bg); }
.problem-card.active-card { background: var(--input-bg); border-left: 3px solid var(--accent-cyan); padding-left: calc(1rem - 3px); }
.card-left { display: flex; flex-direction: column; gap: 0.2rem; }
.card-title { font-weight: 600; font-size: 0.95rem; }
.card-num { color: var(--text-secondary); font-size: 0.8rem; margin-right: 0.5rem; }
.card-meta { display: flex; gap: 0.5rem; align-items: center; font-size: 0.75rem; color: var(--text-secondary); }
.diff-text { font-weight: 700; text-transform: uppercase; font-size: 0.7rem; }
.diff-text.easy { color: var(--color-easy); }
.diff-text.medium { color: var(--color-medium); }
.diff-text.hard { color: var(--color-hard); }

/* Detail Pane */
.detail-header-actions { display: flex; justify-content: flex-end; padding: 0.5rem; border-bottom: 1px solid var(--border-color); }
.detail-content { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem; }
.detail-title { font-size: 1.2rem; margin-bottom: 0.5rem; }
.detail-links { display: flex; gap: 1rem; }
.topic-tag { display: inline-block; background: var(--input-bg); border: 1px solid var(--border-color); color: var(--text-primary); padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.4rem; margin-bottom: 0.4rem; }
.similar-problems-list { display: flex; flex-direction: column; gap: 0.5rem; }
.similar-problem-item { background: var(--input-bg); border: 1px solid var(--border-color); padding: 0.6rem; border-radius: var(--border-radius); cursor: pointer; font-size: 0.85rem; display: flex; justify-content: space-between; }
.similar-problem-item:hover { border-color: var(--accent-cyan); }

/* Social Links */
.social-links { display: flex; gap: 1rem; flex-wrap: wrap; }
.social-links a { color: var(--text-secondary); font-size: 1.2rem; text-decoration: none; transition: color 0.2s; }
.social-links a:hover { color: var(--text-primary); }

/* Theme Switch */
.theme-switch { display: inline-block; width: 44px; height: 24px; position: relative; }
.theme-switch input { opacity: 0; width: 0; height: 0; }
.theme-switch .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--input-bg); border: 1px solid var(--border-color); transition: 0.4s; border-radius: 24px; display: flex; align-items: center; justify-content: space-between; padding: 0 4px; }
.theme-switch .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background-color: white; transition: 0.4s; border-radius: 50%; z-index: 2; }
.theme-switch input:checked + .slider { background-color: var(--accent-cyan); border-color: var(--accent-cyan); }
.theme-switch input:checked + .slider:before { transform: translateX(20px); }
.theme-switch .icon { font-size: 10px; z-index: 1; }

.toy-float { display: none; }
body.pink-mode .toy-float { display: block; position: fixed; z-index: -1; opacity: 0.5; animation: float 6s infinite ease-in-out; }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
"""

JS_TEMPLATE = """\
document.addEventListener("DOMContentLoaded", () => {
  // -------------------------------------------------------------
  // 1. DATA INITIALIZATION
  // -------------------------------------------------------------
  const data = typeof dsaData !== "undefined"
      ? dsaData
      : { problems: [], total: 0, difficulty: { Easy: 0, Medium: 0, Hard: 0 }, categories: {} };

  // Parse local dates correctly to avoid UTC shift bugs
  data.problems.forEach(p => {
      if (p.date) {
          // p.date is expected as "YYYY-MM-DD"
          const parts = p.date.split('-');
          if (parts.length === 3) {
              p._localDate = new Date(parseInt(parts[0]), parseInt(parts[1])-1, parseInt(parts[2]), 12, 0, 0, 0); // Noon local time avoids timezone shifts
          }
      }
  });

  // -------------------------------------------------------------
  // 2. RESIZER LOGIC
  // -------------------------------------------------------------
  function setupResizer(resizerId, prevElementId, nextElementId, direction = 'H') {
      const resizer = document.getElementById(resizerId);
      const prevElement = document.getElementById(prevElementId);
      const nextElement = document.getElementById(nextElementId);
      if(!resizer || !prevElement || !nextElement) return;

      let isResizing = false;
      let startX, startY, startWidth, startHeight;

      resizer.addEventListener('mousedown', function(e) {
          isResizing = true;
          startX = e.clientX;
          startY = e.clientY;
          startWidth = prevElement.getBoundingClientRect().width;
          startHeight = prevElement.getBoundingClientRect().height;
          resizer.classList.add('resizing');
          document.body.style.cursor = direction === 'H' ? 'col-resize' : 'row-resize';
          document.body.style.userSelect = 'none'; // Prevent text selection
      });

      document.addEventListener('mousemove', function(e) {
          if (!isResizing) return;
          if (direction === 'H') {
              let dx = e.clientX - startX;
              let newWidth = startWidth + dx;
              let containerWidth = resizer.parentNode.getBoundingClientRect().width;
              
              // Limits (min 200px each side)
              if (newWidth > 200 && (containerWidth - newWidth) > 200) {
                  prevElement.style.flex = `0 0 ${newWidth}px`;
                  nextElement.style.flex = `1 1 0`; // Takes remaining space
              }
          }
      });

      document.addEventListener('mouseup', function(e) {
          if (isResizing) {
              isResizing = false;
              resizer.classList.remove('resizing');
              document.body.style.cursor = '';
              document.body.style.userSelect = '';
          }
      });
  }

  // Setup Resizers
  setupResizer('main-resizer', 'sidebar', 'main-content', 'H');
  setupResizer('explorer-resizer', 'problem-list-pane', 'problem-detail-pane', 'H');

  // -------------------------------------------------------------
  // 3. STATS CALCULATION ENGINE
  // -------------------------------------------------------------
  function calculateStats(problemList) {
      let e = 0, m = 0, h = 0;
      const dateMap = new Map();
      
      problemList.forEach(p => {
          if (p.difficulty === 'Easy') e++;
          else if (p.difficulty === 'Medium') m++;
          else if (p.difficulty === 'Hard') h++;

          if (p.date) {
              if (!dateMap.has(p.date)) dateMap.set(p.date, 0);
              dateMap.set(p.date, dateMap.get(p.date) + 1);
          }
      });

      const activeDatesStr = Array.from(dateMap.keys()).sort();
      const totalActiveDays = activeDatesStr.length;
      const totalSolved = problemList.length;
      const avgPerDay = totalActiveDays > 0 ? (totalSolved / totalActiveDays).toFixed(1) : "0.0";

      // Streak calculation (Local Time)
      let currentStreak = 0;
      let maxStreak = 0;
      
      const today = new Date();
      const todayStr = today.getFullYear() + "-" + String(today.getMonth()+1).padStart(2,'0') + "-" + String(today.getDate()).padStart(2,'0');
      
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayStr = yesterday.getFullYear() + "-" + String(yesterday.getMonth()+1).padStart(2,'0') + "-" + String(yesterday.getDate()).padStart(2,'0');

      if (activeDatesStr.length > 0) {
          let tempStreak = 1;
          maxStreak = 1;
          
          let lastDate = new Date(activeDatesStr[0] + "T12:00:00");
          
          for (let i = 1; i < activeDatesStr.length; i++) {
              const currDate = new Date(activeDatesStr[i] + "T12:00:00");
              const diffDays = Math.round((currDate - lastDate) / (1000 * 60 * 60 * 24));
              
              if (diffDays === 1) tempStreak++;
              else if (diffDays > 1) tempStreak = 1;
              
              if (tempStreak > maxStreak) maxStreak = tempStreak;
              lastDate = currDate;
          }
          
          // Current streak backwards from today or yesterday
          const lastActiveStr = activeDatesStr[activeDatesStr.length - 1];
          if (lastActiveStr === todayStr || lastActiveStr === yesterdayStr) {
              currentStreak = 1;
              let d = new Date(lastActiveStr + "T12:00:00");
              for (let i = activeDatesStr.length - 2; i >= 0; i--) {
                  d.setDate(d.getDate() - 1);
                  const expectedStr = d.getFullYear() + "-" + String(d.getMonth()+1).padStart(2,'0') + "-" + String(d.getDate()).padStart(2,'0');
                  if (activeDatesStr[i] === expectedStr) {
                      currentStreak++;
                  } else {
                      break;
                  }
              }
          }
      }

      return {
          total: totalSolved,
          easy: e, medium: m, hard: h,
          activeDays: totalActiveDays,
          avgPerDay: avgPerDay,
          currentStreak: currentStreak,
          maxStreak: maxStreak
      };
  }

  function updateSidebarUI(stats) {
      document.getElementById("stat-total").innerText = stats.total;
      document.getElementById("stat-streak").innerText = stats.currentStreak;
      document.getElementById("stat-max-streak").innerText = stats.maxStreak;
      document.getElementById("stat-active-days").innerText = stats.activeDays;
      document.getElementById("stat-avg-day").innerText = stats.avgPerDay;

      // Update Donut Chart
      if (donutChart) {
          donutChart.data.datasets[0].data = [stats.easy, stats.medium, stats.hard];
          donutChart.update();
      }
  }

  // -------------------------------------------------------------
  // 4. CHART.JS CONFIGURATION
  // -------------------------------------------------------------
  const getColors = () => {
      const isPink = document.body.classList.contains('pink-mode');
      return {
          easy: isPink ? '#00e676' : '#00e676',
          medium: isPink ? '#ffd700' : '#ffea00',
          hard: isPink ? '#ff1744' : '#ff1744',
          text: isPink ? '#d81b60' : '#e0e6ed',
          bg: isPink ? '#fff0f5' : '#1e1e1e'
      };
  };

  let colors = getColors();
  Chart.defaults.color = colors.text;
  Chart.defaults.font.family = "'Outfit', sans-serif";

  // A. Donut Chart (Difficulty)
  let donutChart = new Chart(document.getElementById('difficultyDonut'), {
      type: 'doughnut',
      data: {
          labels: ['Easy', 'Medium', 'Hard'],
          datasets: [{
              data: [0, 0, 0], // Initialized by updateSidebarUI
              backgroundColor: [colors.easy, colors.medium, colors.hard],
              borderWidth: 0,
              hoverOffset: 10
          }]
      },
      options: {
          responsive: true, maintainAspectRatio: false, cutout: '75%',
          plugins: { legend: { position: 'bottom', labels: { padding: 20, color: colors.text, usePointStyle: true } } },
          onClick: (e, elements) => {
              if (elements.length > 0) {
                  const idx = elements[0].index;
                  const diffs = ['Easy', 'Medium', 'Hard'];
                  const clickedDiff = diffs[idx];
                  
                  if (currentDifficulty === clickedDiff) {
                      currentDifficulty = "All";
                      const meta = donutChart.getDatasetMeta(0);
                      meta.data.forEach(arc => arc.outerRadius = arc.innerRadius + (arc.outerRadius - arc.innerRadius));
                  } else {
                      currentDifficulty = clickedDiff;
                      const meta = donutChart.getDatasetMeta(0);
                      meta.data.forEach(arc => arc.outerRadius = arc.innerRadius + (arc.outerRadius - arc.innerRadius));
                      const activeArc = meta.data[idx];
                      if(activeArc) activeArc.outerRadius += 10;
                  }
                  donutChart.update();
                  applyFiltersAndSort();
              }
          }
      }
  });

  // Default Full Stats
  updateSidebarUI(calculateStats(data.problems));

  // B. Analytics Stacked Bar Chart
  let barChart = null;
  const renderBarChart = (rangeDays, aggType) => {
      let end = new Date();
      let start = new Date();
      const allDates = data.problems.map(p => p.date).filter(Boolean).sort();
      
      if (rangeDays === 'all') {
          start = new Date((allDates[0] || end.toISOString().split("T")[0]) + "T12:00:00");
      } else if (rangeDays === 'custom') {
          const sVal = document.getElementById('custom-start').value;
          const eVal = document.getElementById('custom-end').value;
          if (sVal) start = new Date(sVal + "T12:00:00");
          else start = new Date((allDates[0] || end.toISOString().split("T")[0]) + "T12:00:00");
          
          if (eVal) end = new Date(eVal + "T12:00:00");
      } else {
          start.setDate(end.getDate() - parseInt(rangeDays));
      }
      
      // Ensure inclusive filtering boundaries
      const filterStart = new Date(start.getTime()); filterStart.setHours(0,0,0,0);
      const filterEnd = new Date(end.getTime()); filterEnd.setHours(23,59,59,999);

      // Update global sidebar stats for this range!
      const problemsInRange = data.problems.filter(p => p._localDate && p._localDate >= filterStart && p._localDate <= filterEnd);
      updateSidebarUI(calculateStats(problemsInRange));

      // Continuous dates generation
      const aggregated = new Map(); // Label -> { Easy, Medium, Hard, _date }
      
      const getWeekStart = (d) => {
          const day = d.getDay(), diff = d.getDate() - day + (day === 0 ? -6 : 1);
          return new Date(d.setDate(diff));
      };
      const getMonthStart = (d) => { return new Date(d.getFullYear(), d.getMonth(), 1, 12, 0, 0); };
      
      // Pre-fill continuous range
      let iterDate = new Date(start.getTime());
      while (iterDate <= end) {
          let labelDate = new Date(iterDate.getTime());
          if (aggType === 'weekly') labelDate = getWeekStart(new Date(iterDate.getTime()));
          else if (aggType === 'monthly') labelDate = getMonthStart(new Date(iterDate.getTime()));
          
          const labelStr = labelDate.toISOString().split("T")[0];
          if (!aggregated.has(labelStr)) {
              aggregated.set(labelStr, { Easy: 0, Medium: 0, Hard: 0, _date: new Date(labelDate.getTime()) });
          }
          iterDate.setDate(iterDate.getDate() + 1);
      }

      problemsInRange.forEach(p => {
          let labelDate = new Date(p._localDate.getTime());
          if (aggType === 'weekly') labelDate = getWeekStart(new Date(p._localDate.getTime()));
          else if (aggType === 'monthly') labelDate = getMonthStart(new Date(p._localDate.getTime()));
          
          const labelStr = labelDate.toISOString().split("T")[0];
          if (aggregated.has(labelStr)) {
              let diff = p.difficulty || "Unknown";
              if (aggregated.get(labelStr)[diff] !== undefined) {
                  aggregated.get(labelStr)[diff]++;
              }
          }
      });

      const sortedKeys = Array.from(aggregated.keys()).sort();
      const labels = [];
      const eData = [], mData = [], hData = [];

      sortedKeys.forEach(k => {
          const obj = aggregated.get(k);
          let niceLabel = k;
          if (aggType === 'daily' || aggType === 'weekly') {
              niceLabel = obj._date.toLocaleDateString(undefined, {month:'short', day:'numeric'});
              if (aggType === 'weekly') niceLabel = "W: " + niceLabel;
          } else {
              niceLabel = obj._date.toLocaleDateString(undefined, {month:'short', year:'numeric'});
          }
          labels.push(niceLabel); eData.push(obj.Easy); mData.push(obj.Medium); hData.push(obj.Hard);
      });

      if (barChart) barChart.destroy();
      
      // Calculate dynamic width based on data points to ensure it scrolls
      const minWidthPerPoint = 15; // px
      const chartWidth = `max(100%, ${labels.length * minWidthPerPoint}px)`;
      const container = document.getElementById('bar-chart-container');
      container.style.width = chartWidth;

      barChart = new Chart(document.getElementById('analyticsBarChart'), {
          type: 'bar',
          data: { labels: labels, datasets: [ { label: 'Easy', data: eData, backgroundColor: colors.easy }, { label: 'Medium', data: mData, backgroundColor: colors.medium }, { label: 'Hard', data: hData, backgroundColor: colors.hard } ] },
          options: {
              responsive: true, maintainAspectRatio: false,
              interaction: { mode: 'index', intersect: false },
              scales: { x: { stacked: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: colors.text } }, y: { stacked: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: colors.text, stepSize: 1 } } },
              plugins: { legend: { display: false }, tooltip: { callbacks: { footer: (items) => { let total = 0; items.forEach(i => total += i.raw); return 'Total: ' + total; } } } },
              onClick: (e, elements) => {
                  if (elements.length > 0) {
                      const index = elements[0].index;
                      applyTimeFilter(sortedKeys[index], aggType);
                  }
              }
          }
      });
      
      // Scroll to end of chart
      setTimeout(() => {
          const wrapper = document.querySelector(".chart-scroll-wrapper");
          if(wrapper) wrapper.scrollLeft = wrapper.scrollWidth;
      }, 50);
  };

  // -------------------------------------------------------------
  // 5. TOPIC PILLS GENERATION
  // -------------------------------------------------------------
  const topicPillsWrapper = document.getElementById("topic-pills-wrapper");
  if (topicPillsWrapper && data.categories) {
      // Build topic counts manually from problems to ensure accuracy with current data
      const topicCount = new Map();
      data.problems.forEach(p => {
          let topTopic = (p.topics && p.topics.length > 0) ? p.topics[0] : p.category;
          if(!topicCount.has(topTopic)) topicCount.set(topTopic, 0);
          topicCount.set(topTopic, topicCount.get(topTopic)+1);
      });
      
      const sortedTopics = Array.from(topicCount.entries()).sort((a,b) => b[1] - a[1]);
      let mainTopics = sortedTopics.slice(0, 8);
      let hiddenTopics = sortedTopics.slice(8);

      const renderPill = (topic, count) => {
          const pill = document.createElement("div"); pill.className = "topic-pill";
          pill.innerHTML = `<span>${topic}</span><span class="count">${count}</span>`;
          pill.addEventListener("click", () => {
              const searchInput = document.getElementById("search-input");
              searchInput.value = `topic:"${topic}"`;
              searchInput.dispatchEvent(new Event("input"));
          });
          return pill;
      };

      mainTopics.forEach(([t, c]) => topicPillsWrapper.appendChild(renderPill(t, c)));

      if (hiddenTopics.length > 0) {
          const hiddenContainer = document.createElement("div");
          hiddenContainer.style.display = "none";
          hiddenContainer.style.gap = "0.5rem";
          hiddenContainer.style.flexWrap = "wrap";
          hiddenTopics.forEach(([t, c]) => hiddenContainer.appendChild(renderPill(t, c)));
          
          const toggleBtn = document.createElement("div");
          toggleBtn.className = "topic-pill"; toggleBtn.style.background = "var(--accent-cyan)"; toggleBtn.style.color = "#000";
          toggleBtn.innerHTML = `<span>+ ${hiddenTopics.length} More</span>`;
          toggleBtn.addEventListener("click", () => {
              if (hiddenContainer.style.display === "none") {
                  hiddenContainer.style.display = "flex";
                  toggleBtn.innerHTML = `<span>- Show Less</span>`;
                  toggleBtn.style.background = "transparent"; toggleBtn.style.color = "var(--text-primary)";
              } else {
                  hiddenContainer.style.display = "none";
                  toggleBtn.innerHTML = `<span>+ ${hiddenTopics.length} More</span>`;
                  toggleBtn.style.background = "var(--accent-cyan)"; toggleBtn.style.color = "#000";
              }
          });
          topicPillsWrapper.appendChild(hiddenContainer);
          topicPillsWrapper.appendChild(toggleBtn);
      }
  }

  // -------------------------------------------------------------
  // 6. UI INTERACTIONS & TOGGLES
  // -------------------------------------------------------------
  const appContainer = document.getElementById("app-container");
  const toggleAnalyticsBtn = document.getElementById("toggle-analytics-btn");
  const analyticsRange = document.getElementById("analytics-range");
  const analyticsAgg = document.getElementById("analytics-agg");
  
  const customDatePicker = document.getElementById("custom-date-picker");
  const customStart = document.getElementById("custom-start");
  const customEnd = document.getElementById("custom-end");
  
  const themeToggle = document.getElementById("theme-toggle");
  const sidebar = document.getElementById("sidebar");
  
  let isAnalyticsMode = false;

  toggleAnalyticsBtn.addEventListener("click", () => {
      isAnalyticsMode = !isAnalyticsMode;
      if (isAnalyticsMode) {
          appContainer.classList.add("analytics-mode");
          sidebar.style.flex = "0 0 65%"; 
          document.getElementById('main-content').style.flex = "1 1 0";
          toggleAnalyticsBtn.innerHTML = `<i class="fa-solid fa-arrow-left"></i> <span>Back to Dashboard</span>`;
          setTimeout(() => { renderBarChart(analyticsRange.value, analyticsAgg.value); donutChart.resize(); }, 100);
      } else {
          appContainer.classList.remove("analytics-mode");
          sidebar.style.flex = "0 0 20%";
          toggleAnalyticsBtn.innerHTML = `<i class="fa-solid fa-chart-line"></i> <span>Detailed Analytics</span>`;
          // Reset global stats back to all time
          updateSidebarUI(calculateStats(data.problems));
          setTimeout(() => { donutChart.resize(); }, 100);
      }
  });

  analyticsRange.addEventListener("change", () => {
      if (analyticsRange.value === 'custom') {
          customDatePicker.style.display = "flex";
      } else {
          customDatePicker.style.display = "none";
          renderBarChart(analyticsRange.value, analyticsAgg.value);
      }
  });

  analyticsAgg.addEventListener("change", () => renderBarChart(analyticsRange.value, analyticsAgg.value));
  customStart.addEventListener("change", () => renderBarChart('custom', analyticsAgg.value));
  customEnd.addEventListener("change", () => renderBarChart('custom', analyticsAgg.value));

  themeToggle.addEventListener("change", () => {
      if (themeToggle.checked) { document.body.classList.add("pink-mode"); document.documentElement.classList.add("pink-mode"); } 
      else { document.body.classList.remove("pink-mode"); document.documentElement.classList.remove("pink-mode"); }
      colors = getColors();
      Chart.defaults.color = colors.text;
      donutChart.data.datasets[0].backgroundColor = [colors.easy, colors.medium, colors.hard];
      donutChart.options.plugins.legend.labels.color = colors.text; donutChart.update();
      if (barChart) {
          barChart.data.datasets[0].backgroundColor = colors.easy; barChart.data.datasets[1].backgroundColor = colors.medium; barChart.data.datasets[2].backgroundColor = colors.hard;
          barChart.options.scales.x.ticks.color = colors.text; barChart.options.scales.y.ticks.color = colors.text; barChart.update();
      }
  });

  // Accordion Logic
  const accHeader = document.getElementById("revision-accordion-header");
  const accordion = document.getElementById("revision-accordion");
  if(accHeader) {
      accHeader.addEventListener("click", () => { accordion.classList.toggle("open"); });
  }

  // -------------------------------------------------------------
  // 7. EXPLORER: LIST, FILTER, DETAIL
  // -------------------------------------------------------------
  const grid = document.getElementById("problems-grid");
  const searchInput = document.getElementById("search-input");
  const sortSelect = document.getElementById("sort-select");
  const resultsCount = document.getElementById("results-count");
  const clearSearchBtn = document.getElementById("clear-search-btn");
  
  const detailPane = document.getElementById("problem-detail-pane");
  const detailContent = document.getElementById("detail-content");
  const explorerResizer = document.getElementById("explorer-resizer");
  const closeDetailBtn = document.getElementById("close-detail-btn");

  const timeFilterContainer = document.getElementById("active-time-filter");
  const timeFilterText = document.getElementById("active-time-filter-text");
  const clearTimeFilterBtn = document.getElementById("clear-time-filter-btn");

  let currentDifficulty = "All"; // Set via Donut click
  let currentSearch = "";
  let currentSort = "date-desc";
  let currentTimeFilter = null; 
  let filteredData = [...data.problems];
  let activeCardDom = null;

  function createProblemCard(p) {
    const card = document.createElement("div");
    const diffClass = p.difficulty ? p.difficulty.toLowerCase() : "neutral";
    card.className = `problem-card`;
    const topTopic = (p.topics && p.topics.length > 0) ? p.topics[0] : p.category;

    card.innerHTML = `
        <div class="card-left">
            <div class="card-title"><span class="card-num">#${p.num}</span> ${p.title}</div>
            <div class="card-meta">
                <span class="diff-text ${diffClass}">${p.difficulty}</span>
                <span>• ${topTopic}</span>
            </div>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-secondary); font-family: monospace;">${p.date || ""}</div>
    `;

    card.addEventListener("click", () => {
        if (activeCardDom) activeCardDom.classList.remove("active-card");
        card.classList.add("active-card");
        activeCardDom = card;
        renderProblemDetail(p);
    });
    return card;
  }

  function renderProblemDetail(p) {
      detailPane.style.display = "flex";
      explorerResizer.style.display = "block";
      
      let githubLink;
      if (p.encoded_folder) githubLink = `[[GITHUB_REPO_URL]]/tree/main/${p.encoded_folder}`;
      else {
          const folderName = p.folder_path.split("\\\\").pop().split("/").pop();
          githubLink = `[[GITHUB_REPO_URL]]/tree/main/${p.category}/${folderName}`;
      }

      const topics = (p.topics && p.topics.length > 0) ? p.topics : [p.category];
      const similar = data.problems.filter(op => op.category === p.category && op.num !== p.num).slice(0, 5);

      detailContent.innerHTML = `
          <div class="detail-title">#${p.num} - ${p.title}</div>
          <div style="display: flex; gap: 1rem; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1rem;">
             <span class="diff-text ${p.difficulty.toLowerCase()}">${p.difficulty}</span>
             <span style="color: var(--text-secondary); font-size: 0.85rem;"><i class="fa-regular fa-calendar"></i> ${p.date || 'Unknown'}</span>
          </div>
          
          <div class="detail-links">
              <a href="${p.link}" target="_blank" class="action-btn small-btn"><i class="fa-solid fa-arrow-up-right-from-square"></i> LeetCode</a>
              <a href="${githubLink}" target="_blank" class="action-btn small-btn"><i class="fa-brands fa-github"></i> Code</a>
          </div>

          <div style="margin-top: 1.5rem;">
              <div class="section-title" style="font-size: 0.85rem;">Topics</div>
              <div>${topics.map(t => `<span class="topic-tag">${t}</span>`).join('')}</div>
          </div>

          <div style="margin-top: 1.5rem;">
              <div class="section-title" style="font-size: 0.85rem;">Similar Problems</div>
              <div class="similar-problems-list">
                  ${similar.length > 0 
                      ? similar.map(s => `<div class="similar-problem-item" data-num="${s.num}"><span>${s.title}</span> <span class="diff-text ${s.difficulty.toLowerCase()}">${s.difficulty}</span></div>`).join('')
                      : '<div style="color: var(--text-secondary); font-size: 0.85rem;">No similar problems found.</div>'
                  }
              </div>
          </div>
      `;

      detailContent.querySelectorAll('.similar-problem-item').forEach(item => {
          item.addEventListener('click', () => {
              const num = item.getAttribute('data-num');
              const target = data.problems.find(op => op.num === num);
              if (target) {
                  searchInput.value = target.title; searchInput.dispatchEvent(new Event("input"));
                  setTimeout(() => {
                      const firstCard = grid.querySelector('.problem-card');
                      if (firstCard) firstCard.click();
                  }, 100);
              }
          });
      });
  }

  closeDetailBtn.addEventListener("click", () => {
      detailPane.style.display = "none";
      explorerResizer.style.display = "none";
      if (activeCardDom) activeCardDom.classList.remove("active-card");
      activeCardDom = null;
  });

  function applyTimeFilter(dateValue, type) {
      currentTimeFilter = { value: dateValue, type: type };
      let text = `Showing problems for ${dateValue}`;
      if (type === 'weekly') {
          const d = new Date(dateValue + "T12:00:00");
          text = `Showing Week of ${d.toLocaleDateString(undefined, {month:'short', day:'numeric'})}`;
      } else if (type === 'monthly') {
          const d = new Date(dateValue + "T12:00:00");
          text = `Showing Month of ${d.toLocaleDateString(undefined, {month:'long', year:'numeric'})}`;
      }
      
      timeFilterText.innerText = text;
      timeFilterContainer.style.display = "flex";
      applyFiltersAndSort();
  }

  clearTimeFilterBtn.addEventListener("click", () => {
      currentTimeFilter = null;
      timeFilterContainer.style.display = "none";
      applyFiltersAndSort();
  });

  function applyFiltersAndSort() {
    let isTopicSearch = false;
    let searchTopic = "";
    const topicMatch = currentSearch.match(/topic:"([^"]+)"/);
    if (topicMatch) { isTopicSearch = true; searchTopic = topicMatch[1]; }

    filteredData = data.problems.filter((p) => {
      let matchesSearch = false;
      if (isTopicSearch) {
        matchesSearch = p.topics && p.topics.some((t) => t.toLowerCase() === searchTopic);
      } else {
        matchesSearch =
          p.title.toLowerCase().includes(currentSearch) ||
          p.category.toLowerCase().includes(currentSearch) ||
          p.num.toString().includes(currentSearch) ||
          (p.topics && p.topics.some((t) => t.toLowerCase().includes(currentSearch)));
      }

      const matchesDiff = currentDifficulty === "All" || p.difficulty === currentDifficulty;
      
      let matchesTime = true;
      if (currentTimeFilter && p._localDate) {
          const pD = p._localDate;
          const filterD = new Date(currentTimeFilter.value + "T12:00:00");
          
          if (currentTimeFilter.type === 'daily') matchesTime = p.date === currentTimeFilter.value;
          else if (currentTimeFilter.type === 'weekly') {
              const endD = new Date(filterD.getTime()); endD.setDate(endD.getDate() + 7);
              matchesTime = pD >= filterD && pD < endD;
          }
          else if (currentTimeFilter.type === 'monthly') {
              matchesTime = pD.getFullYear() === filterD.getFullYear() && pD.getMonth() === filterD.getMonth();
          }
      } else if (currentTimeFilter && !p._localDate) {
          matchesTime = false;
      }
      return matchesSearch && matchesDiff && matchesTime;
    });

    filteredData.sort((a, b) => {
      if (currentSort === "num-asc") return parseInt(a.num) - parseInt(b.num);
      const dateA = a._localDate ? a._localDate.getTime() : 0;
      const dateB = b._localDate ? b._localDate.getTime() : 0;
      if (currentSort === "date-desc") return dateB - dateA; 
      if (currentSort === "date-asc") return dateA - dateB; 
      return 0;
    });

    renderProblems(filteredData);
  }

  function renderProblems(problemsToRender) {
    grid.innerHTML = "";
    resultsCount.innerText = `Found: ${problemsToRender.length}`;
    if(currentDifficulty !== "All") resultsCount.innerText += ` (${currentDifficulty})`;

    problemsToRender.forEach((p) => {
      grid.appendChild(createProblemCard(p));
    });

    if (activeCardDom && !grid.contains(activeCardDom)) {
        closeDetailBtn.click();
    }
  }

  searchInput.addEventListener("input", (e) => {
    currentSearch = e.target.value.toLowerCase();
    if (clearSearchBtn) clearSearchBtn.style.display = currentSearch.length > 0 ? "block" : "none";
    applyFiltersAndSort();
  });
  if (clearSearchBtn) {
    clearSearchBtn.addEventListener("click", () => {
      searchInput.value = ""; currentSearch = ""; clearSearchBtn.style.display = "none";
      applyFiltersAndSort();
    });
  }
  sortSelect.addEventListener("change", (e) => { currentSort = e.target.value; applyFiltersAndSort(); });

  // -------------------------------------------------------------
  // 8. HEATMAP LOGIC
  // -------------------------------------------------------------
  const heatmapData = {};
  let totalHeatmapProblems = 0;
  data.problems.forEach((p) => {
    if (p.date) {
      heatmapData[p.date] = (heatmapData[p.date] || 0) + 1;
      totalHeatmapProblems++;
    }
  });

  document.getElementById("heatmap-total").innerText = `${totalHeatmapProblems} problems in the last year`;

  const heatmapGrid = document.getElementById("heatmap-grid");
  heatmapGrid.innerHTML = "";

  const hToday = new Date();
  const months = [];
  
  // Last 12 months
  for (let i = 11; i >= 0; i--) {
      const d = new Date(hToday.getFullYear(), hToday.getMonth() - i, 1);
      months.push({ year: d.getFullYear(), month: d.getMonth() });
  }

  months.forEach(m => {
      const monthBlock = document.createElement('div');
      monthBlock.className = 'month-block';
      
      const monthLabel = document.createElement('div');
      monthLabel.className = 'month-label';
      monthLabel.innerText = new Date(m.year, m.month, 1).toLocaleDateString(undefined, {month: 'short'});
      
      const monthGrid = document.createElement('div');
      monthGrid.className = 'month-grid';
      
      const daysInMonth = new Date(m.year, m.month + 1, 0).getDate();
      const firstDay = new Date(m.year, m.month, 1).getDay(); // 0 (Sun) to 6 (Sat)
      
      for(let i=0; i<firstDay; i++) {
          const emptyCell = document.createElement('div');
          emptyCell.className = 'heat-box empty';
          monthGrid.appendChild(emptyCell);
      }
      
      for (let day = 1; day <= daysInMonth; day++) {
          const dStr = m.year + "-" + String(m.month+1).padStart(2,'0') + "-" + String(day).padStart(2,'0');
          const count = heatmapData[dStr] || 0;
          
          const cell = document.createElement('div');
          cell.className = 'heat-box';
          let level = 0;
          if (count === 1) level = 1; else if (count === 2) level = 2; else if (count >= 3 && count <= 4) level = 3; else if (count >= 5) level = 4;
          cell.classList.add(`level-${level}`);
          
          const niceDate = new Date(m.year, m.month, day).toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'});
          cell.title = `${count} problem${count !== 1 ? "s" : ""} on ${niceDate}`;
          cell.addEventListener("click", () => applyTimeFilter(dStr, 'daily'));
          
          monthGrid.appendChild(cell);
      }
      
      monthBlock.appendChild(monthLabel);
      monthBlock.appendChild(monthGrid);
      heatmapGrid.appendChild(monthBlock);
  });

  setTimeout(() => {
    const wrapper = document.querySelector(".heatmap-scroll-wrapper");
    if (wrapper) wrapper.scrollLeft = wrapper.scrollWidth;
  }, 100);

  // -------------------------------------------------------------
  // 9. FORGETTING CURVE (REVISION)
  // -------------------------------------------------------------
  const revisionSection = document.getElementById("revision-accordion");
  const revisionGrid = document.getElementById("revision-grid");
  const revisionBadge = document.getElementById("revision-badge");

  if (revisionSection && revisionGrid) {
    const todayDateObj = new Date(); todayDateObj.setHours(12, 0, 0, 0);
    const revisionIntervals = [1, 3, 7, 14, 21, 30, 60, 90];
    const dueProblems = [];

    data.problems.forEach((p) => {
      if (p._localDate) {
        const diffDays = Math.round((todayDateObj - p._localDate) / (1000 * 60 * 60 * 24));
        if (revisionIntervals.includes(diffDays)) dueProblems.push(p);
      }
    });

    if (dueProblems.length > 0) {
      revisionSection.style.display = "block";
      revisionBadge.innerText = dueProblems.length;
      dueProblems.forEach((p) => {
        const card = createProblemCard(p);
        card.addEventListener('click', () => {
           const mainCards = Array.from(grid.querySelectorAll('.problem-card'));
           const target = mainCards.find(c => c.innerHTML.includes(`#${p.num}`));
           if(target) { target.scrollIntoView({behavior:'smooth', block:'center'}); target.click(); }
        });
        revisionGrid.appendChild(card);
      });
    }
  }

  // Double click pie chart wrapper to clear difficulty filter
  document.getElementById("donut-chart-container").addEventListener('dblclick', () => {
      currentDifficulty = "All";
      // Reset pie chart radius
      donutChart.getDatasetMeta(0).data.forEach(arc => arc.outerRadius = arc.innerRadius + (arc.outerRadius - arc.innerRadius));
      donutChart.update();
      applyFiltersAndSort();
  });

  applyFiltersAndSort();
});
"""
