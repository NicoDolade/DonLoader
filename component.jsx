import React, { useState } from 'react';

const THEMES = {
  dark: {
    label: 'Oscuro', background: '#101216', surface: '#181C22', elevated: '#20262F',
    border: '#2B333E', text: '#F3F5F7', muted: '#9AA4B2', coral: '#079C5E',
    info: '#7FA8FF', success: '#43C995', warning: '#F2B866', error: '#079C5E',
  },
  light: {
    label: 'Claro', background: '#F4F7F5', surface: '#FFFFFF', elevated: '#E8F1EC',
    border: '#C8D8CF', text: '#18211C', muted: '#5D6C63', coral: '#079C5E',
    info: '#3167C7', success: '#087F4C', warning: '#AD6A00', error: '#079C5E',
  },
  ocean: {
    label: 'Océano', background: '#0E1720', surface: '#152431', elevated: '#1E3442',
    border: '#2D4A5B', text: '#EFF7FA', muted: '#9BB1BD', coral: '#079C5E',
    info: '#7FA8FF', success: '#43C995', warning: '#F2B866', error: '#079C5E',
  },
  slate: {
    label: 'Pizarra', background: '#17171F', surface: '#22232D', elevated: '#2D303C',
    border: '#454856', text: '#F4F3F8', muted: '#B1B0BE', coral: '#079C5E',
    info: '#B6A7FF', success: '#43C995', warning: '#F2B866', error: '#079C5E',
  },
  sand: {
    label: 'Arena', background: '#F6F2EB', surface: '#FFFCF8', elevated: '#EFE7DB',
    border: '#D8CABA', text: '#28251F', muted: '#756B5E', coral: '#079C5E',
    info: '#3A65A8', success: '#187B50', warning: '#A26700', error: '#079C5E',
  },
};

const COLORS = THEMES.dark;

const AUDIO_QUALITIES = ['128', '192', '256', '320'];

function formatQuality(task) {
  if (task.format === 'MP3') {
    return task.format + ' · ' + (task.quality || '320') + 'k';
  }
  return task.format + ' · ' + (task.videoQuality ? task.videoQuality + 'p' : 'Mejor disponible');
}

function statusColor(status, palette = COLORS) {
  if (status === 'Completado') return palette.success;
  if (status === 'Error') return palette.error;
  if (status === 'Descargando...') return palette.coral;
  return palette.muted;
}

