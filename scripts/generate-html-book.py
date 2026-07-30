#!/usr/bin/env python3

from __future__ import annotations

import re
import html
from pathlib import Path

CHAPTER_FILES = [
    ("ch01-foundations.tex", "Chương 1", "SAT và MaxSAT như một nền tảng giải chính xác"),
    ("ch02-quality.tex", "Chương 2", "Thế nào là một phép mã hóa SAT tốt?"),
    ("ch03-cardinality.tex", "Chương 3", "Bộ công cụ ràng buộc đếm và giả Boolean"),
    ("ch04-experiments.tex", "Chương 4", "Thiết kế thực nghiệm cho phép mã hóa SAT"),
    ("ch05-shared-counters.tex", "Chương 5", "Bộ đếm dùng chung cho các cửa sổ chồng lấn"),
    ("ch06-adaptive-counter.tex", "Chương 6", "Thanh ghi đếm thích nghi cho ràng buộc đúng K"),
    ("ch07-symmetry-channeling.tex", "Chương 7", "Đối xứng, biến quan hệ và liên kết biểu diễn"),
    ("ch08-scheduling.tex", "Chương 8", "Lập lịch và cân bằng dây chuyền"),
    ("ch09-packing.tex", "Chương 9", "Đóng gói và cắt hai chiều"),
    ("ch10-bandwidth.tex", "Chương 10", "Bandwidth, antibandwidth và tô đa màu"),
    ("ch11-labeling.tex", "Chương 11", "Gán nhãn và phân bổ tần số"),
    ("conclusion.tex", "Chương 12", "Kết luận và chương trình nghiên cứu"),
]

FIGURE_MAP = {
    "ch01": ("fig_ch01.webp", "Hình 1.3 · Sơ đồ vòng lặp CDCL trong bộ giải SAT"),
    "ch03": ("fig_ch03.webp", "Hình 3.2 · Lưới trạng thái bộ đếm tuần tự (Sequential Counter)"),
    "ch04": ("fig_ch04.webp", "Hình 4.2 · Hồ sơ hiệu năng dạng bậc thang (Performance Profile)"),
    "ch05": ("fig_ch05.webp", "Hình 5.3 · Bộ đếm dùng chung (Shared Counter)"),
    "ch06": ("fig_ch06.webp", "Hình 6.2 · Thanh ghi đếm thích nghi và miền trạng thái tam giác (NSC)"),
    "ch07": ("fig_ch07.webp", "Hình 7.2 · Quỹ đạo đại diện phá đối xứng (Symmetry Breaking)"),
    "ch08": ("fig_ch08.webp", "Hình 8.3 · Cửa sổ ALSC tái sử dụng trong lập lịch"),
    "ch09": ("fig_ch09.webp", "Hình 9.2 · Bố trí nguyên & Quan hệ tách trong Đóng gói 2D"),
    "ch10": ("fig_ch10.webp", "Hình 10.2 · Cặp nhãn bị cấm và bài toán Antibandwidth"),
    "ch11": ("fig_ch11.webp", "Hình 11.2 · Gán nhãn radio khả thi và nén khoảng cấm"),
}

BIB_MAP = {}

def load_bib_entries(repo_root: Path):
    bib_file = repo_root / "book" / "references.bib"
    if not bib_file.exists():
        return
    content = bib_file.read_text(encoding="utf-8")
    entries = re.findall(r'@\w+\{([^,]+),\s*(.*?)\n\}', content, re.DOTALL)
    for key, body in entries:
        key = key.strip()
        author_m = re.search(r'author\s*=\s*[\{"]([^"\}]+)[\}"]', body, re.IGNORECASE)
        year_m = re.search(r'year\s*=\s*[\{"]?(\d{4})[\}"]?', body, re.IGNORECASE)
        year = year_m.group(1) if year_m else ""
        if author_m:
            authors_raw = author_m.group(1).split(" and ")
            first_author = authors_raw[0].split(",")[0].strip()
            if len(authors_raw) > 2:
                citation_text = f"{first_author} et al., {year}"
            elif len(authors_raw) == 2:
                second_author = authors_raw[1].split(",")[0].strip()
                citation_text = f"{first_author} & {second_author}, {year}"
            else:
                citation_text = f"{first_author}, {year}"
        else:
            citation_text = year or key
        BIB_MAP[key] = citation_text

