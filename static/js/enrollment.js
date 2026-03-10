(function () {
    const form = document.querySelector('form');
    const nameInput = document.getElementById('name');
    const employeeIdInput = document.getElementById('employee_id');
    const photoFileInput = document.getElementById('photoFile');
    const uploadArea = document.getElementById('uploadArea');
    const cameraArea = document.getElementById('cameraArea');
    const video = document.getElementById('video');
    const ipStream = document.getElementById('ipStream');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('captureBtn');
    const ipInput = document.getElementById('ipInput');
    const webcamUrlInput = document.getElementById('webcamUrl');
    const connectIpBtn = document.getElementById('connectIp');
    const msg = document.getElementById('msg');
    const previewArea = document.getElementById('previewArea');
    const previewImg = document.getElementById('previewImg');
    const retakeBtn = document.getElementById('retakeBtn');

    let localStream = null;
    let ipWebcamBase = '';
    let capturedDataUrl = null;

    function showMsg(text, type) {
        msg.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-info');
        msg.classList.add('alert-' + (type || 'info'));
        msg.textContent = text;
    }

    // 照片来源切换
    document.querySelectorAll('input[name="photoSource"]').forEach(radio => {
        radio.onchange = () => {
            const isCamera = radio.value === 'camera';
            uploadArea.style.display = isCamera ? 'none' : 'block';
            cameraArea.style.display = isCamera ? 'block' : 'none';
            photoFileInput.required = !isCamera;
            capturedDataUrl = null;
            previewArea.style.display = 'none';
            if (isCamera) {
                startLocalCamera();
            } else {
                stopLocalCamera();
            }
            showMsg('', '');
        };
    });

    // 摄像头来源切换
    document.querySelectorAll('input[name="camSource"]').forEach(radio => {
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
            capturedDataUrl = null;
            previewArea.style.display = 'none';
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
        if (document.querySelector('input[name="photoSource"]:checked').value !== 'camera') return;
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
        ipStream.onerror = () => showMsg('无法连接 IP Webcam', 'danger');
        ipStream.onload = () => showMsg('已连接', 'success');
        capturedDataUrl = null;
    };

    captureBtn.onclick = async () => {
        const isIp = document.querySelector('input[name="camSource"]:checked').value === 'ip';
        if (isIp) {
            if (!ipWebcamBase) {
                showMsg('请先连接 IP Webcam', 'danger');
                return;
            }
            try {
                const r = await fetch('/checkin/frame/?url=' + encodeURIComponent(ipWebcamBase + '/shot.jpg'));
                if (!r.ok) throw new Error('获取快照失败');
                const blob = await r.blob();
                capturedDataUrl = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                });
                previewImg.src = capturedDataUrl;
                previewArea.style.display = 'block';
                showMsg('拍照成功，请点击提交录入', 'success');
            } catch (err) {
                showMsg('获取画面失败: ' + err.message, 'danger');
            }
        } else {
            if (!video.srcObject) {
                showMsg('请等待摄像头就绪', 'danger');
                return;
            }
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            capturedDataUrl = canvas.toDataURL('image/jpeg', 0.9);
            previewImg.src = capturedDataUrl;
            previewArea.style.display = 'block';
            showMsg('拍照成功，请点击提交录入', 'success');
        }
    };

    retakeBtn.onclick = () => {
        capturedDataUrl = null;
        previewArea.style.display = 'none';
        previewImg.src = '';
        showMsg('', '');
    };

    form.onsubmit = async (e) => {
        e.preventDefault();
        const name = nameInput.value.trim();
        const employeeId = employeeIdInput.value.trim();
        if (!name || !employeeId) {
            showMsg('请填写姓名和工号', 'danger');
            return;
        }

        const isCamera = document.querySelector('input[name="photoSource"]:checked').value === 'camera';
        showMsg('处理中...', 'info');
        msg.classList.remove('d-none');

        try {
            let r;
            if (isCamera) {
                if (!capturedDataUrl) {
                    showMsg('请先拍照', 'danger');
                    return;
                }
                const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
                const headers = { 'Content-Type': 'application/json' };
                if (csrf) headers['X-CSRFToken'] = csrf.value;
                r = await fetch('/enrollment/upload/', {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({ name, employee_id: employeeId, image: capturedDataUrl }),
                    credentials: 'same-origin'
                });
            } else {
                if (!photoFileInput.files.length) {
                    showMsg('请选择照片', 'danger');
                    return;
                }
                const fd = new FormData(form);
                r = await fetch('/enrollment/upload/', {
                    method: 'POST',
                    body: fd,
                    credentials: 'same-origin'
                });
            }
            const data = await r.json();
            msg.textContent = data.msg;
            msg.classList.remove('alert-info');
            msg.classList.add(data.ok ? 'alert-success' : 'alert-danger');
            if (data.ok) {
                nameInput.value = '';
                employeeIdInput.value = '';
                photoFileInput.value = '';
                capturedDataUrl = null;
                previewArea.style.display = 'none';
                previewImg.src = '';
            }
        } catch (err) {
            showMsg('请求失败: ' + err.message, 'danger');
        }
    };
})();
