const pptxgen = require('pptxgenjs');
const path = require('path');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Nusacodes Bootcamp Data Engineer';
pptx.company = 'Nusacodes';
pptx.subject = 'Automation, scheduling, orchestration, Dagster, Kestra, and Prefect';
pptx.title = 'Automation, Scheduling, dan Orchestration';
pptx.lang = 'id-ID';
pptx.theme = {
  headFontFace: 'Calibri',
  bodyFontFace: 'Calibri',
  lang: 'id-ID',
};
pptx.defineSlideMaster({
  title: 'LIGHT',
  background: { color: 'F8FAFC' },
  objects: [],
  slideNumber: { x: 12.55, y: 7.12, w: 0.3, h: 0.18, color: '64748B', fontFace: 'Calibri', fontSize: 9, align: 'right' },
});

const C = {
  ink: '0F172A',
  navy: '111C35',
  blue: '2563EB',
  blueDark: '1D4ED8',
  cyan: '0891B2',
  green: '059669',
  amber: 'D97706',
  red: 'DC2626',
  violet: '7C3AED',
  muted: '64748B',
  line: 'CBD5E1',
  pale: 'E2E8F0',
  white: 'FFFFFF',
  bg: 'F8FAFC',
  bluePale: 'DBEAFE',
  cyanPale: 'CFFAFE',
  greenPale: 'D1FAE5',
  amberPale: 'FEF3C7',
  redPale: 'FEE2E2',
  violetPale: 'EDE9FE',
};

const FONT = 'Calibri';
const OUT = path.join(__dirname, 'Automation Scheduling dan Orchestration.pptx');

function addText(slide, text, x, y, w, h, options = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: FONT,
    fontSize: 18,
    color: C.ink,
    margin: 0,
    breakLine: false,
    valign: 'mid',
    isTextBox: true,
    ...options,
  });
}

function addTitle(slide, title, subtitle) {
  addText(slide, title, 0.62, 0.38, 12.05, 0.55, { fontSize: 34, bold: true, color: C.ink, valign: 'top' });
  if (subtitle) addText(slide, subtitle, 0.64, 0.98, 11.7, 0.34, { fontSize: 14, color: C.muted, valign: 'top' });
}

function box(slide, x, y, w, h, fill, line = C.line, radius = 0.12) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: radius,
    fill: { color: fill },
    line: { color: line, width: 1 },
  });
}

function circle(slide, x, y, d, fill, line = fill) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x, y, w: d, h: d,
    fill: { color: fill },
    line: { color: line, width: 1 },
  });
}

function arrow(slide, x, y, w, h, color = C.muted, width = 2) {
  slide.addShape(pptx.ShapeType.line, {
    x, y, w, h,
    line: { color, width, beginArrowType: 'none', endArrowType: 'triangle' },
  });
}

function addSectionLabel(slide, text, x, y, color = C.blue) {
  addText(slide, text.toUpperCase(), x, y, 2.8, 0.25, { fontSize: 10, bold: true, color, charSpacing: 1.2 });
}

function addBullets(slide, items, x, y, w, h, options = {}) {
  const runs = items.map((item, i) => ({
    text: item,
    options: {
      bullet: { indent: 18 },
      hanging: 4,
      breakLine: i < items.length - 1,
      paraSpaceAfterPt: 10,
    },
  }));
  slide.addText(runs, {
    x, y, w, h,
    fontFace: FONT,
    fontSize: options.fontSize || 17,
    color: options.color || C.ink,
    margin: options.margin ?? 0.04,
    valign: 'top',
    isTextBox: true,
    breakLine: false,
  });
}

function addSourceNote(slide, sources, extra = '') {
  slide.addNotes(`${extra}${extra ? '\n\n' : ''}Sumber:\n${sources.join('\n')}`);
}

