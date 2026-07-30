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
    return re.sub(r'\\parencite\{([^}]+)\}', replace_cite, text)

def clean_inline(text: str) -> str:
    text = re.sub(r'\\emph\{([^}]+)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\textbf\{([^}]+)\}', r'<strong>\1</strong>', text)
    text = re.sub(r'\\CNF', 'CNF', text)
    text = re.sub(r'\\SAT', 'SAT', text)
    text = re.sub(r'\\MaxSAT', 'MaxSAT', text)
    text = re.sub(r'\\PySAT', 'PySAT', text)
    text = re.sub(r'\\sffamily', '', text)
    text = re.sub(r'\\bfseries', '', text)
    text = text.replace("``", "“").replace("''", "”")
    text = format_citations(text)
    return text.strip()

def parse_tables(text: str) -> str:
    def replace_center_table(match):
        block = match.group(1)
        
        # Caption
        cap_match = re.search(r'\\captionof\{table\}\{([^}]+)\}', block)
        caption_html = ""
        if cap_match:
            caption_text = clean_inline(cap_match.group(1))
            caption_html = f'<div class="reader-table-caption">Bảng: {caption_text}</div>'
            
        # Extract tabularx/tabular content
        tab_match = re.search(r'\\begin\{(?:tabularx|tabular)\}(.*?)\\end\{(?:tabularx|tabular)\}', block, re.DOTALL)
        if not tab_match:
            return ""
            
        tab_content = tab_match.group(1).strip()
        
        # Strip preamble up to \toprule or \hline if present
        if r'\toprule' in tab_content:
            tab_content = tab_content.split(r'\toprule', 1)[1]
        elif r'\hline' in tab_content:
            tab_content = tab_content.split(r'\hline', 1)[1]
        else:
            # Strip leading argument braces {...}
            tab_content = re.sub(r'^(?:\{[^{}]*\}|\s+)+', '', tab_content).strip()
            
        tab_content = re.sub(r'\\(top|mid|bottom)rule', '', tab_content)
        tab_content = re.sub(r'\\label\{[^}]+\}', '', tab_content)
        
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

    text = re.sub(r'\\begin\{center\}(.*?)\\end\{center\}', replace_center_table, text, flags=re.DOTALL)
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
    pattern = r'\\flowdiagram\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}\s*\{([^}]+)\}\{([^}]+)\}'
    return re.sub(pattern, replace_flow, text)

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

    text = re.sub(r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}', replace_enum, text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', replace_item, text, flags=re.DOTALL)
    return text

def clean_latex_document(text: str) -> str:
    # Comments & Index
    text = re.sub(r'(?<!\\)%.*', '', text)
    text = re.sub(r'\\index\{[^}]+\}', '', text)
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    
    # Remove TikZ environments if raw
    text = re.sub(r'\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}', '', text, flags=re.DOTALL)
    
    # Flow diagrams
    text = parse_flowdiagrams(text)
    
    # Tables
    text = parse_tables(text)
    
    # Lists
    text = parse_lists(text)
    
    # Chapter lead
    text = re.sub(r'\\chapterlead\{([^}]+)\}', r'<div class="chapter-lead">\1</div>', text)
    text = re.sub(r'\\chapter\{([^}]+)\}', '', text)
    
    # Headings
    text = re.sub(r'\\section\{([^}]+)\}', r'<h3 class="reader-h2">\1</h3>', text)
    text = re.sub(r'\\subsection\{([^}]+)\}', r'<h4 class="reader-h3">\1</h4>', text)
    
    # Inline formatting & quotes
    text = clean_inline(text)
    
    # Convert math delimiters for KaTeX
    text = re.sub(r'\\\[(.*?)\\\]', r'\[\1\]', text, flags=re.DOTALL)
    
    # Paragraphs: split by double newlines, wrap non-block items in <p>
    paragraphs = []
    blocks = re.split(r'\n\s*\n', text)
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if any(b.startswith(tag) for tag in ['<h2', '<h3', '<h4', '<div', '<ol', '<ul', '<table']):
            paragraphs.append(b)
        else:
            paragraphs.append(f'<p>{b}</p>')
            
    return "\n".join(paragraphs)

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
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
      onload="renderMathInElement(document.body);"></script>

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
        border-bottom: 2px solid var(--color-brand-light);
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
        background: var(--color-brand-light);
        color: var(--color-brand-primary);
        text-decoration: none;
      }}
      .toc-num {{
        font-family: var(--font-mono);
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--color-brand-primary);
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
        border-bottom: 2px solid var(--color-brand-light);
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
        color: var(--color-brand-primary);
        background: var(--color-brand-light);
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
        border-left: 4px solid var(--color-brand-primary);
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
        border: 1px solid var(--color-brand-border);
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
        background: var(--color-brand-light);
        border-color: var(--color-brand-border);
        color: var(--color-brand-primary);
      }}
      .flow-arrow {{
        color: var(--color-brand-primary);
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
      .cite {{
        font-size: 0.9rem;
        color: var(--color-brand-primary);
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
          <span class="brand-title">Biểu diễn SAT tối ưu</span>
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
