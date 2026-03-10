(function () {
    const video = document.getElementById('video');
    const ipStream = document.getElementById('ipStream');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const msg = document.getElementById('msg');
    const ipInput = document.getElementById('ipInput');
    const webcamUrlInput = document.getElementById('webcamUrl');
    const connectIpBtn = document.getElementById('connectIp');
    const resultCard = document.getElementById('resultCard');

    let localStream = null;
    let ipWebcamBase = '';
    let autoTimer = null;
    let processing = false;

    const LIVENESS_FRAMES = 3;
    const LIVENESS_INTERVAL = 250;
    const LIVENESS_THRESHOLD = 2.0;
    const AUTO_SCAN_INTERVAL = 2000;
    const AFTER_SUCCESS_PAUSE = 5000;

    function showMsg(text, type) {
        msg.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-info', 'alert-warning');
        msg.classList.add('alert-' + (type || 'info'));
        msg.textContent = text;
    }

    function hideMsg() { msg.classList.add('d-none'); }
    function hideResult() { resultCard.classList.add('d-none'); }

    function showResult(data) {
        const photo = document.getElementById('resultPhoto');
        const noPhoto = document.getElementById('resultNoPhoto');
        if (data.photo_url) {
            photo.src = data.photo_url;
            photo.style.display = 'block';
            noPhoto.style.display = 'none';
        } else {
            photo.style.display = 'none';
            noPhoto.style.cssText = 'width:80px;height:80px;display:inline-flex!important';
        }
        document.getElementById('resultName').textContent = data.name;
        document.getElementById('resultId').textContent = data.employee_id;
        document.getElementById('resultTime').textContent = data.check_in_time;
        const badge = document.getElementById('resultBadge');
        if (data.status === 'late') {
            badge.className = 'badge bg-warning text-dark';
            badge.textContent = '迟到';
        } else {
            badge.className = 'badge bg-success';
            badge.textContent = '正常';
        }
        resultCard.classList.remove('d-none');
    }

    // --- 视频源 ---

    document.querySelectorAll('input[name="source"]').forEach(radio => {
        radio.onchange = () => {
            const isIp = radio.value === 'ip';
            ipInput.style.display = isIp ? 'block' : 'none';
            video.style.display = isIp ? 'none' : 'block';
            ipStream.style.display = isIp ? 'block' : 'none';
            stopAutoScan();
            if (isIp) {
                stopLocalCamera();
                ipStream.src = '';
                ipWebcamBase = '';
            } else {
                ipStream.src = '';
                startLocalCamera();
            }
            hideMsg();
            hideResult();
        };
    });

    function stopLocalCamera() {
        if (localStream) { localStream.getTracks().forEach(t => t.stop()); localStream = null; }
        video.srcObject = null;
    }

    function startLocalCamera() {
        navigator.mediaDevices.getUserMedia({ video: true, audio: false })
            .then(stream => {
                localStream = stream;
                video.srcObject = stream;
                startAutoScan();
            })
            .catch(err => showMsg('无法访问摄像头: ' + err.message, 'danger'));
    }

    connectIpBtn.onclick = () => {
        let base = webcamUrlInput.value.trim().replace(/\/$/, '');
        if (!base) { showMsg('请输入 IP Webcam 地址', 'danger'); return; }
        ipWebcamBase = base;
        ipStream.src = base + '/video';
        ipStream.onerror = () => showMsg('无法连接 IP Webcam', 'danger');
        ipStream.onload = () => { showMsg('已连接', 'success'); startAutoScan(); };
    };

    // --- 活体检测 ---

    function captureLocalFrame() {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        return ctx.getImageData(0, 0, canvas.width, canvas.height);
    }

    async function captureIpFrame() {
        const r = await fetch('/checkin/frame/?url=' + encodeURIComponent(ipWebcamBase + '/shot.jpg'));
        if (!r.ok) throw new Error('获取快照失败');
        const blob = await r.blob();
        const bmp = await createImageBitmap(blob);
        ctx.drawImage(bmp, 0, 0, canvas.width, canvas.height);
        return ctx.getImageData(0, 0, canvas.width, canvas.height);
    }

    function calcFrameDiff(f1, f2) {
        const d1 = f1.data, d2 = f2.data;
        let sum = 0;
        for (let i = 0; i < d1.length; i += 4) {
            sum += Math.abs(d1[i] - d2[i]) + Math.abs(d1[i+1] - d2[i+1]) + Math.abs(d1[i+2] - d2[i+2]);
        }
        return sum / (d1.length / 4) / 3;
    }

    function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

    async function livenessCheck(isIp) {
        const frames = [];
        for (let i = 0; i < LIVENESS_FRAMES; i++) {
            frames.push(isIp ? await captureIpFrame() : captureLocalFrame());
            if (i < LIVENESS_FRAMES - 1) await sleep(LIVENESS_INTERVAL);
        }
        let maxDiff = 0;
        for (let i = 1; i < frames.length; i++) {
            maxDiff = Math.max(maxDiff, calcFrameDiff(frames[0], frames[i]));
        }
        return maxDiff >= LIVENESS_THRESHOLD;
    }

    // --- 自动签到 ---

    async function doCheckin() {
        if (processing) return;
        const isIp = document.querySelector('input[name="source"]:checked').value === 'ip';
        if (isIp && !ipWebcamBase) return;
        if (!isIp && !video.srcObject) return;

        processing = true;
        try {
            const alive = await livenessCheck(isIp);
            if (!alive) { processing = false; return; }
        } catch (_) { processing = false; return; }

        let dataUrl;
        if (isIp) {
            try {
                const r = await fetch('/checkin/frame/?url=' + encodeURIComponent(ipWebcamBase + '/shot.jpg'));
                if (!r.ok) throw new Error();
                const blob = await r.blob();
                dataUrl = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                });
            } catch (_) { processing = false; return; }
        } else {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        }

        try {
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
            const headers = { 'Content-Type': 'application/json' };
            if (csrf) headers['X-CSRFToken'] = csrf.value;
            const r = await fetch('/checkin/submit/', {
                method: 'POST', headers, credentials: 'same-origin',
                body: JSON.stringify({ image: dataUrl })
            });
            const data = await r.json();
            if (data.ok) {
                showMsg(data.msg, 'success');
                showResult(data);
                pauseAutoScan(AFTER_SUCCESS_PAUSE);
            } else if (data.name) {
                showMsg(data.msg, 'warning');
            }
        } catch (_) {}
        processing = false;
    }

    function startAutoScan() {
        stopAutoScan();
        scheduleNext(1000);
    }

    function stopAutoScan() {
        if (autoTimer) { clearTimeout(autoTimer); autoTimer = null; }
    }

    function pauseAutoScan(ms) {
        stopAutoScan();
        scheduleNext(ms);
    }

    function scheduleNext(delay) {
        autoTimer = setTimeout(async () => {
            await doCheckin();
            scheduleNext(AUTO_SCAN_INTERVAL);
        }, delay);
    }

    startLocalCamera();
})();
