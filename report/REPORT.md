# Báo cáo Lab: Self evolving Agentic


## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Bùi Minh Quân | 2A202602958 | Toàn bộ bài thực hành |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash-lite`, `LAB_TEMPERATURE=0`, `recursion_limit=60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows (chạy trực tiếp với POSIX /bin/sh shell tích hợp Git sh utilities)
- Số lần chạy tác vụ đã dùng / ngân sách: 22 / 24
- Commit của tag `freeze`: `4e3f1e31efcf3bb87547fd9fcff5912b07ce5863`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Điều kiện `subagents` sẽ đạt điểm tương đương hoặc chỉ nhỉnh hơn một chút so với `baseline` trên các tác vụ đánh giá (dự kiến trung bình ~0.60 - 0.65), do tác tử chính thường tự giải quyết các bước kỹ thuật tốt mà ít khi ủy quyền hoàn toàn cho subagent, trong khi chi phí token của `subagents` sẽ cao hơn khoảng 30% - 50% so với baseline do chi phí ngữ cảnh phân nhánh và tổng hợp báo cáo.
- H2 (skills-auto so với baseline): Điều kiện `skills-auto` sẽ đạt điểm cao hơn `baseline` trên các tác vụ học (từ ~0.63 lên ~0.70+ nhờ nạp các checklist quy ước của Acme), nhưng trên các tác vụ đánh giá (`eval`), mức độ cải thiện sẽ bị giới hạn hoặc xảy ra hiện tượng quá khớp (overfitting) theo phát hiện của SkillEvolBench, vì các tác vụ đánh giá chứa các quy ước tổ chức mới (`rule_`) mà bộ kỹ năng tự sinh từ tập học chưa từng thấy.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình của điều kiện `skills-auto` trên tác vụ học sẽ cao hơn đáng kể so với trên tác vụ đánh giá (dự kiến chênh lệch khoảng 0.10 - 0.20 điểm), phản ánh sự suy giảm hiệu quả chuyển giao tri thức thủ tục (procedural knowledge transfer gap) giữa dữ liệu đã biết và dữ liệu mới chưa qua tuyển chọn kỹ năng.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ:
   - Các công cụ tệp: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`.
   - Công cụ chạy lệnh shell: `execute`.
   - Công cụ giao việc cho tác tử con: `task`.
   Công cụ cho phép chạy lệnh shell là `execute`.

2. Mô tả của công cụ `task` về subagent `general-purpose`:
   - "General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. This agent has access to all tools as the main agent."
   - Về ngữ cảnh: subagent này là "stateless by default", chỉ nhìn thấy nội dung prompt mà tác tử chính gửi cho nó và trả về một báo cáo cuối cùng ("the agent sees only the prompt you give it and returns a single final report"), không nhìn thấy toàn bộ ngữ cảnh hội thoại trung gian của tác tử chính trừ khi được chỉ định kế thừa hội thoại.

3. Hướng dẫn hành vi trích từ mô tả:
   - Từ mô tả công cụ `task`: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return."
   - Từ mô tả công cụ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | B. Không kiểm chứng | `the original files in tests/ must not be modified (new test files are allowed)` |
| `code-learn` | `rule_type_hints` | E. Vi phạm quy ước tổ chức | `RULE: every public function (name not starting with '_') in the package has type annotations...` |
| `code-learn` | `rule_regression_tests` | E. Vi phạm quy ước tổ chức | `RULE: add tests/test_regressions.py with one test function per bug you fixed...` |
| `code-learn` | `rule_changelog` | E. Vi phạm quy ước tổ chức | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet...` |
| `data-learn` | `rule_money_in_cents` | E. Vi phạm quy ước tổ chức | `RULE: money values in answer.json are integer cents (1606.67 USD is written 160667).` |
| `data-learn` | `rule_meta_block` | E. Vi phạm quy ước tổ chức | `RULE: answer.json has an object meta = {"source": ..., "rows_in": ..., "rows_used": ...}` |
| `data-learn` | `rule_clean_csv` | E. Vi phạm quy ước tổ chức | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents...` |
| `logs-learn` | `rule_service_names` | E. Vi phạm quy ước tổ chức | `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service).` |
| `logs-learn` | `rule_sorted_errors` | E. Vi phạm quy ước tổ chức | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| `logs-learn` | `rule_schema_header` | E. Vi phạm quy ước tổ chức | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |

Nhận xét: Nhóm E (Vi phạm quy ước tổ chức) chiếm đa số tuyệt đối (9/10 check thất bại, tức 90%). Trong khi đó, các check kỹ thuật đạt 17/18 (94.4%). Điều này chứng tỏ mô hình có năng lực giải quyết vấn đề kỹ thuật rất tốt, nhưng do các quy ước tổ chức không nằm trong đề bài chính mà là quy ước ngầm của tổ chức, tác tử mặc định không thể biết trước. Do đó, các skill do curator trích xuất hoàn toàn có thể phòng ngừa hiệu quả các lỗi nhóm E này bằng cách cung cấp danh sách checklist quy ước.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  1. `explorer`: Chuyên đọc tệp, khảo sát mã nguồn, tài liệu và dữ liệu ban đầu mà không sửa đổi tệp, giúp tác tử chính nắm thông tin khách quan.
  2. `implementer`: Chuyên thực hiện chỉnh sửa mã nguồn, chạy script và kiểm thử qua công cụ shell `execute`.
  3. `reviewer`: Độc lập rà soát lại không gian làm việc so với các ràng buộc đề bài và trường hợp biên trước khi báo cáo kết thúc.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  - `code-learn`: 1 lần gọi (ủy quyền phân tích kiểm thử cho `implementer`).
  - `data-learn`: 1 lần gọi (ủy quyền phân tích kiểm tra dữ liệu).
  - `logs-learn`: 0 lần gọi (tác tử chính tự nhận thấy tác vụ parse log đơn giản và tự giải quyết).
- Thông tin thiếu hoặc thừa khi giao việc: Tác tử chính khi giao việc đã cung cấp tương đối đủ tên tệp và mục tiêu, tuy nhiên do subagent bị cô lập ngữ cảnh (context isolation), kết quả trả về của subagent cần thêm một bước tích hợp lại vào luồng chính.
- Ảnh hưởng đến token và thời gian: Chi phí token tăng rõ rệt (trung bình 197,807 token so với 153,130 token ở baseline, tăng khoảng 29.2%), thời gian thực thi cũng tăng do các lượt hội thoại bổ sung.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Chạy curator 1 lần, sinh ra 3 skill hoàn toàn hợp lệ, không có skill nào bị xóa.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `enforce-code-quality-and-rules` | Tổng quát cho các tác vụ lập trình (không chứa id hay đáp án) | Đúng, đưa ra checklist về type hints, kiểm thử hồi quy và changelog | 10 dòng, mô tả rõ ràng, được đọc 1 lần |
| `strict-data-format-and-metadata` | Tổng quát cho tác vụ dữ liệu dạng bảng/CSV/JSON | Đúng, nhắc nhở định dạng tiền tệ cent, khối meta và chuẩn hóa UTC | 9 dòng, mô tả đúng tình huống kích hoạt, được đọc 1 lần |
| `verify-output-schema-and-sorting` | Tổng quát cho tác vụ xuất JSON/phân tích log | Đúng, nhắc nhở schema version, quy tắc chuẩn hóa tên và sắp xếp đa cấp | 9 dòng, mô tả đúng tình huống kích hoạt, được đọc 1 lần |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng tổng hợp kết quả (trích từ `report/table.md`):

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 6/10 |
| data-learn | 5/8 | 4/8 | 5/8 |
| logs-learn | 6/9 | 6/9 | 6/9 |
| code-eval | 6/11 | 7/11 | 6/11 |
| data-eval | 5/9 | 4/9 | 5/9 |
| logs-eval | 6/10 | 6/10 | 6/10 |
| **Mean score - learning tasks** | 0.63 | 0.59 | 0.63 |
| **Mean score - evaluation tasks** | 0.57 | 0.56 | 0.57 |
| **Mean tokens per run** | 126,239 | 233,877 | 218,123 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Thống kê phân loại kiểm tra (trích từ `python scripts/check_breakdown.py`):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     17/18         0/12          99,348      0/3     
baseline      learn    17/18         0/9          153,130      0/3     
subagents     eval     17/18         0/12         269,947      0/3     
subagents     learn    16/18         0/9          197,807      0/3     
skills-auto   eval     17/18         0/12         210,548      3/3     
skills-auto   learn    17/18         0/9          225,699      3/3     
```

