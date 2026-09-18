# Project Index Map & Navigation Router

Tệp này là **Bản Đồ Chỉ Mục Trung Tâm (Master Index Map)** của dự án. Mọi AI Agent sử dụng tệp này để định tuyến tài liệu và nắm bắt toàn bộ bản đồ cấu trúc mã nguồn, luồng giao tiếp và các điểm vào (Entry Points).

---

## 🧭 1. ĐIỀU HƯỚNG TÀI LIỆU & KẾ HOẠCH (Documentation & Planning Router)

Khi nhận nhiệm vụ, Agent tra cứu bảng này để đọc **chính xác** tài liệu chuyên sâu liên quan:

| Lĩnh vực / Nhiệm vụ | Tài liệu chuyên trách | Nội dung chính |
| :--- | :--- | :--- |
| **Ký ức nóng phiên gần nhất** | [`memory/hot/today.md`](memory/hot/today.md) & [`state.json`](memory/hot/state.json) | Trạng thái máy (JSON), nhật ký làm việc theo phiên và kết quả benchmark gần nhất. |
| **Khởi động / Quy tắc chung** | [`memory-distill.txt`](memory-distill.txt) | Kernel hiện trạng, Startup Protocol, Tech stack cốt lõi. |
| **Tổng quan dự án** | [`project-intro.md`](project-intro.md) | Mục tiêu, kiến trúc tổng thể. |
| **Kế hoạch nâng cấp & RFCs** | [`planning/`](../planning/) | Thư mục chứa các bản kế hoạch theo chuẩn `[STT]_[YYYY-MM-DD]_[Ten-Ngan]`; hồ sơ gần nhất `planning/04_2026-09-18_gemini-quota-cache/` (Done). |
| **Lỗi khó / Cạm bẫy / Gotchas** | [`-known-gotchas.md`](-known-gotchas.md) | Tổng hợp các bẫy kỹ thuật và lỗi dị biệt đã gặp. |
| **Kiến trúc dữ liệu & Data Flow** | [`-data-architecture.md`](-data-architecture.md) | Cấu trúc dữ liệu, cơ chế lưu trữ và State Flow. |
| **Lộ trình nâng cấp & Ý tưởng** | [`roadmap.md`](roadmap.md) | Active tasks, Kho Ý Tưởng (Idea Vault) và các mốc đã hoàn thành. |
| **Lịch sử cập nhật** | [`changelog.md`](changelog.md) | Lịch sử Semantic Releases (vX.Y.Z). |
| **Tài liệu kỹ thuật module** | [`docs/`](../docs/) | Thư mục chứa tài liệu chuyên trách 1-1 cho từng module. |
| **Backend Quiz Remediation MVP** | [`docs/backend.md`](../docs/backend.md) | API table, schema `RemediationItem.path` (4 đường đi), env, cách bật Gemini thật. |
| **Đặc tả sản phẩm CP4** | [`spec.md`](../spec.md) | Vision/persona, quy tắc nghiệp vụ, quality bar, kiểm thử, phân công — nộp CP4. |

---

### 🛠️ 1.2. Bảng Định Tuyến Kỹ Năng Chuyên Dụng (Workspace Skills Router - `.agents/skills/`)

| STT | Tên Skill (`.agents/skills/`) | File Quy Chuẩn (`SKILL.md`) | Vai Trò & Chức Năng Cốt Lõi |
| :---: | :--- | :--- | :--- |
| **1** | `nao-commit` | `SKILL.md` | Gọi `nao-dong-bo` để đồng bộ não rồi stage tường minh và commit Conventional Commits tiếng Anh, không push. |
| **2** | `nao-dong-bo` | `SKILL.md` | Đồng bộ tài liệu não trong `brain4agent/` theo Ma Trận 6 Điểm từ git diff, rà thêm `project-intro`/`-data-architecture` khi đổi nền cấu trúc. |
| **3** | `nao-dong-phien` | `SKILL.md` | Đúc kết bối cảnh phiên, quyết định, gotcha và trạng thái máy vào `brain4agent/memory/hot/`, đồng bộ roadmap và gotchas, giữ Root Clean. |
| **4** | `nao-ten-phien` | `SKILL.md` | Tính tên phiên gợi ý từ kế hoạch đang active trong `planning/` và nhắc đổi tên phiên, chỉ đọc. |
| **5** | `vai-dieu-phoi` | `SKILL.md` | Nhận vai super orchestrator của repo với ba chế độ thảo luận, lập kế hoạch, phóng; leo thang lên chủ tịch chỉ ba loại việc. |
| **6** | `vai-thi-cong` | `SKILL.md` | Nhận vai worker của repo, thi công hoặc thẩm định đúng một handoff tự chứa, report chỉ số đo. |

