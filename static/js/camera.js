(function () {
    const video = document.getElementById('video');
    const ipStream = document.getElementById('ipStream');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const captureBtn = document.getElementById('capture');
    const toggleAutoBtn = document.getElementById('toggleAuto');
    const msg = document.getElementById('msg');
    const ipInput = document.getElementById('ipInput');
    const webcamUrlInput = document.getElementById('webcamUrl');
    const connectIpBtn = document.getElementById('connectIp');
    const resultCard = document.getElementById('resultCard');
    const scanIndicator = document.getElementById('scanIndicator');
    const scanOverlay = document.getElementById('scanOverlay');

    let localStream = null;
    let ipWebcamBase = '';
    let autoMode = false;
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

    // --- 视频源切换 ---

    document.querySelectorAll('input[name="source"]').forEach(radio => {
        radio.onchange = () => {
            const isIp = radio.value === 'ip';
            ipInput.style.display = isIp ? 'block' : 'none';
            video.style.display = isIp ? 'none' : 'block';
            ipStream.style.display = isIp ? 'block' : 'none';
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
            if (autoMode) stopAutoScan();
        };
    });

    function stopLocalCamera() {
        if (localStream) { localStream.getTracks().forEach(t => t.stop()); localStream = null; }
        video.srcObject = null;
    }

    function startLocalCamera() {
        navigator.mediaDevices.getUserMedia({ video: true, audio: false })
            .then(stream => { localStream = stream; video.srcObject = stream; })
            .catch(err => showMsg('无法访问摄像头: ' + err.message, 'danger'));
    }

    connectIpBtn.onclick = () => {
        let base = webcamUrlInput.value.trim().replace(/\/$/, '');
        if (!base) { showMsg('请输入 IP Webcam 地址', 'danger'); return; }
        ipWebcamBase = base;
        ipStream.src = base + '/video';
        ipStream.onerror = () => showMsg('无法连接 IP Webcam', 'danger');
        ipStream.onload = () => showMsg('已连接', 'success');
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

    // --- 核心签到流程 ---

    async function doCheckin(silent) {
        if (processing) return;
        const isIp = document.querySelector('input[name="source"]:checked').value === 'ip';
        if (isIp && !ipWebcamBase) { if (!silent) showMsg('请先连接 IP Webcam', 'danger'); return; }
        if (!isIp && !video.srcObject) { if (!silent) showMsg('请等待摄像头就绪', 'danger'); return; }

        processing = true;
        captureBtn.disabled = true;

        try {
            const alive = await livenessCheck(isIp);
            if (!alive) {
                if (!silent) showMsg('活体检测未通过，请确认是本人面对摄像头', 'warning');
                processing = false;
                captureBtn.disabled = false;
                return;
            }
        } catch (err) {
            if (!silent) showMsg('检测失败: ' + err.message, 'danger');
            processing = false;
            captureBtn.disabled = false;
            return;
        }

        let dataUrl;
        if (isIp) {
            try {
                const r = await fetch('/checkin/frame/?url=' + encodeURIComponent(ipWebcamBase + '/shot.jpg'));
                if (!r.ok) throw new Error('获取快照失败');
                const blob = await r.blob();
                dataUrl = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                });
            } catch (err) {
                processing = false;
                captureBtn.disabled = false;
                return;
            }
        } else {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        }

        if (!silent) showMsg('识别中...', 'info');

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
                if (autoMode) {
                    pauseAutoScan(AFTER_SUCCESS_PAUSE);
                }
            } else if (!silent || data.name) {
                msg.textContent = data.msg + (data.name ? ` - ${data.name} (${data.employee_id})` : '');
                msg.classList.remove('d-none', 'alert-info', 'alert-success', 'alert-warning');
                msg.classList.add(data.name ? 'alert-warning' : 'alert-danger');
            }
        } catch (err) {
            if (!silent) showMsg('请求失败: ' + err.message, 'danger');
        }
        processing = false;
        captureBtn.disabled = false;
    }

    // --- 自动扫描控制 ---

    function startAutoScan() {
        autoMode = true;
        toggleAutoBtn.innerHTML = '<i class="bi bi-pause-circle me-1"></i>暂停自动识别';
        toggleAutoBtn.classList.remove('btn-success');
        toggleAutoBtn.classList.add('btn-warning');
        scanIndicator.classList.remove('d-none');
        scanOverlay.classList.remove('d-none');
        hideResult();
        hideMsg();
        scheduleNext(500);
    }

    function stopAutoScan() {
        autoMode = false;
        if (autoTimer) { clearTimeout(autoTimer); autoTimer = null; }
        toggleAutoBtn.innerHTML = '<i class="bi bi-play-circle me-1"></i>开启自动识别';
        toggleAutoBtn.classList.remove('btn-warning');
        toggleAutoBtn.classList.add('btn-success');
        scanIndicator.classList.add('d-none');
        scanOverlay.classList.add('d-none');
    }

    function pauseAutoScan(ms) {
        if (autoTimer) { clearTimeout(autoTimer); autoTimer = null; }
        scheduleNext(ms);
    }

    function scheduleNext(delay) {
        if (!autoMode) return;
        autoTimer = setTimeout(async () => {
            if (!autoMode) return;
            await doCheckin(true);
            if (autoMode) scheduleNext(AUTO_SCAN_INTERVAL);
        }, delay);
    }

    toggleAutoBtn.onclick = () => {
        if (autoMode) stopAutoScan();
        else startAutoScan();
    };

    captureBtn.onclick = () => doCheckin(false);

    startLocalCamera();
})();
