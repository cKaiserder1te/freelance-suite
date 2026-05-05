(function () {
  "use strict";

  const navLinks = Array.from(document.querySelectorAll(".nav-link"));
  const pages = Array.from(document.querySelectorAll(".page"));
  const dateLabel = document.getElementById("current-date");
  const revenuePeriod = document.getElementById("revenue-period");
  const revenueFrom = document.getElementById("revenue-from");
  const revenueTo = document.getElementById("revenue-to");
  const hoursFrom = document.getElementById("hours-from");
  const hoursTo = document.getElementById("hours-to");
  const invoiceStatus = document.getElementById("invoice-status");

  let overviewRevenueChart;
  let revenueChart;
  let hoursChart;
  let clientPieChart;
  let clientData = [];
  let clientSort = { key: "total_revenue", direction: "desc" };

  function formatDate() {
    const now = new Date();
    return now.toLocaleDateString("en-US", {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  function setActivePage(route) {
    pages.forEach((page) => {
      page.classList.toggle("active", page.dataset.page === route);
    });
    navLinks.forEach((link) => {
      link.classList.toggle("active", link.dataset.route === route);
    });
  }

  function getRoute() {
    const hash = window.location.hash.replace("#", "");
    return hash || "overview";
  }

  function formatCurrency(value) {
    if (typeof value !== "number") {
      return "--";
    }
    return value.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function renderKPIs(kpis) {
    document.getElementById("kpi-mtd-revenue").textContent =
      formatCurrency(kpis.mtd_revenue) + " EUR";
    document.getElementById("kpi-mtd-hours").textContent =
      formatCurrency(kpis.mtd_hours) + " h";
    document.getElementById("kpi-ytd-revenue").textContent =
      formatCurrency(kpis.ytd_revenue) + " EUR";
    document.getElementById("kpi-active-projects").textContent =
      String(kpis.active_projects_count || 0);
  }

  async function loadOverview() {
    const [kpis, revenue, clients, heatmap] = await Promise.all([
      window.dashboardApi.fetchKPIs(),
      window.dashboardApi.fetchRevenue("month"),
      window.dashboardApi.fetchClients(),
      window.dashboardApi.fetchHeatmap(new Date().getFullYear()),
    ]);

    renderKPIs(kpis);

    const revenueCtx = document.getElementById("overview-revenue-chart");
    if (overviewRevenueChart) {
      overviewRevenueChart.destroy();
    }
    overviewRevenueChart = window.dashboardCharts.createRevenueChart(
      revenueCtx,
      revenue
    );

    const clientCtx = document.getElementById("overview-client-chart");
    if (clientPieChart) {
      clientPieChart.destroy();
    }
    clientPieChart = window.dashboardCharts.createClientPieChart(clientCtx, {
      labels: clients.map((item) => item.name),
      values: clients.map((item) => item.total_revenue),
    });

    const heatmapCanvas = document.getElementById("overview-heatmap");
    window.dashboardCharts.createHeatmap(heatmapCanvas, heatmap);
  }

  async function loadRevenue() {
    const period = revenuePeriod.value;
    const data = await window.dashboardApi.fetchRevenue(
      period,
      revenueFrom.value,
      revenueTo.value
    );
    const revenueCtx = document.getElementById("revenue-chart");
    if (revenueChart) {
      revenueChart.destroy();
    }
    revenueChart = window.dashboardCharts.createRevenueChart(revenueCtx, data);
  }

  async function loadHours() {
    const data = await window.dashboardApi.fetchHours(
      "client",
      hoursFrom.value,
      hoursTo.value
    );
    const hoursCtx = document.getElementById("hours-chart");
    if (hoursChart) {
      hoursChart.destroy();
    }
    hoursChart = window.dashboardCharts.createHoursChart(hoursCtx, data);
  }

  function sortClients(data) {
    const sorted = data.slice();
    const key = clientSort.key;
    const direction = clientSort.direction === "asc" ? 1 : -1;
    sorted.sort((a, b) => {
      const left = a[key];
      const right = b[key];
      if (typeof left === "string") {
        return left.localeCompare(right) * direction;
      }
      return (left - right) * direction;
    });
    return sorted;
  }

  function renderClientsTable(data) {
    const tbody = document.querySelector("#clients-table tbody");
    tbody.innerHTML = "";
    data.forEach((client) => {
      const row = document.createElement("tr");
      row.innerHTML =
        "<td>" +
        client.name +
        "</td><td>" +
        formatCurrency(client.total_hours) +
        "</td><td>" +
        formatCurrency(client.total_revenue) +
        "</td><td>" +
        formatCurrency(client.avg_rate) +
        "</td><td>" +
        client.project_count +
        "</td>";
      tbody.appendChild(row);
    });
  }

  async function loadClients() {
    clientData = await window.dashboardApi.fetchClients();
    renderClientsTable(sortClients(clientData));
  }

  function statusClass(status, dueDate) {
    if (status === "paid") {
      return "paid";
    }
    if (status === "open") {
      if (dueDate && new Date(dueDate) < new Date()) {
        return "overdue";
      }
      return "open";
    }
    return "open";
  }

  async function loadInvoices() {
    const data = await window.dashboardApi.fetchInvoices(invoiceStatus.value);
    const tbody = document.querySelector("#invoices-table tbody");
    tbody.innerHTML = "";
    data.forEach((invoice) => {
      const badgeClass = statusClass(invoice.status, invoice.due_date);
      const row = document.createElement("tr");
      row.innerHTML =
        "<td>" +
        invoice.number +
        "</td><td>" +
        invoice.client +
        "</td><td>" +
        formatCurrency(invoice.amount) +
        "</td><td>" +
        invoice.due_date +
        "</td><td><span class=\"badge " +
        badgeClass +
        "\">" +
        invoice.status +
        "</span></td>";
      tbody.appendChild(row);
    });
  }

  async function init() {
    dateLabel.textContent = formatDate();
    setActivePage(getRoute());
    await loadOverview();
    await loadRevenue();
    await loadHours();
    await loadClients();
    await loadInvoices();
  }

  window.addEventListener("hashchange", () => setActivePage(getRoute()));

  navLinks.forEach((link) =>
    link.addEventListener("click", () => setActivePage(link.dataset.route))
  );

  document.querySelectorAll(".sort-button").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.sort;
      if (clientSort.key === key) {
        clientSort.direction = clientSort.direction === "asc" ? "desc" : "asc";
      } else {
        clientSort.key = key;
        clientSort.direction = "desc";
      }
      renderClientsTable(sortClients(clientData));
    });
  });

  revenuePeriod.addEventListener("change", loadRevenue);
  revenueFrom.addEventListener("change", loadRevenue);
  revenueTo.addEventListener("change", loadRevenue);
  hoursFrom.addEventListener("change", loadHours);
  hoursTo.addEventListener("change", loadHours);
  invoiceStatus.addEventListener("change", loadInvoices);

  init().catch((error) => {
    console.error(error);
  });
})();