// Slide 1: Cover
{
  const slide = pptx.addSlide();
  slide.background = { color: C.navy };
  addText(slide, 'AUTOMATION  /  DATA ENGINEERING', 0.72, 0.68, 5.9, 0.3, { fontSize: 11, bold: true, color: '93C5FD', charSpacing: 1.8 });
  addText(slide, 'Automation, Scheduling,\ndan Orchestration', 0.72, 1.32, 7.5, 1.65, { fontSize: 42, bold: true, color: C.white, valign: 'top', breakLine: false });
  addText(slide, 'Implementasi Dagster pada YouTube Trend Analytics\ndan perbandingan dengan Kestra serta Prefect', 0.76, 3.24, 6.75, 0.86, { fontSize: 19, color: 'CBD5E1', valign: 'top', breakLine: false });
  addText(slide, 'Final Project · Bootcamp Data Engineer', 0.76, 6.55, 5.4, 0.35, { fontSize: 13, color: '94A3B8' });

  const nodes = [
    { x: 9.0, y: 1.0, label: 'CSV', color: C.cyan },
    { x: 10.65, y: 1.78, label: 'RAW', color: C.blue },
    { x: 10.8, y: 3.62, label: 'DBT', color: C.violet },
    { x: 9.25, y: 4.75, label: 'GOLD', color: C.amber },
    { x: 7.85, y: 3.35, label: 'API', color: C.green },
  ];
  nodes.forEach((n, i) => {
    if (i < nodes.length - 1) arrow(slide, n.x + 0.54, n.y + 0.54, nodes[i + 1].x - n.x, nodes[i + 1].y - n.y, '64748B', 2.2);
  });
  arrow(slide, nodes[4].x + 0.45, nodes[4].y + 0.15, nodes[0].x - nodes[4].x + 0.15, nodes[0].y - nodes[4].y + 0.4, '64748B', 2.2);
  nodes.forEach(n => {
    circle(slide, n.x, n.y, 1.08, n.color);
    addText(slide, n.label, n.x, n.y + 0.33, 1.08, 0.28, { fontSize: 14, bold: true, color: C.white, align: 'center' });
  });
  circle(slide, 9.12, 2.65, 1.55, '1E293B', '475569');
  addText(slide, 'ORCH', 9.12, 3.12, 1.55, 0.3, { fontSize: 17, bold: true, color: C.white, align: 'center' });
  addText(slide, 'Dagster', 9.12, 2.91, 1.55, 0.22, { fontSize: 11, color: '93C5FD', align: 'center' });
  addSourceNote(slide, [], 'Materi presentasi final-project YouTube Trend Analytics.');
}

// Slide 2: Why orchestration
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Orchestration mengelola seluruh siklus eksekusi', 'Satu script dapat menjalankan task, tetapi orchestrator menjaga dependensi, state, retry, dan riwayat run.');
  addSectionLabel(slide, 'Tanpa orchestrator', 0.7, 1.55, C.red);
  addBullets(slide, [
    'Urutan task bergantung pada operator atau script tunggal',
    'Failure di tengah proses sulit dilanjutkan secara aman',
    'Log dan status tersebar di beberapa command',
    'Jadwal mudah berjalan tanpa validasi output',
  ], 0.72, 1.93, 4.25, 3.5, { fontSize: 18 });
  box(slide, 0.72, 5.55, 4.25, 0.76, C.redPale, 'FCA5A5');
  addText(slide, 'Risiko utama: pipeline selesai sebagian tetapi terlihat “sudah jalan”.', 0.96, 5.68, 3.8, 0.46, { fontSize: 17, bold: true, color: '991B1B', valign: 'top' });

  addSectionLabel(slide, 'Dengan orchestrator', 5.65, 1.55, C.blue);
  const steps = [
    ['1', 'Trigger'], ['2', 'Dependencies'], ['3', 'Execution'], ['4', 'Observe'], ['5', 'Recover'],
  ];
  steps.forEach((s, i) => {
    const x = 5.72 + i * 1.38;
    if (i < steps.length - 1) arrow(slide, x + 0.95, 2.55, 0.43, 0, C.line, 1.8);
    circle(slide, x, 2.15, 0.92, [C.cyan, C.blue, C.violet, C.amber, C.green][i]);
    addText(slide, s[0], x, 2.39, 0.92, 0.25, { fontSize: 19, bold: true, color: C.white, align: 'center' });
    addText(slide, s[1], x - 0.13, 3.18, 1.18, 0.35, { fontSize: 14, bold: true, align: 'center' });
  });
  box(slide, 5.72, 4.05, 6.9, 1.58, C.white, C.line);
  addText(slide, 'Orchestrator menyimpan konteks setiap run', 6.08, 4.32, 5.9, 0.36, { fontSize: 22, bold: true, color: C.blueDark });
  addText(slide, 'Task mana yang berhasil, task mana yang gagal, kapan retry terjadi, dan output apa yang harus divalidasi.', 6.08, 4.86, 5.95, 0.55, { fontSize: 17, color: C.muted, valign: 'top' });
  addSourceNote(slide, ['https://docs.dagster.io/getting-started/quickstart'], 'Penjelasan orchestration dikaitkan dengan implementasi lokal pada orchestration/definitions.py.');
}

