const state = { charts: {}, filters: {}, loading: false };

const palette = ["#2563eb", "#7c3aed", "#d97706", "#0f9f6e", "#db2777", "#0891b2"];
const compact = new Intl.NumberFormat("id-ID", { notation: "compact", maximumFractionDigits: 1 });
const number = new Intl.NumberFormat("id-ID");

const $ = (selector) => document.querySelector(selector);
const api = async (path, params = {}) => {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined));
  const response = await fetch(`${path}?${query}`);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `API error ${response.status}`);
  }
  return response.json();
};

function queryParams() {
  return {
    start_date: $("#start-date").value,
    end_date: $("#end-date").value,
    category_id: $("#category-select").value,
  };
}

function setLoading(loading) {
  state.loading = loading;
  $("#refresh-button").disabled = loading;
  $("#refresh-button span").textContent = loading ? "Memuat…" : "Refresh data";
  document.querySelectorAll(".kpi-card strong").forEach((node) => node.classList.toggle("loading", loading));
}

function setChart(name, elementId, config) {
  if (state.charts[name]) state.charts[name].destroy();
  const context = document.getElementById(elementId).getContext("2d");
  state.charts[name] = new Chart(context, config);
}

function commonOptions() {
  const dark = document.documentElement.dataset.theme === "dark";
  const textColor = dark ? "#a9b6cb" : "#5f6b7d";
  const gridColor = dark ? "rgba(169,182,203,.13)" : "rgba(95,107,125,.12)";
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "nearest", intersect: false },
    plugins: {
      legend: { position: "top", align: "end", labels: { color: textColor, boxWidth: 9, boxHeight: 9, usePointStyle: true, pointStyle: "circle", padding: 16, font: { family: "Fira Sans", size: 11 } } },
      tooltip: { backgroundColor: dark ? "#020617" : "#172033", padding: 11, titleFont: { family: "Fira Sans", size: 12 }, bodyFont: { family: "Fira Sans", size: 11 }, cornerRadius: 9 },
    },
    scales: {
      x: { ticks: { color: textColor, font: { family: "Fira Sans", size: 10 }, maxRotation: 0 }, grid: { color: gridColor } },
      y: { beginAtZero: true, ticks: { color: textColor, font: { family: "Fira Code", size: 9 }, callback: (value) => compact.format(value) }, grid: { color: gridColor } },
    },
  };
}

function renderOverview(data) {
  $("#kpi-appearances").textContent = compact.format(data.trending_appearances);
  $("#kpi-videos").textContent = compact.format(data.unique_videos);
  $("#kpi-channels").textContent = number.format(data.unique_channels);
  $("#kpi-engagement").textContent = `${data.average_engagement_pct ?? 0}%`;
  $("#kpi-category").textContent = data.top_category || "—";
  $("#kpi-views").textContent = `Total views: ${compact.format(data.total_views || 0)}`;
  $("#overview-summary").textContent = `${number.format(data.unique_videos)} video dari ${number.format(data.unique_channels)} channel masuk trending pada periode terpilih.`;
}

function renderCategoryTrends(payload) {
  const rows = payload.data;
  const periods = [...new Set(rows.map((row) => row.period))];
  const categories = [...new Set(rows.map((row) => row.category_name))];
  const datasets = categories.map((category, index) => ({
    label: category,
    data: periods.map((period) => rows.find((row) => row.period === period && row.category_name === category)?.appearances || 0),
    borderColor: palette[index % palette.length],
    backgroundColor: `${palette[index % palette.length]}18`,
    borderWidth: 2,
    pointRadius: periods.length > 40 ? 0 : 2,
    pointHoverRadius: 5,
    tension: .28,
    fill: false,
  }));
  setChart("categories", "category-chart", { type: "line", data: { labels: periods, datasets }, options: commonOptions() });
  if (rows.length) {
    const totals = categories.map((category) => ({ category, total: rows.filter((row) => row.category_name === category).reduce((sum, row) => sum + row.appearances, 0) })).sort((a, b) => b.total - a.total);
    $("#category-summary").textContent = `${totals[0].category} menjadi kategori paling konsisten dengan ${number.format(totals[0].total)} kemunculan pada rentang terpilih.`;
  } else $("#category-summary").textContent = "Tidak ada data kategori pada rentang ini.";
}