---

## 🗺️ 2. BẢN ĐỒ CẤU TRÚC MÃ NGUỒN (Codebase Directory Map)

```text
project-root/
├── AGENTS.md                         # [QUY TẮC TỐI THƯỢNG] Nguồn chân lý DUY NHẤT (Gemini/Codex đọc trực tiếp)
├── CLAUDE.md                         # [SHIM] Điểm nạp tự động của Claude Code — chỉ chứa @AGENTS.md
├── brain4agent-v1.7.1.md   # [MARKER] Phiên bản khung não — soi nhanh ở root
├── README.md                         # Tài liệu giới thiệu và hướng dẫn build dự án
├── spec.md                           # [SPEC SẢN PHẨM] Vision/persona, quy tắc nghiệp vụ, quality bar, kiểm thử — nộp CP4
├── canvas.md                         # Nguồn ý tưởng/bối cảnh gốc của nhóm (đầu vào cho spec.md, KHÔNG sửa)
├── frontend/                         # [BẢN CŨ MỒ CÔI] không còn được sản phẩm dùng, chờ người duyệt xoá — CẤM chạm khi chưa có lệnh
├── brain4agent/                      # [BỘ NHỚ DỰ ÁN] Single Source of Truth
│   ├── memory/hot/                   # [HOT MEMORY] Ký ức nóng phiên (today.md, state.json)
│   ├── memory-distill.txt            # [KERNEL] Bản cô đọng tối thượng (< 100 dòng)
│   ├── index.md                      # [ROUTER] Master Index Map & Codebase Navigation
│   ├── roadmap.md                    # [ROADMAP] Tiến độ, Active tasks & Idea Vault
│   ├── changelog.md                  # [CHANGELOG] Lịch sử Semantic Releases
│   ├── -known-gotchas.md             # [GOTCHAS] Tổng hợp lỗi dị biệt & bẫy kỹ thuật
│   ├── -data-architecture.md         # [DATA ARCH] Kiến trúc dữ liệu & Data Flow
│   └── project-intro.md              # [INTRO] Tổng quan dự án & Tech stack
├── planning/                         # [QUẢN LÝ KẾ HOẠCH NÂNG CẤP] Chứa các bản kế hoạch RFCs
│   ├── 01_2026-09-17_mock-data-mvp/  # Hồ sơ #01: backend FastAPI + mock-data + validator (Done)
│   ├── 02_2026-09-17_frontend-api-wiring/ # Hồ sơ #02: nối frontend nhóm vào API + 4 đường đi (Done)
│   ├── 03_2026-09-18_cp4-spec-hardening/  # Hồ sơ #03: chốt spec.md + gia cố chẩn đoán/Gemini + golden set ≥20 (Done)
│   └── 04_2026-09-18_gemini-quota-cache/  # Hồ sơ #04: Gemini xoay model + Groq dự phòng + cache đĩa + số đo thật (Done)
│       ├── handoffs/                 # H01–H03: bàn giao tự chứa cho từng worker
│       ├── reports/                  # R01–R03: số đo + phán quyết ✅ của từng handoff
│       └── evidence/                 # output máy nguyên văn (pytest/eval/demo video+ảnh), CẤM sửa tay
├── .agents/skills/                   # [WORKSPACE SKILLS] Kỹ năng chuyên dụng cục bộ dự án
├── docs/                             # [MODULE DOCS] Tài liệu kỹ thuật chi tiết
│   └── backend.md                    # API table, schema RemediationItem.path, env, provider chain Gemini→Groq→Mock
└── codebase/                         # [MÃ NGUỒN SẢN PHẨM] Quiz Remediation MVP (Python 3.13 FastAPI + vanilla JS)
    ├── backend/app/                  # main.py, schemas.py, data.py, retriever.py, llm.py (Mock/Gemini/Groq/Chain), validator.py, service.py
    ├── backend/tests/ + backend/eval/ # pytest (gồm test_llm_gemini.py, test_llm_groq.py) + run_eval.py (golden-set, --llm-stats/--sleep)
    ├── backend/.runtime/             # gitignored: events.jsonl, llm-cache.json (Gemini), llm-cache-groq.json (Groq)
    ├── mock-data/                    # lessons.json, quiz-day01.json, golden-set.json (21 case, toàn bộ MOCK)
    ├── frontend/                     # index.html/app.js/style.css thuần, không build step — sản phẩm thật đang dùng
    ├── index.html                    # [PROTOTYPE CP2] bản clickable gốc của nhóm, KHÔNG sửa (nguồn port UI)
    └── (flowchart.md đã bị xoá trên main ngày 17/9 bởi nhóm trưởng; sơ đồ 4 đường đi giữ trong lịch sử git commit 7d3d8a3)
```