// Slide 3: Concepts
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Automation, scheduling, dan orchestration', 'Ketiganya saling terkait, tetapi menjawab pertanyaan operasional yang berbeda.');
  const columns = [
    { x: 0.72, color: C.blue, pale: C.bluePale, title: 'ORCHESTRATION', q: 'Bagaimana workflow berjalan?', body: 'Mengatur dependency, state, retry, concurrency, logging, dan validasi lintas task.' },
    { x: 4.48, color: C.violet, pale: C.violetPale, title: 'AUTOMATION', q: 'Kondisi apa yang memicu aksi?', body: 'Menjalankan workflow atau respons lain ketika aturan waktu, event, atau status terpenuhi.' },
    { x: 8.24, color: C.amber, pale: C.amberPale, title: 'SCHEDULING', q: 'Kapan workflow dimulai?', body: 'Menentukan cadence berbasis waktu, timezone, kalender, dan ekspresi cron.' },
  ];
  columns.forEach((c, i) => {
    box(slide, c.x, 1.65, 3.35, 4.65, c.pale, c.color);
    circle(slide, c.x + 0.28, 1.97, 0.66, c.color);
    addText(slide, String(i + 1), c.x + 0.28, 2.14, 0.66, 0.22, { fontSize: 16, bold: true, color: C.white, align: 'center' });
    addText(slide, c.title, c.x + 1.1, 1.98, 1.95, 0.3, { fontSize: 14, bold: true, color: c.color, charSpacing: 0.8 });
    addText(slide, c.q, c.x + 0.3, 2.86, 2.75, 0.78, { fontSize: 24, bold: true, color: C.ink, valign: 'top' });
    addText(slide, c.body, c.x + 0.3, 4.05, 2.75, 1.2, { fontSize: 17, color: C.muted, valign: 'top' });
  });
  arrow(slide, 4.09, 3.78, 0.32, 0, C.line, 2);
  arrow(slide, 7.85, 3.78, 0.32, 0, C.line, 2);
  addText(slide, 'Contoh project: Dagster mengorkestrasi job, schedule memicu pukul 02.00 WIB, daemon mengotomatisasi evaluasi jadwal.', 1.18, 6.58, 11.0, 0.42, { fontSize: 16, bold: true, color: C.navy, align: 'center' });
  addSourceNote(slide, [
    'https://dagster.io/docs/guides/automate/schedules',
    'https://dagster.io/docs/guides/automate/sensors',
  ]);
}

// Slide 4: Scheduling mechanics
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Schedule harian pukul 02.00 WIB', 'Cron menentukan cadence, timezone menghilangkan ambiguitas, dan daemon mengevaluasi jadwal.');
  box(slide, 0.72, 1.55, 5.05, 2.35, C.navy, C.navy);
  addText(slide, 'ScheduleDefinition(', 1.05, 1.9, 4.2, 0.3, { fontFace: 'Courier New', fontSize: 18, color: '93C5FD' });
  addText(slide, '  cron_schedule="0 2 * * *",\n  execution_timezone="Asia/Jakarta",\n  default_status=STOPPED,\n)', 1.05, 2.28, 4.2, 1.25, { fontFace: 'Courier New', fontSize: 15.5, color: C.white, valign: 'top', breakLine: false });

  addSectionLabel(slide, 'Anatomi cron', 6.35, 1.55, C.amber);
  const cron = [
    ['0', 'menit'], ['2', 'jam'], ['*', 'tanggal'], ['*', 'bulan'], ['*', 'hari'],
  ];
  cron.forEach((c, i) => {
    const x = 6.35 + i * 1.16;
    box(slide, x, 2.02, 0.88, 0.88, i < 2 ? C.amberPale : C.white, i < 2 ? C.amber : C.line);
    addText(slide, c[0], x, 2.17, 0.88, 0.34, { fontFace: 'Courier New', fontSize: 25, bold: true, color: i < 2 ? C.amber : C.ink, align: 'center' });
    addText(slide, c[1], x - 0.08, 3.05, 1.04, 0.28, { fontSize: 12, color: C.muted, align: 'center' });
  });
  addText(slide, 'Artinya: setiap hari pada 02:00 menurut timezone Asia/Jakarta.', 6.35, 3.58, 5.95, 0.38, { fontSize: 18, bold: true, color: C.navy });

  addSectionLabel(slide, 'Urutan evaluasi', 0.72, 4.45, C.blue);
  const timeline = [
    ['01:59', 'Daemon aktif'], ['02:00', 'Schedule tick'], ['02:00', 'Run queued'], ['02:00+', 'Job executes'], ['Selesai', 'Status tersimpan'],
  ];
  slide.addShape(pptx.ShapeType.line, { x: 1.2, y: 5.42, w: 10.85, h: 0, line: { color: C.line, width: 4 } });
  timeline.forEach((t, i) => {
    const x = 1.02 + i * 2.7;
    circle(slide, x, 5.14, 0.56, i === 1 ? C.amber : C.blue);
    addText(slide, t[0], x - 0.35, 4.78, 1.26, 0.28, { fontSize: 14, bold: true, color: i === 1 ? C.amber : C.blue, align: 'center' });
    addText(slide, t[1], x - 0.58, 5.86, 1.72, 0.34, { fontSize: 14, color: C.ink, align: 'center' });
  });
  addText(slide, 'Status STOPPED mencegah schedule berjalan sebelum operator menyelesaikan validasi awal.', 2.08, 6.65, 9.3, 0.34, { fontSize: 15, color: C.muted, align: 'center' });
  addSourceNote(slide, ['https://dagster.io/docs/guides/automate/schedules'], 'Potongan konfigurasi berasal dari orchestration/definitions.py pada final-project.');
}