function renderChannels(rows) {
  const options = commonOptions();
  options.indexAxis = "y";
  options.plugins.legend.display = false;
  options.scales.y.ticks.callback = function(value) { const label = this.getLabelForValue(value); return label.length > 24 ? `${label.slice(0, 24)}…` : label; };
  setChart("channels", "channel-chart", {
    type: "bar",
    data: { labels: rows.map((row) => row.channel_name), datasets: [{ label: "Trending appearances", data: rows.map((row) => row.trending_appearances), backgroundColor: rows.map((_, index) => `${palette[index % palette.length]}cc`), borderRadius: 6, borderSkipped: false }] },
    options,
  });
  $("#channel-table-body").innerHTML = rows.length ? rows.map((row, index) => `<tr><td>${index + 1}</td><td title="${escapeHtml(row.channel_name)}">${escapeHtml(row.channel_name)}</td><td>${number.format(row.trending_appearances)}</td><td>${row.average_rank}</td></tr>`).join("") : '<tr><td colspan="4">Tidak ada data channel.</td></tr>';
}

function renderEngagement(rows) {
  const maxComments = Math.max(...rows.map((row) => row.comments), 1);
  const points = rows.filter((row) => row.views > 0 && row.likes > 0).map((row) => ({
    x: row.views,
    y: row.likes,
    r: 4 + Math.sqrt(row.comments / maxComments) * 14,
    videoTitle: row.video_title,
    channelName: row.channel_name,
    comments: row.comments,
    bestRank: row.best_rank,
  }));
  const options = commonOptions();
  options.scales.x.type = "logarithmic";
  options.scales.x.title = { display: true, text: "Views (log scale)" };
  options.scales.y.type = "logarithmic";
  options.scales.y.title = { display: true, text: "Likes (log scale)" };
  options.plugins.legend.display = false;
  options.plugins.tooltip.callbacks = {
    title: (items) => items[0].raw.videoTitle,
    label: (context) => {
      const point = context.raw;
      return [`Channel: ${point.channelName}`, `Views: ${number.format(point.x)}`, `Likes: ${number.format(point.y)}`, `Comments: ${number.format(point.comments)}`, `Best rank: ${point.bestRank}`];
    },
  };
  setChart("engagement", "engagement-chart", {
    type: "bubble",
    data: { datasets: [{ label: "Video", data: points, backgroundColor: "rgba(37,99,235,.55)", borderColor: "#1e40af", borderWidth: 1 }] },
    options,
  });
  if (rows.length) {
    const leader = [...rows].sort((a, b) => b.engagement_pct - a.engagement_pct)[0];
    $("#engagement-summary").textContent = `${leader.video_title} memiliki engagement tertinggi (${leader.engagement_pct}%) di antara sampel video dengan views terbesar.`;
  }
}

function renderDuration(rows) {
  const options = commonOptions();
  options.scales.engagement = { position: "right", beginAtZero: true, ticks: { callback: (value) => `${value}%` }, grid: { drawOnChartArea: false } };
  setChart("duration", "duration-chart", {
    data: { labels: rows.map((row) => row.duration_bucket), datasets: [
      { type: "bar", label: "Average views", data: rows.map((row) => row.average_views), backgroundColor: "rgba(37,99,235,.75)", borderRadius: 6, borderSkipped: false },
      { type: "line", label: "Engagement %", data: rows.map((row) => row.average_engagement_pct), yAxisID: "engagement", borderColor: "#d97706", backgroundColor: "#d97706", pointRadius: 4, tension: .25 },
    ] }, options,
  });
}

