document.addEventListener("DOMContentLoaded", () => {
    const lazyImages = document.querySelectorAll(".lazy-load");

    // Lazy load images
    lazyImages.forEach(img => {
        const spinnerContainer = img.previousElementSibling; // Get the loading container
        const src = img.getAttribute("data-src"); // Get actual image URL

        const image = new Image();
        image.src = src;
        image.onload = () => {
            img.src = src;  // Set image source
            img.style.display = "block"; // Show image
            spinnerContainer.style.display = "none"; // Hide spinner
        };
    });

    // Fade-in effect on scroll
    const fadeElements = document.querySelectorAll(".graph-fade-in");

    function handleScroll() {
        fadeElements.forEach(el => {
            let position = el.getBoundingClientRect().top;
            if (position < window.innerHeight - 100) {
                el.classList.add("visible");
            } else {
                el.classList.remove("visible"); // Removes class when scrolled back up
            }
        });
    }

    document.addEventListener("scroll", handleScroll);
    handleScroll(); // Run once on page load
});