// Slide 5: Project architecture
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Arsitektur YouTube Trend Analytics', 'Dagster mengontrol urutan load, transformasi, test, dan validasi sebelum data dipakai API.');
  const stages = [
    { x: 0.55, w: 1.65, title: 'CSV', sub: 'source + master', fill: C.cyanPale, color: C.cyan },
    { x: 2.55, w: 1.82, title: 'BRONZE', sub: 'raw_* · String', fill: C.bluePale, color: C.blue },
    { x: 4.78, w: 1.82, title: 'SILVER', sub: 'clean + typed', fill: C.violetPale, color: C.violet },
    { x: 7.02, w: 1.82, title: 'GOLD', sub: '5 data marts', fill: C.amberPale, color: C.amber },
    { x: 9.25, w: 1.55, title: 'API', sub: 'FastAPI', fill: C.greenPale, color: C.green },
    { x: 11.2, w: 1.55, title: 'WEB', sub: 'dashboard', fill: C.white, color: C.navy },
  ];
  stages.forEach((s, i) => {
    if (i < stages.length - 1) arrow(slide, s.x + s.w + 0.08, 3.22, stages[i + 1].x - (s.x + s.w) - 0.15, 0, C.line, 2);
    box(slide, s.x, 2.38, s.w, 1.65, s.fill, s.color);
    addText(slide, s.title, s.x, 2.73, s.w, 0.38, { fontSize: 20, bold: true, color: s.color, align: 'center' });
    addText(slide, s.sub, s.x + 0.08, 3.25, s.w - 0.16, 0.3, { fontSize: 13, color: C.muted, align: 'center' });
  });
  box(slide, 1.62, 1.35, 8.25, 0.52, C.navy, C.navy);
  addText(slide, 'DAGSTER JOB: load_bronze  →  build_silver  →  build_gold  →  tests  →  validation', 1.86, 1.47, 7.78, 0.28, { fontSize: 14, bold: true, color: C.white, align: 'center' });

  const details = [
    ['Input', 'data/source dan data/master'],
    ['Transform', 'dbt/models/silver dan dbt/models/gold'],
    ['Serve', 'dashboard/app.py dan dashboard/static'],
  ];
  details.forEach((d, i) => {
    const x = 1.2 + i * 4.08;
    addText(slide, d[0], x, 4.82, 0.9, 0.28, { fontSize: 12, bold: true, color: [C.cyan, C.violet, C.green][i] });
    addText(slide, d[1], x, 5.2, 3.65, 0.55, { fontSize: 17, bold: true, color: C.ink, valign: 'top' });
  });
  box(slide, 1.2, 6.18, 10.98, 0.6, C.white, C.line);
  addText(slide, 'Port terisolasi: ClickHouse 18123/19000  ·  Dagster 13000  ·  Dashboard 18080', 1.45, 6.32, 10.5, 0.28, { fontSize: 14, color: C.muted, align: 'center' });
  addSourceNote(slide, [], 'Sumber implementasi lokal: docker-compose.yml, orchestration/definitions.py, dbt/, ingestion/, dan dashboard/.');
}

