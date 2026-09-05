/**
 * Mehran WiFi Service - Main Frontend Logic
 */
document.addEventListener('DOMContentLoaded', () => {
  // 1. Navbar scroll effect
  const navbar = document.querySelector('.navbar-mehran');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  // 2. EasyPaisa Copy Number Helper
  window.copyEasyPaisaNumber = function(text, btnElement) {
    if (!text) text = '03454524086';
    navigator.clipboard.writeText(text).then(() => {
      const originalHtml = btnElement ? btnElement.innerHTML : null;
      if (btnElement) {
        btnElement.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i> Copied!';
        setTimeout(() => {
          btnElement.innerHTML = originalHtml;
        }, 2500);
      }
      showToast('Copied to clipboard: ' + text, 'success');
    }).catch(err => {
      // Fallback
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      showToast('Copied to clipboard: ' + text, 'success');
    });
  };

  // 3. Simple Toast Function
  window.showToast = function(message, type = 'info') {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
      toastContainer.style.zIndex = '9999';
      document.body.appendChild(toastContainer);
    }

    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success text-white' : (type === 'error' ? 'bg-danger text-white' : 'bg-dark text-white');
    const toastHtml = `
      <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 show shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body d-flex align-items-center gap-2">
            <i class="bi bi-info-circle-fill"></i> ${message}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    `;
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    setTimeout(() => {
      const el = document.getElementById(toastId);
      if (el) {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
      }
    }, 4000);
  };

  // 4. Send Receipt Email Ajax Handler
  window.sendReceiptEmail = function(paymentId, btn) {
    if (!paymentId) return;
    const origText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Sending...';

    fetch(`/payments/receipt/${paymentId}/send-email/`, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(r => r.json())
    .then(data => {
      btn.disabled = false;
      btn.innerHTML = origText;
      if (data.status === 'success') {
        showToast(data.message, 'success');
      } else {
        showToast(data.message || 'Failed to send email.', 'error');
      }
    })
    .catch(err => {
      btn.disabled = false;
      btn.innerHTML = origText;
      showToast('Network error while dispatching email.', 'error');
    });
  };

  // 5. Star Rating Selector Helper in Feedback Form
  const ratingStars = document.querySelectorAll('.rating-star-btn');
  const ratingInput = document.getElementById('feedback-rating-input');
  if (ratingStars.length && ratingInput) {
    ratingStars.forEach(star => {
      star.addEventListener('click', function() {
        const val = this.getAttribute('data-val');
        ratingInput.value = val;
        ratingStars.forEach(s => {
          if (parseInt(s.getAttribute('data-val')) <= parseInt(val)) {
            s.classList.add('text-warning');
            s.classList.remove('text-secondary');
          }
        });
      });
    });
  }

  // 6. Theme Mode Toggle (Default: Light Mode, Toggle: Dark Mode)
  const themeToggleBtn = document.getElementById('theme-toggle-btn');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('mehran_theme', theme);
    if (themeToggleBtn) {
      themeToggleBtn.setAttribute('title', theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
      themeToggleBtn.setAttribute('aria-label', theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
    }
  }

  // Initialize theme from storage or default to light
  const currentTheme = localStorage.getItem('mehran_theme') || 'light';
  applyTheme(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
      applyTheme(nextTheme);
      showToast(nextTheme === 'dark' ? '🌙 Dark Cyber Mode Activated' : '☀️ Light Mode Activated', 'info');
    });
  }

  // 7. Interactive Custom Bandwidth Sliders (2 Mbps to 30 Mbps)
  function calculateCustomPrice(speedMb) {
    const speed = Math.max(2, Math.min(30, parseInt(speedMb || 10, 10)));
    return 400 + (speed * 80);
  }

  function updateOrderUrlSpeed(btnEl, speed) {
    if (!btnEl) return;
    const currentHref = btnEl.getAttribute('href');
    if (!currentHref) return;
    try {
      const url = new URL(currentHref, window.location.origin);
      url.searchParams.set('custom_speed', speed);
      btnEl.setAttribute('href', url.pathname + url.search);
    } catch (e) {
      if (currentHref.includes('custom_speed=')) {
        btnEl.setAttribute('href', currentHref.replace(/custom_speed=\d+/, 'custom_speed=' + speed));
      } else {
        const sep = currentHref.includes('?') ? '&' : '?';
        btnEl.setAttribute('href', currentHref + sep + 'custom_speed=' + speed);
      }
    }
  }

  // Homepage Custom Slider
  const homeSlider = document.getElementById('home-custom-speed-slider');
  const homeSpeedVal = document.getElementById('home-custom-speed-val');
  const homePriceVal = document.getElementById('home-custom-price-val');
  const homeOrderBtn = document.getElementById('home-custom-order-btn');

  if (homeSlider) {
    homeSlider.addEventListener('input', function() {
      const speed = Math.max(2, Math.min(30, parseInt(this.value, 10)));
      const price = calculateCustomPrice(speed);
      if (homeSpeedVal) homeSpeedVal.textContent = speed;
      if (homePriceVal) homePriceVal.textContent = 'Rs. ' + price.toLocaleString();
      updateOrderUrlSpeed(homeOrderBtn, speed);
    });
  }

  // Package List Page Custom Slider
  const listSlider = document.getElementById('list-custom-speed-slider');
  const listSpeedVal = document.getElementById('list-custom-speed-val');
  const listSliderBadge = document.getElementById('list-custom-slider-badge');
  const listPriceVal = document.getElementById('list-custom-price-val');
  const listOrderBtn = document.getElementById('list-custom-order-btn');

  if (listSlider) {
    listSlider.addEventListener('input', function() {
      const speed = Math.max(2, Math.min(30, parseInt(this.value, 10)));
      const price = calculateCustomPrice(speed);
      if (listSpeedVal) listSpeedVal.textContent = speed;
      if (listSliderBadge) listSliderBadge.textContent = speed;
      if (listPriceVal) listPriceVal.textContent = 'Rs. ' + price.toLocaleString();
      updateOrderUrlSpeed(listOrderBtn, speed);
    });
  }

  // Global step helper for list page buttons
  window.stepListCustomSpeed = function(delta) {
    if (!listSlider) return;
    let current = parseInt(listSlider.value, 10) || 10;
    let nextVal = Math.max(2, Math.min(30, current + delta));
    listSlider.value = nextVal;
    listSlider.dispatchEvent(new Event('input'));
  };
});


