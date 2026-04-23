// ═══════════════════════════════════════════════════════════
//  ODISHA COLLEGEHUB — MAIN APPLICATION JS
//  Dynamic BG Slider | 3D Cards | Search | Filters | AI | Auth
// ═══════════════════════════════════════════════════════════

// ─── HERO BACKGROUND IMAGES ─────────────────────────────────
const BG_IMAGES = [
  {
    url: 'https://www.tripvaani.com/wp-content/uploads/2020/05/Chariot-Wheel.jpg',
    caption: 'Konark Sun Temple, Odisha'
  },
  {
    url: 'https://img.jagranjosh.com/images/2022/April/1242022/46345839_10155955082252742_998657841386487808_n.jpg',
    caption: 'IIT Bhubaneswar'
  },
  {
    url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/NIT_Rourkela_-_Main_Building.jpg/1280px-NIT_Rourkela_-_Main_Building.jpg',
    caption: 'NIT Rourkela'
  },
  {
    url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/AIIMS_Bhubaneswar.jpg/1280px-AIIMS_Bhubaneswar.jpg',
    caption: 'AIIMS Bhubaneswar'
  },
  {
    url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/KIIT_University_Campus.jpg/1280px-KIIT_University_Campus.jpg',
    caption: 'KIIT University'
  },
  {
    url: 'https://www.mbarendezvous.com/images/top-stories-img/bannerimage_1601294849.jpg',
    caption: 'XIM University'
  }
];

// Fallback gradient backgrounds in case images fail
const BG_GRADIENTS = [
  'linear-gradient(135deg, #0A1628 0%, #1A3A6C 50%, #0F2040 100%)',
  'linear-gradient(135deg, #0F2040 0%, #1E5FCC 50%, #0A1628 100%)',
  'linear-gradient(135deg, #1A0A0A 0%, #4A1200 50%, #0A1628 100%)',
  'linear-gradient(135deg, #0A2818 0%, #145A32 50%, #0A1628 100%)',
  'linear-gradient(135deg, #1A0A28 0%, #3D1A68 50%, #0A1628 100%)',
  'linear-gradient(135deg, #0A1A28 0%, #0F4A6C 50%, #0A1628 100%)'
];

let currentBgIndex = 0;
let bgInterval = null;

// ─── BACKGROUND SLIDER ──────────────────────────────────────
function initBgSlider() {
  const slider = document.getElementById('bg-slider');
  if (!slider) return;

  // Create slides
  BG_IMAGES.forEach((bg, i) => {
    const slide = document.createElement('div');
    slide.className = 'bg-slide' + (i === 0 ? ' active' : '');
    slide.style.background = BG_GRADIENTS[i]; // fallback
    slide.style.backgroundSize = 'cover';
    slide.style.backgroundPosition = 'center';

    // Try to load image
    const img = new Image();
    img.onload = () => {
      slide.style.backgroundImage = `url(${bg.url})`;
      slide.style.background = 'none';
      slide.style.backgroundColor = '#0A1628';
    };
    img.onerror = () => {
      slide.style.background = BG_GRADIENTS[i];
    };
    img.src = bg.url;

    slider.appendChild(slide);
  });

  // Create dots
  const dotsEl = document.getElementById('bg-dots');
  if (dotsEl) {
    BG_IMAGES.forEach((_, i) => {
      const dot = document.createElement('div');
      dot.className = 'bg-dot' + (i === 0 ? ' active' : '');
      dot.onclick = () => goToBg(i);
      dotsEl.appendChild(dot);
    });
  }

  // Auto-advance
  bgInterval = setInterval(nextBg, 6000);
}

function nextBg() {
  goToBg((currentBgIndex + 1) % BG_IMAGES.length);
}

function goToBg(idx) {
  const slides = document.querySelectorAll('.bg-slide');
  const dots = document.querySelectorAll('.bg-dot');

  slides[currentBgIndex].classList.add('exit');
  slides[currentBgIndex].classList.remove('active');
  dots[currentBgIndex]?.classList.remove('active');

  setTimeout(() => {
    slides[currentBgIndex].classList.remove('exit');
  }, 1800);

  currentBgIndex = idx;
  slides[currentBgIndex].classList.add('active');
  dots[currentBgIndex]?.classList.add('active');
}

// ─── CANVAS PARTICLES ──────────────────────────────────────
function initCanvas() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const particles = [];
  const count = 60;

  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - .5) * .4,
      vy: (Math.random() - .5) * .4,
      size: Math.random() * 2.5 + .5,
      opacity: Math.random() * .35 + .1,
      hue: Math.random() > .6 ? 24 : 210
    });
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${p.hue}, 80%, 65%, ${p.opacity})`;
      ctx.fill();
    });

    // Connect nearby particles
    particles.forEach((a, i) => {
      particles.slice(i + 1).forEach(b => {
        const dist = Math.hypot(a.x - b.x, a.y - b.y);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(244,98,42,${.06 * (1 - dist / 120)})`;
          ctx.lineWidth = .6;
          ctx.stroke();
        }
      });
    });

    requestAnimationFrame(draw);
  }
  draw();

  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });
}

// ─── NAVIGATION ─────────────────────────────────────────────
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + id)?.classList.add('active');

  document.querySelectorAll('.nav-link').forEach(l => {
    l.classList.toggle('active', l.dataset.page === id);
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });
  closeMobileNav();

  // Reinitialize observers for new page
  setTimeout(observeCards, 100);
  if (id === 'colleges') renderCollegePage();
  if (id === 'exams') renderExamsPage();
  if (id === 'rankings') renderRankingsPage();
  if (id === 'scholarships') renderScholarshipsPage();
  if (id === 'news') renderNewsPage();

  // Show/hide bg dots (only on home)
  const dotsEl = document.getElementById('bg-dots');
  if (dotsEl) dotsEl.style.display = id === 'home' ? 'flex' : 'none';
}

