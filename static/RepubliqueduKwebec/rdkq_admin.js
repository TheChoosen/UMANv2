// JS minimal pour l'admin RDKQ (prototype CRUD, sans backend réel)
document.addEventListener('DOMContentLoaded', function () {
  const tabs = ['membres', 'cercles', 'roles', 'decisions', 'adhesions', 'publications', 'participations'];
  // Affiche le bon CRUD et masque les autres
  function showTab(tab) {
    tabs.forEach(t => {
      const el = document.getElementById('crud-' + t);
      if (el) {
        if (t === tab) {
          el.classList.remove('d-none');
        } else {
          el.classList.add('d-none');
        }
      }
    });
    // Titre dynamique
    const h2 = document.querySelector('#admin-content h2');
    if (h2) {
      h2.textContent = 'Gestion des ' + tab;
    }
    // Init spécifique membres
    if (tab === 'membres') {
      initCrudMembres();
    } else if (tab === 'cercles') {
      initCrudCercles();
    } else if (tab === 'roles') {
      initCrudRoles();
    } else if (tab === 'decisions') {
      initCrudDecisions();
    } else if (tab === 'adhesions') {
      initCrudAdhesions();
    } else if (tab === 'publications') {
      initCrudPublications();
    } else if (tab === 'participations') {
      initCrudParticipations();
    }
  }

  tabs.forEach(tab => {
    document.getElementById('tab-' + tab)?.addEventListener('click', function () {
      document.querySelectorAll('.list-group-item').forEach(li => li.classList.remove('active'));
      this.classList.add('active');
      showTab(tab);
    });
  });
  // Affiche le tab actif au chargement
  let activeTab = tabs.find(tab => document.getElementById('tab-' + tab)?.classList.contains('active')) || 'membres';
  showTab(activeTab);
});

