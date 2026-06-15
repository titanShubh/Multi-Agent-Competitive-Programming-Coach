/* API client for communicating with the FastAPI backend. */


const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiClient {
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return headers;
  }

  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || `GET request to ${path} failed with status ${res.status}`);
    }
    return res.json() as Promise<T>;
  }

  async post<T>(path: string, body: any): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const errorText = await res.text();
      let parsedError = errorText;
      try {
        const errObj = JSON.parse(errorText);
        parsedError = errObj.detail || errorText;
      } catch {
        // ignore
      }
      throw new Error(parsedError || `POST request to ${path} failed with status ${res.status}`);
    }
    return res.json() as Promise<T>;
  }

  async patch<T>(path: string, body: any): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || `PATCH request to ${path} failed with status ${res.status}`);
    }
    return res.json() as Promise<T>;
  }

  async streamChat(
    sessionId: string,
    message: string,
    includeCode?: string,
    language?: string,
    onEvent?: (event: any) => void,
    onDone?: () => void,
    onError?: (err: any) => void
  ): Promise<void> {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('token');
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
      }

      const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/chat/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          message,
          include_code: includeCode || null,
          language: language || null,
        }),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || 'Streaming request failed');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Readable stream not supported by browser');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            const dataStr = trimmed.slice(6).trim();
            if (dataStr === '[DONE]') {
              onDone?.();
              return;
            }
            try {
              const event = JSON.parse(dataStr);
              onEvent?.(event);
            } catch (err) {
              console.error('Failed to parse SSE event:', err, dataStr);
            }
          }
        }
      }
    } catch (err) {
      onError?.(err);
    }
  }
}

export const api = new ApiClient();
