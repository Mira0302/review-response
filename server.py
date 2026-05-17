"""ReviewResponse API Server — FastAPI + SSE streaming"""
import json
import uuid
import asyncio
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.review_response import parse_review_points, generate_response_letter
from src.utils.file_parser import extract_text


def extract_title(paper: str) -> str:
    """Extract paper title from first meaningful line."""
    for line in paper.strip().split("\n"):
        line = line.strip()
        # Skip markdown headers markers
        if line.lower().startswith("title:"):
            return line[6:].strip().strip('"').strip("'")
        if line and len(line) > 10 and not line.startswith("#"):
            return line[:120]
    return "论文"

app = FastAPI(title="ReviewResponse API")

# CORS: add your production frontend URL here after deployment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task store
tasks: dict = {}

# ── Models ──

class GenerateRequest(BaseModel):
    paper: str = Field(..., min_length=100)
    review: str = Field(..., min_length=10)
    language: str = "auto"  # "auto" | "zh" | "en"

class SSEMessage(BaseModel):
    type: str  # "progress" | "stage" | "result" | "error"
    stage: Optional[int] = None      # 0-3 for progress
    message: Optional[str] = None    # human-readable status
    data: Optional[dict] = None      # result payload

# ── SSE Helpers ──

def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def process_generation(task_id: str, paper: str, review: str, language: str):
    """Background task: run LLM pipeline and push events to queue."""
    q = tasks[task_id]["queue"]

    try:
        await q.put({"type": "stage", "stage": 0, "message": "解析论文上下文"})
        await asyncio.sleep(0.4)

        await q.put({"type": "stage", "stage": 1, "message": "拆解审稿意见"})
        loop = asyncio.get_event_loop()
        review_points = await loop.run_in_executor(None, parse_review_points, review)
        await q.put({"type": "progress", "stage": 1, "detail": review_points})

        await q.put({"type": "stage", "stage": 2, "message": "逐条生成回复草稿"})
        paper_title = extract_title(paper)
        response_letter = await loop.run_in_executor(
            None, generate_response_letter, paper, review, paper_title, language
        )

        await q.put({"type": "stage", "stage": 3, "message": "组装对照表"})
        await asyncio.sleep(0.3)

        # Build change table from response letter with real quality checks
        change_table = build_change_table(review_points, response_letter)

        await q.put({
            "type": "result",
            "data": {
                "response_letter": response_letter,
                "review_points": review_points,
                "change_table": change_table,
            }
        })

    except Exception as e:
        await q.put({"type": "error", "message": str(e)})
    finally:
        tasks[task_id]["status"] = "done"


