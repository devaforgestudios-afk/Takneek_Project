document.addEventListener('DOMContentLoaded', function() {
    const postModal = document.getElementById('postModal');
    const postModalCloseBtn = postModal.querySelector('.close-btn');
    const postForm = document.getElementById('postForm');

    let onPostSuccessCallback = null;

    // Function to open the post modal
    window.openPostModal = function(callback) {
        onPostSuccessCallback = callback;
        postModal.style.display = 'block';
    };

    // Function to close the post modal
    window.closePostModal = function() {
        postModal.style.display = 'none';
        postForm.reset(); // Reset form on close
    };

    // Close modal when clicking on the close button
    if (postModalCloseBtn) {
        postModalCloseBtn.addEventListener('click', window.closePostModal);
    }

    // Close modal when clicking outside of it
    window.addEventListener('click', (event) => {
        if (event.target == postModal) {
            window.closePostModal();
        }
    });

    // Handle form submission
    if (postForm) {
        postForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(postForm);
            
            try {
                const response = await fetch('/api/community/posts', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    window.closePostModal();
                    if (onPostSuccessCallback) {
                        onPostSuccessCallback();
                    }
                } else if (response.status === 401) {
                    window.location.href = '/studio?next=community';
                }
                else {
                    alert('Failed to create post. Please try again.');
                }
            } catch (error) {
                console.error('Error creating post:', error);
                alert('An error occurred. Please try again.');
            }
        });
    }
});