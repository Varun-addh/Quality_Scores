function filterColumnStats(selectedValue) {{
    const allContainers = document.querySelectorAll('.column-container');
    if (selectedValue === 'all') {{
        allContainers.forEach(container => container.style.display = 'block');
    }} else {{
        allContainers.forEach(container => {{
            container.style.display = container.getAttribute('data-column') === selectedValue ? 'block' : 'none';
        }});
    }}
}}
function showSection(sectionId) {{
    const sections = document.querySelectorAll('.section-content');
    sections.forEach(section => section.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
}}
function showRows(rowId) {{
    const allTables = document.querySelectorAll('.row-table');
    allTables.forEach(table => table.style.display = 'none');
    document.getElementById(rowId).style.display = 'block';
}}

document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar-menu');
    const navbarLinks = document.querySelectorAll('.nav-links a');
    // Corrected selector with proper quote escaping
    const detailedReportLink = document.querySelector("a[onclick=\"showSection('detailed-report')\"]");

    // Toggle sidebar with animation
    hamburger.addEventListener('click', function (e) {
        e.stopPropagation();
        sidebar.style.display = 'block';
        setTimeout(() => sidebar.classList.add('active'), 10);
        hamburger.style.display = 'none';
    });

    // Close menu when clicking outside the sidebar
    document.addEventListener('click', function (event) {
        if (!sidebar.contains(event.target) && sidebar.classList.contains('active')) {
            closeSidebar();
        }
    });

    // Smooth scroll and hide menu when sidebar link is clicked
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            document.querySelector(targetId).scrollIntoView({
                behavior: 'smooth'
            });
            closeSidebar();
        });
    });

    // Modified: Only hide hamburger for non-detailed-report links
    navbarLinks.forEach(link => {
        if (link !== detailedReportLink) {
            link.addEventListener('click', function () {
                hamburger.style.display = 'none';
            });
        }
    });

    // Handle transition end for cleaner UI
    sidebar.addEventListener('transitionend', function () {
        if (!this.classList.contains('active')) {
            this.style.display = 'none';
        }
    });

    function closeSidebar() {
        sidebar.classList.remove('active');
        setTimeout(() => sidebar.style.display = 'none', 300);
        hamburger.style.display = 'block';
    }
});

// Updated showSection function
function showSection(sectionId) {
    const sections = document.querySelectorAll('.section-content');
    sections.forEach(section => section.classList.remove('active'));

    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Always show hamburger when detailed report is clicked
    const hamburger = document.querySelector('.hamburger-menu');
    hamburger.style.display = 'block'; // Force show hamburger for detailed report
}