function openMobileNav() { document.getElementById('mobileNav').classList.add('open'); }
function closeMobileNav() { document.getElementById('mobileNav').classList.remove('open'); }

// Scroll header effect
window.addEventListener('scroll', () => {
  document.getElementById('mainHeader').classList.toggle('scrolled', window.scrollY > 40);
});

// ─── SEARCH ─────────────────────────────────────────────────
const SUGGESTIONS = [
  { icon: '⚙️', text: 'Engineering colleges in Bhubaneswar', sub: '45+ colleges' },
  { icon: '🏥', text: 'Medical colleges with NEET', sub: 'MBBS, BDS' },
  { icon: '💼', text: 'Top MBA colleges in Odisha', sub: 'XIM, KIIT, SOA' },
  { icon: '🏛️', text: 'Government colleges under ₹1 Lakh fees', sub: '30+ colleges' },
  { icon: '⭐', text: 'Highest placement colleges', sub: 'NIRF ranked' },
];

function handleSearchInput(val) {
  const box = document.getElementById('aiSuggestions');
  if (!val.trim() || val.length < 2) { box.classList.remove('open'); return; }
  const filtered = SUGGESTIONS.filter(s => s.text.toLowerCase().includes(val.toLowerCase()));
  if (!filtered.length) { box.classList.remove('open'); return; }
  box.innerHTML = '<div class="ai-sugg-header">Suggestions</div>' +
    filtered.map(s => `
      <div class="ai-sugg-item" onclick="quickSearch('${s.text}')">
        <span class="ai-sugg-icon">${s.icon}</span>
        <div><div class="ai-sugg-text">${s.text}</div><div class="ai-sugg-sub">${s.sub}</div></div>
      </div>
    `).join('');
  box.classList.add('open');
}
function showSuggestions() { document.getElementById('aiSuggestions').classList.add('open'); }
function hideSuggestions() { setTimeout(() => document.getElementById('aiSuggestions').classList.remove('open'), 150); }
function doSearch() {
  const q = document.getElementById('heroSearch').value.trim();
  quickSearch(q || 'All');
}
function quickSearch(query) {
  showPage('colleges');
  setTimeout(() => {
    document.getElementById('heroSearch').value = query;
    filterColleges(query);
  }, 200);
}
function filterColleges(stream) {
  showPage('colleges');
  setTimeout(() => {
    activeStream = stream;
    renderCollegePage();
    highlightFilterBtn(stream);
  }, 150);
}

// ─── HOME RENDERS ────────────────────────────────────────────
function renderHomeColleges(filter = 'All') {
  const grid = document.getElementById('homeCollegeGrid');
  if (!grid) return;
  const list = filter === 'All' ? COLLEGES.slice(0, 6) :
    COLLEGES.filter(c => c.type === filter || c.stream === filter).slice(0, 6);
  grid.innerHTML = list.map(c => collegeCardHTML(c)).join('');
}

