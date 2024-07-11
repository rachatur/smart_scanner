// script.js

function enter() {
    const item = document.getElementById('item').value;
    if (item.trim() === '') {
        alert('Please enter an item');
        return;
    }

    const fetchUrl = `/fetch_external_data?item_number=${encodeURIComponent(item)}`;
    window.location.href = fetchUrl;
}

function openCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            document.body.appendChild(video);

            video.style.position = 'fixed';
            video.style.top = '50%';
            video.style.left = '50%';
            video.style.transform = 'translate(-50%, -50%)';
            video.style.zIndex = '1000';
            video.style.border = '5px solid #007BFF';
            video.style.borderRadius = '10px';
            video.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.5)';

            const closeButton = document.createElement('button');
            closeButton.textContent = 'Close Camera';
            closeButton.style.position = 'fixed';
            closeButton.style.top = 'calc(50% + 200px)';
            closeButton.style.left = '50%';
            closeButton.style.transform = 'translateX(-50%)';
            closeButton.style.zIndex = '1001';
            closeButton.style.backgroundColor = '#007BFF';
            closeButton.style.color = 'white';
            closeButton.style.border = 'none';
            closeButton.style.padding = '10px 20px';
            closeButton.style.borderRadius = '5px';
            closeButton.style.cursor = 'pointer';

            closeButton.onclick = () => {
                video.pause();
                stream.getTracks().forEach(track => track.stop());
                document.body.removeChild(video);
                document.body.removeChild(closeButton);
            };

            document.body.appendChild(closeButton);
        })
        .catch(error => {
            console.error('Error accessing the camera:', error);
            alert('Error accessing the camera: ' + error.message);
        });
}
