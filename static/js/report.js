(function () {
    const chartDom = document.getElementById('chart');
    const chart = echarts.init(chartDom);
    const periodSelect = document.getElementById('period');
    const daysSelect = document.getElementById('days');
    const refreshBtn = document.getElementById('refresh');
    const detailTable = document.getElementById('detailTable');

    async function load() {
        try {
            const params = new URLSearchParams({
                period: periodSelect.value,
                days: daysSelect.value
            });
            const r = await fetch('/api/attendance/stats/?' + params);
            const res = await r.json();
            if (!res.ok || !Array.isArray(res.data)) return;
            const dates = res.data.map(d => d.date);
            const counts = res.data.map(d => d.count);
            chart.setOption({
                title: { text: '签到人次统计' },
                tooltip: { trigger: 'axis' },
                xAxis: { type: 'category', data: dates },
                yAxis: { type: 'value', name: '人次' },
                series: [{ type: 'bar', data: counts }]
            });
        } catch (e) {
            console.error('Chart load error:', e);
        }
        loadDetail();
    }

    async function loadDetail() {
        if (!detailTable) return;
        try {
            const days = daysSelect.value;
            const r = await fetch('/api/attendance/detail/?days=' + encodeURIComponent(days));
            const res = await r.json();
            if (!res.ok) {
                detailTable.innerHTML = '<tr><td colspan="4" class="text-center text-danger">加载失败</td></tr>';
                return;
            }
            const data = res.data;
            if (!data || data.length === 0) {
                detailTable.innerHTML = '<tr><td colspan="4" class="text-center text-muted">暂无考勤记录</td></tr>';
                return;
            }
            const escape = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
            detailTable.innerHTML = data.map(row =>
                `<tr><td>${escape(row.name)}</td><td>${escape(row.employee_id)}</td><td>${escape(row.check_in_time)}</td><td>${escape(row.source)}</td></tr>`
            ).join('');
        } catch (e) {
            console.error('Detail load error:', e);
            detailTable.innerHTML = '<tr><td colspan="4" class="text-center text-danger">加载失败</td></tr>';
        }
    }

    refreshBtn.onclick = load;
    periodSelect.onchange = load;
    daysSelect.onchange = load;
    load();
})();
