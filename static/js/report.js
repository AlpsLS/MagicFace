(function () {
    const chartDom = document.getElementById('chart');
    const chart = echarts.init(chartDom);
    const periodSelect = document.getElementById('period');
    const daysSelect = document.getElementById('days');
    const refreshBtn = document.getElementById('refresh');
    const detailTable = document.getElementById('detailTable');
    const pagination = document.getElementById('pagination');
    const pageInfo = document.getElementById('pageInfo');

    const PAGE_SIZE = 10;
    let currentPage = 1;

    async function loadChart() {
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
    }

    async function loadDetail(page) {
        if (!detailTable) return;
        currentPage = page || 1;
        try {
            const params = new URLSearchParams({
                days: daysSelect.value,
                page: currentPage,
                page_size: PAGE_SIZE
            });
            const r = await fetch('/api/attendance/detail/?' + params);
            const res = await r.json();
            if (!res.ok) {
                detailTable.innerHTML = '<tr><td colspan="4" class="text-center text-danger">加载失败</td></tr>';
                renderPagination(0, 1, 1);
                return;
            }
            const data = res.data;
            if (!data || data.length === 0) {
                detailTable.innerHTML = '<tr><td colspan="4" class="text-center text-muted">暂无考勤记录</td></tr>';
                renderPagination(0, 1, 1);
                return;
            }
            const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
            detailTable.innerHTML = data.map(row =>
                `<tr><td>${esc(row.name)}</td><td>${esc(row.employee_id)}</td><td>${esc(row.check_in_time)}</td><td>${esc(row.source)}</td></tr>`
            ).join('');
            renderPagination(res.total, res.page, res.total_pages);
        } catch (e) {
            console.error('Detail load error:', e);
            detailTable.innerHTML = '<tr><td colspan="4" class="text-center text-danger">加载失败</td></tr>';
            renderPagination(0, 1, 1);
        }
    }

    function renderPagination(total, page, totalPages) {
        pageInfo.textContent = total > 0 ? `共 ${total} 条记录，第 ${page} / ${totalPages} 页` : '';
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let items = [];
        items.push(pgItem('«', page - 1, page <= 1));

        let start = Math.max(1, page - 2);
        let end = Math.min(totalPages, page + 2);
        if (start > 1) {
            items.push(pgItem('1', 1, false));
            if (start > 2) items.push(pgItem('…', 0, true));
        }
        for (let i = start; i <= end; i++) {
            items.push(pgItem(String(i), i, false, i === page));
        }
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
        const page = parseInt(link.dataset.page);
        if (page > 0) loadDetail(page);
    });

    function load() {
        loadChart();
        loadDetail(1);
    }

    refreshBtn.onclick = load;
    periodSelect.onchange = load;
    daysSelect.onchange = load;
    load();
})();
