(function () {
    const video = document.getElementById('video');
    const ipStream = document.getElementById('ipStream');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture');
    const msg = document.getElementById('msg');
    const ipInput = document.getElementById('ipInput');
    const webcamUrlInput = document.getElementById('webcamUrl');
    const connectIpBtn = document.getElementById('connectIp');

    let localStream = null;
    let ipWebcamBase = '';

    function showMsg(text, type) {
        msg.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-info');
        msg.classList.add('alert-' + (type || 'info'));
        msg.textContent = text;
    }

    function hideMsg() {
        msg.classList.add('d-none');
        msg.textContent = '';
    }

    // 切换来源
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
        };
    });

    function stopLocalCamera() {
        if (localStream) {
            localStream.getTracks().forEach(t => t.stop());
            localStream = null;
        }
        video.srcObject = null;
    }

    function startLocalCamera() {
        navigator.mediaDevices.getUserMedia({ video: true, audio: false })
            .then(stream => {
                localStream = stream;
                video.srcObject = stream;
            })
            .catch(err => {
                showMsg('无法访问摄像头: ' + err.message, 'danger');
            });
    }

    connectIpBtn.onclick = () => {
        let base = webcamUrlInput.value.trim().replace(/\/$/, '');
        if (!base) {
            showMsg('请输入 IP Webcam 地址', 'danger');
            return;
        }
        ipWebcamBase = base;
        ipStream.src = base + '/video';
        ipStream.onerror = () => {
            showMsg('无法连接 IP Webcam，请检查地址', 'danger');
        };
        ipStream.onload = () => {
            showMsg('已连接', 'success');
        };
    };

    captureBtn.onclick = async () => {
        const isIp = document.querySelector('input[name="source"]:checked').value === 'ip';
        let dataUrl;

        if (isIp) {
            if (!ipWebcamBase) {
                showMsg('请先连接 IP Webcam', 'danger');
                return;
            }
            showMsg('获取画面中...', 'info');
            try {
                const r = await fetch('/checkin/frame/?url=' + encodeURIComponent(ipWebcamBase + '/shot.jpg'));
                if (!r.ok) throw new Error('获取快照失败');
                const blob = await r.blob();
                const reader = new FileReader();
                dataUrl = await new Promise((resolve, reject) => {
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                });
            } catch (err) {
                showMsg('获取 IP Webcam 画面失败: ' + err.message, 'danger');
                return;
            }
        } else {
            if (!video.srcObject) {
                showMsg('请等待摄像头就绪', 'danger');
                return;
            }
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        }

        showMsg('识别中...', 'info');
        try {
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
            const headers = { 'Content-Type': 'application/json' };
            if (csrf) headers['X-CSRFToken'] = csrf.value;
            const r = await fetch('/checkin/submit/', {
                method: 'POST',
                headers,
                body: JSON.stringify({ image: dataUrl }),
                credentials: 'same-origin'
            });
            const data = await r.json();
            msg.textContent = data.msg + (data.name ? ` - ${data.name} (${data.employee_id})` : '');
            msg.classList.remove('d-none', 'alert-info');
            msg.classList.add(data.ok ? 'alert-success' : 'alert-danger');
        } catch (err) {
            showMsg('请求失败: ' + err.message, 'danger');
        }
    };

    // 默认启动本地摄像头
    startLocalCamera();
})();
