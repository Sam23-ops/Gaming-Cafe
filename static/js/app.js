/**
 * Gammers Adda - Frontend Core Reactive Engine
 * Handles live countdown session timers, toast alerts, seat selection events.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide icons if loaded
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Auto-dismiss Django Messages after 5 seconds
  setTimeout(() => {
    document.querySelectorAll('.toast-alert').forEach(toast => {
      toast.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 500);
    });
  }, 5000);

  // Initialize Live Session Timers across Live Arena
  const timerElements = document.querySelectorAll('[data-timer-seconds]');
  timerElements.forEach(el => {
    let remaining = parseInt(el.getAttribute('data-timer-seconds'), 10);
    if (isNaN(remaining) || remaining <= 0) return;

    const interval = setInterval(() => {
      remaining--;
      if (remaining <= 0) {
        clearInterval(interval);
        el.textContent = 'SESSION ENDED';
        el.classList.remove('badge-green', 'badge-amber');
        el.classList.add('badge-red');
        return;
      }

      const hrs = Math.floor(remaining / 3600);
      const mins = Math.floor((remaining % 3600) / 60);
      const secs = remaining % 60;

      let formatted = '';
      if (hrs > 0) {
        formatted = `${hrs}h ${mins.toString().padStart(2, '0')}m`;
      } else {
        formatted = `${mins}m ${secs.toString().padStart(2, '0')}s`;
      }

      el.textContent = formatted;

      // Color shift when time is low
      if (remaining < 300) { // < 5 mins
        el.classList.remove('badge-green');
        el.classList.add('badge-red', 'timer-pulse');
      } else if (remaining < 900) { // < 15 mins
        el.classList.remove('badge-green');
        el.classList.add('badge-amber');
      }
    }, 1000);
  });
});

// Toast notification helper
window.showToast = function(message, type = 'info') {
  const container = document.getElementById('toast-container') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast-alert toast-${type}`;
  toast.innerHTML = `
    <div style="flex: 1; font-size: 0.9rem; font-weight: 500;">${message}</div>
    <button onclick="this.parentElement.remove()" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.2rem;">&times;</button>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
};

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.className = 'toast-container';
  document.body.appendChild(container);
  return container;
}