def format_citations(text: str) -> str:
    def replace_cite(m):
        keys = [k.strip() for k in m.group(1).split(",")]
        formatted = []
        for k in keys:
            if k in BIB_MAP:
                formatted.append(BIB_MAP[k])
            else:
                formatted.append(k)
        return f'<span class="cite">({"; ".join(formatted)})</span>'
    return re.sub(r'\\(?:parencite|textcite|cite)\{([^}]+)\}', replace_cite, text)

def clean_inline(text: str) -> str:
    text = re.sub(r'\\texorpdfstring\{([^}]+)\}\{[^}]*\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\textbf\{([^}]+)\}', r'<strong>\1</strong>', text)
    text = re.sub(r'\\texttt\{([^}]+)\}', r'<code>\1</code>', text)
    text = re.sub(r'\\textsc\{([^}]+)\}', r'<span class="small-caps">\1</span>', text)
    
    # Custom TeX Macros outside math
    text = re.sub(r'\\UNSAT\b', 'UNSAT', text)
    text = re.sub(r'\\SAT\b', 'SAT', text)
    text = re.sub(r'\\OPT\b', 'OPT', text)
    text = re.sub(r'\\BKS\b', 'BKS', text)
    text = re.sub(r'\\CNF\b', 'CNF', text)
    text = re.sub(r'\\MaxSAT\b', 'MaxSAT', text)
    text = re.sub(r'\\AMK\b', 'AMK', text)
    text = re.sub(r'\\ExactlyOne\b', 'ExactlyOne', text)
    text = re.sub(r'\\PySAT\b', 'PySAT', text)
    
    # Formatting & Spacing Macros
    text = re.sub(r'\\qquad\b', ' ', text)
    text = re.sub(r'\\quad\b', ' ', text)
    text = re.sub(r'\\sffamily\b', '', text)
    text = re.sub(r'\\bfseries\b', '', text)
    text = re.sub(r'\\centering\b', '', text)
    text = re.sub(r'\\raggedright\b', '', text)
    text = re.sub(r'\\arraybackslash\b', '', text)
    text = re.sub(r'\\endfirsthead\b', '', text)
    text = re.sub(r'\\endhead\b', '', text)
    text = re.sub(r'\\small\b', '', text)
    
    # References & Equations
    text = re.sub(r'\\cref\{([^}]+)\}', r'(xem mục \1)', text)
    text = re.sub(r'\\ref\{([^}]+)\}', r'(xem hình \1)', text)
    text = re.sub(r'\\eqref\{([^}]+)\}', r'(công thức \1)', text)
    text = re.sub(r'\\set\{([^}]+)\}', r'\{\1\}', text)
    text = re.sub(r'\\card\{([^}]+)\}', r'|\1|', text)

    text = text.replace("``", "“").replace("''", "”")
    text = format_citations(text)
    return text.strip()

def parse_callouts(text: str) -> str:
    callout_types = [
        ("designrule", "design-rule", "💡 Nguyên lý Thiết kế"),
        ("workedexample", "worked-example", "📝 Ví dụ Thực thi"),
        ("keyidea", "key-idea", "🔑 Ý tưởng Cốt lõi"),
        ("summarybox", "summary-box", "📌 Tổng kết Bài học"),
        ("resultbox", "result-box", "📊 Kết quả Thực nghiệm"),
    ]
    for env_name, css_class, default_title in callout_types:
        pattern = r'\\begin\{' + env_name + r'\}\s*(?:\[([^\]]*)\]|\{([^}]*)\})?(.*?)\\end\{' + env_name + r'\}'
        def replace_callout(m):
            raw_title = m.group(1) or m.group(2) or ""
            title = clean_inline(raw_title.strip()) if raw_title.strip() else default_title
            body = clean_inline(m.group(3).strip())
            return f'''
            <div class="reader-callout {css_class}">
              <div class="callout-header"><strong>{title}</strong></div>
              <div class="callout-body">{body}</div>
            </div>
            '''
        text = re.sub(pattern, replace_callout, text, flags=re.DOTALL)
    return text

