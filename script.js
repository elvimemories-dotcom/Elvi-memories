(function () {
  'use strict';

  // ---- NAVBAR SCROLL ----

  const navbar = document.getElementById('navbar');

  window.addEventListener('scroll', function () {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }, { passive: true });


  // ---- MOBILE MENU ----

  const menuToggle = document.getElementById('menuToggle');
  const menuClose = document.getElementById('menuClose');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileLinks = mobileMenu.querySelectorAll('a');

  function openMenu() {
    mobileMenu.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeMenu() {
    mobileMenu.classList.remove('open');
    document.body.style.overflow = '';
  }

  menuToggle.addEventListener('click', openMenu);
  menuClose.addEventListener('click', closeMenu);

  mobileLinks.forEach(function (link) {
    link.addEventListener('click', closeMenu);
  });


  // ---- SCROLL REVEAL ----

  const revealEls = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');

  const revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px'
  });

  revealEls.forEach(function (el) {
    revealObserver.observe(el);
  });


  // ---- ABOUT PHOTO — cambia con scroll ----

  var aboutSection  = document.getElementById('sobre-mi');
  var aboutSlides   = document.querySelectorAll('.about__slide');
  var aboutDots     = document.querySelectorAll('.about__dot');
  var currentAbout  = 0;

  function setAboutPhoto(idx) {
    if (idx === currentAbout) return;
    currentAbout = idx;
    aboutSlides.forEach(function (s, i) { s.classList.toggle('active', i === idx); });
    aboutDots.forEach(function (d, i)   { d.classList.toggle('active', i === idx); });
  }

  if (aboutSection && aboutSlides.length > 1) {
    window.addEventListener('scroll', function () {
      var rect     = aboutSection.getBoundingClientRect();
      var progress = (-rect.top + window.innerHeight * 0.4) / aboutSection.offsetHeight;
      setAboutPhoto(progress > 0.45 ? 1 : 0);
    }, { passive: true });
  }


  // ---- TESTIMONIALS — grid layout, no slider needed ----


  // ---- BOOKING FORM ----

  var bookingSession = '';
  var bookingStyle   = '';
  var bookingDate    = null;

  var BOOKING_STYLES = {
    'Maternidad': ['Natural & Luminoso', 'Clásico & Elegante', 'Artístico & Soñador', 'Bohemio & Romántico'],
    'Familia':    ['Natural & Lifestyle', 'Clásico & Formal', 'Casual & Divertido', 'Exterior & Aventura'],
    'Cumpleaños': ['Glamour & Celebración', 'Natural & Fresco', 'Artístico & Dramático', 'Chic & Moderno'],
    'XV Años':    ['Clásico & Elegante', 'Romántico & Floral', 'Moderno & Urbano', 'Artístico & Conceptual'],
    'Parejas':    ['Romántico & Natural', 'Íntimo & Emotivo', 'Exterior & Aventura', 'Moderno & Editorial'],
    'Niños':      ['Natural & Juguetón', 'Temático & Creativo', 'Clásico & Tierno', 'Exterior & Alegre'],
    'Artísticas': ['Conceptual & Dramático', 'Minimalista & Moderno', 'Bohemio & Etéreo', 'Dark & Editorial'],
    'Revelación': ['Natural & Alegre', 'Temático & Creativo', 'Íntimo & Familiar', 'Especial & Emotivo']
  };

  document.querySelectorAll('.session-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.session-btn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      bookingSession = btn.getAttribute('data-session');
      bookingStyle   = '';
      renderStyleOptions(bookingSession);
    });
  });

  function renderStyleOptions(session) {
    var block  = document.getElementById('styleBlock');
    var grid   = document.getElementById('styleGrid');
    var styles = BOOKING_STYLES[session] || [];
    if (!block || !grid) return;

    grid.innerHTML = '';
    styles.forEach(function (s) {
      var pill = document.createElement('button');
      pill.type = 'button';
      pill.className = 'style-pill';
      pill.textContent = s;
      pill.addEventListener('click', function () {
        document.querySelectorAll('.style-pill').forEach(function (p) { p.classList.remove('active'); });
        pill.classList.add('active');
        bookingStyle = s;
      });
      grid.appendChild(pill);
    });

    block.classList.add('visible');
  }

  // Calendar
  var calYear  = new Date().getFullYear();
  var calMonth = new Date().getMonth();

  var CAL_MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

  function buildCalendar(year, month) {
    var label  = document.getElementById('calMonthLabel');
    var daysEl = document.getElementById('calDays');
    if (!label || !daysEl) return;

    label.textContent = CAL_MONTHS[month] + ' ' + year;
    daysEl.innerHTML  = '';

    var today = new Date();
    today.setHours(0, 0, 0, 0);

    var firstWeekday = new Date(year, month, 1).getDay();
    var daysInMonth  = new Date(year, month + 1, 0).getDate();
    var daysInPrev   = new Date(year, month, 0).getDate();

    for (var p = firstWeekday - 1; p >= 0; p--) {
      var el = document.createElement('button');
      el.type = 'button';
      el.className = 'cal-day cal-day--other';
      el.textContent = daysInPrev - p;
      el.disabled = true;
      daysEl.appendChild(el);
    }

    for (var d = 1; d <= daysInMonth; d++) {
      (function (day) {
        var date = new Date(year, month, day);
        var el   = document.createElement('button');
        el.type  = 'button';
        el.className = 'cal-day';
        el.textContent = day;

        if (date < today) {
          el.classList.add('cal-day--past');
          el.disabled = true;
        } else {
          if (date.getTime() === today.getTime()) el.classList.add('cal-day--today');
          if (bookingDate && date.getTime() === bookingDate.getTime()) el.classList.add('cal-day--selected');
          el.addEventListener('click', function () {
            bookingDate = date;
            buildCalendar(calYear, calMonth);
            updateCalPick();
          });
        }
        daysEl.appendChild(el);
      })(d);
    }

    var total = Math.ceil((firstWeekday + daysInMonth) / 7) * 7;
    for (var n = 1; firstWeekday + daysInMonth + (n - 1) < total; n++) {
      var el = document.createElement('button');
      el.type = 'button';
      el.className = 'cal-day cal-day--other';
      el.textContent = n;
      el.disabled = true;
      daysEl.appendChild(el);
    }
  }

  function updateCalPick() {
    var pickEl = document.getElementById('calPickDisplay');
    var textEl = document.getElementById('calPickText');
    if (!pickEl || !textEl) return;
    if (bookingDate) {
      var opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      textEl.textContent = bookingDate.toLocaleDateString('es-ES', opts);
      pickEl.classList.add('has-date');
    } else {
      textEl.textContent = 'Elige un día en el calendario';
      pickEl.classList.remove('has-date');
    }
  }

  var calPrevBtn = document.getElementById('calPrev');
  var calNextBtn = document.getElementById('calNext');

  if (calPrevBtn) {
    calPrevBtn.addEventListener('click', function () {
      calMonth--;
      if (calMonth < 0) { calMonth = 11; calYear--; }
      buildCalendar(calYear, calMonth);
    });
  }

  if (calNextBtn) {
    calNextBtn.addEventListener('click', function () {
      calMonth++;
      if (calMonth > 11) { calMonth = 0; calYear++; }
      buildCalendar(calYear, calMonth);
    });
  }

  buildCalendar(calYear, calMonth);

  // Time slots
  var bookingTime = '';

  document.querySelectorAll('.time-slot').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.time-slot').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      bookingTime = btn.getAttribute('data-time');
    });
  });

  // Build message helper
  function buildBookingMessage() {
    var nombre   = document.getElementById('bNombre').value.trim();
    var email    = document.getElementById('bEmail').value.trim();
    var telefono = document.getElementById('bTelefono').value.trim();
    var mensaje  = document.getElementById('bMensaje').value.trim();

    if (!nombre || !email) {
      alert('Por favor completa tu nombre y correo electrónico.');
      return null;
    }

    var text = 'Hola Luisa! Quiero reservar una sesión con Elvi Memories.\n\n';
    text += 'Nombre: ' + nombre + '\n';
    text += 'Email: ' + email + '\n';
    if (telefono)       text += 'Teléfono: ' + telefono + '\n';
    if (bookingSession) text += 'Tipo de sesión: ' + bookingSession + '\n';
    if (bookingStyle)   text += 'Estilo preferido: ' + bookingStyle + '\n';
    if (bookingDate) {
      var opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
      text += 'Fecha deseada: ' + bookingDate.toLocaleDateString('es-ES', opts) + '\n';
    }
    if (bookingTime) text += 'Horario preferido: ' + bookingTime + '\n';
    if (mensaje)     text += '\nMensaje adicional: ' + mensaje;

    return text;
  }

  function showBookingSuccess() {
    var wrap    = document.getElementById('bookingSubmitWrap');
    var success = document.getElementById('bookingSuccess');
    if (wrap)    wrap.style.display    = 'none';
    if (success) success.style.display = 'block';
  }

  var submitWa  = document.getElementById('submitWhatsapp');
  var submitSms = document.getElementById('submitSMS');

  if (submitWa) {
    submitWa.addEventListener('click', function () {
      var text = buildBookingMessage();
      if (!text) return;
      window.open('https://wa.me/14705539163?text=' + encodeURIComponent(text), '_blank');
      showBookingSuccess();
    });
  }

  if (submitSms) {
    submitSms.addEventListener('click', function () {
      var text = buildBookingMessage();
      if (!text) return;
      window.open('sms:+14705539163?body=' + encodeURIComponent(text), '_blank');
      showBookingSuccess();
    });
  }


  // ---- CONTACT FORM removed — booking form (#reserva) covers this ----


  // ---- SMOOTH SCROLL for anchor links ----

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      const offset = navbar.offsetHeight + 16;
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });


  // ================================================================
  //  DYNAMIC LAYER
  // ================================================================

  // ---- SERVICES CAROUSEL — infinite loop ----

  var svcCarousel = document.getElementById('svcCarousel');
  var svcPrev     = document.getElementById('svcPrev');
  var svcNext     = document.getElementById('svcNext');
  var svcDots     = document.querySelectorAll('.svc-dot');

  if (svcCarousel) {

    // Duplicate cards for seamless loop
    var origCards = Array.from(svcCarousel.querySelectorAll('.svc-card'));
    origCards.forEach(function (card) {
      var clone = card.cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      clone.querySelectorAll('img').forEach(function (img) {
        img.loading = 'eager';
      });
      svcCarousel.appendChild(clone);
    });

    var loopSpeed   = 0.7;   // px per frame
    var isPaused    = false;
    var isDragging  = false;
    var dragStartX  = 0;
    var scrollStart = 0;

    function cardStep() {
      var card = origCards[0];
      if (!card) return 300;
      return card.offsetWidth + (parseInt(getComputedStyle(svcCarousel).gap) || 24);
    }

    function loopWidth() {
      return origCards.length * cardStep();
    }

    function updateSvcDots() {
      var step = cardStep();
      var idx  = Math.round(svcCarousel.scrollLeft / step) % origCards.length;
      svcDots.forEach(function (d, i) {
        d.classList.toggle('active', i === idx);
      });
    }

    // RAF loop
    function tick() {
      if (!isPaused && !isDragging) {
        svcCarousel.scrollLeft += loopSpeed;
        if (svcCarousel.scrollLeft >= loopWidth()) {
          svcCarousel.scrollLeft -= loopWidth();
        }
      }
      updateSvcDots();
      requestAnimationFrame(tick);
    }

    // Pause on hover so user can read / interact
    svcCarousel.addEventListener('mouseenter', function () { isPaused = true; });
    svcCarousel.addEventListener('mouseleave', function () { isPaused = false; });

    // Drag-to-scroll
    svcCarousel.addEventListener('mousedown', function (e) {
      isDragging  = true;
      dragStartX  = e.clientX;
      scrollStart = svcCarousel.scrollLeft;
      svcCarousel.classList.add('is-dragging');
      e.preventDefault();
    });

    document.addEventListener('mousemove', function (e) {
      if (!isDragging) return;
      svcCarousel.scrollLeft = scrollStart - (e.clientX - dragStartX);
    });

    document.addEventListener('mouseup', function () {
      if (!isDragging) return;
      isDragging = false;
      svcCarousel.classList.remove('is-dragging');
    });

    // Prev / Next buttons
    if (svcPrev) {
      svcPrev.addEventListener('click', function () {
        var step = cardStep();
        if (svcCarousel.scrollLeft < step) {
          svcCarousel.scrollLeft += loopWidth();
        }
        svcCarousel.scrollLeft -= step;
      });
    }

    if (svcNext) {
      svcNext.addEventListener('click', function () {
        svcCarousel.scrollLeft += cardStep();
        if (svcCarousel.scrollLeft >= loopWidth()) {
          svcCarousel.scrollLeft -= loopWidth();
        }
      });
    }

    // Dot click
    svcDots.forEach(function (dot, i) {
      dot.addEventListener('click', function () {
        svcCarousel.scrollLeft = i * cardStep();
      });
    });

    requestAnimationFrame(tick);
  }


  // ---- SCROLL PROGRESS BAR ----

  var progressBar = document.getElementById('scrollProgress');

  function updateProgress() {
    var scrollTop = window.scrollY;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    progressBar.style.width = pct + '%';
  }

  window.addEventListener('scroll', updateProgress, { passive: true });


  // ---- PARALLAX (hero bg drift is CSS, no JS needed) ----


  // ---- HERO STATS COUNT-UP — eliminado (métricas reemplazadas por pillars) ----

  // ---- CUSTOM CURSOR — eliminado ----


  // ---- HERO PHOTO 3D TILT ----

  var heroFrame = document.querySelector('.hero__photo-frame');
  if (heroFrame && window.matchMedia('(pointer: fine)').matches) {
    heroFrame.addEventListener('mousemove', function (e) {
      var rect = heroFrame.getBoundingClientRect();
      var cx = rect.left + rect.width  / 2;
      var cy = rect.top  + rect.height / 2;
      var dx = (e.clientX - cx) / (rect.width  / 2);
      var dy = (e.clientY - cy) / (rect.height / 2);
      heroFrame.style.transform = 'rotateY(' + (dx * 10) + 'deg) rotateX(' + (-dy * 8) + 'deg) scale(1.02)';
    });
    heroFrame.addEventListener('mouseleave', function () {
      heroFrame.style.transform = 'rotateY(0deg) rotateX(0deg) scale(1)';
    });
  }


  // ---- MAGNETIC BUTTONS ----

  document.querySelectorAll('.btn--primary, .btn--outline').forEach(function (btn) {
    btn.addEventListener('mousemove', function (e) {
      var rect = btn.getBoundingClientRect();
      var x = e.clientX - rect.left - rect.width  / 2;
      var y = e.clientY - rect.top  - rect.height / 2;
      btn.style.transform = 'translate(' + (x * 0.18) + 'px, ' + (y * 0.18) + 'px)';
    });
    btn.addEventListener('mouseleave', function () {
      btn.style.transform = '';
    });
  });


  // ---- 3D TILT — Portfolio cards ----

  document.querySelectorAll('.masonry-card').forEach(function (card) {
    card.addEventListener('mousemove', function (e) {
      var rect = card.getBoundingClientRect();
      var x = (e.clientX - rect.left) / rect.width  - 0.5;
      var y = (e.clientY - rect.top)  / rect.height - 0.5;
      card.style.transform =
        'perspective(700px) rotateY(' + (x * 10) + 'deg) rotateX(' + (-y * 10) + 'deg) scale(1.03)';
    });
    card.addEventListener('mouseleave', function () {
      card.style.transform = '';
    });
  });


  // ---- 3D TILT — Package cards ----

  document.querySelectorAll('.package-card').forEach(function (card) {
    card.addEventListener('mousemove', function (e) {
      var rect = card.getBoundingClientRect();
      var x = (e.clientX - rect.left) / rect.width  - 0.5;
      var y = (e.clientY - rect.top)  / rect.height - 0.5;
      card.style.transform =
        'perspective(900px) rotateY(' + (x * 8) + 'deg) rotateX(' + (-y * 8) + 'deg) translateZ(8px)';
    });
    card.addEventListener('mouseleave', function () {
      card.style.transform = '';
    });
  });


  // ---- FLOATING PETALS — Canvas ----

  (function initPetals() {
    var canvas = document.getElementById('petals-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');

    var W = 0, H = 0;
    var petals = [];

    var COLORS = [
      'rgba(249,196,216,ALPHA)',
      'rgba(232,180,208,ALPHA)',
      'rgba(212,160,200,ALPHA)',
      'rgba(242,212,232,ALPHA)',
      'rgba(201,160,220,ALPHA)',
      'rgba(255,220,235,ALPHA)',
      'rgba(225,170,200,ALPHA)'
    ];

    var COUNT = Math.min(45, Math.floor(window.innerWidth / 28));

    function resize() {
      W = canvas.width  = window.innerWidth;
      H = canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resize, { passive: true });
    resize();

    function randomPetal(fromTop) {
      var size = 7 + Math.random() * 11;
      return {
        x:        Math.random() * W,
        y:        fromTop ? -size * 2 - Math.random() * H * 0.6 : Math.random() * H,
        size:     size,
        speedY:   0.35 + Math.random() * 0.55,
        speedX:   (Math.random() - 0.5) * 0.5,
        rotation: Math.random() * Math.PI * 2,
        rotSpeed: (Math.random() - 0.5) * 0.025,
        wobble:   Math.random() * Math.PI * 2,
        wobbleSpeed: 0.012 + Math.random() * 0.018,
        wobbleAmp:   18 + Math.random() * 28,
        color:    COLORS[Math.floor(Math.random() * COLORS.length)],
        alpha:    0.35 + Math.random() * 0.45,
        scaleX:   0.55 + Math.random() * 0.35
      };
    }

    for (var i = 0; i < COUNT; i++) {
      petals.push(randomPetal(false));
    }

    function drawPetal(p) {
      var colorStr = p.color.replace('ALPHA', p.alpha.toFixed(2));
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rotation);
      ctx.scale(p.scaleX, 1);
      ctx.beginPath();
      ctx.moveTo(0, -p.size);
      ctx.bezierCurveTo(
         p.size * 0.65, -p.size * 0.45,
         p.size * 0.82,  p.size * 0.35,
         0,              p.size
      );
      ctx.bezierCurveTo(
        -p.size * 0.82,  p.size * 0.35,
        -p.size * 0.65, -p.size * 0.45,
         0,             -p.size
      );
      ctx.fillStyle = colorStr;
      ctx.fill();
      ctx.restore();
    }

    function tick() {
      ctx.clearRect(0, 0, W, H);

      for (var j = 0; j < petals.length; j++) {
        var p = petals[j];
        p.wobble   += p.wobbleSpeed;
        p.rotation += p.rotSpeed;
        p.y += p.speedY;
        p.x += p.speedX + Math.sin(p.wobble) * 0.38;

        if (p.y > H + p.size * 3) {
          petals[j] = randomPetal(true);
        }

        drawPetal(p);
      }

      requestAnimationFrame(tick);
    }

    tick();

  })();


})();
