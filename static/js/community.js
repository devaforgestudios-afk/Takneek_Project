document.addEventListener('DOMContentLoaded', function() {
    const createPostBtn = document.getElementById('createPostBtn');
    const modal = document.getElementById('postModal');
    const closeBtn = document.querySelector('.close-btn');
    const postForm = document.getElementById('postForm');
    const postFeed = document.getElementById('postFeed');

    // Show modal
    createPostBtn.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    // Hide modal
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    // Handle form submission
    postForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(postForm);
        
        try {
            const response = await fetch('/api/community/posts', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                modal.style.display = 'none';
                postForm.reset();
                fetchPosts();
            } else {
                alert('Failed to create post. Please try again.');
            }
        } catch (error) {
            console.error('Error creating post:', error);
            alert('An error occurred. Please try again.');
        }
    });

    // Fetch and display posts
    async function fetchPosts() {
        try {
            const response = await fetch('/api/community/posts');
            if (!response.ok) throw new Error('Failed to fetch posts');
            const posts = await response.json();
            displayPosts(posts);
        } catch (error) {
            console.error('Error fetching posts:', error);
            postFeed.innerHTML = '<p>Could not load posts. Please try again later.</p>';
        }
    }

    function displayPosts(posts) {
        postFeed.innerHTML = posts.map(post => `
            <div class="post-card">
                <div class="post-header">
                    <img src="/static/assets/hero-artisans.jpg" alt="Artist Avatar" class="artist-avatar">
                    <div class="artist-info">
                        <h4>${post.artist_name}</h4>
                        <p class="post-timestamp">${new Date(post.timestamp).toLocaleString()}</p>
                    </div>
                </div>
                <div class="post-content">
                    <p class="post-description">${post.description}</p>
                    ${post.image ? `<img src="${post.image}" alt="Post Image" class="post-image">` : ''}
                </div>
            </div>
        `).join('');

        document.querySelectorAll('.post-description').forEach(desc => {
            if (desc.scrollHeight > desc.clientHeight) {
                const readMoreBtn = document.createElement('button');
                readMoreBtn.textContent = 'Read more';
                readMoreBtn.classList.add('read-more-btn');
                desc.parentElement.appendChild(readMoreBtn);

                readMoreBtn.addEventListener('click', () => {
                    desc.classList.toggle('expanded');
                    if (desc.classList.contains('expanded')) {
                        readMoreBtn.textContent = 'Read less';
                    } else {
                        readMoreBtn.textContent = 'Read more';
                    }
                });
            }
        });
    }

    // Initial fetch
    fetchPosts();
});
