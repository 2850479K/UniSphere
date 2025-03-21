document.addEventListener("DOMContentLoaded", function () {
    // Copy to clipboard
    window.copyToClipboard = function (link) {
        navigator.clipboard.writeText(link).then(() => {
            alert("Link copied to clipboard!");
        });
    };

    // Like button AJAX handler
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

                // Update heart symbol
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

    // CSRF helper
    function getCSRFToken() {
        const cookie = document.cookie.split(";").find(cookie => cookie.trim().startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }
});
