import { useEffect, useRef, useState } from 'react'
import { AlertTriangle, CheckCircle2, ChevronLeft, ChevronRight, FileImage, ScanLine, Search, Upload, X } from 'lucide-react'
import { motion } from 'framer-motion'
import { datasetThumbnailUrl, fetchDatasetImage, fetchDatasetImages, inspectImage } from '../api/inspection'

const acceptedTypes = ['image/jpeg', 'image/png']

export default function VisualInspection() {
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dragging, setDragging] = useState(false)
  const [dataset, setDataset] = useState({ total_images: 0, matching_count: 0, displayed_count: 0, page: 1, total_pages: 0, class_filters: [], images: [] })
  const [datasetLoading, setDatasetLoading] = useState(true)
  const [datasetError, setDatasetError] = useState('')
  const [classFilter, setClassFilter] = useState('')
  const [filenameSearch, setFilenameSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [datasetPage, setDatasetPage] = useState(1)
  const [selectedDatasetImage, setSelectedDatasetImage] = useState(null)
  const [loadingImageId, setLoadingImageId] = useState(null)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(filenameSearch.trim()), 250)
    return () => clearTimeout(timer)
  }, [filenameSearch])

  useEffect(() => {
    const controller = new AbortController()
    setDatasetLoading(true)
    setDatasetError('')
    fetchDatasetImages({ classId: classFilter, search: debouncedSearch, page: datasetPage, signal: controller.signal })
      .then((payload) => {
        setDataset(payload)
        if (payload.page !== datasetPage) setDatasetPage(payload.page)
      })
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') setDatasetError(requestError.message)
      })
      .finally(() => { if (!controller.signal.aborted) setDatasetLoading(false) })
    return () => controller.abort()
  }, [classFilter, debouncedSearch, datasetPage])

  useEffect(() => {
    if (!file) {
      setPreviewUrl('')
      return undefined
    }
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  function selectFile(nextFile, datasetImage = null) {
    if (!nextFile) return
    setResult(null)
    setError('')
    setSelectedDatasetImage(datasetImage)
    if (!acceptedTypes.includes(nextFile.type)) {
      setFile(null)
      setError('Choose a JPG or PNG image to begin inspection.')
      return
    }
    setFile(nextFile)
  }

  async function runInspection() {
    if (!file || loading) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      setResult(await inspectImage(file))
    } catch (requestError) {
      setError(requestError.message || 'The inspection could not be completed.')
    } finally {
      setLoading(false)
    }
  }

  async function chooseDatasetImage(image) {
    setLoadingImageId(image.image_id)
    setDatasetError('')
    try {
      const datasetFile = await fetchDatasetImage(image)
      selectFile(datasetFile, image)
    } catch (requestError) {
      setDatasetError(requestError.message || 'Could not load the dataset image.')
    } finally {
      setLoadingImageId(null)
    }
  }

  const defects = result?.detections.filter((item) => item.detected_class !== 'Good Welding') ?? []

  return <motion.div className="page-content inspection-page" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: .22 }}>
    <section className="welcome-row inspection-welcome"><div><div className="eyebrow"><span className="eyebrow-line" />VISION AI · WELD QUALITY</div><h1>Visual Inspection</h1><p className="page-description">Inspect weld imagery for surface anomalies with the CELLGUARD vision model.</p></div><div className="inspection-model-badge"><span className="online-dot" /> YOLO DETECTOR READY</div></section>

    <section className="inspection-workspace">
      <article className="panel glass-card upload-panel">
        <div className="panel-heading"><div><div className="panel-kicker">INSPECTION INPUT</div><h2>Upload weld image</h2></div><span className="upload-format">JPG · PNG</span></div>
        <input ref={inputRef} className="inspection-file-input" type="file" accept="image/jpeg,image/png" onChange={(event) => selectFile(event.target.files?.[0])} />
        <button type="button" className={`drop-zone ${dragging ? 'dragging' : ''}`} onClick={() => inputRef.current?.click()} onDragOver={(event) => { event.preventDefault(); setDragging(true) }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); selectFile(event.dataTransfer.files?.[0]) }} aria-label="Choose or drop a JPG or PNG image">
          <span className="drop-zone-icon"><Upload size={25} /></span><strong>Drop an image here</strong><span>or click to browse your device</span><small>JPG or PNG · one image per inspection</small>
        </button>
        {file && <div className="selected-file"><span className="selected-file-icon"><FileImage size={19} /></span><span className="selected-file-copy"><strong>{file.name}</strong><small>{selectedDatasetImage ? `Dataset image · ${selectedDatasetImage.split} split` : `${(file.size / (1024 * 1024)).toFixed(2)} MB · Uploaded image`}</small></span><button type="button" className="icon-button remove-file" aria-label="Remove image" onClick={() => { setFile(null); setSelectedDatasetImage(null); setResult(null); setError('') }}><X size={17} /></button></div>}
        <button type="button" className="inspect-button" disabled={!file || loading} onClick={runInspection}>{loading ? <><span className="button-spinner" /> Inspecting image…</> : <><ScanLine size={19} /> Run visual inspection</>}</button>
        <p className="inspection-note">The image is processed by the existing CELLGUARD weld detector. Confidence threshold: 25%.</p>
      </article>

      <section className="inspection-results" aria-live="polite">
        {loading && <article className="panel glass-card inspection-state"><span className="state-icon loading-icon"><ScanLine size={25} /></span><h2>Analyzing weld image</h2><p>The vision model is locating and classifying visible weld features.</p><div className="loading-track"><span /></div></article>}
        {!loading && error && <article className="panel glass-card inspection-state error-state" role="alert"><span className="state-icon"><AlertTriangle size={24} /></span><h2>Inspection unavailable</h2><p>{error}</p></article>}
        {!loading && !error && !result && <article className="panel glass-card inspection-state empty-state"><span className="state-icon"><ScanLine size={25} /></span><h2>Inspection results</h2><p>Choose a weld image and run an inspection to see the model output here.</p></article>}
        {result && file && <>
          <div className="image-comparison">
            <article className="panel glass-card inspection-image-panel"><div className="panel-heading"><div><div className="panel-kicker">SOURCE IMAGE</div><h2>Original</h2></div><span className="image-dimensions">{result.image_width} × {result.image_height}</span></div><img className="inspection-image" src={previewUrl} alt="Original weld submitted for inspection" /></article>
            <article className="panel glass-card inspection-image-panel"><div className="panel-heading"><div><div className="panel-kicker">VISION MODEL OUTPUT</div><h2>Detection overlay</h2></div><span className="overlay-indicator"><i /> ANNOTATED</span></div><img className="inspection-image" src={result.annotated_image} alt="Weld image with model detections and bounding boxes" /></article>
          </div>
          <article className="panel glass-card detections-panel"><div className="panel-heading"><div><div className="panel-kicker">DETECTION BREAKDOWN</div><h2>Inspection findings</h2></div><span className="finding-count">{result.detections.length} {result.detections.length === 1 ? 'finding' : 'findings'}</span></div>
            {result.detections.length === 0 ? <div className="no-detections"><CheckCircle2 size={22} /><div><strong>No features detected above threshold</strong><span>Try another image or review the weld visually.</span></div></div> : <div className="detection-grid">{result.detections.map((detection, index) => { const isDefect = detection.detected_class !== 'Good Welding'; return <article className={`detection-card ${isDefect ? 'defect' : 'good'}`} key={`${detection.detected_class}-${index}`}><div className="detection-card-top"><span className="detection-mark">{isDefect ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}</span><span className={`detection-kind ${isDefect ? 'defect' : 'good'}`}>{isDefect ? 'DEFECT CLASS' : 'QUALITY CLASS'}</span><span className="detection-index">#{String(index + 1).padStart(2, '0')}</span></div><h3>{detection.detected_class}</h3><div className="confidence-row"><span>Confidence</span><strong>{(detection.confidence * 100).toFixed(1)}%</strong></div><div className="confidence-bar"><span style={{ width: `${Math.min(detection.confidence * 100, 100)}%` }} /></div><div className="bbox-row"><span>Bounding box</span><code>[{detection.bounding_box.map((value) => Math.round(value)).join(', ')}]</code></div></article> })}</div>}
            {defects.length > 0 && <div className="inspection-summary"><AlertTriangle size={18} /><span><strong>{defects.length} defect {defects.length === 1 ? 'region' : 'regions'} detected</strong> · Review flagged areas before disposition.</span></div>}
          </article>
        </>}
      </section>
    </section>

    <section className="panel glass-card dataset-explorer" aria-label="Dataset Explorer">
      <div className="dataset-explorer-top"><div><div className="panel-kicker">DATASET EXPLORER</div><h2>Browse weld imagery</h2><p>Dataset images are demonstration data from the train, validation, and test splits.</p></div><span className="dataset-total">{dataset.total_images.toLocaleString()} <small>images available</small></span></div>
      <div className="dataset-controls"><label className="dataset-filter"><span>Class filter</span><select value={classFilter} onChange={(event) => { setClassFilter(event.target.value); setDatasetPage(1) }}><option value="">All classes</option>{dataset.class_filters.map((item) => <option key={item.class_id} value={item.class_id}>{item.class_name}</option>)}</select></label><label className="dataset-search"><Search size={18} /><input type="search" value={filenameSearch} onChange={(event) => { setFilenameSearch(event.target.value); setDatasetPage(1) }} placeholder="Search filename…" aria-label="Search dataset filenames" /></label><div className="dataset-counts" aria-live="polite"><strong>{dataset.displayed_count}</strong> shown <span>·</span> {dataset.matching_count.toLocaleString()} matching</div></div>
      {datasetLoading ? <div className="dataset-message" aria-busy="true">Loading dataset index…</div> : datasetError ? <div className="dataset-message dataset-error" role="alert">{datasetError}</div> : dataset.images.length === 0 ? <div className="dataset-message">No dataset images match these filters. Clear the search or choose another class.</div> : <>
        <div className="dataset-grid">{dataset.images.map((image) => <button type="button" className={`dataset-card ${selectedDatasetImage?.image_id === image.image_id ? 'selected' : ''}`} key={image.image_id} onClick={() => chooseDatasetImage(image)} disabled={loadingImageId !== null} aria-pressed={selectedDatasetImage?.image_id === image.image_id} aria-label={`Load dataset image ${image.filename} for inspection`}>{loadingImageId === image.image_id ? <span className="dataset-card-loading">Loading image…</span> : <img src={datasetThumbnailUrl(image)} alt={`Dataset image ${image.filename}`} loading="lazy" />}<span className="dataset-card-details"><strong title={image.filename}>{image.filename}</strong><span>{image.class_names.length ? image.class_names.join(' · ') : 'Unlabeled image'}</span><small>{image.split.toUpperCase()} DATASET</small></span></button>)}</div>
        <div className="dataset-pagination"><span>Page {dataset.page} of {Math.max(dataset.total_pages, 1)}</span><div><button type="button" className="dataset-page-button" onClick={() => setDatasetPage((page) => Math.max(1, page - 1))} disabled={datasetLoading || dataset.page <= 1}><ChevronLeft size={18} /> Previous</button><button type="button" className="dataset-page-button" onClick={() => setDatasetPage((page) => Math.min(dataset.total_pages, page + 1))} disabled={datasetLoading || dataset.page >= dataset.total_pages}>Next <ChevronRight size={18} /></button></div></div>
      </>}
    </section>
  </motion.div>
}
