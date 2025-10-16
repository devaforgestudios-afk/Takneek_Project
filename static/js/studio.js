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
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        isLoggedIn = false;
        disableStudioFeatures();
        openAuthModal();
    }
});

// File handling
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');

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

document.getElementById('suggestPriceBtn').addEventListener('click', async () => {
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

document.getElementById('suggestPriceBtnInline').addEventListener('click', async () => {
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

document.getElementById('generateDescBtn').addEventListener('click', async () => {
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
        } else {
            alert('Failed to generate description: ' + data.message);
        }
    } catch (error) {
        console.error('Error generating description:', error);
        alert('An error occurred while generating the description.');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 16px;">auto_awesome</span> Generate';
    }
});

document.getElementById('generateDescBtnAi').addEventListener('click', async () => {
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
        
        // Create preview for images
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

// Form submission
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
    
    // Create FormData
    const formData = new FormData();
    formData.append('title', title);
    formData.append('category', category);
    formData.append('material', material);
    formData.append('description', description);
    formData.append('price', price);
    
    // Append files
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });
    
    // Show loading state
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
            
            // Reset form
            document.getElementById('artworkForm').reset();
            filePreview.innerHTML = '';
            selectedFiles = [];
            
            // Switch to "My Works" tab
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

// Load user's artworks
async function loadMyArtworks() {
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
    qrCodeContainer.innerHTML = ''; // Clear previous QR code
    const img = document.createElement('img');
    img.src = `/api/generate-qr/${artworkId}`;
    qrCodeContainer.appendChild(img);
    document.getElementById('qrCodeModal').style.display = 'flex';
}

function closeQrCodeModal() {
    document.getElementById('qrCodeModal').style.display = 'none';
}

function viewProduct(productId) {
    // You can implement a modal or redirect to product detail page
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

// Tab switching
document.querySelectorAll('.studio-tab').forEach(tab => {
    tab.addEventListener('click', function () {
        const tabName = this.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    document.querySelectorAll('.studio-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    if (tabName === 'works') {
        loadMyArtworks();
    }
}

// Auth functions
function disableStudioFeatures() {
    const form = document.getElementById('artworkForm');
    const inputs = form.querySelectorAll('input, textarea, select, button');
    const uploadArea = document.getElementById('uploadArea');
    const logout  = document.getElementById('logout-button');


    inputs.forEach(input => {
        input.disabled = true;
    });

    uploadArea.style.opacity = '0.5';
    uploadArea.style.cursor = 'not-allowed';
    uploadArea.style.pointerEvents = 'none';

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

    logout.style.display = 'none';
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

    uploadArea.style.opacity = '1';
    uploadArea.style.cursor = 'pointer';
    uploadArea.style.pointerEvents = 'auto';

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