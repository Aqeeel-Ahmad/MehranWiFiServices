/**
 * Mehran WiFi Service - Interactive Fiber Optic Canvas Animation
 * Adapts seamlessly to Light Mode (default) and Dark Cyber Mode.
 */
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('fiber-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];
  let pulses = [];
  const maxDistance = 160;
  const particleCount = window.innerWidth < 768 ? 35 : 70;

  let mouse = {
    x: null,
    y: null,
    radius: 180
  };

  function resize() {
    width = canvas.width = canvas.offsetWidth;
    height = canvas.height = canvas.offsetHeight;
  }

  window.addEventListener('resize', resize);
  resize();

  window.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  });

  window.addEventListener('mouseout', () => {
    mouse.x = null;
    mouse.y = null;
  });

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.7;
      this.vy = (Math.random() - 0.5) * 0.7;
      this.radius = Math.random() * 2.2 + 1.2;
      this.color = Math.random() > 0.4 ? '#38BDF8' : (Math.random() > 0.5 ? '#818CF8' : '#00F2FE');
      this.pulseSpeed = Math.random() * 0.03 + 0.01;
      this.pulsePhase = Math.random() * Math.PI * 2;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;

      // Mouse gentle interaction
      if (mouse.x !== null && mouse.y !== null) {
        let dx = mouse.x - this.x;
        let dy = mouse.y - this.y;
        let dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          let force = (mouse.radius - dist) / mouse.radius;
          this.x -= (dx / dist) * force * 1.5;
          this.y -= (dy / dist) * force * 1.5;
        }
      }

      this.pulsePhase += this.pulseSpeed;
    }

    draw(isDark) {
      let dynamicRadius = this.radius + Math.sin(this.pulsePhase) * 0.6;
      ctx.beginPath();
      ctx.arc(this.x, this.y, Math.max(0.5, dynamicRadius), 0, Math.PI * 2);

      let particleColor = this.color;
      if (!isDark) {
        particleColor = this.color === '#00F2FE' ? '#0284C7' : (this.color === '#38BDF8' ? '#0EA5E9' : '#6366F1');
      }

      ctx.fillStyle = particleColor;
      if (isDark) {
        ctx.shadowBlur = 10;
        ctx.shadowColor = particleColor;
      }
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }

  // Initialize nodes
  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  function drawFiberConnections(isDark) {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        let dx = particles[i].x - particles[j].x;
        let dy = particles[i].y - particles[j].y;
        let dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDistance) {
          let alpha = (1 - dist / maxDistance) * (isDark ? 0.35 : 0.3);
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);

          // Optical fiber gradient line
          let gradient = ctx.createLinearGradient(
            particles[i].x, particles[i].y,
            particles[j].x, particles[j].y
          );

          if (isDark) {
            gradient.addColorStop(0, `rgba(56, 189, 248, ${alpha})`);
            gradient.addColorStop(0.5, `rgba(129, 140, 248, ${alpha * 1.2})`);
            gradient.addColorStop(1, `rgba(0, 242, 254, ${alpha})`);
          } else {
            gradient.addColorStop(0, `rgba(2, 132, 199, ${alpha})`);
            gradient.addColorStop(0.5, `rgba(99, 102, 241, ${alpha * 1.2})`);
            gradient.addColorStop(1, `rgba(14, 165, 233, ${alpha})`);
          }

          ctx.strokeStyle = gradient;
          ctx.lineWidth = dist < maxDistance * 0.5 ? 1.4 : 0.8;
          ctx.stroke();

          // Occasionally spawn light photon pulse traveling along fiber
          if (Math.random() < 0.001 && pulses.length < 15) {
            pulses.push({
              p1: particles[i],
              p2: particles[j],
              progress: 0,
              speed: 0.015 + Math.random() * 0.02,
              color: isDark ? '#00F2FE' : '#0284C7'
            });
          }
        }
      }
    }
  }

  function updateAndDrawPulses(isDark) {
    for (let i = pulses.length - 1; i >= 0; i--) {
      let p = pulses[i];
      p.progress += p.speed;

      if (p.progress >= 1) {
        pulses.splice(i, 1);
        continue;
      }

      let px = p.p1.x + (p.p2.x - p.p1.x) * p.progress;
      let py = p.p1.y + (p.p2.y - p.p1.y) * p.progress;

      ctx.beginPath();
      ctx.arc(px, py, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = isDark ? '#FFFFFF' : '#0284C7';
      if (isDark) {
        ctx.shadowBlur = 12;
        ctx.shadowColor = p.color;
      }
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

    particles.forEach(p => {
      p.update();
      p.draw(isDark);
    });

    drawFiberConnections(isDark);
    updateAndDrawPulses(isDark);

    requestAnimationFrame(animate);
  }

  animate();
});
