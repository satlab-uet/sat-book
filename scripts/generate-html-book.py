#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import html
import re
import sys
from pathlib import Path

CHAPTER_FILES = [
    "ch01-foundations.tex",
    "ch02-quality.tex",
    "ch03-cardinality.tex",
    "ch04-experiments.tex",
    "ch05-shared-counters.tex",
    "ch06-adaptive-counter.tex",
    "ch07-symmetry-channeling.tex",
    "ch08-scheduling.tex",
    "ch09-packing.tex",
    "ch10-bandwidth.tex",
    "ch11-labeling.tex",
    "conclusion.tex",
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


def book_source_digest(repo_root: Path) -> str:
    book_dir = repo_root / "book"
    source_paths = sorted(
        path
        for path in book_dir.rglob("*")
        if path.is_file() and path.suffix in {".tex", ".sty", ".lbx", ".bib"}
    )
    if not source_paths:
        raise FileNotFoundError(f"No LaTeX source found in {book_dir}")

    digest = hashlib.sha256()
    for source_path in source_paths:
        relative_path = source_path.relative_to(repo_root).as_posix()
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(source_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def extract_braced_command(text: str, command: str) -> str:
    match = re.search(rf"\\{re.escape(command)}\s*\{{", text)
    if not match:
        raise ValueError(f"Missing \\{command}{{...}} command")

    opening_brace = match.end() - 1
    depth = 0
    for index in range(opening_brace, len(text)):
        character = text[index]
        if character == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif character == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[opening_brace + 1 : index].strip()
    raise ValueError(f"Unclosed argument for \\{command}")


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

def _extract_brace_arg(tex: str, cmd: str):
    """Find all occurrences of \\cmd{...} in tex, correctly handling nested braces.
    Yields (start, end, content) for each match, where tex[start:end] is the
    full \\cmd{...} token and content is everything between the outer braces."""
    search = '\\' + cmd + '{'
    i = 0
    while True:
        pos = tex.find(search, i)
        if pos == -1:
            break
        j = pos + len(search)   # j now points to first char INSIDE the outer {
        depth = 1
        while j < len(tex) and depth > 0:
            c = tex[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            j += 1
        # tex[pos+len(search) : j-1] is the content; tex[pos:j] is the whole token
        yield pos, j, tex[pos + len(search): j - 1]
        i = j


def _replace_brace_macro(tex: str, cmd: str, replace_fn) -> str:
    """Replace all \\cmd{...} (with proper nested-brace matching) using replace_fn(content)."""
    parts = []
    prev = 0
    for start, end, content in _extract_brace_arg(tex, cmd):
        parts.append(tex[prev:start])
        parts.append(replace_fn(content))
        prev = end
    parts.append(tex[prev:])
    return ''.join(parts)


def expand_tex_math_macros(tex: str) -> str:
    """Pre-expand custom TeX macros into standard LaTeX for max compatibility."""
    # Expand \\set{} and \\card{} FIRST with proper nested-brace extraction,
    # so that inner macros like \\SAT do not yet carry extra braces.
    tex = _replace_brace_macro(tex, 'set',  lambda c: r'\left\{' + c + r'\right\}')
    tex = _replace_brace_macro(tex, 'card', lambda c: r'\left|'   + c + r'\right|')

    # Now expand shorthand macros to their \\mathrm{} equivalents
    tex = re.sub(r'\\SAT\b',        r'\\mathrm{SAT}',        tex)
    tex = re.sub(r'\\UNSAT\b',      r'\\mathrm{UNSAT}',      tex)
    tex = re.sub(r'\\OPT\b',        r'\\mathrm{OPT}',        tex)
    tex = re.sub(r'\\BKS\b',        r'\\mathrm{BKS}',        tex)
    tex = re.sub(r'\\CNF\b',        r'\\mathrm{CNF}',        tex)
    tex = re.sub(r'\\MaxSAT\b',     r'\\mathrm{MaxSAT}',     tex)
    tex = re.sub(r'\\AMK\b',        r'\\mathrm{AMK}',        tex)
    tex = re.sub(r'\\AMO\b',        r'\\mathrm{AMO}',        tex)
    tex = re.sub(r'\\ALK\b',        r'\\mathrm{ALK}',        tex)
    tex = re.sub(r'\\ExactlyOne\b', r'\\mathrm{ExactlyOne}', tex)
    tex = re.sub(r'\\PySAT\b',      r'\\mathrm{PySAT}',      tex)

    # Format comma spacing inside inline bounds like (LB,UB) -> (LB, UB)
    tex = re.sub(r'([A-Za-z0-9]+),([A-Za-z0-9]+)', r'\1, \2', tex)
    return tex

def clean_inline(text: str) -> str:
    # 1. Clean TeX hyperlinks & URLs
    text = re.sub(r'\\href\{([^}]+)\}\{([^}]+)\}', r'<a href="\1" target="_blank" rel="noopener noreferrer">\2</a>', text)
    text = re.sub(r'\\url\{([^}]+)\}', r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', text)

    # 2. Convert double backslashes \\ to <br> line breaks
    text = re.sub(r'\\\\', '<br>', text)

    # 3. Clean texorpdfstring & formatting
    text = re.sub(r'\\texorpdfstring\{([^}]+)\}\{[^}]*\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\textbf\{([^}]+)\}', r'<strong>\1</strong>', text)
    text = re.sub(r'\\texttt\{([^}]+)\}', r'<code>\1</code>', text)
    text = re.sub(r'\\textsc\{([^}]+)\}', r'<span class="small-caps">\1</span>', text)
    
    # 4. Custom TeX Macros outside math
    text = re.sub(r'\\UNSAT\b', 'UNSAT', text)
    text = re.sub(r'\\SAT\b', 'SAT', text)
    text = re.sub(r'\\OPT\b', 'OPT', text)
    text = re.sub(r'\\BKS\b', 'BKS', text)
    text = re.sub(r'\\CNF\b', 'CNF', text)
    text = re.sub(r'\\MaxSAT\b', 'MaxSAT', text)
    text = re.sub(r'\\AMK\b', 'AMK', text)
    text = re.sub(r'\\AMO\b', 'AMO', text)
    text = re.sub(r'\\ALK\b', 'ALK', text)
    text = re.sub(r'\\ExactlyOne\b', 'ExactlyOne', text)
    text = re.sub(r'\\PySAT\b', 'PySAT', text)
    
    # 5. Layout & Spacing TeX Macros
    text = re.sub(r'\\hspace\*?\{[^}]*\}', ' ', text)
    text = re.sub(r'\\vspace\*?\{[^}]*\}', '', text)
    text = re.sub(r'\\qquad\b', ' ', text)
    text = re.sub(r'\\quad\b', ' ', text)
    text = re.sub(r'\\hfill\b', ' ', text)
    text = re.sub(r'\\vfill\b', '', text)
    text = re.sub(r'\\noindent\b', '', text)
    text = re.sub(r'\\clearpage\b', '', text)
    text = re.sub(r'\\newpage\b', '', text)
    text = re.sub(r'\\sffamily\b', '', text)
    text = re.sub(r'\\bfseries\b', '', text)
    text = re.sub(r'\\centering\b', '', text)
    text = re.sub(r'\\raggedright\b', '', text)
    text = re.sub(r'\\arraybackslash\b', '', text)
    text = re.sub(r'\\endfirsthead\b', '', text)
    text = re.sub(r'\\endhead\b', '', text)
    text = re.sub(r'\\small\b', '', text)
    text = re.sub(r'\\mid\b', '|', text)
    
    # 6. Clean escaped punctuation, backslash spaces, and residual backslashes
    text = re.sub(r'\\(?=\s|$)', ' ', text)
    text = re.sub(r'\\([?!.,:;])', r'\1', text)
    text = re.sub(r'([?!.,:;])\\', r'\1 ', text)
    text = re.sub(r'\\[,:;!]', ' ', text)
    text = re.sub(r'\\(?![\w<])', '', text)

    # 7. References & Citations
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    text = re.sub(r'\\cref\{([^}]+)\}', r'(xem mục \1)', text)
    text = re.sub(r'\\ref\{([^}]+)\}', r'(xem hình \1)', text)
    text = re.sub(r'\\eqref\{([^}]+)\}', r'(công thức \1)', text)

    # 8. Punctuation & Quotes
    text = text.replace("---", "—").replace("--", "–")
    text = text.replace("``", "“").replace("''", "”")
    text = format_citations(text)
    
    # 9. Normalize spaces
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()

def capitalize_title(title: str) -> str:
    if not title:
        return ""
    title = title.strip()
    return title[0].upper() + title[1:]

def parse_callouts(text: str) -> str:
    callout_types = [
        ("designrule", "design-rule", "Nguyên lý Thiết kế"),
        ("workedexample", "worked-example", "Ví dụ Thực thi"),
        ("keyidea", "key-idea", "Ý tưởng Cốt lõi"),
        ("summarybox", "summary-box", "Tổng kết Bài học"),
        ("resultbox", "result-box", "Kết quả Thực nghiệm"),
    ]
    for env_name, css_class, default_title in callout_types:
        pattern = r'\\begin\{' + env_name + r'\}\s*(?:\[([^\]]*)\]|\{([^}]*)\})?(.*?)\\end\{' + env_name + r'\}'
        def replace_callout(m):
            raw_title = m.group(1) or m.group(2) or ""
            title = capitalize_title(clean_inline(raw_title.strip())) if raw_title.strip() else default_title
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
            title_text = f" ({capitalize_title(clean_inline(raw_title.strip()))})" if raw_title.strip() else ""
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
        title = capitalize_title(clean_inline(cap_match.group(1))) if cap_match else "Thuật toán"
        
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
    fig_idx = [0]
    def replace_figure(m):
        fig_idx[0] += 1
        block = m.group(1)
        cap_match = re.search(r'\\caption\{([^}]+)\}', block)
        label_match = re.search(r'\\label\{([^}]+)\}', block)
        
        cap_text = clean_inline(cap_match.group(1)) if cap_match else ""
        label_raw = label_match.group(1) if label_match else f"fig_{fig_idx[0]}"
        label_clean = label_raw.replace(":", "_").replace("-", "_")
        
        img_html = f'''
        <div class="reader-figure-img">
          <img src="assets/images/diagrams/{label_clean}.webp" alt="Hình: {cap_text}" loading="lazy" />
        </div>
        '''
        caption_html = f'<div class="reader-inline-caption"><em>Hình: {cap_text}</em></div>' if cap_text else ""
        
        return f'''
        <div class="reader-figure-box" id="{label_clean}">
          {img_html}
          {caption_html}
        </div>
        '''
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
    # Comments & Index
    text = re.sub(r'(?<!\\)%.*', '', text)
    text = re.sub(r'\\index\{[^}]+\}', '', text)
    text = re.sub(r'\\texorpdfstring\{([^}]+)\}\{[^}]*\}', r'\1', text)
    
    # ------------------------------------------------------------------
    # STEP 1: MATH PROTECTION PHASE
    # Extract all KaTeX math blocks, expand custom TeX macros into standard TeX
    # ------------------------------------------------------------------
    math_store: list[str] = []

    def protect_display_math(m):
        idx = len(math_store)
        content = expand_tex_math_macros(m.group(1).strip())
        safe_content = content.replace("<", "&lt;").replace(">", "&gt;")
        math_store.append(f"\\[\n{safe_content}\n\\]")
        return f"\n___MATH_BLOCK_{idx}___\n"

    def protect_inline_math(m):
        idx = len(math_store)
        content = expand_tex_math_macros(m.group(1).strip())
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
    text = re.sub(r'\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}', '', text, flags=re.DOTALL)
    
    text = re.sub(r'\\chapterlead\{((?:[^{}]|\{[^{}]*\})*)\}', r'<div class="chapter-lead">\1</div>', text)
    text = re.sub(r'\\chapter\{([^}]+)\}', '', text)
    text = parse_headings(text)
    
    text = parse_callouts(text)
    text = parse_theorems(text)
    text = parse_algorithms(text)
    text = parse_figures(text)
    
    text = parse_flowdiagrams(text)
    text = parse_tables(text)
    text = parse_lists(text)
    
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
    # ------------------------------------------------------------------
    for idx, math_html in enumerate(math_store):
        result = result.replace(f"___MATH_BLOCK_{idx}___", math_html)

    return result

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#102536">
    <meta name="sat-book-source-sha256" content="__SOURCE_SHA256__">
    <title>Đọc trực tuyến | Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp</title>
    <link rel="shortcut icon" href="./favicon.ico">
    <link rel="icon" type="image/x-icon" href="./favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="./assets/images/favicon-32.png">
    <link rel="apple-touch-icon" href="./assets/images/apple-touch-icon.png">
    <link rel="stylesheet" href="./assets/css/main.css">
    
    <!-- MathJax 3 — full-document math rendering -->
    <script>
      window.MathJax = {
        tex: {
          inlineMath: [['\\\\(', '\\\\)'], ['$', '$']],
          displayMath: [['\\\\[', '\\\\]'], ['$$', '$$']],
          processEscapes: true,
          processEnvironments: true,
          tags: 'ams',
          macros: {
            SAT: '{\\\\mathrm{SAT}}',
            UNSAT: '{\\\\mathrm{UNSAT}}',
            OPT: '{\\\\mathrm{OPT}}',
            BKS: '{\\\\mathrm{BKS}}',
            CNF: '{\\\\mathrm{CNF}}',
            MaxSAT: '{\\\\mathrm{MaxSAT}}',
            AMK: '{\\\\mathrm{AMK}}',
            AMO: '{\\\\mathrm{AMO}}',
            ALK: '{\\\\mathrm{ALK}}',
            ExactlyOne: '{\\\\mathrm{ExactlyOne}}',
            suchthat: '{\\\\;\\\\middle|\\\\;}',
            card: ['{\\\\lvert #1 \\\\rvert}', 1],
            set: ['{\\\\left\\\\{ #1 \\\\right\\\\}}', 1]
          }
        },
        chtml: {
          scale: 1,
          matchFontHeight: false
        },
        startup: {
          typeset: true
        }
      };
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

    <style>
      body {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: var(--font-sans);
        line-height: 1.7;
      }
      .reader-header {
        position: sticky;
        top: 0;
        z-index: 100;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #e2e8f0;
        padding: 12px 0;
      }
      .reader-header-inner {
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .reader-layout {
        display: grid;
        grid-template-columns: 280px 1fr;
        gap: 36px;
        margin-top: 24px;
        margin-bottom: 64px;
      }
      .reader-toc {
        position: sticky;
        top: 80px;
        max-height: calc(100vh - 100px);
        overflow-y: auto;
        padding-right: 12px;
        font-size: 0.88rem;
      }
      .reader-toc h3 {
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 12px;
      }
      .reader-toc ul {
        list-style: none;
        padding: 0;
        margin: 0;
      }
      .reader-toc li {
        margin-bottom: 8px;
      }
      .reader-toc a {
        color: #334155;
        text-decoration: none;
        display: block;
        padding: 4px 8px;
        border-radius: 6px;
      }
      .reader-toc a:hover {
        background: #e2e8f0;
        color: #0f172a;
      }
      .reader-content {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 40px 48px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      }
      .chapter-title {
        font-family: var(--font-display);
        font-size: 1.85rem;
        color: #0f172a;
        margin-bottom: 16px;
        border-bottom: 2px solid #0284c7;
        padding-bottom: 8px;
      }
      .chapter-lead {
        font-size: 1.08rem;
        color: #334155;
        background: #f0f9ff;
        border-left: 4px solid #0284c7;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 28px;
        font-style: italic;
      }
      .reader-h2 {
        font-family: var(--font-display);
        font-size: 1.35rem;
        color: #0f172a;
        margin-top: 36px;
        margin-bottom: 14px;
      }
      .reader-h3 {
        font-family: var(--font-display);
        font-size: 1.12rem;
        color: #1e293b;
        margin-top: 24px;
        margin-bottom: 10px;
      }
      .reader-callout {
        border-radius: 6px;
        padding: 18px 22px;
        margin: 20px 0;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #000000;
      }
      .reader-callout.design-rule,
      .reader-callout.worked-example,
      .reader-callout.key-idea,
      .reader-callout.summary-box,
      .reader-callout.result-box,
      .reader-callout.theorem-box,
      .reader-callout.lemma-box,
      .reader-callout.proposition-box,
      .reader-callout.example-box {
        background: #f8fafc;
        border-left-color: #000000;
      }
      .callout-header {
        font-family: var(--font-display);
        font-size: 1.02rem;
        margin-bottom: 8px;
        color: #000000;
        font-weight: 700;
      }
      .callout-body {
        font-size: 0.95rem;
        line-height: 1.65;
      }
      .reader-figure-box {
        margin: 28px 0;
        text-align: center;
      }
      .reader-figure-img {
        margin-bottom: 10px;
        display: flex;
        justify-content: center;
      }
      .reader-figure-img img {
        max-width: 100%;
        height: auto;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        background: #ffffff;
        padding: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
      }
      .reader-inline-caption {
        font-size: 0.92rem;
        color: #475569;
        margin-top: 6px;
      }
      .reader-proof {
        background: #f8fafc;
        border-left: 3px solid #94a3b8;
        padding: 12px 18px;
        margin: 16px 0;
        font-size: 0.94rem;
      }
      .proof-qedsymbol {
        float: right;
        color: #64748b;
      }
      .reader-algorithm-box {
        background: #0f172a;
        color: #f8fafc;
        border-radius: 8px;
        padding: 18px;
        margin: 24px 0;
        font-family: var(--font-mono);
        font-size: 0.88rem;
      }
      .algo-header {
        color: #38bdf8;
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
        margin-bottom: 12px;
      }
      .reader-table-wrapper {
        overflow-x: auto;
        margin: 24px 0;
      }
      .reader-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
      }
      .reader-table th {
        background: #f1f5f9;
        color: #0f172a;
        font-weight: 700;
        padding: 10px 14px;
        border: 1px solid #cbd5e1;
        text-align: left;
      }
      .reader-table td {
        padding: 8px 14px;
        border: 1px solid #e2e8f0;
      }
      .reader-table tr:nth-child(even) {
        background: #f8fafc;
      }
      .reader-table-caption, .reader-inline-caption {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 8px;
        text-align: center;
      }
      .reader-flow-diagram {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin: 24px 0;
        flex-wrap: wrap;
      }
      .flow-box {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 0.88rem;
        font-weight: 600;
      }
      .flow-box.highlight {
        background: #e0f2fe;
        border-color: #0284c7;
        color: #0369a1;
      }
      .flow-arrow {
        color: #94a3b8;
        font-size: 1.2rem;
      }
      .flow-branches {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .flow-subbox {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
      }
      .reader-figure-img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 16px 0 8px;
      }
      .cite {
        color: #1d4ed8;
        font-weight: 600;
      }
      .small-caps {
        font-variant: small-caps;
        letter-spacing: 0.05em;
      }

      /* KaTeX & MathJax Font Fallback Overrides to Protect Vietnamese Diacritics */
      .katex, .katex .text, .katex-display {
        font-family: var(--font-sans) !important;
      }
      
      @media (max-width: 900px) {
        .reader-layout {
          grid-template-columns: 1fr;
        }
        .reader-toc {
          position: static;
          max-height: none;
          margin-bottom: 24px;
        }
        .reader-content {
          padding: 24px;
        }
      }
    </style>
  </head>
  <body>
    <!-- Top Announcement Banner -->
    <div class="top-banner">
      SATLab paper on Cyclic Antibandwidth accepted in Computational Optimization and Applications (Q1 ISI)! <a href="./publications.html">View Publications ↗</a>
    </div>

    <header class="reader-header">
      <div class="shell reader-header-inner">
        <a class="brand" href="./">
          <img src="./assets/images/satlab.png" alt="SATLab Logo" class="brand-logo-img">
          <span class="brand-title">SATLab</span>
        </a>
        <div style="display: flex; gap: 12px; align-items: center;">
          <a href="./downloads/sat-book.pdf" class="btn btn-outline" style="padding: 4px 12px; font-size: 0.82rem;">Tải PDF ↗</a>
          <a href="./" class="btn btn-primary" style="padding: 4px 12px; font-size: 0.82rem;">Trở về Trang chủ</a>
        </div>
      </div>
    </header>

    <main class="shell reader-layout">
      <aside class="reader-toc">
        <h3>Mục lục Sách Chuyên khảo</h3>
        <ul>
          __TOC_ITEMS__
        </ul>
      </aside>

      <article class="reader-content">
        <h1 style="font-family: var(--font-display); font-size: 1.85rem; color: #0f172a; margin-bottom: 24px; font-weight: 800;">Sách Chuyên khảo: Biểu diễn SAT tối ưu cho các bài toán tối ưu hóa tổ hợp</h1>
        __CHAPTERS_HTML__
      </article>
    </main>

    <footer class="site-footer">
      <div class="shell footer-grid">
        <div>
          <img src="./assets/images/satlab.png" alt="SATLab Logo" class="footer-logo">
          <div class="footer-brand">SATLab UET — Phòng nghiên cứu Biểu diễn SAT</div>
          <p>© 2026 SATLab UET. All rights reserved.</p>
        </div>
        <div>
          <a href="https://www.facebook.com/satlab.uet/" target="_blank" rel="noopener noreferrer" style="color: #94a3b8; margin-right: 16px;">Facebook ↗</a>
          <a href="./about.html" style="color: #94a3b8; margin-right: 16px;">Giới thiệu</a>
          <a href="./downloads/sat-book.pdf" style="color: #94a3b8;">Tải PDF</a>
        </div>
      </div>
    </footer>


  </body>
</html>
"""

def generate_html_book(output_path: Path, repo_root: Path):
    load_bib_entries(repo_root)
    source_digest = book_source_digest(repo_root)
    chapters_dir = repo_root / "book" / "chapters"

    chapter_titles = [
        ("ch01-foundations.tex", "Chương 1: Nền tảng Biểu diễn và Bộ giải SAT"),
        ("ch02-quality.tex", "Chương 2: Đánh giá Chất lượng và Tiêu chuẩn Mã hóa"),
        ("ch03-cardinality.tex", "Chương 3: Phép Mã hóa Ràng buộc Cardinality"),
        ("ch04-experiments.tex", "Chương 4: Quy trình và Đánh giá Thực nghiệm"),
        ("ch05-shared-counters.tex", "Chương 5: Phép Mã hóa Bộ đếm Dùng chung"),
        ("ch06-adaptive-counter.tex", "Chương 6: Phép Mã hóa Bộ đếm Thích nghi"),
        ("ch07-symmetry-channeling.tex", "Chương 7: Phá Đối xứng và Kênh liên kết Variable-Channeling"),
        ("ch08-scheduling.tex", "Chương 8: Ứng dụng trong Lập lịch và Dây chuyền Sản xuất"),
        ("ch09-packing.tex", "Chương 9: Ứng dụng trong Bài toán Đóng gói 2D"),
        ("ch10-bandwidth.tex", "Chương 10: Ứng dụng trong Gán nhãn Đồ thị và Antibandwidth"),
        ("ch11-labeling.tex", "Chương 11: Ứng dụng trong Radio Labeling"),
        ("conclusion.tex", "Kết luận và Hướng phát triển"),
    ]

    toc_html_list = []
    chapters_html_list = []

    for idx, (filename, title) in enumerate(chapter_titles, 1):
        filepath = chapters_dir / filename
        if not filepath.exists():
            continue

        slug = filename.replace(".tex", "")
        toc_html_list.append(f'<li><a href="#chap-{idx}">{title}</a></li>')

        raw_tex = filepath.read_text(encoding="utf-8")
        clean_html = clean_latex_document(raw_tex)

        # Inject figure if mapped
        fig_html = ""
        prefix = slug.split("-")[0]
        if prefix in FIGURE_MAP:
            img_name, caption = FIGURE_MAP[prefix]
            fig_html = f'''
            <div style="text-align: center; margin: 24px 0;">
              <img src="./assets/images/diagrams/{img_name}" alt="{caption}" class="reader-figure-img">
              <div class="reader-inline-caption"><em>{caption}</em></div>
            </div>
            '''

        ch_block = f'''
        <section id="chap-{idx}" data-slug="{slug}" style="margin-bottom: 48px; scroll-margin-top: 100px;">
          <h2 class="chapter-title">{title}</h2>
          {fig_html}
          {clean_html}
        </section>
        '''
        chapters_html_list.append(ch_block)

    full_html = HTML_TEMPLATE.replace("__SOURCE_SHA256__", source_digest)
    full_html = full_html.replace("__TOC_ITEMS__", "\n".join(toc_html_list))
    full_html = full_html.replace("__CHAPTERS_HTML__", "\n".join(chapters_html_list))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(full_html, encoding="utf-8")
    print(f"[✓] Generated clean HTML reader edition at: {output_path}")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    output_file = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "_site" / "read.html"
    )
    generate_html_book(output_file, repo_root)