function renderRank(rows) {
  const options = commonOptions();
  options.plugins.legend.display = false;
  setChart("rank", "rank-chart", { type: "bar", data: { labels: rows.map((row) => row.rank_bucket), datasets: [{ label: "Average views", data: rows.map((row) => row.average_views), backgroundColor: ["#1e40af", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd"], borderRadius: 7, borderSkipped: false }] }, options });
}

function renderSeasonal(rows) {
  const options = commonOptions();
  options.indexAxis = "y";
  options.plugins.legend.display = false;
  setChart("seasonal", "seasonal-chart", { type: "bar", data: { labels: rows.map((row) => row.season_name), datasets: [{ label: "Trending appearances", data: rows.map((row) => row.trending_appearances), backgroundColor: rows.map((_, index) => `${palette[index % palette.length]}cc`), borderRadius: 6, borderSkipped: false }] }, options });
}

function renderInsights({ overview, channels, duration, seasonal }) {
  const durationLeader = [...duration].sort((a, b) => b.average_engagement_pct - a.average_engagement_pct)[0];
  const seasonalLeader = [...seasonal].filter((row) => row.season_name !== "Regular period").sort((a, b) => b.average_engagement_pct - a.average_engagement_pct)[0];
  const cards = [
    ["Content leader", `${overview.top_category} memimpin kemunculan trending pada periode ini.`],
    ["Creator leader", channels[0] ? `${channels[0].channel_name} muncul ${number.format(channels[0].trending_appearances)} kali.` : "Belum ada data creator."],
    ["Duration signal", durationLeader ? `Video ${durationLeader.duration_bucket} memiliki rata-rata engagement tertinggi (${durationLeader.average_engagement_pct}%).` : "Belum ada data durasi."],
    ["Cultural moment", seasonalLeader ? `${seasonalLeader.season_name} mencatat engagement ${seasonalLeader.average_engagement_pct}%.` : "Belum ada data seasonal."],
  ];
  $("#insight-list").innerHTML = cards.map(([label, value]) => `<div class="insight-item"><span>${label}</span><strong>${escapeHtml(value)}</strong></div>`).join("");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

async function loadDashboard() {
  if (state.loading) return;
  setLoading(true);
  $("#error-banner").hidden = true;
  const params = queryParams();
  try {
    const [overview, trends, channels, engagement, duration, rank, seasonal] = await Promise.all([
      api("/api/overview", params),
      api("/api/category-trends", { ...params, granularity: $("#granularity-select").value }),
      api("/api/top-channels", { ...params, limit: 10 }),
      api("/api/engagement-scatter", { ...params, limit: 180 }),
      api("/api/duration-performance", params),
      api("/api/rank-performance", params),
      api("/api/seasonal", { category_id: params.category_id }),
    ]);
    state.filters = params;
    renderOverview(overview);
    renderCategoryTrends(trends);
    renderChannels(channels);
    renderEngagement(engagement);
    renderDuration(duration);
    renderRank(rank);
    renderSeasonal(seasonal);
    renderInsights({ overview, channels, duration, seasonal });
    $("#last-updated").textContent = `Updated ${new Intl.DateTimeFormat("id-ID", { dateStyle: "medium", timeStyle: "short" }).format(new Date())}`;
  } catch (error) {
    $("#error-message").textContent = error.message;
    $("#error-banner").hidden = false;
  } finally {
    setLoading(false);
  }
}

async function initialize() {
  setLoading(true);
  try {
    const filters = await api("/api/filters");
    $("#start-date").value = filters.min_date;
    $("#end-date").value = filters.max_date;
    $("#category-select").insertAdjacentHTML("beforeend", filters.categories.map((item) => `<option value="${item.category_id}">${escapeHtml(item.category_name)}</option>`).join(""));
  } catch (error) {
    $("#error-message").textContent = error.message;
    $("#error-banner").hidden = false;
  } finally {
    setLoading(false);
  }
  await loadDashboard();
}

$("#filter-form").addEventListener("submit", (event) => { event.preventDefault(); loadDashboard(); });
$("#refresh-button").addEventListener("click", loadDashboard);
$("#retry-button").addEventListener("click", loadDashboard);
$("#theme-toggle").addEventListener("click", () => {
  const dark = document.documentElement.dataset.theme !== "dark";
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  $("#theme-toggle").setAttribute("aria-pressed", String(dark));
  $("#theme-toggle").setAttribute("aria-label", dark ? "Aktifkan mode terang" : "Aktifkan mode gelap");
  localStorage.setItem("dashboard-theme", dark ? "dark" : "light");
  if (Object.keys(state.filters).length) loadDashboard();
});
document.documentElement.dataset.theme = localStorage.getItem("dashboard-theme") || "light";

const sections = [...document.querySelectorAll(".section-block")];
const links = [...document.querySelectorAll(".nav-link")];
new IntersectionObserver((entries) => {
  entries.filter((entry) => entry.isIntersecting).forEach((entry) => {
    links.forEach((link) => link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`));
  });
}, { rootMargin: "-30% 0px -60%" }).observe(sections[0]);
sections.slice(1).forEach((section) => new IntersectionObserver((entries) => {
  entries.filter((entry) => entry.isIntersecting).forEach((entry) => links.forEach((link) => link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`)));
}, { rootMargin: "-30% 0px -60%" }).observe(section));

window.addEventListener("DOMContentLoaded", initialize);
