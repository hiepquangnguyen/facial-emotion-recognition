// 🎥 Improved Camera Access Handler for Emotion Recognition
// Better error handling and user guidance

// Test camera directly
window.testCameraDirectly = async function() {
    try {
        showInfo('🧪 Đang test camera trực tiếp...');
        
        const testStream = await navigator.mediaDevices.getUserMedia({ video: true });
        testStream.getTracks().forEach(track => track.stop());
        
        showSuccess('✅ Camera hardware hoạt động bình thường! Vấn đề có thể là ở constraints hoặc permissions.');
        
    } catch (err) {
        showError(`❌ Camera hardware test failed: ${err.name} - ${err.message}`);
    }
};

// Show detailed instructions
window.showDetailedInstructions = function() {
    const instructions = `
        <div class="alert alert-info mt-3" style="text-align: left;">
            <h6><i class="fas fa-tools"></i> Hướng Dẫn Khắc Phục Chi Tiết:</h6>
            
            <div class="mt-3">
                <strong>🔧 Windows Camera Privacy:</strong>
                <ol>
                    <li>Bấm <kbd>Win + I</kbd> → Privacy & Security</li>
                    <li>Camera → Bật "Let apps access your camera"</li>
                    <li>Desktop apps → Bật cho browser</li>
                </ol>
            </div>
            
            <div class="mt-3">
                <strong>🌐 Chrome Settings:</strong>
                <ol>
                    <li>Vào <code>chrome://settings/content/camera</code></li>
                    <li>Thêm site này vào "Allow" list</li>
                    <li>Hoặc click 🔒 icon → Camera = Allow</li>
                </ol>
            </div>
            
            <div class="mt-3">
                <strong>⚡ Quick Fix:</strong>
                <ol>
                    <li>Đóng tất cả tabs/windows của browser</li>
                    <li>Restart browser hoàn toàn</li>
                    <li>Mở lại và cho phép camera access</li>
                </ol>
            </div>
            
            <div class="mt-3">
                <strong>📱 Alternative:</strong>
                <p>Thử mở trên điện thoại cùng WiFi: <code>${window.location.origin}</code></p>
            </div>
            
            <div class="mt-3">
                <button class="btn btn-sm btn-success" onclick="window.location.reload()">
                    🔄 Thử Lại
                </button>
                <button class="btn btn-sm btn-info" onclick="testCameraDirectly()">
                    🧪 Test Camera
                </button>
            </div>
        </div>
    `;
    
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.innerHTML = instructions;
    }
};

// Enhanced error handling for camera access
window.handleCameraError = function(err) {
    console.error('Camera error:', err);
    
    let errorMsg = '❌ Không thể truy cập camera. ';
    let solution = '';
    
    switch(err.name) {
        case 'NotAllowedError':
            errorMsg += 'Bạn đã từ chối quyền camera.';
            solution = `
                <div class="mt-3">
                    <strong>💡 Cách khắc phục:</strong>
                    <ol class="mt-2 text-start">
                        <li>Click vào biểu tượng <strong>🔒</strong> bên trái URL</li>
                        <li>Đổi Camera từ "Block" thành "Allow"</li>
                        <li>Refresh trang (F5) và thử lại</li>
                    </ol>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-info" onclick="window.open('chrome://settings/content/camera', '_blank')">
                            🔧 Chrome Camera Settings
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="showDetailedInstructions()">
                            📋 Hướng Dẫn Chi Tiết
                        </button>
                    </div>
                </div>
            `;
            break;
            
        case 'NotFoundError':
            errorMsg += 'Không tìm thấy camera.';
            solution = `
                <div class="mt-3">
                    <strong>💡 Kiểm tra:</strong>
                    <ul class="mt-2 text-start">
                        <li>Camera có được kết nối không?</li>
                        <li>Thử mở Camera app của Windows</li>
                        <li>Restart computer nếu cần</li>
                    </ul>
                    <button class="btn btn-sm btn-warning" onclick="showDetailedInstructions()">
                        📋 Hướng Dẫn Chi Tiết
                    </button>
                </div>
            `;
            break;
            
        case 'NotReadableError':
            errorMsg += 'Camera đang được dùng bởi app khác.';
            solution = `
                <div class="mt-3">
                    <strong>💡 Đóng các app sau:</strong>
                    <ul class="mt-2 text-start">
                        <li>Skype, Teams, Zoom, OBS Studio</li>
                        <li>Tabs browser khác đang dùng camera</li>
                        <li>Windows Camera app</li>
                    </ul>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-success" onclick="window.location.reload()">
                            🔄 Thử Lại
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="showDetailedInstructions()">
                            📋 Hướng Dẫn Chi Tiết
                        </button>
                    </div>
                </div>
            `;
            break;
            
        case 'OverconstrainedError':
            errorMsg += 'Camera không hỗ trợ settings yêu cầu.';
            solution = `
                <div class="mt-3">
                    <strong>💡 Đang thử với chất lượng thấp hơn...</strong>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-info" onclick="tryLowerQualityCamera()">
                            📹 Thử Camera Chất Lượng Thấp
                        </button>
                    </div>
                </div>
            `;
            break;
            
        case 'SecurityError':
            errorMsg += 'Lỗi bảo mật - cần HTTPS.';
            solution = `
                <div class="mt-3">
                    <strong>💡 Giải pháp:</strong>
                    <ul class="mt-2 text-start">
                        <li>Đảm bảo URL là <code>https://</code> hoặc <code>localhost</code></li>
                        <li>Nếu deploy online, cần HTTPS</li>
                    </ul>
                    <div class="alert alert-warning mt-2">
                        <small>Current URL: <code>${window.location.href}</code></small>
                    </div>
                </div>
            `;
            break;
            
        default:
            errorMsg += `Lỗi không xác định: ${err.message}`;
            solution = `
                <div class="mt-3">
                    <strong>💡 Thử các bước sau:</strong>
                    <ol class="mt-2 text-start">
                        <li>Thử browser khác (Chrome, Firefox, Edge)</li>
                        <li>Restart browser hoàn toàn</li>
                        <li>Kiểm tra Windows Camera Privacy Settings</li>
                        <li>Update browser lên phiên bản mới nhất</li>
                    </ol>
                    <div class="mt-3">
                        <button class="btn btn-sm btn-info" onclick="testCameraDirectly()">
                            🧪 Test Camera
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="showDetailedInstructions()">
                            📋 Hướng Dẫn Chi Tiết
                        </button>
                        <button class="btn btn-sm btn-success" onclick="window.location.reload()">
                            🔄 Thử Lại
                        </button>
                    </div>
                </div>
            `;
    }
    
    showError(errorMsg + solution);
};

