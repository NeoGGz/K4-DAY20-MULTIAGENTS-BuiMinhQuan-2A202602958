"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .model import make_model
from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    target_out_dir = Path(out_dir) if out_dir is not None else (ROOT / "skills" / "auto")
    results_path = Path(results_dir) / source_condition

    runs = []
    if results_path.exists():
        for run_file in sorted(results_path.glob("*/run.json")):
            try:
                r = json.loads(run_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            if r.get("role") != "learn":
                continue
            trace_file = run_file.parent / "trace.md"
            trace = ""
            if trace_file.exists():
                try:
                    trace = trace_file.read_text(encoding="utf-8")[-6000:]
                except Exception:
                    trace = ""
            failed = [
                (c.get("name", ""), c.get("detail", ""))
                for c in r.get("checks", [])
                if not c.get("passed", False)
            ]
            runs.append({
                "task": r.get("task", run_file.parent.name),
                "failed": failed,
                "trace": trace,
            })

    if not any(run["failed"] for run in runs):
        print("Warning: không có check thất bại ở tác vụ học.")
        return []

    runs_info_parts = []
    for run in runs:
        if not run["failed"]:
            continue
        parts = [f"### Task: {run['task']}", "Failed checks:"]
        for name, detail in run["failed"]:
            detail_str = f" - {detail}" if detail else ""
            parts.append(f"- {name}{detail_str}")
        if run["trace"]:
            parts.append("Trace snippet:")
            parts.append(run["trace"])
        runs_info_parts.append("\n".join(parts))

    runs_info = "\n\n".join(runs_info_parts)
    prompt = (
        f"Bạn viết SKILL cho một tác tử lập trình và phân tích dữ liệu.\n"
        f"Dưới đây là các check thất bại (tên và nhận xét của bot đánh giá) và vết của các lần chạy.\n"
        f"Hãy tìm các lỗi QUY TRÌNH chung (không phải đáp án cụ thể) và viết tối đa {max_skills} skill ngắn\n"
        f"giúp tránh các lỗi đó trên tác vụ MỚI cùng loại.\n\n"
        f"Quy tắc:\n"
        f"- Skill phải tổng quát: không nêu id tác vụ, không nêu tên tệp riêng của một tác vụ, không nêu đáp án hay con số.\n"
        f"- Mỗi skill có frontmatter YAML gồm `name` (chữ thường, gạch ngang) và `description` (một câu: DÙNG KHI NÀO),\n"
        f"  sau đó tối đa 40 dòng chỉ dẫn mệnh lệnh (danh sách kiểm tra - checklist - hoạt động tốt).\n"
        f"- Định dạng đầu ra, đúng từng ký tự:\n"
        f"=== SKILL: <name> ===\n"
        f"---\n"
        f"name: <name>\n"
        f"description: <khi nào dùng>\n"
        f"---\n"
        f"<nội dung>\n"
        f"=== END ===\n\n"
        f"{runs_info}\n"
    )

    llm = model if model is not None else make_model()
    response = llm.invoke(prompt)
    if hasattr(response, "content") and isinstance(response.content, list):
        reply = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content)
    elif hasattr(response, "content"):
        reply = str(response.content)
    else:
        reply = str(response)

    written = []
    for name, text in parse_skill_blocks(reply):
        if len(written) >= max_skills:
            break
        problems = validate_skill(text, expected_name=name)
        if problems:
            continue
        skill_dir = target_out_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(text.strip() + "\n", encoding="utf-8")
        written.append(skill_file)

    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