function filterHomeColleges(btn, filter) {
  document.querySelectorAll('#homeCollegeFilter .fbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderHomeColleges(filter);
  setTimeout(observeCards, 50);
}

function renderHomeExams() {
  const grid = document.getElementById('homeExamGrid');
  if (!grid) return;
  grid.innerHTML = EXAMS.slice(0, 4).map(e => examCardHTML(e)).join('');
}

function renderHomeNews() {
  const grid = document.getElementById('homeNewsGrid');
  if (!grid) return;
  grid.innerHTML = NEWS_DATA.slice(0, 3).map(n => newsSmallCardHTML(n)).join('');
}

function renderTestimonials() {
  const grid = document.getElementById('testimonialsGrid');
  if (!grid) return;
  grid.innerHTML = TESTIMONIALS.map(t => `
    <div class="testimonial-card">
      <div class="tc-avatar">${t.avatar}</div>
      <div class="tc-name">${t.name}</div>
      <div class="tc-college">${t.college}</div>
      <div class="tc-stream">${t.stream} • ${t.year}</div>
      <div class="tc-text">${t.text}</div>
      <div class="tc-stars">${'★'.repeat(t.rating)}${'☆'.repeat(5 - t.rating)}</div>
    </div>
  `).join('');
}

// ─── COLLEGE CARDS HTML ─────────────────────────────────────
function collegeCardHTML(c) {
  const tags = c.tags.slice(0, 3).map((t, i) =>
    `<span class="ctag ${i === 1 ? 'blue' : i === 2 ? 'green' : ''}">${t}</span>`
  ).join('');

  const logoHTML = c.logo
    ? `<img src="${c.logo}" alt="${c.name}" onerror="this.style.display='none';this.parentNode.innerHTML='<span style=color:${c.color}>${c.short}</span>'">`
    : `<span style="color:${c.color}">${c.short}</span>`;

  return `
    <div class="college-card" onclick="openCollegeDetail(${c.id})">
      <div class="cc-header">
        <div class="cc-bg" style="background-image:url('${c.image}');background-color:${c.color}20"
          onerror="this.style.backgroundImage='none';this.style.background='linear-gradient(135deg,${c.color}40,${c.color}20)'"></div>
        <div class="cc-overlay"></div>
        <div class="cc-logo">${logoHTML}</div>
        ${c.badge ? `<div class="cc-badge">${c.badge}</div>` : ''}
      </div>
      <div class="cc-body">
        <div class="cc-name">${c.name}</div>
        <div class="cc-loc">📍 ${c.loc} • ${c.type}</div>
        <div class="cc-tags">${tags}</div>
      </div>
      <div class="cc-footer">
        <div class="cc-rating">
          <span class="stars">${getStars(c.rating)}</span>
          <span class="rating-val">${c.rating}</span>
          <span class="rating-count">(${c.reviews.toLocaleString()})</span>
        </div>
        <div class="cc-fee">
          <div class="cc-fee-lbl">Annual Fees</div>
          <div class="cc-fee-val">${c.fees}</div>
        </div>
      </div>
      <div class="cc-actions">
        <button class="btn-cc-detail" onclick="event.stopPropagation();openCollegeDetail(${c.id})">View Details</button>
        <button class="btn-cc-compare" onclick="event.stopPropagation();addToCompare(${c.id})">⚖️</button>
        <button class="btn-cc-wish" onclick="event.stopPropagation();toggleWishlist(${c.id},this)">🤍</button>
      </div>
    </div>
  `;
}

function getStars(rating) {
  const full = Math.floor(rating);
  const half = rating % 1 >= .5 ? 1 : 0;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(5 - full - half);
}

// ─── EXAM CARD HTML ─────────────────────────────────────────
function examCardHTML(e) {
  const statusLabel = e.status === 'open' ? '🟢 Open' : e.status === 'closed' ? '🔴 Closed' : '🟡 Soon';
  return `
    <div class="exam-page-card" onclick="window.open('${e.website}','_blank')">
      <div class="epc-header">
        <div class="epc-icon">${e.icon}</div>
        <div>
          <div class="epc-name">${e.name}</div>
          <div class="epc-full">${e.full}</div>
        </div>
      </div>
      <div class="epc-body">
        <div class="epc-row"><span class="epc-key">Level</span><span class="epc-val">${e.level}</span></div>
        <div class="epc-row"><span class="epc-key">Exam Date</span><span class="epc-val">${e.date}</span></div>
        <div class="epc-row"><span class="epc-key">Mode</span><span class="epc-val">${e.mode}</span></div>
        <div class="epc-row"><span class="epc-key">Registration</span><span class="epc-val">${e.regDeadline}</span></div>
        <div class="epc-row"><span class="epc-key">Status</span><span class="epc-status ${e.status}">${statusLabel}</span></div>
        <div class="epc-row"><span class="epc-key">Eligible</span><span class="epc-val">${e.eligible}</span></div>
      </div>
      <div class="epc-footer">
        <button class="btn-exam-detail" onclick="event.stopPropagation();window.open('${e.website}','_blank')">View Details →</button>
        <button class="btn-exam-alert" onclick="event.stopPropagation();showToast('Alert set for ${e.name}!','success')">🔔 Alert</button>
      </div>
    </div>
  `;
}

// ─── NEWS CARD HTML ──────────────────────────────────────────
function newsSmallCardHTML(n) {
  return `
    <div class="news-card" style="background:var(--white);border:1.5px solid var(--border);border-radius:16px;overflow:hidden;cursor:pointer;transition:.3s;"
      onmouseover="this.style.boxShadow='0 12px 40px rgba(10,22,40,.12)';this.style.transform='translateY(-3px)'"
      onmouseout="this.style.boxShadow='';this.style.transform=''">
      <div style="height:100px;display:flex;align-items:center;justify-content:center;font-size:3rem;background:${n.bg};">${n.emoji}</div>
      <div style="padding:16px 18px">
        <div style="font-size:10px;font-weight:800;color:var(--saffron);text-transform:uppercase;letter-spacing:.8px;margin-bottom:7px">${n.cat}</div>
        <div style="font-size:14px;font-weight:700;color:var(--deep);line-height:1.4;margin-bottom:8px;font-family:var(--font-display)">${n.title}</div>
        <div style="font-size:12px;color:var(--gray)">${n.date}</div>
      </div>
    </div>
  `;
}

// ─── COLLEGES FULL PAGE ──────────────────────────────────────
let activeStream = 'All';
let activeView = 'list';
let currentColleges = [...COLLEGES];

function renderCollegePage() {
  let list = [...COLLEGES];
  if (activeStream && activeStream !== 'All') {
    list = list.filter(c =>
      c.stream.toLowerCase().includes(activeStream.toLowerCase()) ||
      c.type.toLowerCase().includes(activeStream.toLowerCase()) ||
      c.name.toLowerCase().includes(activeStream.toLowerCase()) ||
      c.tags.some(t => t.toLowerCase().includes(activeStream.toLowerCase()))
    );
  }
  currentColleges = list;
  document.getElementById('collegeCount').textContent = list.length;
  renderCollegeListItems(list);
}

function renderCollegeListItems(list) {
  const el = document.getElementById('collegeListEl');
  if (!el) return;

  if (activeView === 'grid') {
    el.style.display = 'grid';
    el.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
    el.style.gap = '22px';
    el.innerHTML = list.map(c => collegeCardHTML(c)).join('');
  } else {
    el.style.display = 'flex';
    el.style.flexDirection = 'column';
    el.style.gridTemplateColumns = '';
    el.innerHTML = list.map(c => collegeListItemHTML(c)).join('');
  }
  setTimeout(observeCards, 80);
}

function collegeListItemHTML(c) {
  const tags = c.tags.slice(0, 3).map((t, i) =>
    `<span class="ctag ${i === 1 ? 'blue' : i === 2 ? 'green' : ''}">${t}</span>`
  ).join('');

  return `
    <div class="college-list-item" onclick="openCollegeDetail(${c.id})">
      <div class="cli-thumb" style="min-height:140px">
        <img src="${c.image}" alt="${c.name}"
          style="width:100%;height:100%;object-fit:cover;min-height:140px"
          onerror="this.style.display='none';this.parentNode.style.background='linear-gradient(135deg,${c.color}40,${c.color}20)'">
        ${c.badge ? `<div style="position:absolute;bottom:10px;left:10px;background:linear-gradient(135deg,var(--gold),#c8810d);color:#fff;font-size:10px;font-weight:800;padding:4px 10px;border-radius:7px">${c.badge}</div>` : ''}
      </div>
      <div class="cli-body">
        <div>
          <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap">
            <div>
              <div style="font-family:var(--font-display);font-size:16px;font-weight:800;color:var(--deep);margin-bottom:4px">${c.name}</div>
              <div style="font-size:12.5px;color:var(--gray);display:flex;align-items:center;gap:10px;flex-wrap:wrap">
                <span>📍 ${c.loc}</span>
                <span>• ${c.type}</span>
                <span class="stars" style="font-size:13px">★ ${c.rating}</span>
              </div>
            </div>
            <div style="text-align:right;flex-shrink:0">
              <div style="font-family:var(--font-display);font-size:1.3rem;font-weight:800;color:var(--saffron)">${c.fees}</div>
              <div style="font-size:11px;color:var(--gray)">per year</div>
            </div>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin:12px 0">${tags}</div>
        </div>
        <div class="cli-actions">
          <div style="display:flex;gap:20px;flex-wrap:wrap;flex:1">
            <div class="cli-stat"><div class="cli-stat-val">${c.placement}</div><div class="cli-stat-key">Avg Package</div></div>
            <div class="cli-stat"><div class="cli-stat-val">#${c.rank}</div><div class="cli-stat-key">Odisha Rank</div></div>
            <div class="cli-stat"><div class="cli-stat-val">${c.score}</div><div class="cli-stat-key">NIRF Score</div></div>
          </div>
          <div style="display:flex;gap:8px">
            <button class="btn-cc-detail" onclick="event.stopPropagation();openCollegeDetail(${c.id})">View Details</button>
            <button class="btn-cc-compare" onclick="event.stopPropagation();addToCompare(${c.id})">⚖️</button>
            <button class="btn-cc-wish" onclick="event.stopPropagation();toggleWishlist(${c.id},this)">🤍</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function applyFilters() {
  const types = [];
  if (document.getElementById('type-govt')?.checked) types.push('Government');
  if (document.getElementById('type-private')?.checked) types.push('Private');
  if (document.getElementById('type-deemed')?.checked) types.push('Deemed');

  const streams = [];
  if (document.getElementById('str-eng')?.checked) streams.push('Engineering');
  if (document.getElementById('str-med')?.checked) streams.push('Medical');
  if (document.getElementById('str-mba')?.checked) streams.push('MBA');
  if (document.getElementById('str-arts')?.checked) streams.push('Arts');
  if (document.getElementById('str-sci')?.checked) streams.push('Science');

  let list = [...COLLEGES];
  if (types.length) list = list.filter(c => types.includes(c.type));
  if (streams.length) list = list.filter(c => streams.includes(c.stream));
  if (activeStream && activeStream !== 'All') {
    list = list.filter(c => c.stream.includes(activeStream) || c.type.includes(activeStream));
  }

  currentColleges = list;
  document.getElementById('collegeCount').textContent = list.length;
  renderCollegeListItems(list);
  showToast(`Showing ${list.length} colleges`, 'info');
}

function clearFilters() {
  document.querySelectorAll('.sidebar input[type=checkbox]').forEach(cb => cb.checked = false);
  activeStream = 'All';
  renderCollegePage();
  showToast('Filters cleared', 'info');
}

function sortColleges(val) {
  const list = [...currentColleges];
  if (val === 'rank') list.sort((a, b) => a.rank - b.rank);
  if (val === 'rating') list.sort((a, b) => b.rating - a.rating);
  if (val === 'fees_low') list.sort((a, b) => parseFee(a.fees) - parseFee(b.fees));
  if (val === 'fees_high') list.sort((a, b) => parseFee(b.fees) - parseFee(a.fees));
  renderCollegeListItems(list);
}

function parseFee(str) {
  const s = str.replace(/[₹,\s]/g, '');
  if (s.includes('L')) return parseFloat(s) * 100000;
  if (s.includes('K')) return parseFloat(s) * 1000;
  return parseFloat(s) || 0;
}

function setView(view, btn) {
  activeView = view;
  document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderCollegeListItems(currentColleges);
}

function highlightFilterBtn(stream) {
  document.querySelectorAll('#colleges-filter-bar .fbtn').forEach(b => {
    b.classList.toggle('active', b.textContent.trim().includes(stream));
  });
}

// ─── EXAMS PAGE ──────────────────────────────────────────────
function renderExamsPage() {
  const grid = document.getElementById('examPageGrid');
  if (!grid) return;
  grid.innerHTML = EXAMS.map(e => examCardHTML(e)).join('');
  setTimeout(observeCards, 80);
}

function filterExams(btn, cat) {
  document.querySelectorAll('#examFilter .fbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const grid = document.getElementById('examPageGrid');
  const list = cat === 'All' ? EXAMS : EXAMS.filter(e => e.cat === cat || e.level === cat);
  grid.innerHTML = list.map(e => examCardHTML(e)).join('');
  setTimeout(observeCards, 80);
}

// ─── RANKINGS PAGE ───────────────────────────────────────────
function renderRankingsPage() {
  renderRankTable([...COLLEGES].sort((a, b) => a.rank - b.rank));
}

function renderRankTable(list) {
  const tbody = document.getElementById('rankTableBody');
  if (!tbody) return;
  const colors = ['linear-gradient(135deg,#F59E0B,#D97706)','linear-gradient(135deg,#6B7280,#4B5563)','linear-gradient(135deg,#B45309,#92400E)','linear-gradient(135deg,var(--blue),#1A4FA0)'];
  tbody.innerHTML = list.map((c, i) => `
    <tr>
      <td>
        <div class="rank-num" style="background:${colors[i] || 'linear-gradient(135deg,var(--gray),#4B5563)'}">#${c.rank}</div>
      </td>
      <td>
        <div class="rank-college-name">${c.name}</div>
        <div class="rank-college-loc">📍 ${c.loc}</div>
      </td>
      <td><span class="ctag">${c.stream}</span></td>
      <td>
        <div class="score-bar-wrap">
          <div class="score-bar"><div class="score-fill" style="width:${c.score}%"></div></div>
          <div class="score-val">${c.score}/100</div>
        </div>
      </td>
      <td>
        <span class="stars" style="font-size:13px">★</span>
        <strong style="font-size:13px"> ${c.rating}</strong>
        <span style="font-size:11px;color:var(--gray)"> (${c.reviews.toLocaleString()})</span>
      </td>
      <td>
        <button class="btn-exam-detail" onclick="openCollegeDetail(${c.id})" style="padding:8px 16px">View →</button>
      </td>
    </tr>
  `).join('');
}

function filterRanks(btn, cat) {
  document.querySelectorAll('#rankFilter .fbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const list = cat === 'All' ? [...COLLEGES] : COLLEGES.filter(c => c.stream === cat || c.type === cat);
  renderRankTable(list.sort((a, b) => a.rank - b.rank));
}

// ─── SCHOLARSHIPS PAGE ──────────────────────────────────────
function renderScholarshipsPage() {
  const grid = document.getElementById('scholarGrid');
  if (!grid) return;
  grid.innerHTML = SCHOLARSHIPS.map(s => `
    <div class="scholar-card">
      <div class="sc-header">
        <div class="sc-icon-box">${s.icon}</div>
        <div>
          <div class="sc-name">${s.name}</div>
          <div class="sc-org">${s.org}</div>
        </div>
      </div>
      <div class="sc-amount">
        <div class="amount">${s.amount}</div>
        <div class="per">${s.per}</div>
      </div>
      <div class="sc-details">
        <div class="sc-detail-row"><span class="sc-detail-key">Eligibility</span><span class="sc-detail-val">${s.eligibility}</span></div>
        <div class="sc-detail-row"><span class="sc-detail-key">Deadline</span><span class="sc-detail-val">${s.deadline}</span></div>
        <div class="sc-detail-row"><span class="sc-detail-key">Coverage</span><span class="sc-detail-val">${s.coverage}</span></div>
        <div class="sc-detail-row"><span class="sc-detail-key">Category</span><span class="sc-detail-val">${s.category}</span></div>
      </div>
      <div class="sc-footer">
        <button class="btn-sc-apply" onclick="window.open('${s.link}','_blank')">Apply Now</button>
        <button class="btn-sc-info" onclick="showToast('Opening ${s.name} details','info')">More Info</button>
      </div>
    </div>
  `).join('');
  setTimeout(observeCards, 80);
}

function setFilterActive(btn) {
  document.querySelectorAll('#page-scholarships .fbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

// ─── NEWS PAGE ───────────────────────────────────────────────
function renderNewsPage() {
  const main = document.getElementById('newsMain');
  if (main) {
    main.innerHTML = NEWS_DATA.map(n => `
      <div class="news-card-lg">
        <div class="ncl-thumb" style="background:${n.bg};">${n.emoji}</div>
        <div class="ncl-body">
          <div class="ncl-cat">${n.cat}</div>
          <div class="ncl-title">${n.title}</div>
          <div class="ncl-excerpt">${n.excerpt}</div>
          <div class="ncl-meta">
            <span>📅 ${n.date}</span>
            <span style="color:var(--green);font-weight:600">${n.trending ? '🔥 Trending' : ''}</span>
          </div>
        </div>
      </div>
    `).join('');
  }

  const trending = document.getElementById('trendingNews');
  if (trending) {
    const t = NEWS_DATA.filter(n => n.trending);
    trending.innerHTML = t.map((n, i) => `
      <div class="ns-item">
        <div class="ns-item-num">${i + 1}</div>
        <div class="ns-item-title">${n.title}</div>
      </div>
    `).join('');
  }
}

// ─── COLLEGE DETAIL MODAL ────────────────────────────────────
function openCollegeDetail(id) {
  const c = COLLEGES.find(x => x.id === id);
  if (!c) return;

  // Set hero image
  document.getElementById('cdmHeroImg').style.backgroundImage = `url('${c.image}')`;

  // Logo
  const logoEl = document.getElementById('cdmLogoEl');
  if (c.logo) {
    logoEl.innerHTML = `<img src="${c.logo}" alt="${c.name}" style="width:100%;height:100%;object-fit:contain;padding:6px" onerror="this.parentNode.innerHTML='<span style=color:${c.color};font-family:var(--font-display);font-size:18px;font-weight:900>${c.short}</span>'">`;
  } else {
    logoEl.innerHTML = `<span style="color:${c.color};font-family:var(--font-display);font-size:20px;font-weight:900">${c.short}</span>`;
  }

  document.getElementById('cdmCollegeName').textContent = c.name;
  document.getElementById('cdmCollegeMeta').textContent = `📍 ${c.loc}  •  ${c.type}  •  Est. ${c.estYear}`;

  // Overview
  document.getElementById('cdm-overview').innerHTML = `
    <div class="cdm-stats-grid">
      <div class="cdm-stat"><div class="cdm-stat-val">${c.rating}/5</div><div class="cdm-stat-key">Overall Rating</div></div>
      <div class="cdm-stat"><div class="cdm-stat-val">${c.fees}</div><div class="cdm-stat-key">Annual Fees</div></div>
      <div class="cdm-stat"><div class="cdm-stat-val">${c.placement}</div><div class="cdm-stat-key">Avg Package</div></div>
      <div class="cdm-stat"><div class="cdm-stat-val">#${c.rank}</div><div class="cdm-stat-key">Odisha Rank</div></div>
    </div>
    <p class="cdm-desc">${c.desc}</p>
    <div style="margin-top:18px;display:flex;gap:8px;flex-wrap:wrap">
      ${c.accreditation ? `<span class="ctag green">✓ ${c.accreditation}</span>` : ''}
      ${c.hostel ? `<span class="ctag blue">🏠 Hostel</span>` : ''}
      ${c.scholarship ? `<span class="ctag">🎓 Scholarships</span>` : ''}
    </div>
  `;

  // Courses
  document.getElementById('cdm-courses').innerHTML = c.courses.map(cr => `
    <div class="cdm-course-row">
      <div class="cdm-course-name">${cr.name}</div>
      <div class="cdm-course-meta">
        <span class="cdm-course-fee">${cr.fee}</span>
        <span class="cdm-course-dur">${cr.dur}</span>
        <span style="font-size:11px;color:var(--gray)">${cr.seats} seats</span>
      </div>
    </div>
  `).join('');

  // Placements
  document.getElementById('cdm-placements').innerHTML = `
    <div class="cdm-stats-grid">
      <div class="cdm-stat"><div class="cdm-stat-val">${c.avgPkg}</div><div class="cdm-stat-key">Avg Package</div></div>
      <div class="cdm-stat"><div class="cdm-stat-val">${c.highPkg}</div><div class="cdm-stat-key">Highest Package</div></div>
      <div class="cdm-stat"><div class="cdm-stat-val">${c.placed}</div><div class="cdm-stat-key">Placement Rate</div></div>
      <div class="cdm-stat"><div class="cdm-stat-val">#${c.rank}</div><div class="cdm-stat-key">NIRF Rank</div></div>
    </div>
    <p class="cdm-desc"><strong>Top Recruiters:</strong> ${c.topRecruiter}</p>
  `;

  // Campus
  document.getElementById('cdm-campus').innerHTML = `
    <div class="cdm-stats-grid" style="grid-template-columns:repeat(2,1fr)">
      <div class="cdm-stat"><div class="cdm-stat-val">Est. ${c.estYear}</div><div class="cdm-stat-key">Year Founded</div></div>
      <div class="cdm-stat"><div class="cdm-stat-val">${c.type}</div><div class="cdm-stat-key">College Type</div></div>
    </div>
    <p class="cdm-desc"><strong>Campus:</strong> ${c.campus}</p>
    <p class="cdm-desc" style="margin-top:12px"><strong>Accreditation:</strong> ${c.accreditation}</p>
    <p class="cdm-desc" style="margin-top:8px">
      <a href="${c.website}" target="_blank" style="color:var(--blue);font-weight:600">🌐 Visit Official Website →</a>
    </p>
  `;

  // Footer buttons
  document.getElementById('cdmFooterBtns').innerHTML = `
    <button class="btn-apply-lg" onclick="applyCollege('${c.name}')">🎓 Apply Now</button>
    <button class="btn-compare-lg" onclick="addToCompare(${c.id});closeCollegeDetail()">⚖️ Compare</button>
    <button class="btn-brochure-lg" onclick="window.open('${c.website}','_blank')">🌐 Website</button>
  `;

  // Reset tab
  switchCDMTab('overview', document.querySelector('.cdm-tab'));
  document.getElementById('collegeDetailModal').classList.add('open');
}

function closeCollegeDetail() {
  document.getElementById('collegeDetailModal').classList.remove('open');
}

function switchCDMTab(tab, btn) {
  document.querySelectorAll('.cdm-tab').forEach(t => t.classList.remove('active'));
  if (btn) btn.classList.add('active');
  else {
    const tabs = document.querySelectorAll('.cdm-tab');
    if (tab === 'overview') tabs[0]?.classList.add('active');
  }
  document.querySelectorAll('.cdm-section').forEach(s => s.classList.remove('active'));
  document.getElementById('cdm-' + tab)?.classList.add('active');
}

// ─── COMPARE ─────────────────────────────────────────────────
let compareList = [];
function addToCompare(id) {
  const c = COLLEGES.find(x => x.id === id);
  if (!c) return;
  if (compareList.find(x => x.id === id)) { showToast(`${c.name} already in compare`, 'info'); return; }
  if (compareList.length >= 3) { showToast('Max 3 colleges for comparison', 'error'); return; }
  compareList.push(c);
  updateCompareBar();
  showToast(`${c.name} added to compare`, 'success');
}

function removeFromCompare(id) {
  compareList = compareList.filter(x => x.id !== id);
  updateCompareBar();
}

function updateCompareBar() {
  const bar = document.getElementById('compareBar');
  const btn = document.getElementById('doCompareBtn');
  if (compareList.length > 0) bar.classList.add('visible');
  else bar.classList.remove('visible');

  for (let i = 0; i < 3; i++) {
    const slot = document.getElementById('cslot' + i);
    if (!slot) continue;
    if (compareList[i]) {
      slot.className = 'compare-slot filled';
      slot.innerHTML = `<span>${compareList[i].short}</span><button class="remove-cmp" onclick="removeFromCompare(${compareList[i].id})">✕</button>`;
    } else {
      slot.className = 'compare-slot';
      slot.innerHTML = '+ Add College';
    }
  }
  btn.disabled = compareList.length < 2;
}

function clearComparison() {
  compareList = [];
  updateCompareBar();
}

function runComparison() {
  if (compareList.length < 2) return;
  const cols = compareList;
  const rows = [
    ['Location', ...cols.map(c => c.loc)],
    ['Type', ...cols.map(c => c.type)],
    ['Stream', ...cols.map(c => c.stream)],
    ['Annual Fees', ...cols.map(c => c.fees)],
    ['Avg Package', ...cols.map(c => c.placement)],
    ['Highest Package', ...cols.map(c => c.highPkg)],
    ['Placement Rate', ...cols.map(c => c.placed)],
    ['Rating', ...cols.map(c => c.rating + '/5')],
    ['NIRF Score', ...cols.map(c => c.score + '/100')],
    ['Odisha Rank', ...cols.map(c => '#' + c.rank)],
    ['Accreditation', ...cols.map(c => c.accreditation)],
    ['Hostel', ...cols.map(c => c.hostel ? '✅ Yes' : '❌ No')],
  ];

  const html = `
    <div style="overflow-x:auto">
      <table style="width:100%;border-collapse:collapse;font-size:13.5px">
        <thead>
          <tr>
            <th style="padding:12px 16px;background:linear-gradient(135deg,var(--deep),#142240);color:rgba(255,255,255,.6);text-align:left;font-size:11px;text-transform:uppercase">Parameter</th>
            ${cols.map(c => `<th style="padding:12px 16px;background:linear-gradient(135deg,var(--deep),#142240);color:#fff;text-align:left;font-family:var(--font-display)">${c.short}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${rows.map((r, i) => `
            <tr style="border-bottom:1px solid var(--border);${i % 2 === 0 ? 'background:var(--light)' : ''}">
              <td style="padding:12px 16px;color:var(--gray);font-weight:600">${r[0]}</td>
              ${r.slice(1).map(v => `<td style="padding:12px 16px;font-weight:500;color:var(--deep)">${v}</td>`).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;

  // Show in a simple overlay
  const overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;inset:0;z-index:3000;background:rgba(10,22,40,.85);backdrop-filter:blur(16px);display:flex;align-items:center;justify-content:center;padding:20px;';
  overlay.innerHTML = `
    <div style="background:#fff;border-radius:24px;max-width:800px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 32px 96px rgba(0,0,0,.4)">
      <div style="padding:24px 28px;border-bottom:1.5px solid var(--border);display:flex;align-items:center;justify-content:space-between">
        <div style="font-family:var(--font-display);font-size:1.4rem;font-weight:900;color:var(--deep)">College Comparison</div>
        <button onclick="this.closest('div[style]').remove()" style="background:var(--light);border:none;cursor:pointer;width:36px;height:36px;border-radius:9px;font-size:18px">✕</button>
      </div>
      <div style="padding:24px">${html}</div>
    </div>
  `;
  document.body.appendChild(overlay);
}

// ─── WISHLIST ────────────────────────────────────────────────
const wishlist = new Set();
function toggleWishlist(id, btn) {
  if (wishlist.has(id)) {
    wishlist.delete(id);
    btn.textContent = '🤍';
    showToast('Removed from wishlist', 'info');
  } else {
    wishlist.add(id);
    btn.textContent = '❤️';
    showToast('Added to wishlist', 'success');
  }
}

// ─── AUTH MODAL ──────────────────────────────────────────────
let currentUser = null;

function openModal(tab = 'login') {
  document.getElementById('authModal').classList.add('open');
  switchAuthTab(tab);
}

function closeModal() {
  document.getElementById('authModal').classList.remove('open');
}

function switchAuthTab(tab) {
  document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('[data-auth-tab]').forEach(t => {
    t.style.display = t.dataset.authTab === tab ? 'block' : 'none';
  });
  document.querySelector(`.modal-tab[onclick*="${tab}"]`)?.classList.add('active');
}

function doLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const pass = document.getElementById('loginPass').value;
  if (!email || !pass) { showToast('Please fill all fields', 'error'); return; }
  currentUser = { name: email.split('@')[0], email };
  updateUserUI();
  closeModal();
  showToast(`Welcome back, ${currentUser.name}!`, 'success');
}

function doRegister() {
  const name = document.getElementById('regName').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const pass = document.getElementById('regPass').value;
  if (!name || !email || !pass) { showToast('Please fill all fields', 'error'); return; }
  currentUser = { name, email };
  updateUserUI();
  closeModal();
  showToast(`Welcome to CollegeHub, ${name}!`, 'success');
}

function logout() {
  currentUser = null;
  updateUserUI();
  document.getElementById('pdMenu').classList.remove('open');
  showToast('Logged out successfully', 'info');
}

function updateUserUI() {
  const actions = document.getElementById('headerActions');
  if (currentUser) {
    actions.innerHTML = `
      <div class="profile-dropdown visible">
        <div class="user-avatar" onclick="document.getElementById('pdMenu').classList.toggle('open')">${currentUser.name[0].toUpperCase()}</div>
        <div class="pd-menu" id="pdMenu">
          <div class="pd-item" onclick="showToast('My Profile – coming soon!','info')">👤 My Profile</div>
          <div class="pd-item" onclick="showToast('My Applications – coming soon!','info')">📋 My Applications</div>
          <div class="pd-item" onclick="showToast('Saved Colleges – coming soon!','info')">❤️ Saved Colleges</div>
          <div class="pd-item danger" onclick="logout()">🚪 Logout</div>
        </div>
      </div>
    `;
  } else {
    actions.innerHTML = `
      <button class="btn-login" onclick="openModal('login')">Login</button>
      <button class="btn-register" onclick="openModal('register')">Register Free</button>
    `;
  }
}

function applyCollege(name) {
  if (currentUser) showToast(`Application submitted for ${name}! 🎉`, 'success');
  else { openModal('login'); showToast('Please login to apply', 'info'); }
}

// ─── AI COUNSELOR ─────────────────────────────────────────────
let aiPanelOpen = false;
const aiConversation = [];

function toggleAIPanel() {
  aiPanelOpen = !aiPanelOpen;
  document.getElementById('aiPanel').classList.toggle('open', aiPanelOpen);
  if (aiPanelOpen) {
    setTimeout(() => document.getElementById('aiInput')?.focus(), 300);
  }
}

async function sendAIMessage(presetMsg) {
  const input = document.getElementById('aiInput');
  const msg = (presetMsg || input.value).trim();
  if (!msg) return;
  input.value = '';

  const messagesEl = document.getElementById('aiMessages');
  messagesEl.innerHTML += `<div class="ai-msg user">${msg}</div>`;
  document.getElementById('aiTyping').classList.add('visible');
  document.getElementById('aiQuickReplies').style.display = 'none';
  messagesEl.scrollTop = messagesEl.scrollHeight;

  try {
    aiConversation.push({ role: 'user', content: msg });
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 400,
        system: `You are Vidya, an AI college counselor for Odisha CollegeHub.
Help students find colleges in Odisha, India. Be friendly, concise, helpful and encouraging.
Key colleges: IIT Bhubaneswar (Engineering, #1, ₹18 LPA avg), NIT Rourkela (Engineering, #2, ₹14 LPA avg), AIIMS Bhubaneswar (Medical, #3), KIIT University (Engineering/MBA, #4), SOA University (#5), Utkal University (Arts, oldest, ₹28K fees), XIM University (MBA, ₹22 LPA avg, top 10 B-school), VSSUT Burla (Engineering).
Key exams: OJEE (state engineering, deadline Mar 31), NEET (medical, May 4), JEE Main (engineering), CAT (MBA, November).
Scholarships: Medhabruti (Odisha Govt), Post-Matric SC/ST, INSPIRE (science).
Keep responses to 2-3 sentences. Use emojis. Always recommend visiting the site.`,
        messages: aiConversation
      })
    });
    const data = await response.json();
    const reply = data.content ? data.content.map(b => b.text || '').join('') : generateFallbackReply(msg);
    aiConversation.push({ role: 'assistant', content: reply });
    document.getElementById('aiTyping').classList.remove('visible');
    messagesEl.innerHTML += `<div class="ai-msg bot">${reply}</div>`;
    messagesEl.scrollTop = messagesEl.scrollHeight;
  } catch (err) {
    document.getElementById('aiTyping').classList.remove('visible');
    const fallback = generateFallbackReply(msg);
    aiConversation.push({ role: 'assistant', content: fallback });
    messagesEl.innerHTML += `<div class="ai-msg bot">${fallback}</div>`;
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }
}