function initCrudMembres() {
  const tableBody = document.querySelector('#table-membres tbody');
  const formContainer = document.getElementById('form-membre-container');
  const form = document.getElementById('form-membre');
  const btnAdd = document.getElementById('btn-add-membre');
  const btnCancel = document.getElementById('btn-cancel-membre');
  const resultDiv = document.getElementById('form-membre-result');

  if (!tableBody || !form) return;

  // Charger les cercles et rôles disponibles
  loadCerclesAndRoles();
  
  // Charger les membres (AJAX)
  function loadMembres() {
    fetch('/rdkq/api/membres').then(r => r.json()).then(data => {
      tableBody.innerHTML = '';
      if (data && data.length) {
        data.forEach(m => {
          const cercles = m.cercles ? m.cercles.split(',').slice(0, 2).join(', ') + (m.cercles.split(',').length > 2 ? '...' : '') : '';
          const roles = m.roles ? m.roles.split(',').slice(0, 2).join(', ') + (m.roles.split(',').length > 2 ? '...' : '') : '';
          
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${m.prenom || ''}</td>
            <td>${m.nom || ''}</td>
            <td>${m.email || ''}</td>
            <td>${m.organisation || ''}</td>
            <td><small class="text-muted">${cercles}</small></td>
            <td><small class="text-muted">${roles}</small></td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-1" data-id="${m.id}" data-action="edit">Éditer</button>
              <button class="btn btn-sm btn-outline-info me-1" data-id="${m.id}" data-action="historique">Historique</button>
              <button class="btn btn-sm btn-outline-danger" data-id="${m.id}" data-action="delete">Supprimer</button>
            </td>
          `;
          tableBody.appendChild(tr);
        });
      } else {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">Aucun membre</td></tr>';
      }
    }).catch(() => {
      tableBody.innerHTML = '<tr><td colspan="7" class="text-center">Erreur de chargement</td></tr>';
    });
  }

  function loadCerclesAndRoles() {
    // Charger les cercles disponibles
    fetch('/rdkq/api/cercles').then(r => r.json()).then(data => {
      const container = document.getElementById('membre-cercles-container');
      if (container && data && data.length) {
        container.innerHTML = data.map(cercle => `
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" name="cercles[]" value="${cercle.id}" id="cercle-${cercle.id}">
            <label class="form-check-label" for="cercle-${cercle.id}">
              ${cercle.nom}
            </label>
          </div>
        `).join('');
      }
    }).catch(error => console.error('Erreur chargement cercles:', error));

    // Charger les rôles disponibles
    fetch('/rdkq/api/roles').then(r => r.json()).then(data => {
      const container = document.getElementById('membre-roles-container');
      if (container && data && data.length) {
        container.innerHTML = data.map(role => `
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" name="roles[]" value="${role.id}" id="role-${role.id}">
            <label class="form-check-label" for="role-${role.id}">
              ${role.nom} <small class="text-muted">(Niv.${role.niveau || ''})</small>
            </label>
          </div>
        `).join('');
      }
    }).catch(error => console.error('Erreur chargement rôles:', error));
  }

  // Afficher le formulaire d'ajout/édition
  btnAdd?.addEventListener('click', function () {
    form.reset();
    document.getElementById('membre-id').value = '';
    formContainer.classList.remove('d-none');
    resultDiv.innerHTML = '';
  });

  btnCancel?.addEventListener('click', function () {
    formContainer.classList.add('d-none');
    resultDiv.innerHTML = '';
  });

  // Soumission du formulaire (AJAX)
  form?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    
    // Vérifier les mots de passe
    const password = formData.get('password');
    const passwordConfirm = formData.get('password_confirm');
    
    if (password && password !== passwordConfirm) {
      resultDiv.innerHTML = '<div class="alert alert-danger">Les mots de passe ne correspondent pas</div>';
      return;
    }
    
    // Ajouter les cercles sélectionnés
    const cerclesChecked = document.querySelectorAll('input[name="cercles[]"]:checked');
    const cercles = Array.from(cerclesChecked).map(cb => cb.value);
    formData.append('cercles', cercles.join(','));
    
    // Ajouter les rôles sélectionnés
    const rolesChecked = document.querySelectorAll('input[name="roles[]"]:checked');
    const roles = Array.from(rolesChecked).map(cb => cb.value);
    formData.append('roles', roles.join(','));
    
    const id = formData.get('id');
    const url = id ? `/rdkq/api/membres/${id}` : '/rdkq/api/membres';
    const method = id ? 'PUT' : 'POST';
    fetch(url, {
      method: method,
      body: formData
    })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          resultDiv.innerHTML = '<div class="alert alert-success">Enregistré !</div>';
          formContainer.classList.add('d-none');
          loadMembres();
        } else {
          resultDiv.innerHTML = `<div class="alert alert-danger">${data.error || 'Erreur'}</div>`;
        }
      });
  });

  // Actions éditer/supprimer/historique
  tableBody?.addEventListener('click', function (e) {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const id = btn.getAttribute('data-id');
    const action = btn.getAttribute('data-action');
    if (action === 'edit') {
      fetch(`/rdkq/api/membres/${id}`).then(r => r.json()).then(m => {
        document.getElementById('membre-id').value = m.id;
        document.getElementById('membre-prenom').value = m.prenom || '';
        document.getElementById('membre-nom').value = m.nom || '';
        document.getElementById('membre-email').value = m.email || '';
        document.getElementById('membre-organisation').value = m.organisation || '';
        document.getElementById('membre-telephone').value = m.telephone || '';
        
        // Cocher les cercles du membre
        document.querySelectorAll('input[name="cercles[]"]').forEach(cb => {
          cb.checked = m.cercles && m.cercles.split(',').includes(cb.value);
        });
        
        // Cocher les rôles du membre
        document.querySelectorAll('input[name="roles[]"]').forEach(cb => {
          cb.checked = m.roles && m.roles.split(',').includes(cb.value);
        });
        
        formContainer.classList.remove('d-none');
        resultDiv.innerHTML = '';
      });
    } else if (action === 'historique') {
      showMembreHistorique(id);
    } else if (action === 'delete') {
      if (confirm('Supprimer ce membre ?')) {
        fetch(`/rdkq/api/membres/${id}`, { method: 'DELETE' })
          .then(r => r.json())
          .then(data => {
            if (data.ok) loadMembres();
          });
      }
    }
  });

  // Initial load
  loadMembres();
}

// ========== CRUD CERCLES ==========
function initCrudCercles() {
  const tableBody = document.querySelector('#table-cercles tbody');
  const formContainer = document.getElementById('form-cercle-container');
  const form = document.getElementById('form-cercle');
  const btnAdd = document.getElementById('btn-add-cercle');
  const btnCancel = document.getElementById('btn-cancel-cercle');
  const resultDiv = document.getElementById('form-cercle-result');

  if (!tableBody || !form) return;

  function loadCercles() {
    fetch('/rdkq/api/cercles').then(r => r.json()).then(data => {
      tableBody.innerHTML = '';
      if (data && data.length) {
        data.forEach(c => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${c.nom || ''}</td>
            <td>${c.description || ''}</td>
            <td><span class="badge bg-${c.statut === 'actif' ? 'success' : 'secondary'}">${c.statut || ''}</span></td>
            <td>${c.nb_membres || 0}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-1" data-id="${c.id}" data-action="edit">Éditer</button>
              <button class="btn btn-sm btn-outline-danger" data-id="${c.id}" data-action="delete">Supprimer</button>
            </td>
          `;
          tableBody.appendChild(tr);
        });
      } else {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Aucun cercle</td></tr>';
      }
    }).catch(() => {
      tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Erreur de chargement</td></tr>';
    });
  }

  btnAdd?.addEventListener('click', function () {
    form.reset();
    document.getElementById('cercle-id').value = '';
    formContainer.classList.remove('d-none');
    resultDiv.innerHTML = '';
  });

  btnCancel?.addEventListener('click', function () {
    formContainer.classList.add('d-none');
    resultDiv.innerHTML = '';
  });

  form?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    const id = formData.get('id');
    const url = id ? `/rdkq/api/cercles/${id}` : '/rdkq/api/cercles';
    const method = id ? 'PUT' : 'POST';
    fetch(url, { method: method, body: formData })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          resultDiv.innerHTML = '<div class="alert alert-success">Enregistré !</div>';
          formContainer.classList.add('d-none');
          loadCercles();
        } else {
          resultDiv.innerHTML = `<div class="alert alert-danger">${data.error || 'Erreur'}</div>`;
        }
      });
  });

  tableBody?.addEventListener('click', function (e) {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const id = btn.getAttribute('data-id');
    const action = btn.getAttribute('data-action');
    if (action === 'edit') {
      fetch(`/rdkq/api/cercles/${id}`).then(r => r.json()).then(c => {
        document.getElementById('cercle-id').value = c.id;
        document.getElementById('cercle-nom').value = c.nom || '';
        document.getElementById('cercle-description').value = c.description || '';
        document.getElementById('cercle-statut').value = c.statut || 'actif';
        formContainer.classList.remove('d-none');
        resultDiv.innerHTML = '';
      });
    } else if (action === 'delete') {
      if (confirm('Supprimer ce cercle ?')) {
        fetch(`/rdkq/api/cercles/${id}`, { method: 'DELETE' })
          .then(r => r.json())
          .then(data => { if (data.ok) loadCercles(); });
      }
    }
  });

  loadCercles();
}

