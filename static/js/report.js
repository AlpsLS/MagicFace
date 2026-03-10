(function () {
    const chartDom = document.getElementById('chart');
    const pieChartDom = document.getElementById('pieChart');
    const chart = echarts.init(chartDom);
    const pieChart = echarts.init(pieChartDom);
    const periodSelect = document.getElementById('period');
    const daysSelect = document.getElementById('days');
    const refreshBtn = document.getElementById('refresh');
    const exportBtn = document.getElementById('exportBtn');
    const detailTable = document.getElementById('detailTable');
    const pagination = document.getElementById('pagination');
    const pageInfo = document.getElementById('pageInfo');

    const PAGE_SIZE = 5;
    let currentPage = 1;

    async function loadChart() {
        try {
            const params = new URLSearchParams({ period: periodSelect.value, days: daysSelect.value });
            const r = await fetch('/api/attendance/stats/?' + params);
            const res = await r.json();
            if (!res.ok || !Array.isArray(res.data)) return;
            chart.setOption({
                title: { text: '签到人次统计', textStyle: { fontSize: 14 } },
                tooltip: { trigger: 'axis' },
                xAxis: { type: 'category', data: res.data.map(d => d.date) },
                yAxis: { type: 'value', name: '人次' },
                series: [{ type: 'bar', data: res.data.map(d => d.count), itemStyle: { borderRadius: [4, 4, 0, 0] } }]
            });
        } catch (e) {
            console.error('Chart load error:', e);
        }
    }

    async function loadSummary() {
        try {
            const r = await fetch('/api/attendance/summary/?days=' + daysSelect.value);
            const res = await r.json();
            if (!res.ok) return;
            document.getElementById('statTotal').textContent = res.total_persons;
            document.getElementById('statNormal').textContent = res.normal;
            document.getElementById('statLate').textContent = res.late;
            document.getElementById('statAbsent').textContent = res.absent_persons;

            pieChart.setOption({
                title: { text: '出勤构成', textStyle: { fontSize: 14 }, left: 'center' },
                tooltip: { trigger: 'item' },
                legend: { bottom: 0 },
                series: [{
                    type: 'pie', radius: ['40%', '65%'],
                    label: { formatter: '{b}: {c}' },
                    data: [
                        { value: res.normal, name: '正常', itemStyle: { color: '#198754' } },
                        { value: res.late, name: '迟到', itemStyle: { color: '#ffc107' } },
                        { value: res.absent_persons, name: '未签到', itemStyle: { color: '#dc3545' } },
                    ]
                }]
            });
        } catch (e) {
            console.error('Summary load error:', e);
        }
    }

    async function loadDetail(page) {
        if (!detailTable) return;
        currentPage = page || 1;
        try {
            const params = new URLSearchParams({ days: daysSelect.value, page: currentPage, page_size: PAGE_SIZE });
            const r = await fetch('/api/attendance/detail/?' + params);
            const res = await r.json();
            if (!res.ok) {
                detailTable.innerHTML = '<tr><td colspan="5" class="text-center text-danger">加载失败</td></tr>';
                renderPagination(0, 1, 1);
                return;
            }
            if (!res.data || res.data.length === 0) {
                detailTable.innerHTML = '<tr><td colspan="5" class="text-center text-muted">暂无考勤记录</td></tr>';
                renderPagination(0, 1, 1);
                return;
            }
            const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
            const statusBadge = s => s === 'late'
                ? '<span class="badge bg-warning text-dark">迟到</span>'
                : '<span class="badge bg-success">正常</span>';
            detailTable.innerHTML = res.data.map(row =>
                `<tr><td>${esc(row.name)}</td><td>${esc(row.employee_id)}</td><td>${esc(row.check_in_time)}</td><td>${statusBadge(row.status)}</td><td>${esc(row.source)}</td></tr>`
            ).join('');
            renderPagination(res.total, res.page, res.total_pages);
        } catch (e) {
            console.error('Detail load error:', e);
            detailTable.innerHTML = '<tr><td colspan="5" class="text-center text-danger">加载失败</td></tr>';
            renderPagination(0, 1, 1);
        }
    }

    function renderPagination(total, page, totalPages) {
        pageInfo.textContent = total > 0 ? `共 ${total} 条记录，第 ${page} / ${totalPages} 页` : '';
        if (totalPages <= 1) { pagination.innerHTML = ''; return; }
        let items = [];
        items.push(pgItem('«', page - 1, page <= 1));
        let start = Math.max(1, page - 2), end = Math.min(totalPages, page + 2);
        if (start > 1) {
            items.push(pgItem('1', 1, false));
            if (start > 2) items.push(pgItem('…', 0, true));
        }
        for (let i = start; i <= end; i++) items.push(pgItem(String(i), i, false, i === page));
        if (end < totalPages) {
            if (end < totalPages - 1) items.push(pgItem('…', 0, true));
            items.push(pgItem(String(totalPages), totalPages, false));
        }
        items.push(pgItem('»', page + 1, page >= totalPages));
        pagination.innerHTML = items.join('');
    }

    function pgItem(label, page, disabled, active) {
        if (disabled) return `<li class="page-item disabled"><span class="page-link">${label}</span></li>`;
        if (active) return `<li class="page-item active"><span class="page-link">${label}</span></li>`;
        return `<li class="page-item"><a class="page-link" href="#" data-page="${page}">${label}</a></li>`;
    }

    pagination.addEventListener('click', function (e) {
        e.preventDefault();
        const link = e.target.closest('[data-page]');
        if (!link) return;
        const p = parseInt(link.dataset.page);
        if (p > 0) loadDetail(p);
    });

    exportBtn.onclick = () => {
        window.location.href = '/api/attendance/export/?days=' + daysSelect.value;
    };

    function load() {
        loadChart();
        loadSummary();
        loadDetail(1);
    }

    refreshBtn.onclick = load;
    periodSelect.onchange = load;
    daysSelect.onchange = load;
    load();
})();