def parse_theorems(text: str) -> str:
    theorem_types = [
        ("theorem", "theorem-box", "Định lý"),
        ("lemma", "lemma-box", "Bổ đề"),
        ("proposition", "proposition-box", "Mệnh đề"),
        ("example", "example-box", "Ví dụ minh họa"),
    ]
    for env_name, css_class, label_prefix in theorem_types:
        pattern = r'\\begin\{' + env_name + r'\}\s*(?:\[([^\]]*)\]|\{([^}]*)\})?(.*?)\\end\{' + env_name + r'\}'
        def replace_thm(m):
            raw_title = m.group(1) or m.group(2) or ""
            title_text = f" ({clean_inline(raw_title.strip())})" if raw_title.strip() else ""
            body = clean_inline(m.group(3).strip())
            return f'''
            <div class="reader-callout {css_class}">
              <div class="callout-header"><strong>{label_prefix}{title_text}</strong></div>
              <div class="callout-body">{body}</div>
            </div>
            '''
        text = re.sub(pattern, replace_thm, text, flags=re.DOTALL)

    # Proof environment
    def replace_proof(m):
        body = clean_inline(m.group(1).strip())
        return f'''
        <div class="reader-proof">
          <em>Chứng minh.</em> {body} <span class="proof-qedsymbol">■</span>
        </div>
        '''
    text = re.sub(r'\\begin\{proof\}(.*?)\\end\{proof\}', replace_proof, text, flags=re.DOTALL)
    return text

def parse_algorithms(text: str) -> str:
    def replace_algo(m):
        block = m.group(1)
        cap_match = re.search(r'\\caption\{([^}]+)\}', block)
        title = clean_inline(cap_match.group(1)) if cap_match else "Thuật toán"
        
        clean_body = re.sub(r'\\begin\{minipage\}\{[^}]*\}', '', block)
        clean_body = re.sub(r'\\end\{minipage\}', '', clean_body)
        clean_body = re.sub(r'\\caption\{[^}]+\}', '', clean_body)
        clean_body = clean_inline(clean_body)

        return f'''
        <div class="reader-algorithm-box">
          <div class="algo-header">⚙️ <strong>{title}</strong></div>
          <div class="algo-body">{clean_body}</div>
        </div>
        '''
    text = re.sub(r'\\begin\{algorithm\}(?:\[[^\]]*\])?(.*?)\\end\{algorithm\}', replace_algo, text, flags=re.DOTALL)
    return text

def parse_figures(text: str) -> str:
    def replace_figure(m):
        block = m.group(1)
        cap_match = re.search(r'\\caption\{([^}]+)\}', block)
        if cap_match:
            cap_text = clean_inline(cap_match.group(1))
            return f'<div class="reader-inline-caption"><em>Hình: {cap_text}</em></div>'
        return ""
    text = re.sub(r'\\begin\{figure\*?\}(?:\[[^\]]*\])?(.*?)\\end\{figure\*?\}', replace_figure, text, flags=re.DOTALL)
    return text