// ========== CRUD ROLES ==========
function initCrudRoles() {
  const tableBody = document.querySelector('#table-roles tbody');
  const formContainer = document.getElementById('form-role-container');
  const form = document.getElementById('form-role');
  const btnAdd = document.getElementById('btn-add-role');
  const btnCancel = document.getElementById('btn-cancel-role');
  const resultDiv = document.getElementById('form-role-result');

  if (!tableBody || !form) return;

  function loadRoles() {
    fetch('/rdkq/api/roles').then(r => r.json()).then(data => {
      tableBody.innerHTML = '';
      if (data && data.length) {
        data.forEach(r => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${r.nom || ''}</td>
            <td>${r.permissions || ''}</td>
            <td><span class="badge bg-info">Niveau ${r.niveau || 1}</span></td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-1" data-id="${r.id}" data-action="edit">Éditer</button>
              <button class="btn btn-sm btn-outline-danger" data-id="${r.id}" data-action="delete">Supprimer</button>
            </td>
          `;
          tableBody.appendChild(tr);
        });
      } else {
        tableBody.innerHTML = '<tr><td colspan="4" class="text-center">Aucun rôle</td></tr>';
      }
    }).catch(() => {
      tableBody.innerHTML = '<tr><td colspan="4" class="text-center">Erreur de chargement</td></tr>';
    });
  }

  btnAdd?.addEventListener('click', function () {
    form.reset();
    document.getElementById('role-id').value = '';
    formContainer.classList.remove('d-none');
    resultDiv.innerHTML = '';
  });

  btnCancel?.addEventListener('click', function () {
    formContainer.classList.add('d-none');
    resultDiv.innerHTML = '';
  });

  form?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    const id = formData.get('id');
    const url = id ? `/rdkq/api/roles/${id}` : '/rdkq/api/roles';
    const method = id ? 'PUT' : 'POST';
    fetch(url, { method: method, body: formData })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          resultDiv.innerHTML = '<div class="alert alert-success">Enregistré !</div>';
          formContainer.classList.add('d-none');
          loadRoles();
        } else {
          resultDiv.innerHTML = `<div class="alert alert-danger">${data.error || 'Erreur'}</div>`;
        }
      });
  });

  tableBody?.addEventListener('click', function (e) {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const id = btn.getAttribute('data-id');
    const action = btn.getAttribute('data-action');
    if (action === 'edit') {
      fetch(`/rdkq/api/roles/${id}`).then(r => r.json()).then(role => {
        document.getElementById('role-id').value = role.id;
        document.getElementById('role-nom').value = role.nom || '';
        document.getElementById('role-permissions').value = role.permissions || '';
        document.getElementById('role-niveau').value = role.niveau || 1;
        formContainer.classList.remove('d-none');
        resultDiv.innerHTML = '';
      });
    } else if (action === 'delete') {
      if (confirm('Supprimer ce rôle ?')) {
        fetch(`/rdkq/api/roles/${id}`, { method: 'DELETE' })
          .then(r => r.json())
          .then(data => { if (data.ok) loadRoles(); });
      }
    }
  });

  loadRoles();
}

// ========== CRUD DECISIONS ==========
function initCrudDecisions() {
  const tableBody = document.querySelector('#table-decisions tbody');
  const formContainer = document.getElementById('form-decision-container');
  const form = document.getElementById('form-decision');
  const btnAdd = document.getElementById('btn-add-decision');
  const btnCancel = document.getElementById('btn-cancel-decision');
  const resultDiv = document.getElementById('form-decision-result');

  if (!tableBody || !form) return;

  function loadDecisions() {
    fetch('/rdkq/api/decisions').then(r => r.json()).then(data => {
      tableBody.innerHTML = '';
      if (data && data.length) {
        data.forEach(d => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${d.titre || ''}</td>
            <td><span class="badge bg-secondary">${d.type || ''}</span></td>
            <td><span class="badge bg-${d.statut === 'adoptee' ? 'success' : d.statut === 'rejetee' ? 'danger' : 'warning'}">${d.statut || ''}</span></td>
            <td>${d.date_vote || ''}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-1" data-id="${d.id}" data-action="edit">Éditer</button>
              <button class="btn btn-sm btn-outline-danger" data-id="${d.id}" data-action="delete">Supprimer</button>
            </td>
          `;
          tableBody.appendChild(tr);
        });
      } else {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Aucune décision</td></tr>';
      }
    }).catch(() => {
      tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Erreur de chargement</td></tr>';
    });
  }

  btnAdd?.addEventListener('click', function () {
    form.reset();
    document.getElementById('decision-id').value = '';
    formContainer.classList.remove('d-none');
    resultDiv.innerHTML = '';
  });

  btnCancel?.addEventListener('click', function () {
    formContainer.classList.add('d-none');
    resultDiv.innerHTML = '';
  });

  form?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    const id = formData.get('id');
    const url = id ? `/rdkq/api/decisions/${id}` : '/rdkq/api/decisions';
    const method = id ? 'PUT' : 'POST';
    fetch(url, { method: method, body: formData })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          resultDiv.innerHTML = '<div class="alert alert-success">Enregistré !</div>';
          formContainer.classList.add('d-none');
          loadDecisions();
        } else {
          resultDiv.innerHTML = `<div class="alert alert-danger">${data.error || 'Erreur'}</div>`;
        }
      });
  });

  tableBody?.addEventListener('click', function (e) {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const id = btn.getAttribute('data-id');
    const action = btn.getAttribute('data-action');
    if (action === 'edit') {
      fetch(`/rdkq/api/decisions/${id}`).then(r => r.json()).then(decision => {
        document.getElementById('decision-id').value = decision.id;
        document.getElementById('decision-titre').value = decision.titre || '';
        document.getElementById('decision-type').value = decision.type || 'vote_simple';
        document.getElementById('decision-statut').value = decision.statut || 'en_cours';
        document.getElementById('decision-date-vote').value = decision.date_vote || '';
        document.getElementById('decision-description').value = decision.description || '';
        formContainer.classList.remove('d-none');
        resultDiv.innerHTML = '';
      });
    } else if (action === 'delete') {
      if (confirm('Supprimer cette décision ?')) {
        fetch(`/rdkq/api/decisions/${id}`, { method: 'DELETE' })
          .then(r => r.json())
          .then(data => { if (data.ok) loadDecisions(); });
      }
    }
  });

  loadDecisions();
}

