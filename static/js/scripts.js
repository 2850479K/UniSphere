document.addEventListener("DOMContentLoaded", function() {
    console.log("JavaScript Loaded: Enhancements can be added here!");

    // Example: Smooth scrolling for all links (Future enhancement)
    document.querySelectorAll('a').forEach(anchor => {
        anchor.addEventListener('click', function(event) {
            if (this.getAttribute('href').startsWith('#')) {
                event.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