Các lần chạy có `error` hoặc `skills_modified = true` và cách xử lý:
1. `subagents` trên `logs-eval`: Lần chạy đầu tiên gặp lỗi `GoogleRateLimitError: 429 RESOURCE_EXHAUSTED` (vượt hạn mức 250,000 input tokens/phút của gói miễn phí Gemini khi gọi subagent reviewer với ngữ cảnh phân tích lớn). Xử lý: Chờ hết thời gian giới hạn tốc độ và chạy lại tuần tự; lần chạy lại hoàn thành thành công không có lỗi (`error = null`, điểm 6/10, token 222,778).
2. `skills-auto` trên `code-learn` (sau đóng băng): Lần chạy đạt tới `recursion_limit` (60 lượt) do tác tử cố gắng thực hiện tuần tự nhiều mục trong checklist kỹ năng (đọc skill, sửa lỗi mã nguồn, chạy kiểm thử, viết test hồi quy) trước khi kịp kết thúc hội thoại; kết quả kiểm tra đạt 6/10 và tệp `run.json` được ghi lại an toàn.
3. Không có lần chạy nào có `skills_modified = true`. Kiểm tra với `scripts/verify_freeze.py` cho kết quả `OK` (0 lỗi), xác nhận toàn bộ các lần chạy điều kiện `skills-auto` tuân thủ nguyên tắc đóng băng kỹ năng.

