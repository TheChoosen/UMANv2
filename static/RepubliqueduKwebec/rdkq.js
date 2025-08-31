// JS principal pour la page République du Kwébec (index.html)
// Médiathèque, formulaire, profil public — tout AJAX/minimal

document.addEventListener('DOMContentLoaded', function () {
  // Formulaire participatif
  const form = document.getElementById('form-participer');
  if (form) {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      const res = await fetch('/rdkq/participer', { method: 'POST', body: formData });
      const data = await res.json();
      document.getElementById('resultat-form').innerHTML = data.ok ? '<span class="text-success">Merci, votre proposition a été reçue !</span>' : '<span class="text-danger">Erreur : ' + (data.error || 'Impossible d\'envoyer') + '</span>';
      if (data.ok) form.reset();
    });
  }

  // Médiathèque (chargement JSON)
  fetch('/rdkq/mediatheque').then(r => r.json()).then(list => {
    const cont = document.getElementById('mediatheque-list');
    if (!cont) return;
    cont.innerHTML = '';
    list.forEach(media => {
      const col = document.createElement('div');
      col.className = 'col-md-4 mb-3';
      col.innerHTML = `<div class="card h-100"><img src="${media.img}" class="card-img-top" alt="${media.title}"><div class="card-body"><h5 class="card-title">${media.title}</h5><p class="card-text">${media.desc}</p><button class="btn btn-outline-primary btn-sm" data-id="${media.id}">Détail</button></div></div>`;
      cont.appendChild(col);
      col.querySelector('button').onclick = () => showMediaModal(media);
    });
  });

  // Modal détail médiathèque (Bootstrap 5)
  const mediaModalEl = document.getElementById('media-modal');
  const mediaModal = mediaModalEl ? new bootstrap.Modal(mediaModalEl) : null;
  window.showMediaModal = function (media) {
    if (!mediaModalEl) return;
    document.getElementById('media-modal-title').textContent = media.title || '';
    // sanitize text fields
    const img = media.img ? `<img src="${escapeHtml(media.img)}" class="img-fluid mb-2" alt="${escapeHtml(media.title)}">` : '';
    const desc = `<p>${escapeHtml(media.desc)}</p>`;
    const link = media.src ? `<a href="${escapeHtml(media.src)}" target="_blank" rel="noopener">Voir le document</a>` : '';
    document.getElementById('media-modal-body').innerHTML = img + desc + link;
    if (mediaModal) mediaModal.show();
  };

  // Recherche profil public
  document.getElementById('btn-search-profil')?.addEventListener('click', async function () {
    const nom = document.getElementById('profil-search').value.trim();
    if (!nom) return;
    const res = await fetch('/rdkq/profil?nom=' + encodeURIComponent(nom));
    const data = await res.json();
    const cont = document.getElementById('profil-result');
    if (data.ok) {
      cont.innerHTML = `<b>${data.nom}</b><br>Email: ${data.email}<br>Biens: ${data.biens?.join(', ') || 'Aucun'}<br><a href="${data.doc}" target="_blank">Documents</a>`;
    } else {
      cont.innerHTML = '<span class="text-danger">Aucun membre trouvé.</span>';
    }
  });
});