def parse_tables(text: str) -> str:
    def replace_table_block(match):
        block = match.group(1)
        
        cap_match = re.search(r'\\caption(?:of\{table\})?\{([^}]+)\}', block)
        caption_html = ""
        if cap_match:
            caption_text = clean_inline(cap_match.group(1))
            caption_html = f'<div class="reader-table-caption">Bảng: {caption_text}</div>'
            
        tab_match = re.search(r'\\begin\{(?:tabularx|tabular|longtable)\}(.*?)\\end\{(?:tabularx|tabular|longtable)\}', block, re.DOTALL)
        if not tab_match:
            return ""
            
        tab_content = tab_match.group(1).strip()
        
        if r'\toprule' in tab_content:
            tab_content = tab_content.split(r'\toprule', 1)[1]
        elif r'\hline' in tab_content:
            tab_content = tab_content.split(r'\hline', 1)[1]
        else:
            tab_content = re.sub(r'^(?:\{[^{}]*\}|\s+)+', '', tab_content).strip()
            
        tab_content = re.sub(r'\\(top|mid|bottom)rule', '', tab_content)
        tab_content = re.sub(r'\\label\{[^}]+\}', '', tab_content)
        tab_content = re.sub(r'\\caption\{[^}]+\}', '', tab_content)
        
        rows = [r.strip() for r in tab_content.split(r'\\') if r.strip()]
        if not rows:
            return ""
            
        header_row = rows[0]
        body_rows = rows[1:]
        
        header_cells = [clean_inline(c.strip()) for c in header_row.split('&')]
        th_html = "".join(f'<th>{c}</th>' for c in header_cells)
        
        tr_body_html = []
        for r in body_rows:
            cells = [clean_inline(c.strip()) for c in r.split('&')]
            if any(cells):
                tds = "".join(f'<td>{c}</td>' for c in cells)
                tr_body_html.append(f'<tr>{tds}</tr>')
                
        table_html = f'''
        <div class="reader-table-wrapper">
          {caption_html}
          <table class="reader-table">
            <thead><tr>{th_html}</tr></thead>
            <tbody>{"".join(tr_body_html)}</tbody>
          </table>
        </div>
        '''
        return table_html

    text = re.sub(r'\\begin\{(?:center|table)\}(.*?)\\end\{(?:center|table)\}', replace_table_block, text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{longtable\}(.*?)\\end\{longtable\}', replace_table_block, text, flags=re.DOTALL)
    return text

def parse_flowdiagrams(text: str) -> str:
    def replace_flow(m):
        p1 = clean_inline(m.group(1))
        p2 = clean_inline(m.group(2))
        p3 = clean_inline(m.group(3))
        p4 = clean_inline(m.group(4))
        p5 = clean_inline(m.group(5))
        return f'''
        <div class="reader-flow-diagram">
          <div class="flow-box">{p1}</div>
          <div class="flow-arrow">➔</div>
          <div class="flow-box">{p2}</div>
          <div class="flow-arrow">➔</div>
          <div class="flow-box highlight">{p3}</div>
          <div class="flow-branches">
            <div class="flow-subbox">↙ {p4}</div>
            <div class="flow-subbox">↘ {p5}</div>
          </div>
        </div>
        '''
    pattern = r'\\flowdiagram\s*\{([^}]+)\}\s*\{([^}]+)\}\s*\{([^}]+)\}\s*\{([^}]+)\}\s*\{([^}]+)\}'
    return re.sub(pattern, replace_flow, text, flags=re.DOTALL)

def parse_lists(text: str) -> str:
    def replace_enum(m):
        content = m.group(1)
        items = [clean_inline(it.strip()) for it in content.split(r'\item') if it.strip()]
        rendered = "".join(f'<li>{it}</li>' for it in items)
        return f'<ol class="reader-list">{rendered}</ol>'

    def replace_item(m):
        content = m.group(1)
        items = [clean_inline(it.strip()) for it in content.split(r'\item') if it.strip()]
        rendered = "".join(f'<li>{it}</li>' for it in items)
        return f'<ul class="reader-list">{rendered}</ul>'

    def replace_desc(m):
        content = m.group(1)
        raw_items = [it.strip() for it in content.split(r'\item') if it.strip()]
        rendered = []
        for it in raw_items:
            key_m = re.match(r'^\[([^\]]+)\](.*)$', it, re.DOTALL)
            if key_m:
                dt_text = clean_inline(key_m.group(1).strip())
                dd_text = clean_inline(key_m.group(2).strip())
                rendered.append(f'<dt><strong>{dt_text}</strong></dt><dd>{dd_text}</dd>')
            else:
                rendered.append(f'<dd>{clean_inline(it)}</dd>')
        return f'<dl class="reader-dl">{"".join(rendered)}</dl>'

    text = re.sub(r'\\begin\{enumerate\}(?:\[[^\]]*\])?(.*?)\\end\{enumerate\}', replace_enum, text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{itemize\}(?:\[[^\]]*\])?(.*?)\\end\{itemize\}', replace_item, text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{description\}(?:\[[^\]]*\])?(.*?)\\end\{description\}', replace_desc, text, flags=re.DOTALL)
    return text

def parse_headings(text: str) -> str:
    def replace_sec(m):
        body = m.group(1)
        return f'<h3 class="reader-h2">{clean_inline(body.strip())}</h3>'

    def replace_subsec(m):
        body = m.group(1)
        return f'<h4 class="reader-h3">{clean_inline(body.strip())}</h4>'

    text = re.sub(r'\\section\*?(?:\[[^\]]*\])?\{([^}]+)\}', replace_sec, text)
    text = re.sub(r'\\subsection\*?(?:\[[^\]]*\])?\{([^}]+)\}', replace_subsec, text)
    text = re.sub(r'\\paragraph\*?\{([^}]+)\}', r'<strong>\1</strong>', text)
    return text

