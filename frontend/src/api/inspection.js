const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001'

export async function fetchDatasetImages({ classId = '', search = '', page = 1, signal } = {}) {
  const params = new URLSearchParams({ page: String(page), page_size: '20', search })
  if (classId !== '') params.set('class_id', String(classId))
  const response = await fetch(`${API_BASE_URL}/api/inspection/dataset/images?${params}`, { signal })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || `Dataset browsing failed with HTTP ${response.status}.`)
  }
  return payload
}

export function datasetThumbnailUrl(image) {
  return `${API_BASE_URL}${image.thumbnail_url}`
}

export async function fetchDatasetImage(image) {
  const response = await fetch(`${API_BASE_URL}${image.image_url}`)
  if (!response.ok) {
    throw new Error(`Could not load ${image.filename} from the dataset.`)
  }
  const blob = await response.blob()
  return new File([blob], image.filename, { type: blob.type || 'image/jpeg' })
}

export async function inspectImage(file, { signal } = {}) {
  const formData = new FormData()
  formData.append('image', file)
  const response = await fetch(`${API_BASE_URL}/api/inspection`, {
    method: 'POST',
    body: formData,
    signal,
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || `Inspection failed with HTTP ${response.status}.`)
  }
  return payload
}
