
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  return response.json();
}

// Ask Vruddhi to confirm this endpoint.
export function startTest(data) {
  return request("/tests", {
    method: "POST",
    body: JSON.stringify({
      url: data.url,
      objective: data.objective,
    }),
  });
}

// Ask Vruddhi to confirm this endpoint and response format.
export function getTestStatus(testId) {
  return request(`/tests/${encodeURIComponent(testId)}`);
}
