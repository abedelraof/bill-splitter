const CHART_COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
  '#3b82f6', '#ef4444', '#14b8a6', '#f97316', '#84cc16',
];

function summaryPage() {
  return {
    summary: null,
    loading: true,
    expanded: {},
    chartColors: CHART_COLORS,

    async init() {
      requireAuth();
      const params = new URLSearchParams(window.location.search);
      const billId = params.get('bill_id');
      if (!billId) { window.location.href = '/dashboard.html'; return; }
      try {
        this.summary = await API.get(`/bills/${billId}/summary`);
        this.summary.friends.forEach(f => { this.expanded[f.friend_id] = false; });
        this.loading = false;
        this.$nextTick(() => this.renderChart());
      } catch (e) {
        this.loading = false;
        showToast(e.message, true);
      }
    },

    renderChart() {
      if (!this.summary || this.summary.friends.length === 0) return;
      const ctx = document.getElementById('splitChart');
      if (!ctx) return;
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: this.summary.friends.map(f => f.name),
          datasets: [{
            data: this.summary.friends.map(f => f.total),
            backgroundColor: CHART_COLORS.slice(0, this.summary.friends.length),
            borderWidth: 2,
            borderColor: '#fff',
          }],
        },
        options: {
          cutout: '60%',
          plugins: {
            legend: { position: 'bottom', labels: { padding: 16, font: { size: 12 } } },
            tooltip: {
              callbacks: {
                label: ctx => ` ${ctx.label}: $${ctx.parsed.toFixed(2)}`,
              },
            },
          },
        },
      });
    },

    async shareResult() {
      if (!this.summary) return;
      const lines = [`Bill Summary — Total: $${this.summary.grand_total.toFixed(2)}`, ''];
      this.summary.friends.forEach(f => lines.push(`${f.name}: $${f.total.toFixed(2)}`));
      const text = lines.join('\n');
      if (navigator.share) {
        try { await navigator.share({ title: 'Bill Summary', text }); } catch (_) {}
      } else {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!');
      }
    },
  };
}
