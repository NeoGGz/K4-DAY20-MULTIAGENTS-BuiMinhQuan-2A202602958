"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Delegate to this subagent when you need to inspect files, read instructions or READMEs, "
                "investigate log files or dataset schemas, and report objective findings without making any changes."
            ),
            "system_prompt": (
                "You are an investigative subagent. Your responsibility is to inspect workspace files, "
                "analyze errors, logs, code, or datasets, and provide a clear, factual report. "
                "Do not modify or delete any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Delegate to this subagent when you need to perform modifications, create or edit code and data files, "
                "or execute shell commands and tests to verify fixes."
            ),
            "system_prompt": (
                "You are an implementation subagent. Your responsibility is to execute code changes, write files, "
                "run tests or scripts via the execute tool, and verify that implementations work as required."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Delegate to this subagent when you need an independent check of changes against task instructions, "
                "format constraints, and edge cases before completing the task."
            ),
            "system_prompt": (
                "You are a review subagent. Your responsibility is to critically inspect the workspace files and outputs "
                "against task requirements, check for missing edge cases or format violations, and report issues without modifying files."
            ),
        },
    ]
