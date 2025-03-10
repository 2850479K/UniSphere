document.addEventListener("DOMContentLoaded", function() {
    let buttons = document.querySelectorAll("button");
    buttons.forEach(button => {
        button.addEventListener("mouseover", function() {
            this.style.transform = "scale(1.05)";
        });
        button.addEventListener("mouseleave", function() {
            this.style.transform = "scale(1)";
        });
    });
});
