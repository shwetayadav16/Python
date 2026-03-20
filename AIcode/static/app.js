const statsGrid = document.getElementById("statsGrid");
const chart = document.getElementById("chart");
const chartLegend = document.getElementById("chartLegend");
const activityList = document.getElementById("activityList");
const segments = document.getElementById("segments");
const updatedAt = document.getElementById("updatedAt");
const refreshButton = document.getElementById("refreshButton");

function createStatCard(stat) {
  return `
    <article class="stat-card">
      <div class="stat-top">
        <span>${stat.label}</span>
        <span class="pill ${stat.tone}">${stat.delta}</span>
      </div>
      <strong>${stat.value}</strong>
    </article>
  `;
}

function buildPolyline(values, height) {
  const width = 640;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = Math.max(max - min, 1);

  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - ((value - min) / range) * (height - 40) - 20;
      return `${x},${y}`;
    })
    .join(" ");
}

function renderChart(chartData) {
  const width = 640;
  const height = 280;
  const revenuePath = buildPolyline(chartData.revenue, height);
  const ordersPath = buildPolyline(chartData.orders, height);

  chart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" aria-label="Revenue and orders trend">
      <defs>
        <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgba(255, 119, 65, 0.45)"></stop>
          <stop offset="100%" stop-color="rgba(255, 119, 65, 0)"></stop>
        </linearGradient>
      </defs>
      ${chartData.labels.map((_, index) => {
        const x = (index / (chartData.labels.length - 1)) * width;
        return `<line x1="${x}" y1="0" x2="${x}" y2="${height}" class="grid-line"></line>`;
      }).join("")}
      <polyline points="${revenuePath}" class="revenue-line"></polyline>
      <polyline points="${ordersPath}" class="orders-line"></polyline>
      ${chartData.labels.map((label, index) => {
        const x = (index / (chartData.labels.length - 1)) * width;
        return `<text x="${x}" y="${height - 6}" text-anchor="middle">${label}</text>`;
      }).join("")}
    </svg>
  `;

  chartLegend.innerHTML = `
    <div class="legend-item"><span class="legend-swatch revenue"></span>Revenue</div>
    <div class="legend-item"><span class="legend-swatch orders"></span>Orders</div>
  `;
}

function renderActivities(items) {
  activityList.innerHTML = items.map((item) => `
    <article class="activity-item">
      <div class="activity-head">
        <strong>${item.title}</strong>
        <span>${item.status}</span>
      </div>
      <p>${item.detail}</p>
      <small>${item.time}</small>
    </article>
  `).join("");
}

function renderSegments(items) {
  const total = items.reduce((sum, item) => sum + item.value, 0);
  segments.innerHTML = items.map((item) => `
    <div class="segment-row">
      <div class="segment-copy">
        <strong>${item.name}</strong>
        <span>${item.value}%</span>
      </div>
      <div class="segment-bar">
        <span style="width:${(item.value / total) * 100}%"></span>
      </div>
    </div>
  `).join("");
}

async function loadDashboard() {
  refreshButton.disabled = true;
  refreshButton.textContent = "Refreshing...";

  try {
    const response = await fetch("/api/dashboard");
    const data = await response.json();
    statsGrid.innerHTML = data.stats.map(createStatCard).join("");
    renderChart(data.chart);
    renderActivities(data.activities);
    renderSegments(data.segments);
    updatedAt.textContent = `Updated ${data.generatedAt}`;
  } catch (error) {
    updatedAt.textContent = "Unable to load dashboard data";
    console.error(error);
  } finally {
    refreshButton.disabled = false;
    refreshButton.textContent = "Refresh data";
  }
}

refreshButton.addEventListener("click", loadDashboard);
loadDashboard();
setInterval(loadDashboard, 10000);
