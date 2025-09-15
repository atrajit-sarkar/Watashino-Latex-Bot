// Enhanced JavaScript for Watashino LaTeX Bot website

document.addEventListener('DOMContentLoaded', () => {
  // Smooth scroll for internal links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href') || '';
      if (href.startsWith('#')) {
        e.preventDefault();
        const el = document.querySelector(href);
        if (el) {
          el.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start',
            inline: 'nearest'
          });
        }
      }
    });
  });

  // Header scroll effect
  const header = document.querySelector('.site-header');
  let lastScrollY = window.scrollY;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    
    if (scrollY > 100) {
      header.style.background = 'rgba(10, 14, 26, 0.98)';
      header.style.backdropFilter = 'blur(25px)';
    } else {
      header.style.background = 'rgba(10, 14, 26, 0.95)';
      header.style.backdropFilter = 'blur(20px)';
    }
    
    lastScrollY = scrollY;
  });

  // Intersection Observer for animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Observe cards and sections for animation
  document.querySelectorAll('.card, .feature-card, .example-card, .setup-step').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(el);
  });

  // Code block copy functionality
  document.querySelectorAll('.code-block').forEach(block => {
    const code = block.querySelector('code');
    if (code) {
      // Create copy button
      const copyBtn = document.createElement('button');
      copyBtn.textContent = 'Copy';
      copyBtn.className = 'copy-btn';
      copyBtn.style.cssText = `
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(99, 102, 241, 0.8);
        color: white;
        border: none;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s ease;
      `;
      
      // Make code block relative for positioning
      block.style.position = 'relative';
      block.appendChild(copyBtn);
      
      // Show/hide copy button on hover
      block.addEventListener('mouseenter', () => {
        copyBtn.style.opacity = '1';
      });
      
      block.addEventListener('mouseleave', () => {
        copyBtn.style.opacity = '0';
      });
      
      // Copy functionality
      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(code.textContent);
          copyBtn.textContent = 'Copied!';
          copyBtn.style.background = 'rgba(34, 197, 94, 0.8)';
          
          setTimeout(() => {
            copyBtn.textContent = 'Copy';
            copyBtn.style.background = 'rgba(99, 102, 241, 0.8)';
          }, 2000);
        } catch (err) {
          console.warn('Copy failed:', err);
          copyBtn.textContent = 'Failed';
          setTimeout(() => {
            copyBtn.textContent = 'Copy';
          }, 2000);
        }
      });
    }
  });

  // Typing animation for hero (disabled to preserve HTML structure)
  const heroTitle = document.querySelector('.hero h1');
  if (heroTitle) {
    // Simple fade-in animation instead of typing to preserve HTML
    heroTitle.style.opacity = '0';
    heroTitle.style.transform = 'translateY(20px)';
    heroTitle.style.transition = 'opacity 0.8s ease-out, transform 0.8s ease-out';
    
    setTimeout(() => {
      heroTitle.style.opacity = '1';
      heroTitle.style.transform = 'translateY(0)';
    }, 500);
  }

  // Parallax effect for background
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const stars = document.querySelector('.stars');
    const twinkling = document.querySelector('.twinkling');
    
    if (stars) {
      stars.style.transform = `translateY(${scrolled * 0.2}px)`;
    }
    if (twinkling) {
      twinkling.style.transform = `translateY(${scrolled * 0.1}px)`;
    }
  });

  // FAQ accordion functionality
  document.querySelectorAll('details').forEach(details => {
    details.addEventListener('toggle', function() {
      if (this.open) {
        // Close other details
        document.querySelectorAll('details').forEach(other => {
          if (other !== this && other.open) {
            other.open = false;
          }
        });
      }
    });
  });

  // Add enhanced hover effects
  document.querySelectorAll('.btn, .card, .feature-card').forEach(el => {
    el.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-5px)';
    });
    
    el.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });

  // Dynamic gradient text color
  const gradientTexts = document.querySelectorAll('.gradient-text');
  gradientTexts.forEach(text => {
    let hue = 0;
    setInterval(() => {
      hue = (hue + 1) % 360;
      text.style.background = `linear-gradient(135deg, 
        hsl(${hue}, 70%, 60%), 
        hsl(${(hue + 60) % 360}, 70%, 70%), 
        hsl(${(hue + 120) % 360}, 70%, 65%)
      )`;
      text.style.webkitBackgroundClip = 'text';
      text.style.backgroundClip = 'text';
    }, 100);
  });

  // Mobile menu toggle (if needed)
  const createMobileMenu = () => {
    const nav = document.querySelector('nav');
    const header = document.querySelector('.header-content');
    
    if (window.innerWidth <= 768) {
      if (!document.querySelector('.mobile-menu-toggle')) {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'mobile-menu-toggle';
        toggleBtn.innerHTML = '☰';
        toggleBtn.style.cssText = `
          background: none;
          border: none;
          color: white;
          font-size: 1.5rem;
          cursor: pointer;
          display: block;
        `;
        
        header.insertBefore(toggleBtn, nav);
        
        toggleBtn.addEventListener('click', () => {
          nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
          nav.style.flexDirection = 'column';
          nav.style.position = 'absolute';
          nav.style.top = '100%';
          nav.style.left = '0';
          nav.style.right = '0';
          nav.style.background = 'rgba(10, 14, 26, 0.98)';
          nav.style.padding = '1rem';
          nav.style.zIndex = '1000';
        });
      }
    }
  };

  createMobileMenu();
  window.addEventListener('resize', createMobileMenu);

  // Performance optimization: debounce scroll events
  let scrollTimeout;
  const debouncedScroll = () => {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      // Scroll-based effects here
    }, 10);
  };

  window.addEventListener('scroll', debouncedScroll, { passive: true });

  console.log('🚀 Watashino LaTeX Bot website loaded successfully!');
});

// Service worker registration for potential PWA features
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // Uncomment when you have a service worker
    // navigator.serviceWorker.register('/sw.js')
    //   .then(registration => console.log('SW registered'))
    //   .catch(error => console.log('SW registration failed'));
  });
}