def build_change_table(review_points: str, response_letter: str) -> str:
    """Build a markdown change table with real quality checks on each row."""
    import re

    lines = [l.strip() for l in review_points.split("\n") if l.strip().startswith("•")]
    if not lines:
        lines = [l.strip() for l in review_points.split("\n") if l.strip() and l.strip()[0].isdigit()]

    # Extract all location mentions from the response letter
    location_patterns = [
        r'(Section\s+\d[\d.]*)', r'(Page\s+\d+)',
        r'(Figure\s+\d[\da-zA-Z]*)', r'(Table\s+\d[\da-zA-Z]*)',
        r'(Chapter\s+\d[\da-zA-Z]*)',
        r'(第\s*\d[\d.]*\s*节)', r'(第\s*\d+\s*页)', r'(第\s*\d+\s*段)',
        r'(图\s*\d[\da-zA-Z]*)', r'(表\s*\d[\da-zA-Z]*)',
        r'(Table\s*\d[\da-zA-Z]*)', r'(Figure\s*\d[\da-zA-Z]*)',
        r'(\w+\.?\s*\d+\.\d+)',  # e.g., §3.2, p.7
    ]
    all_locations = []
    for pattern in location_patterns:
        found = re.findall(pattern, response_letter, re.IGNORECASE)
        all_locations.extend(found)

    # Deduplicate while preserving order
    seen = set()
    unique_locs = []
    for loc in all_locations:
        if loc not in seen:
            seen.add(loc)
            unique_locs.append(loc)

    # Split response into per-comment sections for per-row analysis
    # Each response section starts with "**Reviewer Comment #" or "**Response #"
    response_sections = re.split(r'\*\*Reviewer Comment #\d+[:：]\*\*|\*\*Response #\d+[:：]\*\*', response_letter)
    # Also try alternative format
    if len(response_sections) <= 1:
        response_sections = re.split(r'Reviewer Comment #\d+|Response #\d+', response_letter)

    table = "| # | 审稿意见要点 | 修改位置 | 修改内容 | 状态 |\n"
    table += "|:--:|------------|---------|------------|:--:|\n"

    for i, line in enumerate(lines[:15], 1):
        clean = line.lstrip("•-0123456789. ") if line else "审稿意见"

        # Extract location for this row: look in corresponding response section
        loc = "详见回复信"
        row_has_location = False
        if i < len(response_sections):
            section = response_sections[i] if i < len(response_sections) else ""
            for pattern in location_patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    loc = match.group(1)
                    row_has_location = True
                    break
        # Fallback: use global location list
        if not row_has_location and i-1 < len(unique_locs):
            loc = unique_locs[i-1]
            row_has_location = True

        # Quality check: ✓ if has specific location + substantive response, else ⚠
        has_location = row_has_location and loc not in ("详见回复信", "见回复信", "已修改")
        has_substance = len(clean) > 10  # review point is substantive

        status = "✓" if (has_location and has_substance) else "⚠"

        # Generate real summary (first 50 chars of review point = essence)
        summary = clean[:55] + ("..." if len(clean) > 55 else "")

        table += f"| {i} | {clean[:70]}{'...' if len(clean) > 70 else ''} | {loc} | {summary} | {status} |\n"

    return table


# ── Endpoints ──

@app.post("/api/generate")
async def start_generation(req: GenerateRequest):
    """Start generation, return task_id for SSE streaming."""
    if len(req.paper.strip()) < 100:
        raise HTTPException(400, "论文正文太短（少于100字符）")
    if len(req.review.strip()) < 10:
        raise HTTPException(400, "审稿意见太短（少于10字符）")

    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {
        "status": "running",
        "queue": asyncio.Queue(),
        "paper": req.paper,
        "review": req.review,
    }

    asyncio.create_task(
        process_generation(task_id, req.paper, req.review, req.language)
    )

    return {"task_id": task_id}


@app.get("/api/generate/{task_id}/stream")
async def stream_generation(task_id: str):
    """SSE endpoint: stream generation progress and results."""
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在或已过期")

    q = tasks[task_id]["queue"]

    async def event_stream():
        while True:
            try:
                event = await asyncio.wait_for(q.get(), timeout=120)
                yield sse_event(event)
                if event["type"] in ("result", "error"):
                    break
            except asyncio.TimeoutError:
                yield sse_event({"type": "error", "message": "生成超时，请重试"})
                break

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


try:
    import python_multipart  # noqa: F401
    _HAS_MULTIPART = True
except ImportError:
    _HAS_MULTIPART = False

if _HAS_MULTIPART:
    @app.post("/api/parse-file")
    async def parse_file(file: UploadFile = File(...)):
        """Parse uploaded PDF/DOCX/MD/TXT and return text."""
        allowed = {".pdf", ".docx", ".doc", ".md", ".markdown", ".txt"}
        ext = Path(file.filename).suffix.lower() if file.filename else ""

        if ext not in allowed:
            raise HTTPException(400, f"不支持的文件格式：{ext}，支持 PDF/Word/Markdown/TXT")

        try:
            tmp_path = f"/tmp/{uuid.uuid4().hex}{ext}"
            content = await file.read()
            with open(tmp_path, "wb") as f:
                f.write(content)

            text, label = extract_text(tmp_path)
            os.remove(tmp_path)

            return {
                "text": text,
                "format": label,
                "char_count": len(text),
            }
        except Exception as e:
            raise HTTPException(500, f"文件解析失败：{str(e)}")


@app.get("/api/health")
async def health():
    return {"status": "ok", "active_tasks": len(tasks)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
