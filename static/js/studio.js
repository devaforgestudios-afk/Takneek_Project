async function fetchWithXHR(url, options = {}) {
    const defaultHeaders = {
        'X-Requested-With': 'XMLHttpRequest'
    };

    const mergedHeaders = { ...defaultHeaders, ...options.headers };

    return fetch(url, { ...options, headers: mergedHeaders });
}

let isLoggedIn = false;
let selectedFiles = [];

window.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, initializing...');
    
    try {
        const response = await fetchWithXHR('/api/check-auth');
        const data = await response.json();

        if (!data.logged_in) {
            isLoggedIn = false;
            disableStudioFeatures();
            openAuthModal();
        } else {
            isLoggedIn = true;
            enableStudioFeatures();
            loadMyArtworks();

            // Retrieve last active tab from localStorage
            const lastActiveTab = localStorage.getItem('activeStudioTab');
            if (lastActiveTab && document.querySelector(`.studio-tab[data-tab="${lastActiveTab}"]`)) {
                switchTab(lastActiveTab);
            } else {
                switchTab('upload'); // Default to upload if no stored tab or invalid
            }
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        isLoggedIn = false;
        disableStudioFeatures();
        openAuthModal();
    }

    // Setup tab event listeners AFTER DOM is loaded
    setupTabListeners();
});

// Setup tab listeners function
function setupTabListeners() {
    const tabs = document.querySelectorAll('.studio-tab[data-tab]');
    console.log('Found tabs:', tabs.length);
    
    tabs.forEach(tab => {
        const tabName = tab.getAttribute('data-tab');
        console.log('Setting up listener for tab:', tabName);
        
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Tab clicked:', tabName);
            switchTab(tabName);
        });
    });
}

// File handling
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');

