const API_BASE_URL = 'http://127.0.0.1:8001'

export async function predictRisk(processParameters, { signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/api/risk/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(processParameters),
    signal,
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((issue) => `${issue.loc?.at(-1) ?? 'Input'}: ${issue.msg}`).join(' ')
      : payload.detail
    throw new Error(detail || `Risk prediction failed with HTTP ${response.status}.`)
  }
  return payload
}