// ========== CRUD ADHESIONS ==========
function initCrudAdhesions() {
  const tableBody = document.querySelector('#table-adhesions tbody');
  const formContainer = document.getElementById('form-adhesion-container');
  const form = document.getElementById('form-adhesion');
  const btnAdd = document.getElementById('btn-add-adhesion');
  const btnCancel = document.getElementById('btn-cancel-adhesion');
  const resultDiv = document.getElementById('form-adhesion-result');

  if (!tableBody || !form) return;

  function loadAdhesions() {
    fetch('/rdkq/api/adhesions').then(r => r.json()).then(data => {
      tableBody.innerHTML = '';
      if (data && data.length) {
        data.forEach(a => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${a.membre_nom || 'Membre #' + a.membre_id}</td>
            <td><span class="badge bg-info">${a.type || ''}</span></td>
            <td>${a.date_debut || ''}</td>
            <td>${a.date_fin || 'Illimitée'}</td>
            <td><span class="badge bg-${a.statut === 'active' ? 'success' : 'secondary'}">${a.statut || ''}</span></td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-1" data-id="${a.id}" data-action="edit">Éditer</button>
              <button class="btn btn-sm btn-outline-danger" data-id="${a.id}" data-action="delete">Supprimer</button>
            </td>
          `;
          tableBody.appendChild(tr);
        });
      } else {
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Aucune adhésion</td></tr>';
      }
    }).catch(() => {
      tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Erreur de chargement</td></tr>';
    });
  }

  // Charger les membres pour le select
  function loadMembresForSelect() {
    fetch('/rdkq/api/membres').then(r => r.json()).then(membres => {
      const select = document.getElementById('adhesion-membre-id');
      if (select) {
        select.innerHTML = '<option value="">Sélectionner un membre</option>';
        membres.forEach(m => {
          select.innerHTML += `<option value="${m.id}">${m.prenom} ${m.nom}</option>`;
        });
      }
    });
  }

  btnAdd?.addEventListener('click', function () {
    form.reset();
    document.getElementById('adhesion-id').value = '';
    formContainer.classList.remove('d-none');
    resultDiv.innerHTML = '';
    loadMembresForSelect();
  });

  btnCancel?.addEventListener('click', function () {
    formContainer.classList.add('d-none');
    resultDiv.innerHTML = '';
  });

  form?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    const id = formData.get('id');
    const url = id ? `/rdkq/api/adhesions/${id}` : '/rdkq/api/adhesions';
    const method = id ? 'PUT' : 'POST';
    fetch(url, { method: method, body: formData })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          resultDiv.innerHTML = '<div class="alert alert-success">Enregistré !</div>';
          formContainer.classList.add('d-none');
          loadAdhesions();
        } else {
          resultDiv.innerHTML = `<div class="alert alert-danger">${data.error || 'Erreur'}</div>`;
        }
      });
  });

  tableBody?.addEventListener('click', function (e) {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const id = btn.getAttribute('data-id');
    const action = btn.getAttribute('data-action');
    if (action === 'edit') {
      fetch(`/rdkq/api/adhesions/${id}`).then(r => r.json()).then(adhesion => {
        document.getElementById('adhesion-id').value = adhesion.id;
        document.getElementById('adhesion-membre-id').value = adhesion.membre_id || '';
        document.getElementById('adhesion-type').value = adhesion.type || 'standard';
        document.getElementById('adhesion-date-debut').value = adhesion.date_debut || '';
        document.getElementById('adhesion-date-fin').value = adhesion.date_fin || '';
        document.getElementById('adhesion-statut').value = adhesion.statut || 'active';
        formContainer.classList.remove('d-none');
        resultDiv.innerHTML = '';
        loadMembresForSelect();
      });
    } else if (action === 'delete') {
      if (confirm('Supprimer cette adhésion ?')) {
        fetch(`/rdkq/api/adhesions/${id}`, { method: 'DELETE' })
          .then(r => r.json())
          .then(data => { if (data.ok) loadAdhesions(); });
      }
    }
  });

  loadAdhesions();
}

// ========== CRUD PUBLICATIONS ==========
function initCrudPublications() {
  const tableBody = document.querySelector('#table-publications tbody');
  const formContainer = document.getElementById('form-publication-container');
  const form = document.getElementById('form-publication');
  const btnAdd = document.getElementById('btn-add-publication');
  const btnCancel = document.getElementById('btn-cancel-publication');
  const resultDiv = document.getElementById('form-publication-result');

  if (!tableBody || !form) return;

  function loadPublications() {
    fetch('/rdkq/api/publications').then(r => r.json()).then(data => {
      tableBody.innerHTML = '';
      if (data && data.length) {
        data.forEach(p => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${p.titre || ''}</td>
            <td><span class="badge bg-secondary">${p.type || ''}</span></td>
            <td>${p.auteur || ''}</td>
            <td>${p.created_at || ''}</td>
            <td><span class="badge bg-${p.statut === 'publie' ? 'success' : p.statut === 'brouillon' ? 'warning' : 'secondary'}">${p.statut || ''}</span></td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-1" data-id="${p.id}" data-action="edit">Éditer</button>
              <button class="btn btn-sm btn-outline-danger" data-id="${p.id}" data-action="delete">Supprimer</button>
            </td>
          `;
          tableBody.appendChild(tr);
        });
      } else {
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Aucune publication</td></tr>';
      }
    }).catch(() => {
      tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Erreur de chargement</td></tr>';
    });
  }

  btnAdd?.addEventListener('click', function () {
    form.reset();
    document.getElementById('publication-id').value = '';
    formContainer.classList.remove('d-none');
    resultDiv.innerHTML = '';
  });

  btnCancel?.addEventListener('click', function () {
    formContainer.classList.add('d-none');
    resultDiv.innerHTML = '';
  });

  form?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    const id = formData.get('id');
    const url = id ? `/rdkq/api/publications/${id}` : '/rdkq/api/publications';
    const method = id ? 'PUT' : 'POST';
    fetch(url, { method: method, body: formData })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          resultDiv.innerHTML = '<div class="alert alert-success">Enregistré !</div>';
          formContainer.classList.add('d-none');
          loadPublications();
        } else {
          resultDiv.innerHTML = `<div class="alert alert-danger">${data.error || 'Erreur'}</div>`;
        }
      });
  });

  tableBody?.addEventListener('click', function (e) {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const id = btn.getAttribute('data-id');
    const action = btn.getAttribute('data-action');
    if (action === 'edit') {
      fetch(`/rdkq/api/publications/${id}`).then(r => r.json()).then(publication => {
        document.getElementById('publication-id').value = publication.id;
        document.getElementById('publication-titre').value = publication.titre || '';
        document.getElementById('publication-type').value = publication.type || 'article';
        document.getElementById('publication-auteur').value = publication.auteur || '';
        document.getElementById('publication-statut').value = publication.statut || 'brouillon';
        document.getElementById('publication-contenu').value = publication.contenu || '';
        formContainer.classList.remove('d-none');
        resultDiv.innerHTML = '';
      });
    } else if (action === 'delete') {
      if (confirm('Supprimer cette publication ?')) {
        fetch(`/rdkq/api/publications/${id}`, { method: 'DELETE' })
          .then(r => r.json())
          .then(data => { if (data.ok) loadPublications(); });
      }
    }
  });

  loadPublications();
}

