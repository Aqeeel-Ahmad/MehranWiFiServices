/**
 * HAM 3 NETWORK - Step-by-Step Package Wizard
 * Manages dynamic package selection, customizable bandwidth slider (2 to 30 Mbps),
 * date changing, and automatic calculation of expiry date to the 8th of the next month.
 */
document.addEventListener('DOMContentLoaded', () => {
  const dateInput = document.getElementById('wizard-purchase-date');
  const pkgCards = document.querySelectorAll('.selectable-pkg-card');
  const hiddenPkgInput = document.getElementById('selected-package-id');

  // Display Elements
  const displayPkgName = document.getElementById('summary-pkg-name');
  const displaySpeed = document.getElementById('summary-speed');
  const displayPrice = document.getElementById('summary-price');
  const displayStartDate = document.getElementById('summary-start-date');
  const displayExpiryDate = document.getElementById('summary-expiry-date');
  const easyPaisaPayAmount = document.getElementById('easypaisa-pay-amount');

  // Custom Slider Elements
  const customSliderContainer = document.getElementById('wizard-custom-slider-container');
  const customSpeedSlider = document.getElementById('wizard-custom-speed-slider');
  const customSliderSpeedVal = document.getElementById('wizard-slider-speed-val');
  const cardCustomSpeedBadge = document.getElementById('card-custom-speed-badge');
  const cardCustomPriceBadge = document.getElementById('card-custom-price-badge');
  const wizardPresetBtns = document.querySelectorAll('.wizard-preset-btn');

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  function calculateCustomPrice(speedMb) {
    const speed = Math.max(2, Math.min(30, parseInt(speedMb || 10, 10)));
    return 400 + (speed * 80);
  }

  function calculateExpiryFromDateStr(dateStr) {
    if (!dateStr) return { iso: '', formatted: '' };
    const parts = dateStr.split('-');
    if (parts.length !== 3) return { iso: '', formatted: '' };

    let year = parseInt(parts[0], 10);
    let month = parseInt(parts[1], 10); // 1 to 12

    let nextMonth = month + 1;
    let nextYear = year;
    if (nextMonth > 12) {
      nextMonth = 1;
      nextYear += 1;
    }

    const nextMonthStr = String(nextMonth).padStart(2, '0');
    const iso = `${nextYear}-${nextMonthStr}-08`;
    const formatted = `${monthNames[nextMonth - 1]} 08, ${nextYear}`;
    return { iso, formatted };
  }

  function formatReadableDate(dateStr) {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    if (parts.length !== 3) return dateStr;
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10);
    const day = parseInt(parts[2], 10);
    return `${monthNames[month - 1]} ${day < 10 ? '0' + day : day}, ${year}`;
  }

  function updateWizardCalculations() {
    const selectedDate = dateInput ? dateInput.value : '';
    const expiry = calculateExpiryFromDateStr(selectedDate);

    if (displayStartDate && selectedDate) {
      displayStartDate.textContent = formatReadableDate(selectedDate);
    }
    if (displayExpiryDate) {
      displayExpiryDate.textContent = expiry.formatted;
    }

    // Update active package card selection
    const selectedCard = document.querySelector('.selectable-pkg-card.selected');
    if (selectedCard) {
      const id = selectedCard.getAttribute('data-id');
      const isCustom = selectedCard.getAttribute('data-is-custom') === 'true';

      if (hiddenPkgInput) hiddenPkgInput.value = id;

      if (isCustom) {
        if (customSliderContainer) {
          customSliderContainer.style.display = 'block';
        }
        const speed = customSpeedSlider ? parseInt(customSpeedSlider.value, 10) : 10;
        const price = calculateCustomPrice(speed);

        if (customSliderSpeedVal) customSliderSpeedVal.textContent = speed;
        if (cardCustomSpeedBadge) cardCustomSpeedBadge.textContent = speed + 'M';
        if (cardCustomPriceBadge) cardCustomPriceBadge.textContent = 'Rs. ' + price.toLocaleString();

        if (displayPkgName) displayPkgName.textContent = 'Custom ' + speed + ' Mbps Fiber Plan';
        if (displaySpeed) displaySpeed.textContent = speed + ' Mbps';
        if (displayPrice) displayPrice.textContent = 'Rs. ' + price.toLocaleString();
        if (easyPaisaPayAmount) easyPaisaPayAmount.textContent = 'Rs. ' + price.toLocaleString();
      } else {
        if (customSliderContainer) {
          customSliderContainer.style.display = 'none';
        }
        const name = selectedCard.getAttribute('data-name');
        const speed = selectedCard.getAttribute('data-speed');
        const price = selectedCard.getAttribute('data-price');

        if (displayPkgName) displayPkgName.textContent = name;
        if (displaySpeed) displaySpeed.textContent = speed + ' Mbps';
        if (displayPrice) displayPrice.textContent = 'Rs. ' + Number(price).toLocaleString();
        if (easyPaisaPayAmount) easyPaisaPayAmount.textContent = 'Rs. ' + Number(price).toLocaleString();
      }
    }
  }

  // Range Slider live input
  if (customSpeedSlider) {
    customSpeedSlider.addEventListener('input', function() {
      const speed = Math.max(2, Math.min(30, parseInt(this.value, 10)));
      this.value = speed;

      // Highlight active preset button if match
      wizardPresetBtns.forEach(btn => {
        if (parseInt(btn.getAttribute('data-speed'), 10) === speed) {
          btn.classList.add('btn-cyan', 'text-dark');
          btn.classList.remove('btn-outline-secondary');
        } else {
          btn.classList.remove('btn-cyan', 'text-dark');
          btn.classList.add('btn-outline-secondary');
        }
      });

      updateWizardCalculations();
    });
  }

  // Preset Buttons
  wizardPresetBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const speed = parseInt(this.getAttribute('data-speed'), 10);
      if (customSpeedSlider) {
        customSpeedSlider.value = speed;
        customSpeedSlider.dispatchEvent(new Event('input'));
      }
    });
  });

  if (dateInput) {
    dateInput.addEventListener('change', updateWizardCalculations);
  }

  pkgCards.forEach(card => {
    card.addEventListener('click', function() {
      pkgCards.forEach(c => c.classList.remove('selected'));
      this.classList.add('selected');
      updateWizardCalculations();

      // Smooth micro-scroll to step 3/4 if on mobile
      if (window.innerWidth < 768) {
        const step3 = document.getElementById('wizard-step-3');
        if (step3) {
          step3.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });

  // Initial calculation on load
  updateWizardCalculations();
});