function generateFallbackReply(msg) {
  const m = msg.toLowerCase();
  if (m.includes('engineering')) return 'Top engineering colleges: IIT Bhubaneswar (#1, ₹18 LPA avg), NIT Rourkela (#2, ₹14 LPA), VSSUT Burla (₹7 LPA). Use JEE Main or OJEE for admission! ⚙️';
  if (m.includes('medical') || m.includes('mbbs')) return 'Best medical colleges: AIIMS Bhubaneswar (govt, near-100% placement), KIMS (private, ₹10 LPA avg), SOA (deemed). NEET score required! 🏥';
  if (m.includes('mba') || m.includes('management')) return 'Top MBA options: XIM University (₹22 LPA avg, top 10 B-school!), KIIT (₹9 LPA), SOA. Take CAT or OJEE MBA to apply! 💼';
  if (m.includes('fee') || m.includes('cheap') || m.includes('affordable')) return 'Most affordable: Utkal University (₹28K/yr), Sambalpur University (₹24K/yr). Government colleges via OJEE quota offer excellent value! 💰';
  if (m.includes('placement') || m.includes('package')) return 'Best placements: XIM University (₹22 LPA avg, ₹68 LPA highest!), IIT Bhubaneswar (₹18 LPA), NIT Rourkela (₹14 LPA). 🚀';
  if (m.includes('scholarship')) return 'Key scholarships: Medhabruti (Odisha Govt, merit), Post-Matric SC/ST, INSPIRE (science). Apply at scholarship.odisha.gov.in! 🎓';
  return 'I can help you find the perfect college in Odisha! Ask about engineering, medical, MBA, fees, placements, or scholarships. 🎓';
}

