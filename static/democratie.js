// Minimal JS for accessible accordion and simple interactions
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(function(btn){
    btn.addEventListener('click', function(e){
      // default collapse toggle behavior handled by Bootstrap; no extra logic needed here
    });
  });

  // Questionnaire loader: dynamically load questionnaire script only when the wizard is present
  try{
    // helper: ensure the questionnaire helper script is loaded once and optionally call its init helper
    function ensureQuestionnaireLoaded(cb){
      try{
        // already initialized by the module
        if(window.__qInit && typeof window.__qInit === 'function'){
          try{ window.__qInit(); }catch(e){}
          if(cb) cb();
          return;
        }
        // avoid inserting duplicate script tags
        if(document.querySelector('script[src="/static/democratiequestionnaire.js"]')){
          // script present but not yet initialized — attach a short polling to wait for __qInit
          var waited = 0;
          var iv = setInterval(function(){ if(window.__qInit){ clearInterval(iv); try{ window.__qInit(); }catch(e){} if(cb) cb(); } waited += 50; if(waited > 3000){ clearInterval(iv); if(cb) cb(); } }, 50);
          return;
        }
        if(document.getElementById('qWizard')){
          var s = document.createElement('script');
          s.src = '/static/democratiequestionnaire.js';
          s.defer = true;
          s.onload = function(){ try{ if(window.__qInit) window.__qInit(); }catch(e){} if(cb) cb(); };
          s.onerror = function(){ console.warn('Failed to load questionnaire script'); if(cb) cb(); };
          document.body.appendChild(s);
          return;
        }
      }catch(e){ console.warn('ensureQuestionnaireLoaded failed', e); if(cb) cb(); }
    }

    // If wizard exists at load time, ensure script is loaded
    try{ if(document.getElementById('qWizard')) ensureQuestionnaireLoaded(); }catch(e){}

    // Also ensure the questionnaire initializes when the modal is opened (if present)
    try{
      if(window.jQuery && typeof jQuery === 'function'){
        jQuery('#modalQuestionnaire').on('shown.bs.modal', function(){ ensureQuestionnaireLoaded(); });
      } else {
        var mq = document.getElementById('modalQuestionnaire');
        if(mq) mq.addEventListener('shown.bs.modal', function(){ ensureQuestionnaireLoaded(); });
      }
    }catch(e){ /* non-fatal */ }
  }catch(e){ console.warn('questionnaire loader failed', e); }

  // Render small 'phases' component into #phases-container if present.
  // Defensive: idempotent, uses inline data if provided, falls back to sensible defaults.
  function escapeHtml(str){
    return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function renderPhases(){
    try{
      var container = document.getElementById('phases-container');
      if(!container) return;
      if(container.dataset.rendered) return; // already rendered

      // allow optional JSON blob in an element with id="phases-data" and data-phases attribute
      var phases = null;
      var helper = document.getElementById('phases-data');
      if(helper && helper.dataset && helper.dataset.phases){
        try{ phases = JSON.parse(helper.dataset.phases); }catch(e){ phases = null; }
      }

      if(!Array.isArray(phases)){
        phases = [
          { title: 'Consultation', text: 'Collecte d\'avis et rencontres locales avec les citoyens.' },
          { title: 'Délibération', text: 'Ateliers, comités et synthèses pour structurer les propositions.' },
          { title: 'Rédaction', text: 'Rédaction du texte constitutionnel ou des lois organiques.' },
          { title: 'Plébiscite', text: 'Vote populaire (plébiscite\/référendum) pour valider les choix majeurs.' },
          { title: 'Mise en œuvre', text: 'Adoption des mesures et déploiement des dispositifs institutionnels.' },
          { title: 'Suivi', text: 'Évaluation, audits et possibilité de révision en fonction des retours.' }
        ];
      }

      var frag = document.createDocumentFragment();
      var list = document.createElement('div');
      list.className = 'phases-list';
      phases.forEach(function(p, idx){
        var card = document.createElement('div');
        card.className = 'phase-card mb-3 p-3 bg-light border rounded';
        card.innerHTML = '<h4 class="h6">Phase ' + (idx+1) + ': ' + escapeHtml(p.title) + '</h4>' +
                         '<div class="small text-muted">' + escapeHtml(p.text) + '</div>';
        list.appendChild(card);
      });
      frag.appendChild(list);
      container.appendChild(frag);
      container.dataset.rendered = '1';
    }catch(err){ console.warn('renderPhases failed', err); }
  }

  // call immediately; safe if DOMContentLoaded already firing
  try{ renderPhases(); }catch(e){}

  try {
    if (typeof wireForm === 'function') {
      try { wireForm('contactForm', 'contact_demo', 'contact_submit'); } catch (err) { console.warn('wireForm invocation failed', err); }
    } else {
      console.info('wireForm not defined; skipping contact form wiring');
    }
  } catch (e) { console.warn('guarding wireForm failed', e); }

    // ICS generator for event card -> simple function that returns blob URL
    function makeICS(event){
      // minimal ICS fields: DTSTART, DTEND, SUMMARY, UID, DESCRIPTION, LOCATION
      function fmtDateISO(d){
        // format YYYYMMDDTHHMMSSZ (UTC)
        const y = d.getUTCFullYear(); const m = String(d.getUTCMonth()+1).padStart(2,'0'); const day = String(d.getUTCDate()).padStart(2,'0');
        const hh = String(d.getUTCHours()).padStart(2,'0'); const mm = String(d.getUTCMinutes()).padStart(2,'0'); const ss = String(d.getUTCSeconds()).padStart(2,'0');
        return `${y}${m}${day}T${hh}${mm}${ss}Z`;
      }
      const uid = 'evt-' + (event.id || Math.random().toString(36).slice(2,8));
      const dtstart = event.start instanceof Date ? fmtDateISO(event.start) : fmtDateISO(new Date(event.start));
      const dtend = event.end ? (event.end instanceof Date ? fmtDateISO(event.end) : fmtDateISO(new Date(event.end))) : dtstart;
      const ics = [
        'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//DemocratieDirecte//FR', 'BEGIN:VEVENT',
        'UID:'+uid,
        'DTSTAMP:'+fmtDateISO(new Date()),
        'DTSTART:'+dtstart,
        'DTEND:'+dtend,
        'SUMMARY:'+ (event.title || 'Atelier constituant'),
        'DESCRIPTION:'+ (event.description || ''),
        'LOCATION:'+ (event.location || ''),
        'END:VEVENT','END:VCALENDAR'
      ].join('\r\n');
      const blob = new Blob([ics], {type:'text/calendar;charset=utf-8'});
      return URL.createObjectURL(blob);
    }

    // attach ics generation to any .workshop-ics buttons (if present)
    document.body.addEventListener('click', function(e){
      const btn = e.target.closest('.workshop-ics'); if(!btn) return;
      e.preventDefault();
      const data = btn.dataset || {};
      const ev = { id: data.id || Date.now(), title: data.title || btn.getAttribute('data-title') || 'Atelier', start: data.start || new Date().toISOString(), end: data.end || '', description: data.description || '', location: data.location || '' };
      const url = makeICS(ev);
      // create temporary link to download
      const a = document.createElement('a'); a.href = url; a.download = (ev.title || 'atelier') + '.ics'; document.body.appendChild(a); a.click(); a.remove();
      emitAnalytics('workshop_ics_click', {id:ev.id});
      // free object URL shortly after
      setTimeout(()=>URL.revokeObjectURL(url), 5000);
    });

    // analytics emission stub — replace with real analytics endpoint or dataLayer push in prod
    function emitAnalytics(name, payload){
      try{ if(window.dataLayer) window.dataLayer.push({event:name, ...payload}); }
      catch(e){}
      console.info('analytics event', name, payload);
    }
  // expose to other modules / listeners (some listeners run in separate DOMContentLoaded handlers)
  try{ window.emitAnalytics = emitAnalytics; }catch(e){}
  });

