function openQrCodeModal(artworkId) {
    const qrCodeContainer = document.getElementById('qrCodeContainer');
    qrCodeContainer.innerHTML = ''; // Clear previous QR code
    const img = document.createElement('img');
    img.src = `/api/generate-qr/${artworkId}`;
    qrCodeContainer.appendChild(img);
    document.getElementById('qrCodeModal').style.display = 'flex';
}

function closeQrCodeModal() {
    document.getElementById('qrCodeModal').style.display = 'none';
}