// ─── HERO PARTICLES ─────────────────────────────────────────
function createHeroParticles() {
  const container = document.getElementById('heroParticles');
  if (!container) return;
  const emojis = ['🎓', '📚', '🏛️', '⭐', '🔬', '💼', '⚙️', '🏥'];
  for (let i = 0; i < 20; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size = Math.random() * 20 + 10;
    p.style.cssText = `
      left:${Math.random() * 100}%;
      width:${size}px;height:${size}px;
      font-size:${size * .85}px;
      animation-duration:${Math.random() * 14 + 10}s;
      animation-delay:${Math.random() * 10}s;
      display:flex;align-items:center;justify-content:center;
      border-radius:50%;
      background:rgba(244,98,42,0.07);
      border:1px solid rgba(244,98,42,0.12);
    `;
    if (Math.random() > .65) p.textContent = emojis[Math.floor(Math.random() * emojis.length)];
    container.appendChild(p);
  }
}

// ─── COUNTER ANIMATION ──────────────────────────────────────
function animateCounters() {
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count);
    const dur = 2000, step = target / dur * 16;
    let cur = 0;
    const timer = setInterval(() => {
      cur = Math.min(cur + step, target);
      el.textContent = cur >= 10000 ? Math.floor(cur / 1000) + 'K+' :
        cur >= 1000 ? Math.floor(cur).toLocaleString() + '+' : Math.floor(cur) + '+';
      if (cur >= target) clearInterval(timer);
    }, 16);
  });
}