def clean_latex_document(text: str) -> str:
    # Comments & Index & Labels
    text = re.sub(r'(?<!\\)%.*', '', text)
    text = re.sub(r'\\index\{[^}]+\}', '', text)
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    text = re.sub(r'\\texorpdfstring\{([^}]+)\}\{[^}]*\}', r'\1', text)
    
    # ------------------------------------------------------------------
    # STEP 1: MATH PROTECTION PHASE
    # Extract all KaTeX math blocks and protect HTML special characters <, >
    # ------------------------------------------------------------------
    math_store: list[str] = []

    def protect_display_math(m):
        idx = len(math_store)
        content = m.group(1).strip()
        # Escape < and > so browser HTML parser does not treat them as tags
        safe_content = content.replace("<", "&lt;").replace(">", "&gt;")
        math_store.append(f"\\[\n{safe_content}\n\\]")
        return f"\n___MATH_BLOCK_{idx}___\n"

    def protect_inline_math(m):
        idx = len(math_store)
        content = m.group(1).strip()
        safe_content = content.replace("<", "&lt;").replace(">", "&gt;")
        math_store.append(f"\\({safe_content}\\)")
        return f"___MATH_BLOCK_{idx}___"

    # Convert equation / align* environments to display math
    text = re.sub(r'\\begin\{(?:equation|align\*?)\}(.*?)\\end\{(?:equation|align\*?)\}', protect_display_math, text, flags=re.DOTALL)
    # Convert \[ ... \] display math
    text = re.sub(r'\\\[(.*?)\\\]', protect_display_math, text, flags=re.DOTALL)
    # Convert \( ... \) inline math
    text = re.sub(r'\\\((.*?)\\\)', protect_inline_math, text, flags=re.DOTALL)

    # ------------------------------------------------------------------
    # STEP 2: HTML & STRUCTURAL PARSING PHASE
    # ------------------------------------------------------------------
    # Remove TikZ environments if raw
    text = re.sub(r'\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}', '', text, flags=re.DOTALL)
    
    # Chapter lead & Headings
    text = re.sub(r'\\chapterlead\{((?:[^{}]|\{[^{}]*\})*)\}', r'<div class="chapter-lead">\1</div>', text)
    text = re.sub(r'\\chapter\{([^}]+)\}', '', text)
    text = parse_headings(text)
    
    # Custom Callouts & Theorems
    text = parse_callouts(text)
    text = parse_theorems(text)
    text = parse_algorithms(text)
    text = parse_figures(text)
    
    # Flow diagrams & Tables & Lists
    text = parse_flowdiagrams(text)
    text = parse_tables(text)
    text = parse_lists(text)
    
    # Inline formatting & quotes
    text = clean_inline(text)
    
    # Paragraphs: split by double newlines, wrap non-block items in <p>
    paragraphs = []
    blocks = re.split(r'\n\s*\n', text)
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if any(b.startswith(tag) for tag in ['<h2', '<h3', '<h4', '<div', '<ol', '<ul', '<dl', '<table', '___MATH_BLOCK_']):
            paragraphs.append(b)
        else:
            paragraphs.append(f'<p>{b}</p>')
            
    result = "\n".join(paragraphs)

    # ------------------------------------------------------------------
    # STEP 3: MATH RESTORATION PHASE
    # Re-insert protected math blocks
    # ------------------------------------------------------------------
    for idx, math_html in enumerate(math_store):
        result = result.replace(f"___MATH_BLOCK_{idx}___", math_html)

    return result

