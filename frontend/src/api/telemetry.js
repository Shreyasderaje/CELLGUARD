const API_BASE_URL = 'http://127.0.0.1:8001'

export async function fetchTelemetrySummary({ signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/api/telemetry/summary`, { signal })
  if (!response.ok) {
    throw new Error(`Telemetry request failed with HTTP ${response.status}.`)
  }
  return response.json()
}

export async function fetchTelemetryHistory({ startDate = '', endDate = '', machineId = '', signal } = {}) {
  const params = new URLSearchParams()
  if (startDate) params.set('start_date', startDate)
  if (endDate) params.set('end_date', endDate)
  if (machineId && machineId !== 'ALL') params.set('machine_id', machineId)

  const query = params.toString()
  const response = await fetch(`${API_BASE_URL}/api/telemetry/history${query ? `?${query}` : ''}`, { signal })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((issue) => `${issue.loc?.at(-1) ?? 'Filter'}: ${issue.msg}`).join(' ')
      : payload.detail
    throw new Error(detail || `Telemetry history request failed with HTTP ${response.status}.`)
  }
  return payload
}