// Slide 6: Dagster job
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Job Dagster menjaga urutan dan kualitas data', 'Setiap op hanya berjalan setelah upstream sukses. Retry policy menangani kegagalan sementara.');
  const steps = [
    { name: 'load_bronze', desc: '3 CSV ke raw_*', color: C.cyan },
    { name: 'build_silver', desc: 'clean, type, WIB', color: C.blue },
    { name: 'build_gold', desc: '5 mart analitik', color: C.violet },
    { name: 'run_data_\ntests', desc: 'source + model test', color: C.amber },
    { name: 'validate_\nwarehouse', desc: 'row count + nonempty', color: C.green },
  ];
  steps.forEach((s, i) => {
    const x = 0.55 + i * 2.55;
    if (i < steps.length - 1) arrow(slide, x + 2.08, 3.15, 0.42, 0, C.line, 2.3);
    circle(slide, x + 0.65, 1.72, 0.72, s.color);
    addText(slide, String(i + 1), x + 0.65, 1.91, 0.72, 0.24, { fontSize: 16, bold: true, color: C.white, align: 'center' });
    box(slide, x, 2.6, 2.08, 1.85, C.white, s.color);
    addText(slide, s.name, x + 0.12, 2.86, 1.84, 0.62, { fontFace: 'Courier New', fontSize: 14, bold: true, color: s.color, align: 'center', valign: 'mid' });
    addText(slide, s.desc, x + 0.16, 3.55, 1.76, 0.46, { fontSize: 14, color: C.muted, align: 'center', valign: 'top' });
  });

  box(slide, 0.78, 5.15, 3.55, 1.15, C.bluePale, '93C5FD');
  addText(slide, 'Retry policy', 1.05, 5.4, 1.3, 0.3, { fontSize: 16, bold: true, color: C.blueDark });
  addText(slide, 'max_retries = 2\ndelay = 10 detik', 2.45, 5.32, 1.5, 0.56, { fontFace: 'Courier New', fontSize: 14, color: C.ink, valign: 'top' });
  box(slide, 4.85, 5.15, 3.55, 1.15, C.greenPale, '6EE7B7');
  addText(slide, 'Quality gate', 5.12, 5.4, 1.3, 0.3, { fontSize: 16, bold: true, color: C.green });
  addText(slide, 'Bronze = Silver\nGold tidak kosong', 6.45, 5.32, 1.55, 0.56, { fontFace: 'Courier New', fontSize: 14, color: C.ink, valign: 'top' });
  box(slide, 8.9, 5.15, 3.55, 1.15, C.amberPale, 'FCD34D');
  addText(slide, 'Observability', 9.17, 5.4, 1.35, 0.3, { fontSize: 16, bold: true, color: C.amber });
  addText(slide, 'log per op\nmetadata row count', 10.55, 5.32, 1.55, 0.56, { fontFace: 'Courier New', fontSize: 14, color: C.ink, valign: 'top' });
  addSourceNote(slide, [], 'Sumber implementasi lokal: orchestration/definitions.py.');
}

// Slide 7: Components
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Webserver, daemon, dan code location', 'Schedule hanya berjalan ketika daemon aktif dan definitions berhasil dimuat.');
  const comps = [
    { x: 0.8, y: 1.72, title: 'definitions.py', desc: 'Job, op, schedule, retry', color: C.violet, fill: C.violetPale },
    { x: 4.75, y: 1.72, title: 'Dagster webserver', desc: 'UI, launch, log, run history', color: C.blue, fill: C.bluePale },
    { x: 8.7, y: 1.72, title: 'Dagster daemon', desc: 'Evaluate schedule dan queue run', color: C.amber, fill: C.amberPale },
  ];
  comps.forEach((c, i) => {
    box(slide, c.x, c.y, 3.0, 1.42, c.fill, c.color);
    addText(slide, c.title, c.x + 0.22, c.y + 0.3, 2.56, 0.34, { fontSize: 20, bold: true, color: c.color, align: 'center' });
    addText(slide, c.desc, c.x + 0.22, c.y + 0.82, 2.56, 0.34, { fontSize: 14, color: C.muted, align: 'center' });
    if (i < comps.length - 1) arrow(slide, c.x + 3.12, 2.43, 0.78, 0, C.line, 2);
  });

  // Orthogonal connector: daemon evaluates the schedule and creates a run.
  slide.addShape(pptx.ShapeType.line, {
    x: 10.2, y: 3.14, w: 0, h: 0.76,
    line: { color: C.amber, width: 2.3 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 4.6, y: 3.9, w: 5.6, h: 0,
    line: { color: C.amber, width: 2.3 },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 4.6, y: 3.9, w: 0, h: 0.65,
    line: { color: C.amber, width: 2.3, endArrowType: 'triangle' },
  });
  box(slide, 2.45, 4.55, 4.3, 1.2, C.navy, C.navy);
  addText(slide, 'Queued run', 2.78, 4.72, 3.65, 0.3, { fontSize: 18, bold: true, color: C.white, align: 'center' });
  addText(slide, 'youtube_trending_elt_job', 2.78, 5.2, 3.65, 0.3, { fontFace: 'Courier New', fontSize: 12, color: '93C5FD', align: 'center' });
  arrow(slide, 6.9, 5.15, 0.9, 0, C.line, 2);
  box(slide, 7.95, 4.55, 3.05, 1.2, C.greenPale, C.green);
  addText(slide, 'ClickHouse', 8.18, 4.78, 2.6, 0.3, { fontSize: 19, bold: true, color: C.green, align: 'center' });
  addText(slide, 'bronze · silver · gold', 8.18, 5.22, 2.6, 0.26, { fontSize: 14, color: C.muted, align: 'center' });

  box(slide, 1.42, 6.27, 10.5, 0.56, C.white, C.line);
  addText(slide, 'Schedule disimpan dalam code, status ON/OFF dikelola oleh instance, dan daemon mengeksekusi tick.', 1.7, 6.4, 9.95, 0.28, { fontSize: 15, color: C.ink, align: 'center' });
  addSourceNote(slide, ['https://dagster.io/docs/guides/automate/schedules'], 'Sumber implementasi lokal: docker-compose.yml dan orchestration/.');
}

