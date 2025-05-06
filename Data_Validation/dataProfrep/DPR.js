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

class QuantumNavigation {
    constructor() {
        this.init();
        this.addEventListeners();
        this.initSwipeGestures();
        this.initKeyboardNavigation();
    }

    init() {
        this.DOM = {
            hamburger: document.querySelector('.hamburger-btn'),
            sidebar: document.querySelector('.smart-sidebar'),
            overlay: document.querySelector('.smart-overlay')
        };
        this.isOpen = false;
    }

    toggleNavigation() {
        this.isOpen = !this.isOpen;
        this.DOM.hamburger.classList.toggle('is-active');
        this.DOM.sidebar.setAttribute('aria-hidden', !this.isOpen);
        this.DOM.overlay.style.visibility = this.isOpen ? 'visible' : 'hidden';
        this.DOM.overlay.style.opacity = this.isOpen ? 1 : 0;
        document.body.style.overflow = this.isOpen ? 'hidden' : '';
        
        if(this.isOpen) {
            this.trapFocus();
            this.addParallaxEffect();
        }
    }

    initSwipeGestures() {
        let touchStartX = 0;
        document.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        }, {passive: true});

        document.addEventListener('touchend', e => {
            const touchEndX = e.changedTouches[0].screenX;
            const deltaX = touchEndX - touchStartX;
            
            if(this.isOpen && deltaX < -60) {
                this.toggleNavigation();
            }
        }, {passive: true});
    }

    trapFocus() {
        const focusableElements = this.DOM.sidebar.querySelectorAll('a, button');
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        this.DOM.sidebar.addEventListener('keydown', (e) => {
            if(e.key === 'Tab') {
                if(e.shiftKey && document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                } else if(!e.shiftKey && document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        });
        firstElement.focus();
    }

    addParallaxEffect() {
        this.DOM.overlay.addEventListener('mousemove', (e) => {
            const { clientX: x, clientY: y } = e;
            this.DOM.overlay.style.setProperty('--x', `${x}px`);
            this.DOM.overlay.style.setProperty('--y', `${y}px`);
        });
    }

    initKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if(e.key === 'Escape' && this.isOpen) {
                this.toggleNavigation();
            }
        });
    }

    addEventListeners() {
        this.DOM.hamburger.addEventListener('click', () => this.toggleNavigation());
        this.DOM.overlay.addEventListener('click', () => this.toggleNavigation());
        
        document.querySelectorAll('.menu-link').forEach(link => {
            link.addEventListener('click', () => {
                if(window.innerWidth < 1024) this.toggleNavigation();
            });
        });
    }
}

new QuantumNavigation();

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section-content');
    sections.forEach(section => section.classList.remove('active'));

    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    const hamburger = document.querySelector('.hamburger-menu');
    hamburger.style.display = 'block';
}
