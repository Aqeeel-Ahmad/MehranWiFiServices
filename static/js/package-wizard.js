/**
 * Mehran WiFi Service - SPA Package Wizard
 * Manages the sequential flow of MB Selection -> Summary Popup -> Payment.
 */
document.addEventListener('DOMContentLoaded', () => {
  const dateInput = document.getElementById('wizard-purchase-date');
  const mbDropdown = document.getElementById('mb-dropdown');
  const hiddenCustomSpeedInput = document.getElementById('hidden-custom-speed');

  // Containers
  const selectionContainer = document.getElementById('selection-container');
  const summaryContainer = document.getElementById('summary-container');
  const paymentContainer = document.getElementById('payment-container');

  // Summary Displays
  const displaySpeed = document.getElementById('summary-speed');
  const displayPrice = document.getElementById('summary-price');
  const displayExpiryDate = document.getElementById('summary-expiry-date');

  // Buttons
  const btnCancel = document.getElementById('btn-cancel');
  const btnProceed = document.getElementById('btn-proceed');

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  // Pricing formula for custom MBs: Rs. 400 base + (Rs. 80 * Speed)
  function calculatePrice(speedMb) {
    const speed = Math.max(2, Math.min(30, parseInt(speedMb || 10, 10)));
    return 400 + (speed * 80);
  }

  function calculateExpiryFromDateStr(dateStr) {
    if (!dateStr) return { iso: '', formatted: '' };
    const parts = dateStr.split('-');
    if (parts.length !== 3) return { iso: '', formatted: '' };

    let year = parseInt(parts[0], 10);
    let month = parseInt(parts[1], 10);

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

  function updateExpiryDate() {
    if (!dateInput || !displayExpiryDate) return;
    const expiry = calculateExpiryFromDateStr(dateInput.value);
    displayExpiryDate.textContent = expiry.formatted;
  }

  // When a user selects an MB speed
  if (mbDropdown) {
    mbDropdown.addEventListener('change', function() {
      const speed = this.value;
      if (!speed) return;

      // Update hidden input for backend submission
      if (hiddenCustomSpeedInput) {
        hiddenCustomSpeedInput.value = speed;
      }

      // Update Summary Values
      const price = calculatePrice(speed);
      if (displaySpeed) displaySpeed.textContent = speed + ' Mbps';
      if (displayPrice) displayPrice.textContent = 'Rs. ' + price.toLocaleString();
      updateExpiryDate();

      // UI Flow: Hide selection, Show Summary Popup
      selectionContainer.style.display = 'none';
      summaryContainer.style.display = 'block';
    });
  }

  // When a user clicks Cancel on the Summary
  if (btnCancel) {
    btnCancel.addEventListener('click', function() {
      // Reset dropdown
      if (mbDropdown) mbDropdown.value = '';
      if (hiddenCustomSpeedInput) hiddenCustomSpeedInput.value = '';
      
      // UI Flow: Hide summary, Show selection
      summaryContainer.style.display = 'none';
      paymentContainer.style.display = 'none';
      selectionContainer.style.display = 'block';
    });
  }

  // When a user clicks Proceed on the Summary
  if (btnProceed) {
    btnProceed.addEventListener('click', function() {
      // UI Flow: Hide summary, Show Payment
      summaryContainer.style.display = 'none';
      paymentContainer.style.display = 'block';
    });
  }

  if (dateInput) {
    dateInput.addEventListener('change', updateExpiryDate);
  }
});