// Slide 8: Automation choices
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Pilihan trigger pada Dagster', 'Pilih trigger berdasarkan sinyal yang tersedia, bukan hanya berdasarkan kebiasaan memakai cron.');
  addText(slide, 'Apa sinyal yang memulai pipeline?', 0.78, 1.62, 4.0, 0.42, { fontSize: 24, bold: true, color: C.navy });
  box(slide, 0.8, 2.32, 2.55, 1.2, C.bluePale, C.blue);
  addText(slide, 'WAKTU TETAP', 1.06, 2.58, 2.02, 0.28, { fontSize: 14, bold: true, color: C.blue, align: 'center' });
  addText(slide, 'Schedule', 1.06, 2.98, 2.02, 0.3, { fontSize: 21, bold: true, color: C.ink, align: 'center' });
  box(slide, 0.8, 4.0, 2.55, 1.2, C.violetPale, C.violet);
  addText(slide, 'EVENT TERDETEKSI', 1.06, 4.26, 2.02, 0.28, { fontSize: 14, bold: true, color: C.violet, align: 'center' });
  addText(slide, 'Sensor', 1.06, 4.66, 2.02, 0.3, { fontSize: 21, bold: true, color: C.ink, align: 'center' });
  box(slide, 0.8, 5.68, 2.55, 1.2, C.greenPale, C.green);
  addText(slide, 'PUSH DARI SISTEM', 1.06, 5.94, 2.02, 0.28, { fontSize: 14, bold: true, color: C.green, align: 'center' });
  addText(slide, 'API / GraphQL', 1.06, 6.34, 2.02, 0.3, { fontSize: 21, bold: true, color: C.ink, align: 'center' });

  arrow(slide, 3.57, 2.92, 1.0, 0, C.line, 2);
  arrow(slide, 3.57, 4.6, 1.0, 0, C.line, 2);
  arrow(slide, 3.57, 6.28, 1.0, 0, C.line, 2);
  const responses = [
    { y: 2.32, title: 'Gunakan untuk cadence bisnis yang stabil', body: 'Contoh: refresh data setiap hari pukul 02.00 WIB.', color: C.blue },
    { y: 4.0, title: 'Gunakan saat event perlu diperiksa berkala', body: 'Contoh: file baru muncul, run gagal, atau asset selesai.', color: C.violet },
    { y: 5.68, title: 'Gunakan saat sumber dapat mengirim event', body: 'Contoh: webhook atau aplikasi upstream meminta run.', color: C.green },
  ];
  responses.forEach(r => {
    box(slide, 4.8, r.y, 7.5, 1.2, C.white, C.line);
    addText(slide, r.title, 5.12, r.y + 0.22, 6.8, 0.32, { fontSize: 18, bold: true, color: r.color });
    addText(slide, r.body, 5.12, r.y + 0.66, 6.8, 0.3, { fontSize: 15, color: C.muted });
  });
  addSourceNote(slide, [
    'https://dagster.io/docs/guides/automate/schedules',
    'https://dagster.io/docs/guides/automate/sensors',
  ]);
}