// Fonction pour afficher l'historique d'un membre
function showMembreHistorique(membreId) {
  const modal = new bootstrap.Modal(document.getElementById('modal-membre-historique'));
  
  // Charger les décisions du membre
  fetch(`/rdkq/api/membres/${membreId}/decisions`)
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector('#table-decisions-historique tbody');
      if (data && data.length) {
        tbody.innerHTML = data.map(d => `
          <tr>
            <td>${d.titre || ''}</td>
            <td><span class="badge bg-info">${d.type || ''}</span></td>
            <td><span class="badge bg-${d.vote === 'pour' ? 'success' : d.vote === 'contre' ? 'danger' : 'warning'}">${d.vote || 'abstention'}</span></td>
            <td>${d.date_vote || ''}</td>
            <td><span class="badge bg-${d.statut === 'adoptee' ? 'success' : d.statut === 'rejetee' ? 'danger' : 'secondary'}">${d.statut || ''}</span></td>
          </tr>
        `).join('');
      } else {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucune décision</td></tr>';
      }
    })
    .catch(() => {
      document.querySelector('#table-decisions-historique tbody').innerHTML = '<tr><td colspan="5" class="text-center text-danger">Erreur de chargement</td></tr>';
    });

  // Charger les adhésions du membre
  fetch(`/rdkq/api/membres/${membreId}/adhesions`)
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector('#table-adhesions-historique tbody');
      if (data && data.length) {
        tbody.innerHTML = data.map(a => {
          const dateDebut = new Date(a.date_debut);
          const dateFin = a.date_fin ? new Date(a.date_fin) : null;
          const duree = dateFin ? Math.ceil((dateFin - dateDebut) / (1000 * 60 * 60 * 24)) + ' jours' : 'En cours';
          
          return `
            <tr>
              <td><span class="badge bg-primary">${a.type || ''}</span></td>
              <td>${a.date_debut || ''}</td>
              <td>${a.date_fin || 'N/A'}</td>
              <td><span class="badge bg-${a.statut === 'active' ? 'success' : a.statut === 'expiree' ? 'warning' : 'secondary'}">${a.statut || ''}</span></td>
              <td>${duree}</td>
            </tr>
          `;
        }).join('');
      } else {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucune adhésion</td></tr>';
      }
    })
    .catch(() => {
      document.querySelector('#table-adhesions-historique tbody').innerHTML = '<tr><td colspan="5" class="text-center text-danger">Erreur de chargement</td></tr>';
    });

  // Charger les publications du membre
  fetch(`/rdkq/api/membres/${membreId}/publications`)
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector('#table-publications-historique tbody');
      if (data && data.length) {
        tbody.innerHTML = data.map(p => `
          <tr>
            <td>${p.titre || ''}</td>
            <td><span class="badge bg-secondary">${p.type || ''}</span></td>
            <td>${p.created_at || ''}</td>
            <td><span class="badge bg-${p.statut === 'publie' ? 'success' : p.statut === 'brouillon' ? 'warning' : 'secondary'}">${p.statut || ''}</span></td>
            <td>${p.vues || 0}</td>
          </tr>
        `).join('');
      } else {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucune publication</td></tr>';
      }
    })
    .catch(() => {
      document.querySelector('#table-publications-historique tbody').innerHTML = '<tr><td colspan="5" class="text-center text-danger">Erreur de chargement</td></tr>';
    });

  modal.show();
}