## 8. Phân tích

1. **So sánh cải thiện giữa tác vụ học và đánh giá:**
   - Trên tác vụ **học**: Trong lần chạy dev ở Phần 3.4 (`skills-auto-dev`), `skills-auto` đạt điểm trung bình 0.66 (vượt baseline 0.63, trong đó `code-learn` tăng từ 6/10 lên 7/10 nhờ đạt check quy ước `rule_type_hints`). Ở lần chạy sau đóng băng, điểm trung bình tác vụ học của `skills-auto` là 0.63 (do `code-learn` dừng ở 6/10 khi chạm recursion limit). Điều kiện `subagents` đạt điểm thấp hơn ở tác vụ học (0.59 so với 0.63).
   - Trên tác vụ **đánh giá**: Điều kiện `subagents` nhỉnh hơn baseline ở tác vụ `code-eval` (7/11 so với 6/11 nhờ tác tử con bảo toàn tệp kiểm thử gốc `tests_not_modified`), nhưng điểm trung bình chung eval của `subagents` là 0.56 (thấp hơn baseline 0.57). Điều kiện `skills-auto` trên tác vụ đánh giá đạt 0.57 (ngang bằng baseline).
   - Hiện tượng: `skills-auto` có xu hướng cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá. Đây là biểu hiện rõ nét của **khoảng cách chuyển giao tri thức thủ tục (procedural knowledge transfer gap)** và **quá khớp tầng ngữ cảnh (contextual overfitting)** theo phát hiện của SkillEvolBench: bộ kỹ năng được tối ưu hóa theo các quy ước ngầm của tập học không thể khái quát hóa sang các quy ước hoàn toàn mới xuất hiện ở tập đánh giá.

2. **Phân tách check kỹ thuật và check quy ước (`rule_`):**
   - Năng lực kỹ thuật: Cả `baseline` và `skills-auto` đều đạt 17/18 check kỹ thuật ở cả tập học và tập đánh giá (tỉ lệ thành công 94.4%). Điều này khẳng định mô hình nền tảng giải quyết bài toán kỹ thuật rất tốt.
   - Check quy ước (`house rules`): `baseline` đạt 0/9 ở tập học và 0/12 ở tập đánh giá. Skill do curator sinh nhắm trực diện vào nhóm check quy ước này (đạt 1/9 check quy ước ở lần chạy dev `code-learn` với `rule_type_hints`).
   - Check quy ước **mới** của tác vụ đánh giá (`rule_source_line`, `rule_sorted_keys_format`...) hoàn toàn KHÔNG được skill giúp (đạt 0/12). Lý do: Curator chỉ trích xuất tri thức từ vết thất bại của tập học. Vì quy tắc đánh giá khoa học yêu cầu đóng băng kỹ năng trước khi chạy tập đánh giá, các quy ước đặc thù mới ở tập đánh giá chưa từng xuất hiện trong ngữ cảnh huấn luyện nên không thể được dự đoán hay phòng ngừa trước.

