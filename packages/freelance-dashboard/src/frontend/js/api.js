(function () {
  "use strict";

  const API_BASE = "http://localhost:8765/api";

  async function getJson(path) {
    const response = await fetch(API_BASE + path);
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Request failed");
    }
    return response.json();
  }

  function fetchKPIs() {
    return getJson("/kpis");
  }

  function fetchRevenue(period, fromValue, toValue) {
    const params = new URLSearchParams();
    if (period) {
      params.append("period", period);
    }
    if (fromValue) {
      params.append("from", fromValue);
    }
    if (toValue) {
      params.append("to", toValue);
    }
    return getJson("/revenue?" + params.toString());
  }

  function fetchHours(groupBy, fromValue, toValue) {
    const params = new URLSearchParams();
    if (groupBy) {
      params.append("groupBy", groupBy);
    }
    if (fromValue) {
      params.append("from", fromValue);
    }
    if (toValue) {
      params.append("to", toValue);
    }
    return getJson("/hours?" + params.toString());
  }

  function fetchClients() {
    return getJson("/clients/summary");
  }

  function fetchHeatmap(year) {
    const params = new URLSearchParams();
    if (year) {
      params.append("year", year);
    }
    return getJson("/heatmap?" + params.toString());
  }

  function fetchInvoices(status) {
    const params = new URLSearchParams();
    if (status) {
      params.append("status", status);
    }
    return getJson("/invoices?" + params.toString());
  }

  window.dashboardApi = {
    fetchKPIs: fetchKPIs,
    fetchRevenue: fetchRevenue,
    fetchHours: fetchHours,
    fetchClients: fetchClients,
    fetchHeatmap: fetchHeatmap,
    fetchInvoices: fetchInvoices,
  };
})();