def build_reader_html(repo_root: Path):
    load_bib_entries(repo_root)
    chapters_dir = repo_root / "book" / "chapters"
    site_dir = repo_root / "site"
    output_path = site_dir / "read.html"
    
    chapters_html = []
    toc_links = []
    
    for idx, (filename, num_str, title_str) in enumerate(CHAPTER_FILES, 1):
        file_path = chapters_dir / filename
        if not file_path.exists():
            continue
            
        raw_text = file_path.read_text(encoding="utf-8")
        parsed_body = clean_latex_document(raw_text)
        
        chap_id = f"chap-{idx}"
        toc_links.append(f'<a href="#{chap_id}" class="toc-link"><span class="toc-num">{num_str}</span><span class="toc-name">{title_str}</span></a>')
        
        fig_code = ""
        prefix = filename.split('-')[0]
        if prefix in FIGURE_MAP:
            img_file, caption = FIGURE_MAP[prefix]
            fig_code = f'''
            <div class="reader-figure-card">
              <img src="./assets/images/diagrams/{img_file}" alt="{caption}" loading="lazy">
              <div class="reader-figure-caption">{caption}</div>
            </div>
            '''
            
        chap_html = f'''
        <article id="{chap_id}" class="reader-chapter-article">
          <header class="reader-chapter-header">
            <span class="reader-chap-badge">{num_str}</span>
            <h2 class="reader-chap-title">{title_str}</h2>
          </header>
          <div class="reader-chap-body">
            {parsed_body}
            {fig_code}
          </div>
        </article>
        '''
        chapters_html.append(chap_html)
        
    full_html = f'''<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#1e3a8a">
    <title>Đọc trực tuyến | Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp</title>
    <link rel="shortcut icon" href="./favicon.ico">
    <link rel="icon" type="image/x-icon" href="./favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="./assets/images/favicon-32.png">
    <link rel="apple-touch-icon" href="./assets/images/apple-touch-icon.png">
    <link rel="stylesheet" href="./assets/css/main.css">
    
    <!-- KaTeX for Math rendering -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>

    <script>
      document.addEventListener("DOMContentLoaded", function() {{
        if (typeof renderMathInElement === "function") {{
          renderMathInElement(document.body, {{
            delimiters: [
              {{left: "$$", right: "$$", display: true}},
              {{left: "\\[", right: "\\]", display: true}},
              {{left: "\\(", right: "\\)", display: false}},
              {{left: "$", right: "$", display: false}}
            ],
            ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
            throwOnError: false
          }});
        }}
      }});
    </script>

    <style>
      .reader-layout {{
        display: grid;
        grid-template-columns: 280px 1fr;
        gap: 40px;
        align-items: start;
        padding: 40px 0 80px;
      }}
      .reader-sidebar {{
        position: sticky;
        top: 90px;
        background: #ffffff;
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 20px;
        max-height: calc(100vh - 120px);
        overflow-y: auto;
        box-shadow: var(--shadow-sm);
      }}
      .reader-sidebar-title {{
        font-size: 0.95rem;
        font-weight: 800;
        color: var(--color-ink-900);
        margin-bottom: 14px;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--color-brand-200);
        text-transform: uppercase;
        letter-spacing: 0.04em;
      }}
      .reader-toc-nav {{
        display: flex;
        flex-direction: column;
        gap: 6px;
      }}
      .toc-link {{
        display: flex;
        flex-direction: column;
        padding: 8px 10px;
        border-radius: var(--radius-sm);
        font-size: 0.88rem;
        color: var(--color-ink-700);
        transition: all 0.15s ease;
      }}
      .toc-link:hover {{
        background: var(--color-brand-50);
        color: var(--color-brand-600);
        text-decoration: none;
      }}
      .toc-num {{
        font-family: var(--font-mono);
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--color-brand-600);
      }}
      .toc-name {{
        font-weight: 600;
        line-height: 1.3;
      }}
      .reader-content {{
        background: #ffffff;
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 48px;
        box-shadow: var(--shadow-sm);
        max-width: 820px;
      }}
      .reader-doc-title {{
        font-family: var(--font-serif);
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--color-ink-900);
        margin-bottom: 32px;
        padding-bottom: 20px;
        border-bottom: 2px solid var(--color-brand-200);
      }}
      .reader-chapter-article {{
        margin-bottom: 64px;
        padding-bottom: 48px;
        border-bottom: 2px dashed var(--border-color);
      }}
      .reader-chapter-article:last-child {{
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
      }}
      .reader-chap-badge {{
        font-family: var(--font-mono);
        font-size: 0.82rem;
        font-weight: 700;
        color: var(--color-brand-600);
        background: var(--color-brand-50);
        padding: 4px 12px;
        border-radius: 20px;
      }}
      .reader-chap-title {{
        font-family: var(--font-serif);
        font-size: 1.85rem;
        font-weight: 700;
        color: var(--color-ink-900);
        margin: 12px 0 20px;
        line-height: 1.25;
      }}
      .chapter-lead {{
        font-size: 1.12rem;
        color: var(--color-ink-700);
        background: #f8fafc;
        border-left: 4px solid var(--color-brand-600);
        padding: 16px 20px;
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        margin-bottom: 28px;
        line-height: 1.65;
      }}
      .reader-chap-body p {{
        font-size: 1.05rem;
        color: var(--color-ink-800);
        line-height: 1.8;
        margin-bottom: 20px;
      }}
      .reader-h2 {{
        font-family: var(--font-serif);
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--color-ink-900);
        margin: 36px 0 16px;
      }}
      .reader-h3 {{
        font-size: 1.12rem;
        font-weight: 700;
        color: var(--color-ink-900);
        margin: 28px 0 12px;
      }}
      .reader-list {{
        margin: 16px 0 24px 24px;
        color: var(--color-ink-800);
        font-size: 1.02rem;
        line-height: 1.75;
      }}
      .reader-list li {{
        margin-bottom: 8px;
      }}
      .reader-dl {{
        margin: 20px 0;
        background: #f8fafc;
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 18px 24px;
      }}
      .reader-dl dt {{
        color: var(--color-brand-600);
        font-weight: 700;
        margin-top: 12px;
        font-size: 1.02rem;
      }}
      .reader-dl dt:first-child {{
        margin-top: 0;
      }}
      .reader-dl dd {{
        margin-left: 0;
        color: var(--color-ink-800);
        line-height: 1.65;
        margin-bottom: 8px;
      }}
      /* Callout styling */
      .reader-callout {{
        margin: 28px 0;
        padding: 20px 24px;
        border-radius: var(--radius-md);
        background: #ffffff;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-xs);
      }}
      .callout-header {{
        font-size: 1.05rem;
        margin-bottom: 8px;
        color: var(--color-ink-900);
      }}
      .callout-body {{
        font-size: 0.98rem;
        line-height: 1.65;
        color: var(--color-ink-800);
      }}
      .reader-callout.worked-example {{
        border-left: 5px solid #3b82f6;
        background: #f0f9ff;
      }}
      .reader-callout.design-rule {{
        border-left: 5px solid #10b981;
        background: #ecfdf5;
      }}
      .reader-callout.key-idea {{
        border-left: 5px solid #f59e0b;
        background: #fffbeb;
      }}
      .reader-callout.summary-box {{
        border-left: 5px solid #8b5cf6;
        background: #f5f3ff;
      }}
      .reader-callout.result-box {{
        border-left: 5px solid #06b6d4;
        background: #ecfeff;
      }}
      .reader-callout.theorem-box {{
        border-left: 5px solid #1e3a8a;
        background: #f8fafc;
      }}
      .reader-callout.lemma-box {{
        border-left: 5px solid #6366f1;
        background: #f5f3ff;
      }}
      .reader-callout.proposition-box {{
        border-left: 5px solid #0284c7;
        background: #f0f9ff;
      }}
      .reader-callout.example-box {{
        border-left: 5px solid #059669;
        background: #ecfdf5;
      }}
      .reader-proof {{
        margin: 20px 0;
        padding: 16px 20px;
        background: #f8fafc;
        border-left: 3px solid var(--color-ink-500);
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        font-size: 0.98rem;
      }}
      .proof-qedsymbol {{
        float: right;
        color: var(--color-ink-500);
      }}
      .reader-algorithm-box {{
        margin: 28px 0;
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        background: #f8fafc;
        overflow: hidden;
      }}
      .algo-header {{
        background: #e2e8f0;
        padding: 12px 18px;
        font-size: 0.98rem;
        color: var(--color-ink-900);
        border-bottom: 1px solid var(--border-color);
      }}
      .algo-body {{
        padding: 18px;
        font-size: 0.95rem;
        line-height: 1.65;
      }}
      /* Table styling */
      .reader-table-wrapper {{
        margin: 28px 0;
        overflow-x: auto;
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        background: #ffffff;
      }}
      .reader-table-caption {{
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--color-ink-800);
        padding: 12px 16px;
        background: var(--bg-page);
        border-bottom: 1px solid var(--border-color);
      }}
      .reader-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95rem;
        text-align: left;
      }}
      .reader-table th {{
        background: #f1f5f9;
        color: var(--color-ink-900);
        font-weight: 700;
        padding: 10px 14px;
        border-bottom: 2px solid var(--border-color);
      }}
      .reader-table td {{
        padding: 10px 14px;
        border-bottom: 1px solid var(--border-color);
        color: var(--color-ink-800);
        line-height: 1.5;
      }}
      .reader-table tr:last-child td {{
        border-bottom: none;
      }}
      /* Flow diagram styling */
      .reader-flow-diagram {{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
        margin: 28px 0;
        padding: 18px 22px;
        background: #f8fafc;
        border: 1px solid var(--color-brand-200);
        border-radius: var(--radius-md);
      }}
      .flow-box {{
        background: #ffffff;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 8px 14px;
        font-weight: 600;
        font-size: 0.92rem;
        color: var(--color-ink-900);
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      }}
      .flow-box.highlight {{
        background: var(--color-brand-50);
        border-color: var(--color-brand-200);
        color: var(--color-brand-600);
      }}
      .flow-arrow {{
        color: var(--color-brand-600);
        font-size: 1.1rem;
        font-weight: 700;
      }}
      .flow-branches {{
        display: flex;
        gap: 12px;
        width: 100%;
        margin-top: 6px;
      }}
      .flow-subbox {{
        font-size: 0.85rem;
        color: var(--color-ink-600);
        background: #ffffff;
        padding: 6px 12px;
        border-radius: 4px;
        border: 1px solid var(--border-color);
      }}
      .reader-figure-card {{
        margin: 32px 0;
        background: #ffffff;
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 20px;
        box-shadow: var(--shadow-sm);
        text-align: center;
      }}
      .reader-figure-card img {{
        max-width: 100%;
        height: auto;
        border-radius: 4px;
      }}
      .reader-figure-caption {{
        font-size: 0.92rem;
        color: var(--color-ink-600);
        margin-top: 12px;
        font-weight: 600;
      }}
      .reader-inline-caption {{
        font-size: 0.92rem;
        color: var(--color-ink-600);
        margin: 16px 0;
        text-align: center;
      }}
      .cite {{
        font-size: 0.9rem;
        color: var(--color-brand-600);
        font-weight: 600;
      }}
      @media (max-width: 860px) {{
        .reader-layout {{
          grid-template-columns: 1fr;
        }}
        .reader-sidebar {{
          display: none;
        }}
        .reader-content {{
          padding: 28px;
        }}
      }}
    </style>
  </head>
  <body>
    <header class="site-header">
      <div class="shell header-inner">
        <a class="brand" href="./">
          <img src="./assets/images/satlab.png" alt="SATLab Logo" class="brand-logo-img">
          <span class="brand-title">SATLab</span>
        </a>
        <nav class="nav">
          <a href="./">Trang chủ</a>
          <a href="./downloads/sat-book.pdf">Bản PDF (104 trang)</a>
        </nav>
      </div>
    </header>

    <main class="shell reader-layout">
      <aside class="reader-sidebar">
        <div class="reader-sidebar-title">Danh mục 12 Chương</div>
        <nav class="reader-toc-nav">
          {"".join(toc_links)}
        </nav>
      </aside>

      <section class="reader-content">
        <h1 class="reader-doc-title">Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp — Bản đọc trực tuyến</h1>
        {"".join(chapters_html)}
      </section>
    </main>

    <footer class="site-footer">
      <div class="shell footer-grid">
        <div>
          <img src="./assets/images/satlab.png" alt="SATLab Logo" class="footer-logo">
          <div class="footer-brand">Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp</div>
          <p>© 2026 Các tác giả. SATLab UET.</p>
        </div>
        <div>
          <a href="./" class="btn btn-outline">Trở về Trang chủ ↗</a>
        </div>
      </div>
    </footer>
  </body>
</html>
'''
    output_path.write_text(full_html, encoding="utf-8")
    print(f"[✓] Generated clean HTML reader edition at: {output_path}")

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    build_reader_html(repo_root)