// Slide 9: Three tools
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Dagster, Kestra, dan Prefect', 'Ketiganya mengorkestrasi workflow, tetapi memakai model authoring dan operasi yang berbeda.');
  const tools = [
    { x: 0.68, name: 'Dagster', color: C.blue, pale: C.bluePale, lead: 'Data assets dan Python', lines: ['Job, op, asset', 'Schedule dan sensor', 'UI lineage dan run history'] },
    { x: 4.48, name: 'Kestra', color: C.violet, pale: C.violetPale, lead: 'Flow deklaratif berbasis YAML', lines: ['Task dari plugin', 'Schedule, webhook, polling', 'Worker menjalankan task'] },
    { x: 8.28, name: 'Prefect', color: C.green, pale: C.greenPale, lead: 'Native Python functions', lines: ['@flow dan @task', 'Deployment schedules', 'Events dan automations'] },
  ];
  tools.forEach((t, i) => {
    box(slide, t.x, 1.58, 3.38, 4.82, t.pale, t.color);
    circle(slide, t.x + 0.28, 1.88, 0.78, t.color);
    addText(slide, String(i + 1), t.x + 0.28, 2.1, 0.78, 0.24, { fontSize: 17, bold: true, color: C.white, align: 'center' });
    addText(slide, t.name, t.x + 1.22, 1.9, 1.8, 0.4, { fontSize: 27, bold: true, color: t.color });
    addText(slide, t.lead, t.x + 0.3, 2.9, 2.78, 0.68, { fontSize: 21, bold: true, color: C.ink, valign: 'top' });
    addBullets(slide, t.lines, t.x + 0.28, 4.0, 2.72, 1.65, { fontSize: 16, margin: 0 });
  });
  addText(slide, 'Perbedaan utama ada pada cara mendefinisikan workflow, model trigger, dan cara worker menerima pekerjaan.', 1.15, 6.67, 11.0, 0.34, { fontSize: 15, color: C.muted, align: 'center' });
  addSourceNote(slide, [
    'https://docs.dagster.io/getting-started/quickstart',
    'https://kestra.io/docs/workflow-components/triggers',
    'https://docs.prefect.io/v3/get-started',
  ]);
}

// Slide 10: Comparison table
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Perbandingan pendekatan', 'Ringkasan praktis berdasarkan dokumentasi resmi dan model implementasi masing-masing tool.');
  const rows = [
    [
      { text: 'Dimensi', options: { bold: true, color: C.white, fill: C.navy } },
      { text: 'Dagster', options: { bold: true, color: C.white, fill: C.blue } },
      { text: 'Kestra', options: { bold: true, color: C.white, fill: C.violet } },
      { text: 'Prefect', options: { bold: true, color: C.white, fill: C.green } },
    ],
    ['Authoring', 'Python: asset, job, op', 'YAML: flow dan task plugin', 'Python: function, @flow, @task'],
    ['Time trigger', 'ScheduleDefinition + cron', 'Schedule trigger dalam flow', 'Schedule pada deployment'],
    ['Event trigger', 'Sensor atau API push', 'Webhook, polling, realtime, flow trigger', 'Events dan automations'],
    ['Runtime', 'Webserver, daemon, run executor', 'Server roles dan workers', 'Server/Cloud, work pool, worker'],
    ['Kekuatan praktis', 'Asset lineage, dbt, data quality', 'Workflow lintas tool yang deklaratif', 'Python dinamis dan portable'],
  ];
  slide.addTable(rows, {
    x: 0.62, y: 1.5, w: 12.1, h: 4.95,
    colW: [2.0, 3.25, 3.45, 3.4],
    rowH: [0.6, 0.78, 0.78, 0.9, 0.9, 0.9],
    fontFace: FONT,
    fontSize: 14,
    color: C.ink,
    margin: 0.12,
    border: { type: 'solid', color: C.line, pt: 1 },
    fill: C.white,
    valign: 'mid',
    autoFit: false,
    isTextBox: true,
  });
  addText(slide, '“Kekuatan praktis” adalah inferensi penggunaan, bukan batas kemampuan produk.', 0.75, 6.66, 11.8, 0.28, { fontSize: 12, color: C.muted, italic: true, align: 'center' });
  addSourceNote(slide, [
    'https://dagster.io/docs/guides/automate/schedules',
    'https://dagster.io/docs/guides/automate/sensors',
    'https://kestra.io/docs/workflow-components/triggers',
    'https://docs.prefect.io/v3/concepts/automations',
    'https://docs.prefect.io/v3/how-to-guides/deployments/deploy-via-python',
  ], 'Baris kekuatan praktis adalah inferensi dari model authoring dan fitur resmi.');
}

