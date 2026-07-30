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
    "ch04": ("fig_ch04.webp", "Hình 4.1 · Hồ sơ hiệu năng dạng bậc thang (Performance Profile)"),
    "ch05": ("fig_ch05.webp", "Hình 5.3 · Bộ đếm dùng chung (Shared Counter)"),
    "ch06": ("fig_ch06.webp", "Hình 6.2 · Thanh ghi đếm thích nghi và miền trạng thái tam giác (NSC)"),
    "ch07": ("fig_ch07.webp", "Hình 7.1 · Quỹ đạo đại diện phá đối xứng (Symmetry Breaking)"),
    "ch08": ("fig_ch08.webp", "Hình 8.2 · Cửa sổ ALSC tái sử dụng trong lập lịch"),
    "ch09": ("fig_ch09.webp", "Hình 9.2 · Bố trí nguyên & Quan hệ tách trong Đóng gói 2D"),
    "ch10": ("fig_ch10.webp", "Hình 10.1 · Cặp nhãn bị cấm và bài toán Antibandwidth"),
    "ch11": ("fig_ch11.webp", "Hình 11.2 · Gán nhãn radio khả thi và nén khoảng cấm"),
}

def clean_latex(text: str) -> str:
    # Comments
    text = re.sub(r'(?<!\\)%.*', '', text)
    
    # Index entries
    text = re.sub(r'\\index\{[^}]+\}', '', text)
    
    # Text formatting
    text = re.sub(r'\\emph\{([^}]+)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\textbf\{([^}]+)\}', r'<strong>\1</strong>', text)
    text = re.sub(r'\\CNF', 'CNF', text)
    text = re.sub(r'\\SAT', 'SAT', text)
    text = re.sub(r'\\MaxSAT', 'MaxSAT', text)
    text = re.sub(r'\\PySAT', 'PySAT', text)
    
    # Citations & refs
    text = re.sub(r'\\parencite\{([^}]+)\}', r'<span class="cite">[\1]</span>', text)
    text = re.sub(r'\\ref\{([^}]+)\}', r'<span class="ref">[\1]</span>', text)
    
    # Sections (use h3 for sections, h4 for subsections)
    text = re.sub(r'\\section\{([^}]+)\}', r'</p><h3 class="reader-h2">\1</h3><p>', text)
    text = re.sub(r'\\subsection\{([^}]+)\}', r'</p><h4 class="reader-h3">\1</h4><p>', text)
    text = re.sub(r'\\chapterlead\{([^}]+)\}', r'<div class="chapter-lead">\1</div>', text)
    text = re.sub(r'\\chapter\{([^}]+)\}', '', text)
    
    # Environments
    text = text.replace('\\begin{enumerate}', '</p><ol class="reader-list"><li>')
    text = text.replace('\\end{enumerate}', '</li></ol><p>')
    text = text.replace('\\begin{itemize}', '</p><ul class="reader-list"><li>')
    text = text.replace('\\end{itemize}', '</li></ul><p>')
    text = text.replace('\\item', '</li><li>')
    text = text.replace('<li></li>', '')
    
    # Paragraphs
    text = re.sub(r'\n\s*\n', '</p><p>', text)
    
    # Cleanup empty p tags
    text = re.sub(r'<p>\s*</p>', '', text)
    
    return text.strip()

def build_reader_html(repo_root: Path):
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
        parsed_body = clean_latex(raw_text)
        
        chap_id = f"chap-{idx}"
        toc_links.append(f'<a href="#{chap_id}" class="toc-link"><span class="toc-num">{num_str}</span><span class="toc-name">{title_str}</span></a>')
        
        # Check figure embedding
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
            <p>{parsed_body}</p>
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
    <link rel="icon" type="image/png" sizes="32x32" href="./assets/images/favicon-32.png">
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
        line-height: 1.7;
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
      .cite, .ref {{
        font-size: 0.85rem;
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
          <a href="./downloads/sat-book.pdf">Bản PDF (106 trang)</a>
          <a href="https://github.com/satlab-uet/sat-book" target="_blank" rel="noreferrer">GitHub ↗</a>
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
    print(f"[✓] Generated HTML reader edition at: {output_path}")

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    build_reader_html(repo_root)