// Try lower quality camera
window.tryLowerQualityCamera = async function() {
    try {
        showInfo('🔄 Đang thử với chất lượng camera thấp hơn...');
        
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 320 }, 
                height: { ideal: 240 }
            } 
        });
        
        const video = document.getElementById('video');
        video.srcObject = stream;
        video.style.display = 'block';
        
        const placeholder = document.getElementById('camera-placeholder');
        placeholder.style.display = 'none';
        
        showSuccess('✅ Camera kết nối thành công với chất lượng thấp!');
        
        // Continue with normal flow
        const startBtn = document.getElementById('startRealTime');
        const pauseBtn = document.getElementById('pauseRealTime');
        const stopBtn = document.getElementById('stopRealTime');
        
        startBtn.style.display = 'none';
        pauseBtn.style.display = 'inline-block';
        stopBtn.style.display = 'inline-block';
        
    } catch (err) {
        handleCameraError(err);
    }
};

// Show info message
function showInfo(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.innerHTML = `
            <div class="alert alert-info alert-custom mt-3">
                <i class="fas fa-info-circle"></i> ${message}
            </div>
        `;
    }
}

// Show success message
function showSuccess(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.innerHTML = `
            <div class="alert alert-success alert-custom mt-3">
                <i class="fas fa-check-circle"></i> ${message}
            </div>
        `;
        
        // Auto-hide success message after 3 seconds
        setTimeout(() => {
            const successAlert = errorDiv.querySelector('.alert-success');
            if (successAlert) {
                successAlert.style.opacity = '0';
                setTimeout(() => {
                    if (successAlert.parentNode) {
                        successAlert.remove();
                    }
                }, 500);
            }
        }, 3000);
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.innerHTML = `
            <div class="alert alert-danger alert-custom mt-3">
                <i class="fas fa-exclamation-triangle"></i> ${message}
            </div>
        `;
    }
}

// Auto-initialize camera fixes when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎥 Camera Fix Script Loaded');
    
    // Add improved click handler for start button
    const startBtn = document.getElementById('startRealTime');
    if (startBtn) {
        // Store original handler
        const originalHandler = startBtn.onclick;
        
        // Replace with improved handler
        startBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            try {
                // Check if getUserMedia is supported
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    showError('❌ Camera API không được hỗ trợ. Hãy sử dụng Chrome, Firefox hoặc Edge mới nhất.');
                    return;
                }

                showInfo('🔄 Đang yêu cầu quyền truy cập camera...');
                
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        width: { ideal: 640 }, 
                        height: { ideal: 480 },
                        facingMode: 'user'
                    } 
                });
                
                const video = document.getElementById('video');
                video.srcObject = stream;
                
                // Continue with normal flow
                video.style.display = 'block';
                document.getElementById('camera-placeholder').style.display = 'none';
                startBtn.style.display = 'none';
                document.getElementById('pauseRealTime').style.display = 'inline-block';
                document.getElementById('stopRealTime').style.display = 'inline-block';
                document.getElementById('realtime-results').style.display = 'block';
                
                // Show overlays
                document.getElementById('emotion-overlay').style.display = 'block';
                document.getElementById('confidence-overlay').style.display = 'block';
                document.getElementById('real-time-indicator').style.display = 'block';
                
                showSuccess('✅ Camera kết nối thành công! Bắt đầu phân tích cảm xúc...');
                
                // Call original handler if exists
                if (originalHandler) {
                    originalHandler.call(this, e);
                }
                
            } catch (err) {
                handleCameraError(err);
            }
        });
    }
    
    // Show initial help message
    setTimeout(() => {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv && !errorDiv.innerHTML.trim()) {
            errorDiv.innerHTML = `
                <div class="alert alert-info alert-custom mt-3">
                    <i class="fas fa-lightbulb"></i> 
                    <strong>💡 Mẹo:</strong> Nếu gặp lỗi camera, hãy đảm bảo đã cho phép truy cập camera cho browser này.
                    <button class="btn btn-sm btn-outline-info ms-2" onclick="showDetailedInstructions()">
                        📋 Xem Hướng Dẫn
                    </button>
                </div>
            `;
        }
    }, 2000);
});

console.log('🎥 Enhanced Camera Fix Script Loaded Successfully!'); 