// CRUD Participations
function initCrudParticipations() {
  fetch('/rdkq/api/participations')
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector('#table-participations tbody');
      if (data && data.length) {
        tbody.innerHTML = data.map(p => `
          <tr>
            <td>${p.titre}</td>
            <td><span class="badge bg-info">${p.type_participation}</span></td>
            <td>${p.membre_nom || 'Inconnu'}</td>
            <td>${p.lieu || '-'}</td>
            <td>${p.date_debut ? new Date(p.date_debut).toLocaleDateString() : '-'}</td>
            <td><span class="badge bg-${p.statut === 'complété' ? 'success' : p.statut === 'planifié' ? 'warning' : 'secondary'}">${p.statut}</span></td>
            <td>${p.points_gagne || 0} pts</td>
            <td>
              <button class="btn btn-sm btn-outline-danger" onclick="deleteParticipation(${p.id})">🗑️</button>
            </td>
          </tr>
        `).join('');
      } else {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">Aucune participation</td></tr>';
      }
    })
    .catch(() => {
      document.querySelector('#table-participations tbody').innerHTML = '<tr><td colspan="8" class="text-center text-danger">Erreur de chargement</td></tr>';
    });
}

function deleteParticipation(id) {
  if (confirm('Supprimer cette participation ?')) {
    fetch(`/rdkq/api/participations/${id}`, { method: 'DELETE' })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          initCrudParticipations();
        } else {
          alert('Erreur lors de la suppression');
        }
      })
      .catch(() => alert('Erreur de connexion'));
  }
}