// Slide 11: Selection guide
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Pemilihan tool berdasarkan konteks', 'Tidak ada pemenang universal. Pilihan mengikuti bentuk workflow dan cara tim bekerja.');
  const choices = [
    { y: 1.55, name: 'Dagster', color: C.blue, fill: C.bluePale, title: 'Data platform dan asset lineage', body: 'Cocok ketika tim memodelkan dataset sebagai asset, memakai dbt, dan membutuhkan quality gate yang terlihat jelas.', verdict: 'Dipakai pada final-project ini' },
    { y: 3.35, name: 'Kestra', color: C.violet, fill: C.violetPale, title: 'Workflow deklaratif lintas sistem', body: 'Cocok ketika flow menggabungkan banyak plugin, task infrastruktur, webhook, queue, dan sistem non-Python.', verdict: 'Kuat untuk integrasi heterogen' },
    { y: 5.15, name: 'Prefect', color: C.green, fill: C.greenPale, title: 'Workflow Python yang dinamis', body: 'Cocok ketika control flow Python, data science, atau ML memerlukan branching dan runtime yang fleksibel.', verdict: 'Nyaman bagi tim Python-first' },
  ];
  choices.forEach(c => {
    box(slide, 0.72, c.y, 11.9, 1.42, c.fill, c.color);
    addText(slide, c.name, 1.05, c.y + 0.34, 1.6, 0.42, { fontSize: 25, bold: true, color: c.color });
    addText(slide, c.title, 2.82, c.y + 0.23, 3.35, 0.38, { fontSize: 19, bold: true, color: C.ink });
    addText(slide, c.body, 2.82, c.y + 0.69, 6.55, 0.5, { fontSize: 15, color: C.muted, valign: 'top' });
    addText(slide, c.verdict, 9.65, c.y + 0.42, 2.55, 0.5, { fontSize: 15, bold: true, color: c.color, align: 'center' });
  });
  addSourceNote(slide, [
    'https://docs.dagster.io/getting-started/quickstart',
    'https://kestra.io/docs/workflow-components/triggers',
    'https://docs.prefect.io/v3/get-started',
  ], 'Rekomendasi adalah inferensi praktis dan bukan klaim eksklusif vendor.');
}

// Slide 12: Checklist
{
  const slide = pptx.addSlide();
  slide.background = { color: C.navy };
  addText(slide, 'Checklist sebelum schedule diaktifkan', 0.72, 0.55, 11.9, 0.62, { fontSize: 36, bold: true, color: C.white, valign: 'top' });
  addText(slide, 'Schedule yang tepat waktu tetap berbahaya jika pipeline belum aman untuk dijalankan berulang.', 0.74, 1.28, 11.5, 0.38, { fontSize: 17, color: 'CBD5E1' });
  const checks = [
    ['01', 'Idempotency', 'Run ulang tidak menggandakan data'],
    ['02', 'Timezone', 'WIB dinyatakan secara eksplisit'],
    ['03', 'Failure handling', 'Retry dan status gagal terlihat'],
    ['04', 'Quality gate', 'Test dan row-count validation aktif'],
    ['05', 'Concurrency', 'Overlap dan backfill diputuskan'],
    ['06', 'Alerting', 'Operator menerima sinyal saat gagal'],
  ];
  checks.forEach((c, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.78 + col * 6.1;
    const y = 2.0 + row * 1.4;
    circle(slide, x, y, 0.66, i < 4 ? C.green : C.amber);
    addText(slide, c[0], x, y + 0.19, 0.66, 0.22, { fontSize: 14, bold: true, color: C.white, align: 'center' });
    addText(slide, c[1], x + 0.92, y + 0.02, 2.1, 0.34, { fontSize: 19, bold: true, color: C.white });
    addText(slide, c[2], x + 0.92, y + 0.48, 4.6, 0.38, { fontSize: 15, color: '94A3B8' });
  });
  box(slide, 0.78, 6.35, 11.75, 0.62, '1E293B', '334155');
  addText(slide, 'Current project: poin 01–04 siap. Tahap berikutnya: kebijakan concurrency dan notifikasi failure.', 1.05, 6.5, 11.2, 0.3, { fontSize: 15, bold: true, color: 'BFDBFE', align: 'center' });
  addSourceNote(slide, [], 'Checklist disusun dari risiko operasional pada final-project dan fitur orchestrator yang dibahas dalam deck.');
}

pptx.writeFile({ fileName: OUT });