// ─── INTERSECTION OBSERVER ───────────────────────────────────
function observeCards() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0) rotateX(0)';
      }
    });
  }, { threshold: .06 });

  document.querySelectorAll('.stream-card,.college-card,.exam-page-card,.news-card,.testimonial-card,.scholar-card,.college-list-item,.exam-card,.news-card-lg').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px) rotateX(4deg)';
    el.style.transition = `opacity .55s ${i * .05}s ease, transform .55s ${i * .05}s ease`;
    observer.observe(el);
  });
}

// ─── FEE RANGE ───────────────────────────────────────────────
function updateFeeRange(val) {
  const v = parseInt(val);
  document.getElementById('feeRangeVal').textContent =
    v >= 100000 ? `₹${(v / 100000).toFixed(1)}L` : `₹${(v / 1000).toFixed(0)}K`;
}

// ─── TOAST ───────────────────────────────────────────────────
let toastTimer;
function showToast(msg, type = 'info') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 3000);
}

// ─── 3D CARD TILT ────────────────────────────────────────────
function initCardTilt() {
  document.addEventListener('mousemove', e => {
    document.querySelectorAll('.college-card:hover').forEach(card => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      const rx = (-y / rect.height) * 8;
      const ry = (x / rect.width) * 8;
      card.style.transform = `translateY(-8px) rotateX(${rx}deg) rotateY(${ry}deg)`;
    });
  });
}

// ─── INIT ─────────────────────────────────────────────────────
(function init() {
  initBgSlider();
  initCanvas();
  renderHomeColleges();
  renderHomeExams();
  renderHomeNews();
  renderTestimonials();
  createHeroParticles();
  initCardTilt();
  setTimeout(animateCounters, 600);
  setTimeout(observeCards, 150);
})();