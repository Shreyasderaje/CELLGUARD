const API_BASE_URL = 'http://127.0.0.1:8000'

export async function fetchTelemetrySummary({ signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/api/telemetry/summary`, { signal })
  if (!response.ok) {
    throw new Error(`Telemetry request failed with HTTP ${response.status}.`)
  }
  return response.json()
}
