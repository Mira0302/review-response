import { API_BASE } from "./env";

export type SSECallback = (event: {
  type: "stage" | "progress" | "result" | "error";
  stage?: number;
  message?: string;
  data?: { response_letter: string; review_points: string; change_table: string };
}) => void;

const api = (path: string) => `${API_BASE}${path}`;

export async function startGeneration(
  paper: string,
  review: string,
  language: string,
): Promise<string> {
  const res = await fetch(api("/api/generate"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paper, review, language }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "生成请求失败");
  }
  const data = await res.json();
  return data.task_id as string;
}

export async function streamGeneration(
  taskId: string,
  onEvent: SSECallback,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(api(`/api/generate/${taskId}/stream`), {
    signal,
    headers: { Accept: "text/event-stream" },
  });

  if (!res.ok) {
    throw new Error("无法连接到生成流");
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("不支持流式响应");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const event = JSON.parse(line.slice(6));
          onEvent(event);
        } catch {
          // skip malformed events
        }
      }
    }
  }
}

export async function parseFile(file: File): Promise<{ text: string; format: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(api("/api/parse-file"), {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "文件解析失败");
  }

  return res.json();
}
