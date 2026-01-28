/**
 * Overlay JavaScript for webview
 */

(function () {
    // Initialize overlay functionality
    function initOverlays() {
        const overlays = document.querySelectorAll('.overlay');

        overlays.forEach(overlay => {
            overlay.addEventListener('click', function (e) {
                e.stopPropagation();
                this.classList.toggle('selected');
            });

            overlay.addEventListener('mouseenter', function () {
                showTooltip(this);
            });

            overlay.addEventListener('mouseleave', function () {
                hideTooltip();
            });
        });
    }

    function showTooltip(element) {
        const text = element.dataset.text;
        if (!text) return;

        let tooltip = document.getElementById('block-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'block-tooltip';
            tooltip.className = 'block-tooltip';
            document.body.appendChild(tooltip);
        }

        tooltip.textContent = text.substring(0, 200) + (text.length > 200 ? '...' : '');
        tooltip.style.display = 'block';

        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.bottom + 5) + 'px';
    }

    function hideTooltip() {
        const tooltip = document.getElementById('block-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOverlays);
    } else {
        initOverlays();
    }
})();