if (uploadArea && fileInput) {
    uploadArea.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

document.getElementById('suggestPriceBtn')?.addEventListener('click', async () => {
    const title = document.getElementById('artworkTitle').value;
    const category = document.getElementById('category').value;
    const material = document.getElementById('materialUsed').value;
    const description = document.getElementById('description').value;

    if (!selectedFiles[0]) {
        alert('Please select an image first.');
        return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('category', category);
    formData.append('material', material);
    formData.append('description', description);
    formData.append('file', selectedFiles[0]);

    const suggestBtn = document.getElementById('suggestPriceBtn');
    suggestBtn.disabled = true;
    suggestBtn.innerHTML = 'Suggesting...';

    try {
        const response = await fetchWithXHR('/api/suggest-price', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('price').value = data.price.replace(/[^0-9.]/g, '');
        } else {
            alert('Failed to suggest price: ' + data.message);
        }
    } catch (error) {
        console.error('Error suggesting price:', error);
        alert('An error occurred while suggesting the price.');
    } finally {
        suggestBtn.disabled = false;
        suggestBtn.innerHTML = '<div class="tool-content"><span class="tool-name">Suggest Fair Price</span><span class="tool-desc">Market-based pricing</span></div><span class="tool-arrow">→</span>';
    }
});

async function generateDescription() {
    return new Promise(async (resolve, reject) => {
        const title = document.getElementById('artworkTitle').value;
        const category = document.getElementById('category').value;
        const material = document.getElementById('materialUsed').value;
        const existing_description = document.getElementById('description').value;

        if (!selectedFiles[0]) {
            alert('Please select an image first.');
            return reject('No image selected');
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('category', category);
        formData.append('material', material);
        formData.append('description', existing_description);
        formData.append('file', selectedFiles[0]);

        const generateBtn = document.getElementById('generateDescBtn');
        generateBtn.disabled = true;
        generateBtn.innerHTML = 'Generating...';

        try {
            const response = await fetchWithXHR('/api/generate-description', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('description').value = data.description;
                resolve();
            } else {
                alert('Failed to generate description: ' + data.message);
                reject(data.message);
            }
        } catch (error) {
            console.error('Error generating description:', error);
            alert('An error occurred while generating the description.');
            reject(error);
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 16px;">auto_awesome</span> Generate';
        }
    });
}

document.getElementById('suggestPriceBtnInline')?.addEventListener('click', async () => {
    const description = document.getElementById('description').value;

    if (!description) {
        try {
            await generateDescription();
        } catch (error) {
            return;
        }
    }

    const title = document.getElementById('artworkTitle').value;
    const category = document.getElementById('category').value;
    const material = document.getElementById('materialUsed').value;
    const updatedDescription = document.getElementById('description').value;

    if (!selectedFiles[0]) {
        alert('Please select an image first.');
        return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('category', category);
    formData.append('material', material);
    formData.append('description', updatedDescription);
    formData.append('file', selectedFiles[0]);

    const suggestBtn = document.getElementById('suggestPriceBtnInline');
    suggestBtn.disabled = true;
    suggestBtn.innerHTML = 'Suggesting...';

    try {
        const response = await fetchWithXHR('/api/suggest-price', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('price').value = data.price.replace(/[^0-9.]/g, '');
        } else {
            alert('Failed to suggest price: ' + data.message);
        }
    } catch (error) {
        console.error('Error suggesting price:', error);
        alert('An error occurred while suggesting the price.');
    } finally {
        suggestBtn.disabled = false;
        suggestBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 16px;">auto_awesome</span> Suggest Fair Price';
    }
});

document.getElementById('generateDescBtn')?.addEventListener('click', async () => {
    try {
        await generateDescription();
    } catch (error) {
        // Error already handled
    }
});

document.getElementById('generateDescBtnAi')?.addEventListener('click', async () => {
    const title = document.getElementById('artworkTitle').value;
    const category = document.getElementById('category').value;
    const material = document.getElementById('materialUsed').value;
    const existing_description = document.getElementById('description').value;

    if (!selectedFiles[0]) {
        alert('Please select an image first.');
        return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('category', category);
    formData.append('material', material);
    formData.append('description', existing_description);
    formData.append('file', selectedFiles[0]);

    const generateBtn = document.getElementById('generateDescBtnAi');
    generateBtn.disabled = true;
    generateBtn.innerHTML = 'Generating...';

    try {
        const response = await fetchWithXHR('/api/generate-description', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('description').value = data.description;
        } else {
            alert('Failed to generate description: ' + data.message);
        }
    } catch (error) {
        console.error('Error generating description:', error);
        alert('An error occurred while generating the description.');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<div class="tool-content"><span class="tool-name">Generate Description</span><span class="tool-desc">AI-powered writing</span></div><span class="tool-arrow">→</span>';
    }
});

function handleFiles(files) {
    selectedFiles = Array.from(files);
    filePreview.innerHTML = '';
    
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                fileItem.innerHTML = `
                    <img src="${e.target.result}" alt="Preview" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; margin-right: 10px;">
                    <span>${file.name}</span>
                    <button type="button" onclick="removeFile(${index})">&times;</button>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            fileItem.innerHTML = `
                <span class="material-symbols-outlined">description</span>
                <span>${file.name}</span>
                <button type="button" onclick="removeFile(${index})">&times;</button>
            `;
        }
        
        filePreview.appendChild(fileItem);
    });
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    const dt = new DataTransfer();
    selectedFiles.forEach(file => dt.items.add(file));
    fileInput.files = dt.files;
    handleFiles(selectedFiles);
}

async function handleArtworkSubmit(event) {
    event.preventDefault();
    
    const title = document.getElementById('artworkTitle').value;
    const category = document.getElementById('category').value;
    const material = document.getElementById('materialUsed').value;
    const description = document.getElementById('description').value;
    const price = document.getElementById('price').value;
    
    if (selectedFiles.length === 0) {
        alert('Please upload at least one file');
        return;
    }
    
    const formData = new FormData();
    formData.append('title', title);
    formData.append('category', category);
    formData.append('material', material);
    formData.append('description', description);
    formData.append('price', price);
    
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="material-symbols-outlined">hourglass_empty</span> Uploading...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetchWithXHR('/api/upload-artwork', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Artwork uploaded successfully!');
            
            document.getElementById('artworkForm').reset();
            filePreview.innerHTML = '';
            selectedFiles = [];
            
            switchTab('works');
            loadMyArtworks();
        } else {
            alert('Upload failed: ' + data.message);
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert('An error occurred while uploading');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

async function loadMyArtworks() {
    console.log('Loading my artworks...');
    try {
        const response = await fetchWithXHR('/api/my-artworks');
        const data = await response.json();
        
        if (data.success) {
            displayArtworks(data.artworks);
        }
    } catch (error) {
        console.error('Error loading artworks:', error);
    }
}

function displayArtworks(artworks) {
    const worksGrid = document.querySelector('.works-grid');
    
    if (!worksGrid) {
        console.error('Works grid not found!');
        return;
    }
    
    if (artworks.length === 0) {
        worksGrid.innerHTML = `
            <div class="empty-state">
                <span class="material-symbols-outlined empty-icon">inventory_2</span>
                <h3>No artworks yet</h3>
                <p>Start by uploading your first creation</p>
                <button class="btn-primary" onclick="switchTab('upload')">Upload Artwork</button>
            </div>
        `;
        return;
    }
    
    worksGrid.innerHTML = artworks.map(artwork => `
        <div class="artwork-card">
            <div class="artwork-image">
                <img src="/static/${artwork.files[0]}" alt="${artwork.title}">
                ${artwork.files.length > 1 ? `<span class="file-count">+${artwork.files.length - 1}</span>` : ''}
            </div>
            <div class="artwork-info">
                <h3 class="artwork-title">${artwork.title}</h3>
                <p class="artwork-category">${artwork.category}</p>
                <p class="artwork-material">${artwork.material}</p>
                <p class="artwork-description">${artwork.description.substring(0, 100)}...</p>
                ${artwork.price ? `<p class="artwork-price">₹${artwork.price}</p>` : '<p class="artwork-price">Price not set</p>'}
                <div class="artwork-stats">
                    <span><i class="fas fa-eye"></i> ${artwork.views || 0}</span>
                    <span><i class="fas fa-heart"></i> ${artwork.likes || 0}</span>
                </div>
                <div class="product-actions">
                    <button class="btn-buy" onclick="viewProduct('${artwork.id}')">
                        <span class="material-symbols-outlined">visibility</span>
                        View Artwork
                    </button>
                    <div class="secondary-actions">
                        <button class="btn-contact" onclick="openQrCodeModal('${artwork.id}')">
                            <span class="material-symbols-outlined">qr_code_2</span>
                            QR Code
                        </button>
                        <button class="btn-contact" onclick="deleteArtwork('${artwork.id}')">
                            <span class="material-symbols-outlined">delete</span>
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function openQrCodeModal(artworkId) {
    const qrCodeContainer = document.getElementById('qrCodeContainer');
    qrCodeContainer.innerHTML = '';
    const img = document.createElement('img');
    img.src = `/api/generate-qr/${artworkId}`;
    qrCodeContainer.appendChild(img);
    document.getElementById('qrCodeModal').style.display = 'flex';
}

function closeQrCodeModal() {
    document.getElementById('qrCodeModal').style.display = 'none';
}

function viewProduct(productId) {
    window.location.href = `/product/${productId}`;
}

async function deleteArtwork(artworkId) {
    if (!confirm('Are you sure you want to delete this artwork?')) {
        return;
    }
    
    try {
        const response = await fetchWithXHR(`/api/delete-artwork/${artworkId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Artwork deleted successfully');
            loadMyArtworks();
        } else {
            alert('Delete failed: ' + data.message);
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('An error occurred while deleting');
    }
}

// FIXED: Tab switching function
function switchTab(tabName) {
    console.log('Switching to tab:', tabName);
    
    // Save the active tab to localStorage
    localStorage.setItem('activeStudioTab', tabName);
    
    // Remove active from all tabs
    document.querySelectorAll('.studio-tab').forEach(t => {
        t.classList.remove('active');
    });
    
    // Remove active from all content
    document.querySelectorAll('.tab-content').forEach(c => {
        c.classList.remove('active');
    });

    // Add active to clicked tab
    const clickedTab = document.querySelector(`[data-tab="${tabName}"]`);
    if (clickedTab) {
        clickedTab.classList.add('active');
        console.log('Activated tab button:', tabName);
    } else {
        console.error('Tab button not found:', tabName);
    }

    // Add active to content
    const contentId = tabName + 'Tab';
    const content = document.getElementById(contentId);
    
    if (content) {
        content.classList.add('active');
        console.log('Activated tab content:', contentId);
    } else {
        console.error('Tab content not found:', contentId);
    }
    
    // Load data for specific tabs
    if (tabName === 'works') {
        loadMyArtworks();
    } else if (tabName === 'profile') {
        loadProfileData();
    }
}

// Make switchTab globally available
window.switchTab = switchTab;

function disableStudioFeatures() {
    const form = document.getElementById('artworkForm');
    const inputs = form.querySelectorAll('input, textarea, select, button');
    const uploadArea = document.getElementById('uploadArea');
    const logout = document.getElementById('logout-button');

    inputs.forEach(input => {
        input.disabled = true;
    });

    if (uploadArea) {
        uploadArea.style.opacity = '0.5';
        uploadArea.style.cursor = 'not-allowed';
        uploadArea.style.pointerEvents = 'none';
    }

    const formCard = document.querySelector('.form-card');
    const overlay = document.createElement('div');
    overlay.id = 'authOverlay';
    overlay.innerHTML = `
        <div class="auth-overlay-banner">
            <div class="auth-overlay-icon">
                <span class="material-symbols-outlined">lock</span>
            </div>
            <div class="auth-overlay-text">
                <h3>Authentication Required</h3>
                <p>Create an account or login to start uploading your artworks</p>
            </div>
            <button onclick="openAuthModal()" class="auth-overlay-btn">
                <span class="material-symbols-outlined">login</span>
                Get Started
            </button>
        </div>
    `;

    if (logout) logout.style.display = 'none';
    formCard.style.position = 'relative';
    formCard.insertBefore(overlay, formCard.firstChild);
}

function enableStudioFeatures() {
    const form = document.getElementById('artworkForm');
    const inputs = form.querySelectorAll('input, textarea, select, button');
    const uploadArea = document.getElementById('uploadArea');
    const overlay = document.getElementById('authOverlay');

    inputs.forEach(input => {
        input.disabled = false;
    });

    if (uploadArea) {
        uploadArea.style.opacity = '1';
        uploadArea.style.cursor = 'pointer';
        uploadArea.style.pointerEvents = 'auto';
    }

    if (overlay) {
        overlay.remove();
    }
}

function openAuthModal() {
    document.getElementById('authModal').style.display = 'flex';
}

function closeAuthModal() {
    document.getElementById('authModal').style.display = 'none';
}

function switchAuthTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));

    event.target.classList.add('active');
    document.getElementById(tab + 'Form').classList.add('active');
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetchWithXHR('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();

        if (data.success) {
            closeAuthModal();
            location.reload();
        } else {
            alert('Login failed: ' + data.message);
        }
    } catch (error) {
        console.error(error);
        alert('An error occurred.');
    }
}

async function handleSignup(event) {
    event.preventDefault();
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupConfirmPassword').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    try {
        const response = await fetchWithXHR('/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await response.json();

        if (data.success) {
            closeAuthModal();
            location.reload();
        } else {
            alert('Signup failed: ' + data.message);
        }
    } catch (error) {
        console.error(error);
        alert('An error occurred.');
    }
}

function generateProfileQr(artistName) {
    const qrContainer = document.getElementById('profileQrContainer');
    if (!qrContainer) return;
    
    qrContainer.innerHTML = '';

    const img = document.createElement('img');
    const artistUrl = `${window.location.origin}/artist/${encodeURIComponent(artistName)}`;
    
    img.src = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(artistUrl)}&bgcolor=F5F0E8&color=3E2723`;
    img.alt = 'Artist Profile QR Code';
    img.style.width = '250px';
    img.style.height = '250px';
    
    qrContainer.appendChild(img);
}

function downloadProfileQr() {
    const qrImg = document.querySelector('#profileQrContainer img');
    if (!qrImg) {
        alert('QR code not available');
        return;
    }

    const link = document.createElement('a');
    link.href = qrImg.src;
    link.download = 'artist-profile-qr.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function goToMarketplace() {
    const artistName = document.getElementById('profileName').textContent;
    if (artistName && artistName !== 'Loading...') {
        window.location.href = `/artist/${encodeURIComponent(artistName)}`;
    } else {
        alert('Profile not loaded yet');
    }
}

async function loadProfileData() {
    console.log('Loading profile data...');
    try {
        const authResponse = await fetchWithXHR('/api/check-auth');
        const authData = await authResponse.json();

        if (authData.logged_in && authData.user) {
            const user = authData.user;
            document.getElementById('profileName').textContent = user.name;
            document.getElementById('profileEmail').textContent = user.email;

            const artworksResponse = await fetchWithXHR('/api/my-artworks');
            const artworksData = await artworksResponse.json();

            if (artworksData.success) {
                const artworks = artworksData.artworks;
                const totalViews = artworks.reduce((sum, art) => sum + (art.views || 0), 0);
                const totalLikes = artworks.reduce((sum, art) => sum + (art.likes || 0), 0);

                document.getElementById('totalArtworks').textContent = artworks.length;
                document.getElementById('totalViews').textContent = totalViews;
                document.getElementById('totalLikes').textContent = totalLikes;
            }

            generateProfileQr(user.name);
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// Make functions globally available
window.handleArtworkSubmit = handleArtworkSubmit;
window.removeFile = removeFile;
window.openQrCodeModal = openQrCodeModal;
window.closeQrCodeModal = closeQrCodeModal;
window.viewProduct = viewProduct;
window.deleteArtwork = deleteArtwork;
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.switchAuthTab = switchAuthTab;
window.handleLogin = handleLogin;
window.handleSignup = handleSignup;
window.downloadProfileQr = downloadProfileQr;
window.goToMarketplace = goToMarketplace;