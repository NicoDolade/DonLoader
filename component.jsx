import React, { useState } from 'react';

const COLORS = {
  background: '#101216',
  surface: '#181C22',
  elevated: '#20262F',
  border: '#2B333E',
  text: '#F3F5F7',
  muted: '#9AA4B2',
  coral: '#FF6B5B',
  info: '#7FA8FF',
  success: '#43C995',
  warning: '#F2B866',
  error: '#079C5E',
};

const AUDIO_QUALITIES = ['128', '192', '256', '320'];

function formatQuality(task) {
  if (task.format === 'MP3') {
    return task.format + ' · ' + (task.quality || '320') + 'k';
  }
  return task.format + ' · ' + (task.videoQuality ? task.videoQuality + 'p' : 'Mejor disponible');
}

function statusColor(status) {
  if (status === 'Completado') return COLORS.success;
  if (status === 'Error') return COLORS.error;
  if (status === 'Descargando...') return COLORS.coral;
  return COLORS.muted;
}

export default function DonLoaderPreview({
  tasks = [],
  engineStatus = 'Motor listo',
  initialVideoHeights = [],
  onAnalyze,
  onQueue,
  onClearCompleted,
}) {
  const [url, setUrl] = useState('');
  const [format, setFormat] = useState('MP4');
  const [audioQuality, setAudioQuality] = useState('320');
  const [videoHeights, setVideoHeights] = useState(initialVideoHeights);
  const [videoQuality, setVideoQuality] = useState(null);
  const [analysisState, setAnalysisState] = useState('idle');
  const [analysisError, setAnalysisError] = useState('');

  const isVideo = format === 'MP4' || format === 'MKV';
  const canQueue = url.trim() && (!isVideo || analysisState === 'ready');

  const updateUrl = (value) => {
    setUrl(value);
    setVideoHeights([]);
    setVideoQuality(null);
    setAnalysisState('idle');
    setAnalysisError('');
  };

  const updateFormat = (value) => {
    setFormat(value);
    setVideoHeights([]);
    setVideoQuality(null);
    setAnalysisState('idle');
    setAnalysisError('');
  };

  const analyze = async () => {
    const cleanUrl = url.trim();
    if (!cleanUrl || !isVideo || typeof onAnalyze !== 'function') {
      setAnalysisError('Se necesita una URL y un analizador conectado.');
      setAnalysisState('error');
      return;
    }
    setAnalysisState('loading');
    setAnalysisError('');
    try {
      const result = await onAnalyze(cleanUrl, format);
      const heights = Array.isArray(result)
        ? [...new Set(result.filter((height) => Number.isInteger(height) && height > 0))].sort((a, b) => b - a)
        : [];
      setVideoHeights(heights);
      setVideoQuality(heights.length ? heights[0] : null);
      setAnalysisState('ready');
    } catch (error) {
      setAnalysisState('error');
      setAnalysisError(error && error.message ? error.message : 'No se pudo analizar el enlace.');
    }
  };

  const submit = (event) => {
    event.preventDefault();
    if (!canQueue) return;
    if (typeof onQueue === 'function') {
      onQueue({
        url: url.trim(),
        format,
        quality: audioQuality,
        videoQuality: isVideo ? videoQuality : null,
      });
    }
    setUrl('');
    setVideoHeights([]);
    setVideoQuality(null);
    setAnalysisState('idle');
  };

  const paste = async () => {
    const pasted = await navigator.clipboard.readText().catch(() => '');
    if (pasted) updateUrl(pasted.trim());
  };

  const completedCount = tasks.filter((task) => task.status === 'Completado').length;

  return (
    <main
      className="min-h-screen w-full px-4 py-5 md:px-6"
      style={{ backgroundColor: COLORS.background, color: COLORS.text }}
    >
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4">
        <header className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div
              className="flex h-9 w-9 items-center justify-center rounded-md text-lg font-bold"
              style={{ backgroundColor: COLORS.coral, color: COLORS.background }}
            >
              ↓
            </div>
            <div>
              <h1 className="text-xl font-bold">DonLoader</h1>
              <p className="text-xs" style={{ color: COLORS.muted }}>
                Descargas simples, rápidas y bajo control
              </p>
            </div>
          </div>
          <div
            className="rounded-full border px-3 py-1.5 text-xs font-semibold"
            style={{ borderColor: COLORS.border, backgroundColor: COLORS.surface, color: COLORS.success }}
          >
            ● {engineStatus}
          </div>
        </header>

        <div className="grid min-h-[540px] grid-cols-1 gap-4 lg:grid-cols-[minmax(300px,360px)_minmax(0,1fr)]">
          <section
            className="rounded-xl border p-4"
            style={{ borderColor: COLORS.border, backgroundColor: COLORS.surface }}
          >
            <div className="mb-5">
              <h2 className="text-lg font-bold">Nueva descarga</h2>
              <p className="mt-1 text-xs" style={{ color: COLORS.muted }}>
                Analizá videos para elegir una resolución disponible.
              </p>
            </div>

            <form className="flex h-full flex-col gap-4" onSubmit={submit}>
              <label className="text-xs font-bold uppercase tracking-wide" style={{ color: COLORS.muted }}>
                URL
                <div className="mt-2 flex gap-2">
                  <input
                    value={url}
                    onChange={(event) => updateUrl(event.target.value)}
                    placeholder="Pegá un enlace"
                    className="min-w-0 flex-1 rounded-lg border px-3 py-2.5 text-sm outline-none"
                    style={{ borderColor: COLORS.border, backgroundColor: COLORS.elevated, color: COLORS.text }}
                  />
                  <button
                    type="button"
                    onClick={paste}
                    className="rounded-lg border px-3 text-xs font-bold"
                    style={{ borderColor: COLORS.border, backgroundColor: COLORS.elevated, color: COLORS.text }}
                  >
                    Pegar
                  </button>
                </div>
              </label>

              <div>
                <p className="mb-2 text-xs font-bold uppercase tracking-wide" style={{ color: COLORS.muted }}>
                  Formato
                </p>
                <div className="flex gap-1 rounded-lg border p-1" style={{ borderColor: COLORS.border, backgroundColor: COLORS.elevated }}>
                  {['MP3', 'MP4', 'MKV'].map((value) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => updateFormat(value)}
                      className="flex-1 rounded-md py-2 text-xs font-bold"
                      style={{
                        backgroundColor: format === value ? COLORS.coral : 'transparent',
                        color: format === value ? COLORS.background : COLORS.text,
                      }}
                    >
                      {value}
                    </button>
                  ))}
                </div>
              </div>

              {format === 'MP3' ? (
                <label className="text-xs font-bold uppercase tracking-wide" style={{ color: COLORS.muted }}>
                  Calidad de audio
                  <select
                    value={audioQuality}
                    onChange={(event) => setAudioQuality(event.target.value)}
                    className="mt-2 w-full rounded-lg border px-3 py-2.5 text-sm normal-case outline-none"
                    style={{ borderColor: COLORS.border, backgroundColor: COLORS.elevated, color: COLORS.text }}
                  >
                    {AUDIO_QUALITIES.map((value) => <option key={value} value={value}>{value} kbps</option>)}
                  </select>
                </label>
              ) : (
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-xs font-bold uppercase tracking-wide" style={{ color: COLORS.muted }}>
                      Calidad de video
                    </p>
                    <button
                      type="button"
                      onClick={analyze}
                      disabled={analysisState === 'loading' || !url.trim()}
                      className="rounded-lg border px-3 py-1.5 text-xs font-bold disabled:cursor-not-allowed disabled:opacity-50"
                      style={{ borderColor: COLORS.border, backgroundColor: COLORS.elevated, color: COLORS.text }}
                    >
                      {analysisState === 'loading' ? 'Analizando...' : 'Analizar'}
                    </button>
                  </div>
                  <select
                    value={videoQuality == null ? 'best' : String(videoQuality)}
                    onChange={(event) => setVideoQuality(event.target.value === 'best' ? null : Number(event.target.value))}
                    disabled={analysisState !== 'ready' || !videoHeights.length}
                    className="mt-2 w-full rounded-lg border px-3 py-2.5 text-sm outline-none disabled:opacity-60"
                    style={{ borderColor: COLORS.border, backgroundColor: COLORS.elevated, color: COLORS.text }}
                  >
                    {videoHeights.length
                      ? videoHeights.map((height) => <option key={height} value={height}>{height}p</option>)
                      : <option value="best">Mejor disponible</option>}
                  </select>
                  <p className="mt-2 text-xs" style={{ color: analysisState === 'error' ? COLORS.error : COLORS.muted }}>
                    {analysisState === 'idle' && 'Analizá el enlace para consultar sus alturas reales.'}
                    {analysisState === 'loading' && 'Consultando metadata sin descargar.'}
                    {analysisState === 'ready' && (videoHeights.length ? 'La mayor calidad quedó seleccionada por defecto.' : 'El sitio no informó alturas; se usará la mejor disponible.')}
                    {analysisState === 'error' && analysisError}
                  </p>
                </div>
              )}

              <div className="mt-auto">
                <div className="mb-3 flex items-center justify-between rounded-lg px-3 py-2.5" style={{ backgroundColor: COLORS.elevated }}>
                  <div className="min-w-0">
                    <p className="text-xs font-bold" style={{ color: COLORS.muted }}>Carpeta de destino</p>
                    <p className="truncate text-sm">Descargas del usuario</p>
                  </div>
                  <button type="button" className="text-xs font-bold" style={{ color: COLORS.coral }}>Cambiar</button>
                </div>
                <button
                  type="submit"
                  disabled={!canQueue}
                  className="w-full rounded-lg py-3 text-sm font-bold disabled:cursor-not-allowed disabled:opacity-50"
                  style={{ backgroundColor: COLORS.coral, color: COLORS.background }}
                >
                  Añadir a la cola
                </button>
              </div>
            </form>
          </section>

          <section className="flex min-h-0 flex-col">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-base font-bold">Cola de descargas · {tasks.length}</h2>
              <button
                type="button"
                onClick={onClearCompleted}
                disabled={!completedCount}
                className="text-xs font-semibold disabled:opacity-40"
                style={{ color: COLORS.muted }}
              >
                Limpiar completadas
              </button>
            </div>
            <div className="flex-1 space-y-2 overflow-y-auto">
              {!tasks.length ? (
                <div
                  className="flex min-h-[240px] flex-col items-center justify-center rounded-xl border px-6 text-center"
                  style={{ borderColor: COLORS.border, backgroundColor: COLORS.surface }}
                >
                  <span className="text-3xl font-bold" style={{ color: COLORS.coral }}>↓</span>
                  <p className="mt-2 text-sm font-bold">La cola está vacía</p>
                  <p className="mt-1 text-xs" style={{ color: COLORS.muted }}>Pegá un enlace a la izquierda para empezar.</p>
                </div>
              ) : tasks.map((task) => (
                <article
                  key={task.id}
                  className="rounded-xl border p-3"
                  style={{ borderColor: COLORS.border, backgroundColor: COLORS.surface }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold">{task.title || task.url}</p>
                      <p className="mt-1 text-xs" style={{ color: COLORS.muted }}>{formatQuality(task)}</p>
                    </div>
                    <span className="text-xs font-bold" style={{ color: statusColor(task.status) }}>{task.status}</span>
                  </div>
                  <div className="mt-3 h-1 overflow-hidden rounded-full" style={{ backgroundColor: COLORS.elevated }}>
                    <div
                      className="h-full"
                      style={{ width: String(task.progress || 0) + '%', backgroundColor: task.status === 'Completado' ? COLORS.success : COLORS.coral }}
                    />
                  </div>
                  <div className="mt-2 flex justify-between text-xs" style={{ color: COLORS.muted }}>
                    <span>{task.speed || 'Esperando en cola'}</span>
                    <span>{task.eta ? 'ETA ' + task.eta : ''}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