/* Questionnaire wizard: step navigation, progress and live updates (uses existing fieldsets as steps) */
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    try{
      const wizard = document.getElementById('qWizard');
      if(!wizard) return;
      const stepsContainer = document.getElementById('qSteps');
      if(!stepsContainer) return;
      const rawSteps = Array.from(stepsContainer.querySelectorAll('fieldset[data-section]'));
      if(rawSteps.length === 0) return;

      const steps = rawSteps.map((fs,i)=>{
        fs.classList.add('q-step');
        if(i!==0) fs.hidden = true; else fs.hidden = false;
        // add a small score area header if not present
        if(!fs.querySelector('.q-section-score')){
          const h = document.createElement('div'); h.className='q-section-score text-muted'; h.style.float='right'; h.textContent = '0 / ' + (fs.dataset.max||'');
          const legend = fs.querySelector('legend'); if(legend) legend.appendChild(h);
        }
        return fs;
      });

      let idx = 0;
      const prevBtn = document.getElementById('qPrev');
      const nextBtn = document.getElementById('qNext');
      const prog = document.getElementById('qProgressBar');
      const gauge = document.getElementById('qGaugeVal');
      const qSummary = document.getElementById('qSummary');

      function updateSectionScores(){
        steps.forEach(s=>{
          const max = Number(s.dataset.max||0);
          const names = new Set(Array.from(s.querySelectorAll('input[type=radio]')).map(r=>r.name));
          let sum=0;
          names.forEach(n=>{ const sel = s.querySelector(`[name="${n}"]:checked`); if(sel) sum += Number(sel.value); });
          const scoreEl = s.querySelector('.q-section-score');
          if(scoreEl) scoreEl.textContent = `${sum} / ${max}`;
        });
      }

      function updateProgress(){
  // show progress as completed steps (1..N) over total so final step reports 100%
  const percent = Math.round(((idx + 1) / (steps.length)) * 100);
        if(prog) prog.style.width = percent + '%';
        const total = Array.from(document.querySelectorAll('input[type=radio]:checked')).reduce((a,r)=>a+Number(r.value),0);
        if(gauge) gauge.textContent = total;
        if(qSummary) qSummary.hidden = false;
      }

      function show(i){
        idx = i;
        steps.forEach((s,ii)=> s.hidden = ii!==i);
        if(prevBtn) prevBtn.disabled = i===0;
        if(nextBtn) nextBtn.textContent = (i===steps.length-1)? 'Terminer' : 'Suivant →';
        updateSectionScores(); updateProgress();
        const first = steps[i].querySelector('input'); if(first) first.focus();
      }

      if(nextBtn) nextBtn.addEventListener('click', ()=>{ if(idx < steps.length-1) show(idx+1); else { updateProgress(); /* final action handled by existing compute */ } });
      if(prevBtn) prevBtn.addEventListener('click', ()=>{ if(idx>0) show(idx-1); });

  // live updates: debounce rapid changes to avoid over-firing
  function debounce(fn, wait){ let t = null; return function(){ const args = arguments; clearTimeout(t); t = setTimeout(()=> fn.apply(this, args), wait || 250); }; }

  const debouncedUpdate = debounce(function(){ updateSectionScores(); updateProgress(); /* also trigger compute to refresh sheet/gauge */ const calcBtn = document.getElementById('qCalculate'); if(calcBtn){ /* call compute directly if present */ const ev = new Event('click'); calcBtn.dispatchEvent(ev); } }, 300);

  wizard.addEventListener('change', e=>{ if(e.target.matches('input[type=radio], input[type=checkbox]')){ debouncedUpdate(); } });

      const saveBtn = document.getElementById('qSave'); if(saveBtn) saveBtn.addEventListener('click', ()=>{
        const data = {};
        wizard.querySelectorAll('input[type=radio]:checked').forEach(r=> data[r.name]=r.value);
        wizard.querySelectorAll('input[type=checkbox]:checked').forEach(c=> data[c.name]=c.value);
        try{ localStorage.setItem('q-wizard', JSON.stringify(data)); alert('Sauvegardé localement'); emitAnalytics && emitAnalytics('questionnaire_save',{count:Object.keys(data).length}); }
        catch(e){ alert('Impossible de sauvegarder localement'); }
      });

      const resetBtn = document.getElementById('qReset'); if(resetBtn) resetBtn.addEventListener('click', ()=>{ wizard.querySelectorAll('input[type=radio], input[type=checkbox]').forEach(i=> i.checked=false); updateSectionScores(); updateProgress(); });
      const printBtn = document.getElementById('qPrint'); if(printBtn) printBtn.addEventListener('click', ()=> window.print());

      // init
      show(0); updateProgress();
    }catch(err){ console.error('questionnaire wizard init failed', err); }
  });
})();

  // Questionnaire logic: scoring, interpretation, save/load
  document.addEventListener('DOMContentLoaded', function(){
  // prefer explicit form id 'qForm' but fall back to the wizard container 'qWizard'
  const qForm = document.getElementById('qForm') || document.getElementById('qWizard');
    const qCalc = document.getElementById('qCalculate');
  const qReset = document.getElementById('qReset');
  const qSave = document.getElementById('qSave');
  const qResult = document.getElementById('qResult') || null;
    const qSheet = document.getElementById('qSheet');
    const qSheetContent = document.getElementById('qSheetContent');
    const qPrint = document.getElementById('qPrint');
  const qSummary = document.getElementById('qSummary');

    // helper: animate a numeric change inside an element using requestAnimationFrame
    function shouldAnimate(){
      // session override takes precedence: 'on' or 'off'
      try{ const o = sessionStorage.getItem('motionOverride'); if(o === 'on') return true; if(o === 'off') return false; }catch(e){}
      // otherwise respect system preference
      try{ return !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }catch(e){ return true; }
    }

    function animateNumber(el, to, opts){
      try{
        // Respect session override or user preference for reduced motion
        if(!shouldAnimate()){ el.textContent = to; return; }
        const duration = (opts && opts.duration) || 600;
        const start = Number(el.textContent.replace(/[^0-9\-]/g,'')) || 0;
        if(start === to){ el.textContent = to; return; }
        el.setAttribute('aria-live','polite');
        const startTime = performance.now();
        function step(now){
          const t = Math.min(1, (now - startTime) / duration);
          // easeInOut
          const eased = 0.5 * (1 - Math.cos(Math.PI * t));
          const val = Math.round(start + (to - start) * eased);
          el.textContent = val;
          if(t < 1) requestAnimationFrame(step);
          else el.textContent = to;
        }
        requestAnimationFrame(step);
  }catch(e){ try{ el.textContent = to; }catch(_){} }
    }

    if(!qForm) return;

    // initialize motion toggle (session override) if present
    try{
      const motionToggle = document.getElementById('motionToggle');
      if(motionToggle){
        const val = sessionStorage.getItem('motionOverride');
        if(val === 'on') motionToggle.checked = true;
        else if(val === 'off') motionToggle.checked = false;
        else {
          // default to system preference
          try{ motionToggle.checked = !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }catch(e){ motionToggle.checked = true; }
        }
        motionToggle.addEventListener('change', function(){
          try{ sessionStorage.setItem('motionOverride', motionToggle.checked ? 'on' : 'off'); }catch(e){}
        });
      }
    }catch(e){}

    function sumSection(section){
      const fields = Array.from(qForm.querySelectorAll('[name^="'+section.toLowerCase()+'"]'));
      return fields.reduce((acc, el) => acc + (parseInt(el.value || 0) || 0), 0);
    }

    function compute(){
      // compute each section by summing named inputs
      const sections = ['a','b','c','d','e','f','g','h'];
      let total = 0; const details = {};
      sections.forEach(s=>{
        const nodes = Array.from(qForm.querySelectorAll('[name^="'+s+'"]'));
        const secSum = nodes.reduce((acc, el)=> acc + (parseInt(el.value || 0) || 0), 0);
        details[s.toUpperCase()] = secSum;
        total += secSum;
      });

  // VoxPop quick yes count
  const voxChecks = Array.from(qForm.querySelectorAll('#voxpop input[type="checkbox"]'));
  const voxYes = voxChecks.filter(c=>c.checked).length;

      // interpretation
      let interp = '';
      if(total <= 16) interp = 'Souveraineté déléguée sans contrôle réel — régime essentiellement représentatif.';
      else if(total <= 32) interp = 'Mécanismes limités — la souveraineté populaire n’est pas la règle.';
      else if(total <= 48) interp = 'Transitionnelle — plusieurs leviers en place, cohérence incomplète.';
      else interp = 'Proche d’une démocratie au sens strict — souveraineté exercée, contrôles effectifs.';

  if(qResult) qResult.innerHTML = `<strong>Total : ${total} /64</strong><br>${interp}<br>VoxPop Oui: ${voxYes} /10`;

  // prepare sheet
  if(qSheetContent) qSheetContent.innerHTML = '<ul>' + Object.keys(details).map(k=>`<li>${k}: ${details[k]}</li>`).join('') + `</ul><p><strong>Total:</strong> ${total} /64</p><p>${interp}</p>`;
  if(qSheet) qSheet.style.display = 'block';

  // update the dashboard gauge if present (animated)
  const gaugeEl = document.getElementById('qGaugeVal');
  if(gaugeEl) animateNumber(gaugeEl, total, {duration: 600});

  // guard analytics emission
  try{ if(window && typeof window.emitAnalytics === 'function') window.emitAnalytics('questionnaire_calculate', {total: total, details: details}); else if(typeof emitAnalytics === 'function') emitAnalytics('questionnaire_calculate', {total: total, details: details}); }catch(e){}
      // ---- Live progress & unanswered highlighting (includes checkboxes) ----
      try{
        // collect unique radio and checkbox groups representing single questions
        const radioInputs = Array.from(qForm.querySelectorAll('input[type="radio"]'));
        const checkboxInputs = Array.from(qForm.querySelectorAll('input[type="checkbox"]'));
        const radioNames = [...new Set(radioInputs.map(r=>r.name).filter(Boolean))];
        const checkboxNames = [...new Set(checkboxInputs.map(c=>c.name).filter(Boolean))];
        const names = [...new Set([...radioNames, ...checkboxNames])];
        const totalQuestions = names.length;
        let answered = 0;
        names.forEach(function(n){
          const checked = qForm.querySelector(`[name="${n}"]:checked`);
          const sample = qForm.querySelector(`[name="${n}"]`);
          let container = null;
          if(sample) container = sample.closest('.q-choices') || sample.parentElement || sample;
          if(!checked){
            if(container) container.classList.add('unanswered');
          } else {
            if(container) container.classList.remove('unanswered');
            answered++;
          }
        });

        const percent = totalQuestions ? Math.round((answered/totalQuestions)*100) : 0;
        // update progress bar (wizard progress bar used as overall completion indicator)
        const progBar = document.getElementById('qProgressBar');
        if(progBar) progBar.style.width = percent + '%';
        // update qSummary to show progress numbers
        if(qSummary){
          qSummary.innerHTML = `<div class="small">Réponses: ${answered} / ${totalQuestions} (${percent}%)</div>`;
          qSummary.hidden = false;
        }
        // expose unanswered count in sheet if visible
        if(qSheetContent){
          const unansweredList = names.filter(n=> !qForm.querySelector(`[name="${n}"]:checked`));
          const ulUn = unansweredList.length ? ('<p class="text-danger small">Questions non répondues: ' + unansweredList.length + '</p>') : '';
          qSheetContent.innerHTML = ulUn + '<ul>' + Object.keys(details).map(k=>`<li>${k}: ${details[k]}</li>`).join('') + `</ul><p><strong>Total:</strong> ${total} /64</p><p>${interp}</p>`;
        }
      }catch(e){ console.warn('live progress update failed', e); }
      return {total, details, voxYes, interp};
    }

  if(qCalc) qCalc.addEventListener('click', function(){ compute(); });

  if(qReset) qReset.addEventListener('click', function(){ qForm.reset(); if(qResult) qResult.innerHTML=''; if(qSheet) qSheet.style.display='none'; emitAnalytics('questionnaire_reset', {}); });

  if(qSave) qSave.addEventListener('click', function(){
      // serialize answers
      const data = {};
      new FormData(qForm).forEach((v,k)=>{ data[k]=v; });
      try{ localStorage.setItem('q_answers', JSON.stringify(data)); alert('Réponses sauvegardées localement.'); emitAnalytics('questionnaire_save', {}); }
      catch(e){ alert('Impossible de sauvegarder localement'); }
    });

  // alternate bottom buttons mapping
  const qSaveAlt = document.querySelectorAll('.qSaveAlt'); if(qSaveAlt && qSaveAlt.length){ qSaveAlt.forEach(b=> b.addEventListener('click', ()=> { if(qSave) qSave.click(); })); }
  const qResetAlt = document.querySelectorAll('.qResetAlt'); if(qResetAlt && qResetAlt.length){ qResetAlt.forEach(b=> b.addEventListener('click', ()=> { if(qReset) qReset.click(); })); }
  const qPrintAlt = document.querySelectorAll('.qPrintAlt'); if(qPrintAlt && qPrintAlt.length){ qPrintAlt.forEach(b=> b.addEventListener('click', ()=> { if(qPrint) qPrint.click(); })); }

    // load saved if present
    try{
      const saved = localStorage.getItem('q_answers'); if(saved){ const obj = JSON.parse(saved); Object.keys(obj).forEach(k=>{ const el = qForm.elements[k]; if(el){ if(el.type === 'radio'){ const to = qForm.querySelector('[name="'+k+'"][value="'+obj[k]+'"]'); if(to) to.checked = true; } else if(el.type === 'checkbox'){ el.checked = obj[k]; } else el.value = obj[k]; } }); }
    }catch(e){}

  if(qPrint) qPrint.addEventListener('click', function(){ window.print(); });

  });
