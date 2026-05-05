(function () {
  "use strict";

  function setChartDefaults() {
    if (!window.Chart) {
      return;
    }
    Chart.defaults.color = "#e8eaf0";
    Chart.defaults.font.family = "Space Grotesk, Helvetica Neue, Arial, sans-serif";
    Chart.defaults.borderColor = "rgba(45, 50, 71, 0.6)";
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
  }

  function createRevenueChart(ctx, data) {
    const labels = data.labels || [];
    const values = data.values || [];
    const running = data.running_total || [];

    return new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            type: "bar",
            label: "Revenue",
            data: values,
            backgroundColor: "rgba(108, 99, 255, 0.7)",
            borderRadius: 6,
          },
          {
            type: "line",
            label: "Running total",
            data: running,
            borderColor: "#6c63ff",
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 2,
          },
        ],
      },
      options: {
        responsive: true,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { position: "bottom" },
        },
        scales: {
          x: { grid: { color: "rgba(45, 50, 71, 0.3)" } },
          y: { grid: { color: "rgba(45, 50, 71, 0.3)" } },
        },
      },
    });
  }

  function createHoursChart(ctx, data) {
    return new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.labels || [],
        datasets: [
          {
            label: "Hours",
            data: data.values || [],
            backgroundColor: "rgba(108, 99, 255, 0.7)",
            borderRadius: 6,
          },
        ],
      },
      options: {
        indexAxis: "y",
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "rgba(45, 50, 71, 0.3)" } },
          y: { grid: { display: false } },
        },
      },
    });
  }

  function createClientPieChart(ctx, data) {
    return new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: data.labels || [],
        datasets: [
          {
            data: data.values || [],
            backgroundColor: [
              "#6c63ff",
              "#4caf7d",
              "#f59e0b",
              "#f44336",
              "#3f51b5",
            ],
            borderWidth: 0,
          },
        ],
      },
      options: {
        cutout: "60%",
        plugins: { legend: { position: "bottom" } },
      },
    });
  }

  function createHeatmap(canvas, data) {
    if (!canvas) {
      return;
    }
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    const cellSize = 14;
    const gap = 4;
    const rows = 7;
    const weeks = Math.floor(width / (cellSize + gap));
    const start = new Date(new Date().getFullYear(), 0, 1);
    const dataMap = {};
    (data || []).forEach((item) => {
      dataMap[item.date] = item.count;
    });

    function colorFor(value) {
      if (!value) {
        return "rgba(45, 50, 71, 0.4)";
      }
      if (value < 2) {
        return "rgba(108, 99, 255, 0.35)";
      }
      if (value < 4) {
        return "rgba(108, 99, 255, 0.6)";
      }
      return "rgba(108, 99, 255, 0.9)";
    }

    for (let week = 0; week < weeks; week += 1) {
      for (let day = 0; day < rows; day += 1) {
        const index = week * rows + day;
        const current = new Date(start);
        current.setDate(start.getDate() + index);
        const iso = current.toISOString().slice(0, 10);
        const value = dataMap[iso];
        const x = week * (cellSize + gap);
        const y = day * (cellSize + gap);
        ctx.fillStyle = colorFor(value);
        ctx.fillRect(x, y, cellSize, cellSize);
      }
    }
  }

  setChartDefaults();

  window.dashboardCharts = {
    createRevenueChart: createRevenueChart,
    createHoursChart: createHoursChart,
    createHeatmap: createHeatmap,
    createClientPieChart: createClientPieChart,
  };
})();
