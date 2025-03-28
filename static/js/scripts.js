document.addEventListener("DOMContentLoaded", function () {
    // Copy to clipboard function
    window.copyToClipboard = function (link) {
        navigator.clipboard.writeText(link).then(() => {
            alert("Link copied to clipboard!");
        });
    };

    // AJAX handler for like button
    document.querySelectorAll(".like-button").forEach((btn) => {
        btn.addEventListener("click", () => {
            const postId = btn.getAttribute("data-post-id");

            fetch(`/like-post/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                },
            })
            .then(response => response.json())
            .then(data => {
                const heartSpan = btn.querySelector(".heart");
                const countSpan = btn.querySelector(".like-count");

                // Update heart symbol and style
                if (data.liked) {
                    heartSpan.textContent = "❤";
                    heartSpan.classList.add("liked");
                } else {
                    heartSpan.textContent = "♡";
                    heartSpan.classList.remove("liked");
                }

                // Update like count
                countSpan.textContent = `(${data.likes_count})`;

                // Animate heart
                btn.classList.add("clicked");
                setTimeout(() => btn.classList.remove("clicked"), 300);
            });
        });
    });

    // CSRF helper function
    function getCSRFToken() {
        const cookie = document.cookie.split(";").find(cookie => cookie.trim().startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }

    // Toast notifications auto-show
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    var toastList = toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl, { delay: 3000 }); // Auto-dismiss after 3 seconds
    });
    toastList.forEach(toast => toast.show());

    // Tooltip initialization for elements with data-bs-toggle="tooltip"
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Friend request send handler
    document.querySelectorAll(".btn-send-request").forEach(button => {
        button.addEventListener("click", function() {
            const idAttr = button.getAttribute("data-student-id") || button.getAttribute("data-target-id");
            const csrftoken = getCSRFToken();
            fetch(`/friend-request/send/${idAttr}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ student_id: idAttr })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok. Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data.message);
                showToast(data.message, 'success');
                button.disabled = true;
                button.innerText = "Request Sent";
                button.classList.remove("btn-outline-success", "btn-outline-primary");
                button.classList.add("btn-secondary");
            })
            .catch(error => {
                console.error("Error:", error);
                showToast("An error occurred", "danger");
            });
        });
    });

    // Friend removal handler
    document.querySelectorAll(".remove-friend").forEach(button => {
        button.addEventListener("click", function() {
            const targetId = button.getAttribute("data-target-id");
            const csrftoken = getCSRFToken();
            fetch(`/remove_friend/${targetId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok. Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data.message);
                button.disabled = true;
                button.innerText = "Friend Removed";
                button.classList.remove("btn-danger");
                button.classList.add("btn-secondary");
            })
            .catch(error => {
                console.error("Error:", error);
            });
        });
    });
});

// Function to show toast notifications
function showToast(message, type = 'info') {
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0 mb-2"
             role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto"
                        data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    const container = document.querySelector('.toast-container');
    if (container) {
        container.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    } else {
        console.warn("Toast container not found.");
    }
}
