#!/usr/bin/env python3

import re
from pathlib import Path

def polish_file(file_path: Path):
    if not file_path.exists():
        return
    text = file_path.read_text(encoding="utf-8")
    
    replacements = [
        # User explicitly requested terminology preferences
        (r"bài toán xếp khối", "bài toán đóng gói"),
        (r"Bài toán xếp khối", "Bài toán đóng gói"),
        (r"xếp khối 2D", "đóng gói 2D"),
        (r"xếp khối 3D", "đóng gói 3D"),
        (r"xếp khối", "đóng gói"),
        (r"độ rộng băng", "băng thông"),
        (r"Độ rộng băng", "Băng thông"),
        (r"dán nhãn", "gán nhãn"),
        (r"Dán nhãn", "Gán nhãn"),
        (r"triệt tiêu đối xứng", "phá vỡ đối xứng"),
        (r"Triệt tiêu đối xứng", "Phá vỡ đối xứng"),
        (r"phá đối xứng", "phá vỡ đối xứng"),
        (r"Phá đối xứng", "Phá vỡ đối xứng"),

        # General Core Concepts
        (r"bộ gán bộ phận", "phép gán một phần"),
        (r"Phép gán bộ phận", "Phép gán một phần"),
        (r"sức mạnh lan truyền", "khả năng suy diễn lan truyền"),
        (r"Sức mạnh lan truyền", "Khả năng suy diễn lan truyền"),
        (r"độ tương thích cung", "độ nhất quán cung tổng quát (GAC)"),
        (r"Độ tương thích cung", "Độ nhất quán cung tổng quát (GAC)"),
        (r"Ba dòng nghiên cứu hội tụ", "Sự giao thoa của ba hướng nghiên cứu"),
        (r"nằm ở giao điểm của ba truyền thống", "là sự kết hợp của ba hướng tiếp cận cốt lõi"),
        (r"Ba góc nhìn bổ sung", "Ba tiêu chí bổ trợ"),
        (r"ba góc nhìn bổ sung", "ba tiêu chí bổ trợ"),
        (r"góc nhìn bổ sung", "tiêu chí bổ trợ"),
        (r"Dây chuyền triển khai", "Quy trình triển khai"),
        (r"chứng cứ cận trên", "bằng chứng cận trên"),
        (r"chứng cứ cận dưới", "chứng nhận cận dưới"),
        (r"chứng cứ khả thi", "bằng chứng khả thi"),
        (r"chứng cứ tối ưu", "chứng nhận tối ưu"),
        (r"chứng cứ ngưỡng", "bằng chứng ngưỡng"),
        (r"chứng cứ", "bằng chứng"),
        (r"thí nghiệm bóc tách", "thí nghiệm phân tích thành phần (ablation study)"),
        (r"bóc tách", "phân tích thành phần (ablation)"),
        (r"cửa sổ cắt biên", "cửa sổ giao biên"),
        (r"ràng buộc cắt biên", "ràng buộc giao biên"),
        (r"cắt biên", "giao biên"),
        (r"tính đúng đắn", "tính đúng"),
        (r"kiểm duyệt phải", "dữ liệu bị giới hạn thời gian"),
        (r"mặt Pareto", "biên Pareto (Pareto frontier)"),
        (r"Mặt Pareto", "Biên Pareto (Pareto frontier)"),

        # Visuals & Metaphors
        (r"Một vòng CDCL nhìn từ góc độ thiết kế phép biểu diễn\.", "Sơ đồ vòng lặp CDCL dưới góc nhìn thiết kế biểu diễn."),
        (r"Lan truyền nhìn từ hai biên", "Cơ chế suy diễn lan truyền hai chiều"),
        (r"viên gạch của mạng sắp xếp", "thành phần cơ sở của mạng sắp xếp"),
        (r"viên gạch", "thành phần cơ sở"),

        # Counters & Modules
        (r"bộ đếm dùng chung", "bộ đếm chia sẻ (Shared Counter)"),
        (r"Bộ đếm dùng chung", "Bộ đếm chia sẻ (Shared Counter)"),
        (r"dùng chung", "chia sẻ"),
        (r"Dùng chung", "Chia sẻ"),

        # Processing & Execution
        (r"xử lý trước", "tiền xử lý (preprocessing)"),
        (r"xử lý trong", "xử lý trong khi giải (in-processing)"),
        (r"được cho bởi", "được xác định bởi"),
        (r"cho ra", "thu được"),
        (r"được Tseitin hóa\.", "được chuyển đổi theo phương pháp Tseitin."),
    ]
    
    new_text = text
    for pat, repl in replacements:
        new_text = re.sub(pat, repl, new_text)
    
    if new_text != text:
        file_path.write_text(new_text, encoding="utf-8")
        print(f"[✓] Polished prose in {file_path.name}")

def main():
    repo_root = Path(__file__).resolve().parent.parent
    chapters = sorted(repo_root.glob("book/chapters/*.tex"))
    main_tex = repo_root / "book" / "main.tex"
    
    for ch in chapters:
        polish_file(ch)
    polish_file(main_tex)
    print("Completed terminology updates!")

if __name__ == "__main__":
    main()