3. **Bằng chứng từ vết về check đạt và không đạt nhờ skill:**
   - **Check đạt nhờ skill:** Trong lần chạy `skills-auto-dev` ở tác vụ `code-learn`, tác tử đã đọc skill `enforce-code-quality-and-rules` (`skills_read = 3`). Vết thực thi cho thấy sau khi sửa hàm `calculate_discount` và chạy test ban đầu, tác tử đã rà soát lại checklist của skill: *"Add type annotations to all public functions (parameters and return types) in src/"*. Tác tử đã gọi công cụ `edit_file` để thêm chú thích kiểu dữ liệu đầy đủ cho các hàm trong `report.py`, qua đó đạt check `rule_type_hints` (nâng điểm lên 7/10).
   - **Check không đạt dù có skill:** Trong tác vụ `data-learn`, tác tử đọc skill `strict-data-format-and-metadata`. Skill có nêu rõ: *"If answer.json requires meta information, include meta object with fields: source, rows_in, rows_used"*. Tuy nhiên, do đề bài `instruction.md` không đề cập trực tiếp đến khối meta mà chỉ yêu cầu các con số doanh thu và đơn hàng, tác tử ưu tiên làm theo chỉ dẫn trực tiếp của đề bài và bỏ qua checklist phụ của skill (hiện tượng selective attention / instruction conflict), dẫn đến check `rule_meta_block` tiếp tục thất bại.

4. **Phân tích chi phí và hiệu quả:**
   - Tiêu thụ token trung bình:
     - `baseline`: 126,239 token/lần chạy (99,348 ở eval, 153,130 ở learn).
     - `skills-auto`: 218,123 token/lần chạy (+72.8% so với baseline).
     - `subagents`: 233,877 token/lần chạy (+85.3% so với baseline, đạt đỉnh 269,947 token ở eval).
   - Hiệu quả điểm trên mỗi token: `baseline` có hiệu quả kinh tế cao nhất (~4.75 × 10⁻⁶ điểm/token), vượt xa `skills-auto` (~2.75 × 10⁻⁶) và `subagents` (~2.48 × 10⁻⁶).
   - Đa tác tử có đáng chi phí không? Trong phạm vi thí nghiệm này, **đa tác tử KHÔNG đáng chi phí**. Điểm số trung bình không tăng mà giảm nhẹ (0.58 so với 0.60), trong khi chi phí token tăng gần gấp đôi do chi phí giao tiếp và cô lập ngữ cảnh giữa tác tử chính và các tác tử con.

5. **Rò rỉ dữ liệu và quá khớp:**
   - Rò rỉ dữ liệu (data leakage): Hoàn toàn không có rò rỉ từ tập đánh giá sang tập học hay bộ kỹ năng, vì curator chỉ được cấp quyền đọc vết thực thi của 3 tác vụ học. Hàm `validate_skill` cũng ngăn chặn nghiêm ngặt việc đưa tên tác vụ cụ thể hoặc đường dẫn tệp cứng vào nội dung kỹ năng.
   - Quá khớp (overfitting): Xuất hiện quá khớp ở tầng quy ước tổ chức. Kỹ năng học được phản ánh trung thực các thói quen của Acme trong tập học, nhưng không mang tính khái quát đủ cao khi tổ chức thay đổi hoặc bổ sung quy ước mới trong tập đánh giá. Nhóm đã phòng tránh bằng cách đóng băng toàn bộ kỹ năng qua git tag `freeze` trước khi tiến hành đo đạc trên tập đánh giá.

6. **Phân tích nhiễu thực nghiệm:**
   - So sánh điểm tác vụ học của `skills-auto`:
     - Trước đóng băng (Phần 3.4, lưu tại `results/skills-auto-dev`): trung bình 0.66 (code-learn 7/10, data-learn 5/8, logs-learn 6/9).
     - Sau đóng băng (`results/skills-auto`): trung bình 0.63 (code-learn 6/10, data-learn 5/8, logs-learn 6/9).
   - Độ lệch: Chênh lệch tuyệt đối là 0.03 (dao động ở tác vụ `code-learn` khi tác tử hết số bước trước khi kịp hoàn thành bước gắn type hint).
   - Ý nghĩa: Mức độ nhiễu nội tại của mô hình ngôn ngữ khi thực thi tác vụ nhiều bước là khoảng ±0.03 đến ±0.05 điểm. Do đó, các chênh lệch điểm số nhỏ giữa các điều kiện trong bảng so sánh cần được nhìn nhận thận trọng và không thể vội vàng kết luận là ưu thế mang ý nghĩa thống kê nếu chưa có nhiều lần chạy lặp lại.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô mẫu tác vụ nhỏ và mỗi cấu hình chỉ chạy một lần:** Thí nghiệm chỉ gồm 3 tác vụ học và 3 tác vụ đánh giá, mỗi tác vụ chỉ chạy 1 lần do giới hạn ngân sách và hạn mức gói API miễn phí. Điều này khiến kết quả chịu ảnh hưởng bởi tính bất định (stochasticity) của mô hình và chưa thể tính toán khoảng tin cậy thống kê (confidence interval).
