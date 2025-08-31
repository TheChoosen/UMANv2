// Questionnaire: wizard, live updates, compute, save/reset/print
// Extracted from democratie.js to keep questionnaire behavior in its own file
 (function(){
  // combine initialization so script can be injected after DOMContentLoaded
  function initQuestionnaire(){
    console.debug('democratiequestionnaire: initQuestionnaire called');
    try{
      // Wizard: step navigation, progress and live updates (uses existing fieldsets as steps)
      const wizard = document.getElementById('qWizard');
      if(!wizard) return;
      const stepsContainer = document.getElementById('qSteps');
      if(!stepsContainer) return;
      // If the template is missing the radio inputs, add small defaults so the wizard still works.
      function fillMissingChoices(container){
        Array.from(container.querySelectorAll('fieldset[data-section]')).forEach(function(fs){
          if(fs.id === 'voxpop') return; // skip voxpop (checkboxes handled separately)
          const section = (fs.dataset.section||'').toString().trim();
          const items = Array.from(fs.querySelectorAll('ol > li'));
          items.forEach(function(li, i){
            let choices = li.querySelector('.q-choices');
            // create container if missing
            if(!choices){
              choices = document.createElement('div');
              choices.className = 'q-choices btn-group btn-group-toggle mt-2';
              choices.setAttribute('data-toggle','buttons');
              // try to place after the question text
              const questionEl = li.querySelector('.q-question');
              if(questionEl) questionEl.insertAdjacentElement('afterend', choices);
              else li.appendChild(choices);
            }
            // if there are already inputs, skip
            if(choices.querySelector('input')) return;
            // derive a sensible name: section letter (lower) + index (1-based)
            const base = section && section !== '0' ? section.toLowerCase() : 'q';
            const name = base + String(i+1);
            choices.innerHTML = '' +
              `<label class="btn-chip"><input type="radio" name="${name}" value="2"> <span>Oui</span></label>` +
              `<label class="btn-chip"><input type="radio" name="${name}" value="1"> <span>Partiel</span></label>` +
              `<label class="btn-chip"><input type="radio" name="${name}" value="0"> <span>Non/NSP</span></label>`;
          });
        });
      }

      fillMissingChoices(stepsContainer);
      const rawSteps = Array.from(stepsContainer.querySelectorAll('fieldset[data-section]'));
      if(rawSteps.length === 0) return;

      const steps = rawSteps.map((fs,i)=>{
        fs.classList.add('q-step');
        if(i!==0) fs.hidden = true; else fs.hidden = false;
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

      if(nextBtn) nextBtn.addEventListener('click', ()=>{ if(idx < steps.length-1) show(idx+1); else { updateProgress(); } });
      if(prevBtn) prevBtn.addEventListener('click', ()=>{ if(idx>0) show(idx-1); });

      function debounce(fn, wait){ let t = null; return function(){ const args = arguments; clearTimeout(t); t = setTimeout(()=> fn.apply(this, args), wait || 250); }; }

      const debouncedUpdate = debounce(function(){ updateSectionScores(); updateProgress(); const calcBtn = document.getElementById('qCalculate'); if(calcBtn){ const ev = new Event('click'); calcBtn.dispatchEvent(ev); } }, 300);

      wizard.addEventListener('change', e=>{ if(e.target.matches('input[type=radio], input[type=checkbox]')){ debouncedUpdate(); } });

      const saveBtn = document.getElementById('qSave'); if(saveBtn) saveBtn.addEventListener('click', ()=>{
        const data = {};
        wizard.querySelectorAll('input[type=radio]:checked').forEach(r=> data[r.name]=r.value);
        wizard.querySelectorAll('input[type=checkbox]:checked').forEach(c=> data[c.name]=c.value);
        try{ localStorage.setItem('q-wizard', JSON.stringify(data)); alert('Sauvegardé localement'); if(window && typeof window.emitAnalytics === 'function') window.emitAnalytics('questionnaire_save',{count:Object.keys(data).length}); }
        catch(e){ alert('Impossible de sauvegarder localement'); }
      });

      const resetBtn = document.getElementById('qReset'); if(resetBtn) resetBtn.addEventListener('click', ()=>{ wizard.querySelectorAll('input[type=radio], input[type=checkbox]').forEach(i=> i.checked=false); updateSectionScores(); updateProgress(); });
      const printBtn = document.getElementById('qPrint'); if(printBtn) printBtn.addEventListener('click', ()=> window.print());

      // init wizard view
      show(0); updateProgress();
    }catch(err){ console.error('questionnaire wizard init failed', err); }

    // Questionnaire logic: scoring, interpretation, save/load
    try{
      const qForm = document.getElementById('qForm') || document.getElementById('qWizard');
      const qCalc = document.getElementById('qCalculate');
      const qReset = document.getElementById('qReset');
      const qSave = document.getElementById('qSave');
      const qResult = document.getElementById('qResult') || null;
      const qSheet = document.getElementById('qSheet');
      const qSheetContent = document.getElementById('qSheetContent');
      const qPrint = document.getElementById('qPrint');
      const qSummary = document.getElementById('qSummary');

      function shouldAnimate(){
        try{ const o = sessionStorage.getItem('motionOverride'); if(o === 'on') return true; if(o === 'off') return false; }catch(e){}
        try{ return !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }catch(e){ return true; }
      }

      function animateNumber(el, to, opts){
        try{
          if(!shouldAnimate()){ el.textContent = to; return; }
          const duration = (opts && opts.duration) || 600;
          const start = Number(el.textContent.replace(/[^0-9\-]/g,'')) || 0;
          if(start === to){ el.textContent = to; return; }
          el.setAttribute('aria-live','polite');
          const startTime = performance.now();
          function step(now){
            const t = Math.min(1, (now - startTime) / duration);
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

      try{
        const motionToggle = document.getElementById('motionToggle');
        if(motionToggle){
          const val = sessionStorage.getItem('motionOverride');
          if(val === 'on') motionToggle.checked = true;
          else if(val === 'off') motionToggle.checked = false;
          else { try{ motionToggle.checked = !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }catch(e){ motionToggle.checked = true; } }
          motionToggle.addEventListener('change', function(){ try{ sessionStorage.setItem('motionOverride', motionToggle.checked ? 'on' : 'off'); }catch(e){} });
        }
      }catch(e){}

      function compute(){
        const sections = ['a','b','c','d','e','f','g','h'];
        let total = 0; const details = {};
        sections.forEach(s=>{
          const nodes = Array.from(qForm.querySelectorAll('[name^="'+s+'"]'));
          const secSum = nodes.reduce((acc, el)=> acc + (parseInt(el.value || 0) || 0), 0);
          details[s.toUpperCase()] = secSum;
          total += secSum;
        });

        const voxChecks = Array.from(qForm.querySelectorAll('#voxpop input[type="checkbox"]'));
        const voxYes = voxChecks.filter(c=>c.checked).length;

        let interp = '';
        if(total <= 16) interp = 'Souveraineté déléguée sans contrôle réel — régime essentiellement représentatif.';
        else if(total <= 32) interp = 'Mécanismes limités — la souveraineté populaire n’est pas la règle.';
        else if(total <= 48) interp = 'Transitionnelle — plusieurs leviers en place, cohérence incomplète.';
        else interp = 'Proche d’une démocratie au sens strict — souveraineté exercée, contrôles effectifs.';

        if(qResult) qResult.innerHTML = `<strong>Total : ${total} /64</strong><br>${interp}<br>VoxPop Oui: ${voxYes} /10`;
        if(qSheetContent) qSheetContent.innerHTML = '<ul>' + Object.keys(details).map(k=>`<li>${k}: ${details[k]}</li>`).join('') + `</ul><p><strong>Total:</strong> ${total} /64</p><p>${interp}</p>`;
        if(qSheet) qSheet.style.display = 'block';

        const gaugeEl = document.getElementById('qGaugeVal');
        if(gaugeEl) animateNumber(gaugeEl, total, {duration: 600});

        try{ if(window && typeof window.emitAnalytics === 'function') window.emitAnalytics('questionnaire_calculate', {total: total, details: details}); }catch(e){}

        try{
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
            if(!checked){ if(container) container.classList.add('unanswered'); } else { if(container) container.classList.remove('unanswered'); answered++; }
          });

          const percent = totalQuestions ? Math.round((answered/totalQuestions)*100) : 0;
          const progBar = document.getElementById('qProgressBar'); if(progBar) progBar.style.width = percent + '%';
          if(qSummary){ qSummary.innerHTML = `<div class="small">Réponses: ${answered} / ${totalQuestions} (${percent}%)</div>`; qSummary.hidden = false; }
          if(qSheetContent){ const unansweredList = names.filter(n=> !qForm.querySelector(`[name="${n}"]:checked`)); const ulUn = unansweredList.length ? ('<p class="text-danger small">Questions non répondues: ' + unansweredList.length + '</p>') : ''; qSheetContent.innerHTML = ulUn + '<ul>' + Object.keys(details).map(k=>`<li>${k}: ${details[k]}</li>`).join('') + `</ul><p><strong>Total:</strong> ${total} /64</p><p>${interp}</p>`; }
        }catch(e){ console.warn('live progress update failed', e); }
        return {total, details, voxYes, interp};
      }

      if(qCalc) qCalc.addEventListener('click', function(){ compute(); });

      if(qReset) qReset.addEventListener('click', function(){ qForm.reset(); if(qResult) qResult.innerHTML=''; if(qSheet) qSheet.style.display='none'; try{ if(window && typeof window.emitAnalytics === 'function') window.emitAnalytics('questionnaire_reset', {}); }catch(e){} });

      if(qSave) qSave.addEventListener('click', function(){
        const data = {};
        new FormData(qForm).forEach((v,k)=>{ data[k]=v; });
        try{ localStorage.setItem('q_answers', JSON.stringify(data)); alert('Réponses sauvegardées localement.'); try{ if(window && typeof window.emitAnalytics === 'function') window.emitAnalytics('questionnaire_save', {}); }catch(e){} }
        catch(e){ alert('Impossible de sauvegarder localement'); }
      });

      const qSaveAlt = document.querySelectorAll('.qSaveAlt'); if(qSaveAlt && qSaveAlt.length){ qSaveAlt.forEach(b=> b.addEventListener('click', ()=> { if(qSave) qSave.click(); })); }
      const qResetAlt = document.querySelectorAll('.qResetAlt'); if(qResetAlt && qResetAlt.length){ qResetAlt.forEach(b=> b.addEventListener('click', ()=> { if(qReset) qReset.click(); })); }
      const qPrintAlt = document.querySelectorAll('.qPrintAlt'); if(qPrintAlt && qPrintAlt.length){ qPrintAlt.forEach(b=> b.addEventListener('click', ()=> { if(qPrint) qPrint.click(); })); }

      try{ const saved = localStorage.getItem('q_answers'); if(saved){ const obj = JSON.parse(saved); Object.keys(obj).forEach(k=>{ const el = qForm.elements[k]; if(el){ if(el.type === 'radio'){ const to = qForm.querySelector('[name="'+k+'"][value="'+obj[k]+'"]'); if(to) to.checked = true; } else if(el.type === 'checkbox'){ el.checked = obj[k]; } else el.value = obj[k]; } }); } }catch(e){}

      if(qPrint) qPrint.addEventListener('click', function(){ window.print(); });
    }catch(e){ console.error('questionnaire logic init failed', e); }
  }

  // expose for debugging: call `window.__qInit()` from the console to re-run init
  try{ window.__qInit = initQuestionnaire; }catch(e){}
  if(document.readyState !== 'loading') initQuestionnaire(); else document.addEventListener('DOMContentLoaded', initQuestionnaire);
})();