export default function DonLoaderPreview({
  tasks = [],
  engineStatus = 'Motor listo',
  initialVideoHeights = [],
  onAnalyze,
  onQueue,
  onClearCompleted,
}) {
  const [themeKey, setThemeKey] = useState(() => {
    if (typeof window === 'undefined') return 'dark';
    return window.localStorage.getItem('donloader-theme') || 'dark';
  });
  const [themeMenuOpen, setThemeMenuOpen] = useState(false);
  const COLORS = THEMES[themeKey] || THEMES.dark;
  const [url, setUrl] = useState('');
  const [format, setFormat] = useState('');
  const [audioQuality, setAudioQuality] = useState('320');
  const [videoHeights, setVideoHeights] = useState(initialVideoHeights);
  const [videoQuality, setVideoQuality] = useState(null);
  const [analysisState, setAnalysisState] = useState('idle');
  const [analysisError, setAnalysisError] = useState('');

  const hasUrl = url.trim().length > 0;
  const isVideo = format === 'MP4' || format === 'MKV';
  const hasFormat = format === 'MP3' || isVideo;
  const canDownload = hasUrl && hasFormat && (!isVideo || analysisState === 'ready');

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
    if (!canDownload) return;
    if (typeof onQueue === 'function') {
      onQueue({
        url: url.trim(),
        format,
        quality: audioQuality,
        videoQuality: isVideo ? videoQuality : null,
      });
    }
    setUrl('');
    setFormat('');
    setAudioQuality('320');
    setVideoHeights([]);
    setVideoQuality(null);
    setAnalysisState('idle');
  };

  const paste = async () => {
    const pasted = await navigator.clipboard.readText().catch(() => '');
    if (pasted) updateUrl(pasted.trim());
  };

  const completedCount = tasks.filter((task) => task.status === 'Completado').length;

  const changeTheme = (nextTheme) => {
    setThemeKey(nextTheme);
    setThemeMenuOpen(false);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('donloader-theme', nextTheme);
    }
  };

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
          <div className="flex items-center gap-2">
            <div className="relative">
              <button
                type="button"
                aria-label="Cambiar tema"
                onClick={() => setThemeMenuOpen((open) => !open)}
                className="rounded-lg border px-2 py-1.5 text-sm font-bold transition-colors duration-150"
                style={{ borderColor: COLORS.border, backgroundColor: COLORS.surface, color: COLORS.muted }}
              >
                ◐
              </button>
              {themeMenuOpen && (
                <div
                  className="absolute right-0 z-20 mt-2 w-36 rounded-lg border p-1"
                  style={{ borderColor: COLORS.border, backgroundColor: COLORS.elevated }}
                >
                  {Object.entries(THEMES).map(([key, theme]) => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => changeTheme(key)}
                      className="flex w-full items-center gap-2 rounded-md px-2 py-2 text-left text-xs transition-colors duration-150"
                      style={{
                        backgroundColor: key === themeKey ? COLORS.surface : 'transparent',
                        color: COLORS.text,
                      }}
                    >
                      <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: theme.coral }} />
                      {theme.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div
              className="rounded-full border px-3 py-1.5 text-xs font-semibold"
              style={{ borderColor: COLORS.border, backgroundColor: COLORS.surface, color: COLORS.success }}
            >
              ● {engineStatus}
            </div>
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

              <div className="flex items-center justify-between rounded-lg px-3 py-2.5" style={{ backgroundColor: COLORS.elevated }}>
                <div className="min-w-0">
                  <p className="text-xs font-bold" style={{ color: COLORS.muted }}>Carpeta de destino</p>
                  <p className="truncate text-sm">Descargas del usuario</p>
                </div>
                <button type="button" className="text-xs font-bold" style={{ color: COLORS.coral }}>Cambiar</button>
              </div>

              {hasUrl && (
                <div className="overflow-hidden opacity-100 transition-all duration-200 ease-out">
                  <p className="mb-2 text-xs font-bold uppercase tracking-wide" style={{ color: COLORS.muted }}>
                    Formato
                  </p>
                  <div className="flex gap-1 rounded-lg border p-1" style={{ borderColor: COLORS.border, backgroundColor: COLORS.elevated }}>
                    {['MP3', 'MP4', 'MKV'].map((value) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => updateFormat(value)}
                        className="flex-1 rounded-md py-2 text-xs font-bold transition-colors duration-150"
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
              )}

              {hasFormat && (
                <div className="overflow-hidden opacity-100 transition-all duration-200 ease-out">
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
                          className="rounded-lg border px-3 py-1.5 text-xs font-bold transition-opacity duration-150 disabled:cursor-not-allowed disabled:opacity-50"
                          style={{ borderColor: COLORS.border, backgroundColor: COLORS.elevated, color: COLORS.text }}
                        >
                          {analysisState === 'loading' ? 'Analizando...' : 'Analizar'}
                        </button>
                      </div>
                      <select
                        value={videoQuality == null ? 'best' : String(videoQuality)}
                        onChange={(event) => setVideoQuality(event.target.value === 'best' ? null : Number(event.target.value))}
                        disabled={analysisState !== 'ready' || !videoHeights.length}
                        className="mt-2 w-full rounded-lg border px-3 py-2.5 text-sm outline-none transition-opacity duration-150 disabled:opacity-60"
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
                </div>
              )}

              {canDownload && (
                <button
                  type="submit"
                  className="w-full rounded-lg py-3 text-sm font-bold transition-colors duration-150"
                  style={{ backgroundColor: COLORS.coral, color: COLORS.background }}
                >
                  Descargar
                </button>
              )}
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
                    <span className="text-xs font-bold" style={{ color: statusColor(task.status, COLORS) }}>{task.status}</span>
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