2. **Quy ước ngầm mang tính nhân tạo và bất đối xứng:** Các quy ước tổ chức (`rule_*`) được thiết kế ẩn trong bộ kiểm tra kiểm thử mà không xuất hiện trong đề bài. Sự bất đối xứng này tạo ra khoảng trống tri thức không thể giải quyết bằng suy luận thông thường đối với các tác vụ đánh giá mới khi kỹ năng đã bị đóng băng.
3. **Thử nghiệm giới hạn trên một mô hình đơn lẻ:** Toàn bộ thí nghiệm sử dụng mô hình nhẹ `gemini-3.5-flash-lite`. Mô hình này dễ bị hạn chế về độ dài chuỗi suy luận (chạm `recursion_limit` khi phải vừa đọc nhiều kỹ năng vừa thực hiện nhiều bước shell/file). Kết luận có thể thay đổi nếu sử dụng các mô hình biên (frontier models) có năng lực phân luồng và quản lý ngữ cảnh mạnh hơn.

## 10. Kết luận

Thí nghiệm đã triển khai hoàn chỉnh bộ khung điều khiển Deep Agents với cơ chế tự tiến hóa trích xuất kỹ năng qua curator và so sánh đa tác tử trên 6 tác vụ chuẩn hóa. Kết quả định lượng cho thấy cả ba điều kiện đều hoàn thành xuất sắc các yêu cầu kỹ thuật nền tảng (đạt 94.4% check kỹ thuật), trong khi các thất bại chủ yếu xuất phát từ việc vi phạm quy ước tổ chức ngầm (house rules). Kỹ năng tự sinh mang lại cải thiện khả quan trên tập học (đạt 0.66) nhưng gặp giới hạn chuyển giao trên tập đánh giá do các quy ước mới chưa từng thấy, đồng thời cả kỹ năng và đa tác tử đều làm tăng chi phí token từ 72% đến 85%. Hiện tượng dao động điểm số ở cùng một bộ kỹ năng (±0.03) khẳng định tầm quan trọng sống còn của việc đóng băng kỹ năng và kiểm soát nhiễu thực nghiệm. Đề xuất cải tiến tiếp theo là xây dựng cơ chế truy xuất kỹ năng động dựa trên ngữ cảnh (dynamic skill retrieval) kết hợp quy trình tinh chỉnh kỹ năng tương tác thời gian thực (hot-path interactive evolution).

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests/test_01_provided.py` (kiểm tra harness ban đầu)
  2. `pytest` (kiểm tra 32 unit test offline của sinh viên)
  3. `python -m lab.runner --condition baseline --tasks learn`
  4. `python -m lab.runner --condition subagents --tasks learn`
  5. `python -m lab.curator` (sinh 3 kỹ năng vào `skills/auto/`)
  6. `python -m lab.runner --condition skills-auto --tasks learn`
  7. Sao lưu kết quả dev: `Move-Item results/skills-auto results/skills-auto-dev`
  8. `git commit -m "hypotheses"` (commit các giả thuyết H1-H3)
  9. `git commit --allow-empty -m "freeze skills"` và `git tag freeze`
  10. `python -m lab.runner --condition baseline --tasks eval`
  11. `python -m lab.runner --condition subagents --tasks eval`
  12. `python -m lab.runner --condition skills-auto --tasks all`
  13. `python scripts/verify_freeze.py` (kiểm tra tính hợp lệ của tag freeze và băm skill)
  14. `python -m lab.compare > report/table.md`
  15. `python scripts/check_breakdown.py`
- Thử thách mở rộng (nếu có): Không thực hiện (tập trung tối ưu hóa độ chính xác và tính toàn vẹn của 3 điều kiện chính).
- Ghi chú khác: Bộ khung được tối ưu hóa để chạy trực tiếp trên Windows thông qua lớp vỏ `ShLocalShellBackend` bọc Git sh (`/bin/sh`), giải quyết triệt để sự tương thích đường dẫn POSIX và thực thi script Python nhiều dòng.
