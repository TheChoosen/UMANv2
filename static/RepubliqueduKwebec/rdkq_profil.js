// Gestion du profil membre RDKQ
let currentMember = null;

document.addEventListener('DOMContentLoaded', function () {
  // Vérifier si déjà connecté
  checkSession();
  
  // Gestionnaires d'événements
  const loginForm = document.getElementById('form-login');
  const logoutBtn = document.getElementById('btn-logout');
  
  if (loginForm) loginForm.addEventListener('submit', handleLogin);
  if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);
  
  // Navigation du profil
  document.querySelectorAll('[data-section]').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const section = this.getAttribute('data-section');
      showSection(section);
      
      // Mettre à jour la navigation active
      document.querySelectorAll('[data-section]').forEach(l => l.classList.remove('active'));
      this.classList.add('active');
    });
  });
  
  // Formulaires
  const pubForm = document.getElementById('form-publication');
  const settingsForm = document.getElementById('form-settings');
  const newPubBtn = document.getElementById('btn-new-publication');
  const cancelPubBtn = document.getElementById('btn-cancel-publication');
  const submitVoteBtn = document.getElementById('btn-submit-vote');
  const porteeSelect = document.getElementById('pub-portee');
  const cercleSelect = document.getElementById('pub-cercle');
  
  if (pubForm) pubForm.addEventListener('submit', handlePublicationSubmit);
  if (settingsForm) settingsForm.addEventListener('submit', handleSettingsSubmit);
  if (newPubBtn) newPubBtn.addEventListener('click', showNewPublicationForm);
  if (cancelPubBtn) cancelPubBtn.addEventListener('click', hidePublicationForm);
  if (submitVoteBtn) submitVoteBtn.addEventListener('click', handleVoteSubmit);
  
  // Gestionnaire pour la portée des publications
  if (porteeSelect) {
    porteeSelect.addEventListener('change', function() {
      if (this.value === 'cercle') {
        cercleSelect.disabled = false;
        if (cercleSelect.options.length <= 1) {
          loadMyCircles();
        }
      } else {
        cercleSelect.disabled = true;
        cercleSelect.value = '';
      }
    });
  }
});

// Vérifier la session existante
function checkSession() {
  fetch('/rdkq/api/session')
    .then(r => r.json())
    .then(data => {
      if (data.success && data.member) {
        currentMember = data.member;
        showMemberArea();
        loadDashboard();
      } else {
        showLoginForm();
      }
    })
    .catch(() => showLoginForm());
}

// Connexion
function handleLogin(e) {
  e.preventDefault();
  const formData = new FormData(e.target);
  
  fetch('/rdkq/api/login', {
    method: 'POST',
    body: formData
  })
  .then(r => r.json())
  .then(data => {
    const resultDiv = document.getElementById('login-result');
    if (data.success) {
      currentMember = data.member;
      resultDiv.innerHTML = '<div class="alert alert-success">Connexion réussie !</div>';
      setTimeout(() => {
        showMemberArea();
        loadDashboard();
      }, 1000);
    } else {
      resultDiv.innerHTML = `<div class="alert alert-danger">${data.error || 'Erreur de connexion'}</div>`;
    }
  })
  .catch(error => {
    document.getElementById('login-result').innerHTML = '<div class="alert alert-danger">Erreur réseau</div>';
  });
}

// Déconnexion
function handleLogout() {
  fetch('/rdkq/api/logout', { method: 'POST' })
    .then(() => {
      currentMember = null;
      showLoginForm();
    });
}

// Afficher le formulaire de connexion
function showLoginForm() {
  const loginForm = document.getElementById('login-form');
  const memberArea = document.getElementById('member-area');
  if (loginForm) loginForm.classList.remove('d-none');
  if (memberArea) memberArea.classList.add('d-none');
}

// Afficher l'espace membre
function showMemberArea() {
  const loginForm = document.getElementById('login-form');
  const memberArea = document.getElementById('member-area');
  const memberName = document.getElementById('member-name');
  
  if (loginForm) loginForm.classList.add('d-none');
  if (memberArea) memberArea.classList.remove('d-none');
  if (memberName) memberName.textContent = `${currentMember.prenom} ${currentMember.nom}`;
}

// Navigation entre sections
function showSection(sectionName) {
  document.querySelectorAll('.profile-section').forEach(section => {
    section.classList.add('d-none');
  });
  const targetSection = document.getElementById(`section-${sectionName}`);
  if (targetSection) targetSection.classList.remove('d-none');
  
  // Charger les données spécifiques à la section
  switch(sectionName) {
    case 'dashboard':
      loadDashboard();
      break;
    case 'historique':
      loadHistorique();
      break;
    case 'publications':
      loadPublications();
      break;
    case 'decisions':
      loadDecisionsToVote();
      break;
    case 'settings':
      loadSettings();
      break;
  }
}

// Charger les cercles de l'utilisateur
function loadMyCircles() {
  if (!currentMember) return;
  
  fetch(`/rdkq/api/membres/${currentMember.id}/cercles`)
    .then(r => r.json())
    .then(data => {
      const cercleSelect = document.getElementById('pub-cercle');
      if (cercleSelect) {
        cercleSelect.innerHTML = '<option value="">-- sélectionner un cercle --</option>';
        if (data && data.length) {
          data.forEach(cercle => {
            const option = document.createElement('option');
            option.value = cercle.id;
            option.textContent = cercle.nom;
            cercleSelect.appendChild(option);
          });
        }
      }
    })
    .catch(err => console.error('Erreur chargement cercles:', err));
}

// Charger le tableau de bord
function loadDashboard() {
  if (!currentMember) return;
  
  // Charger les statistiques
  fetch(`/rdkq/api/membres/${currentMember.id}/stats`)
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        const statsElements = {
          'stats-cercles': data.stats.cercles || 0,
          'stats-publications': data.stats.publications || 0,
          'stats-decisions': data.stats.decisions || 0,
          'stats-adhesions': data.stats.adhesions || 0
        };
        
        Object.entries(statsElements).forEach(([id, value]) => {
          const el = document.getElementById(id);
          if (el) el.textContent = value;
        });
      }
    });
    
  // Charger les cercles
  fetch(`/rdkq/api/membres/${currentMember.id}/cercles`)
    .then(r => r.json())
    .then(data => {
      const container = document.getElementById('dashboard-cercles');
      if (container) {
        if (data && data.length) {
          container.innerHTML = data.map(cercle => 
            `<div class="list-group-item">
              <i class="fas fa-users me-2"></i>${cercle.nom}
              <small class="text-muted d-block">${cercle.description || ''}</small>
            </div>`
          ).join('');
        } else {
          container.innerHTML = '<div class="text-muted">Aucun cercle</div>';
        }
      }
    });
    
  // Charger les rôles
  fetch(`/rdkq/api/membres/${currentMember.id}/roles`)
    .then(r => r.json())
    .then(data => {
      const container = document.getElementById('dashboard-roles');
      if (container) {
        if (data && data.length) {
          container.innerHTML = data.map(role => 
            `<div class="list-group-item">
              <i class="fas fa-shield-alt me-2"></i>${role.nom}
              <span class="badge bg-primary ms-2">Niv.${role.niveau}</span>
            </div>`
          ).join('');
        } else {
          container.innerHTML = '<div class="text-muted">Aucun rôle</div>';
        }
      }
    });
}

// Charger l'historique complet
function loadHistorique() {
  if (!currentMember) return;
  
  // Décisions
  fetch(`/rdkq/api/membres/${currentMember.id}/decisions`)
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector('#table-hist-decisions tbody');
      if (tbody) {
        if (data && data.length) {
          tbody.innerHTML = data.map(d => `
            <tr>
              <td>${d.titre}</td>
              <td><span class="badge bg-info">${d.type}</span></td>
              <td><span class="badge bg-${d.vote === 'pour' ? 'success' : d.vote === 'contre' ? 'danger' : 'warning'}">${d.vote}</span></td>
              <td>${d.date_vote || ''}</td>
              <td><span class="badge bg-${d.statut === 'adoptee' ? 'success' : d.statut === 'rejetee' ? 'danger' : 'secondary'}">${d.statut}</span></td>
            </tr>
          `).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucune décision</td></tr>';
        }
      }
    });
    
  // Publications
  fetch(`/rdkq/api/membres/${currentMember.id}/publications`)
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector('#table-hist-publications tbody');
      if (tbody) {
        if (data && data.length) {
          tbody.innerHTML = data.map(p => `
            <tr>
              <td>${p.titre}</td>
              <td><span class="badge bg-secondary">${p.type}</span></td>
              <td>${p.created_at || ''}</td>
              <td><span class="badge bg-${p.statut === 'publie' ? 'success' : p.statut === 'brouillon' ? 'warning' : 'secondary'}">${p.statut}</span></td>
              <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editPublication(${p.id})">Modifier</button>
              </td>
            </tr>
          `).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucune publication</td></tr>';
        }
      }
    });
    
  // Adhésions
  fetch(`/rdkq/api/membres/${currentMember.id}/adhesions`)
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector('#table-hist-adhesions tbody');
      if (tbody) {
        if (data && data.length) {
          tbody.innerHTML = data.map(a => {
            const dateDebut = new Date(a.date_debut);
            const dateFin = a.date_fin ? new Date(a.date_fin) : null;
            const duree = dateFin ? Math.ceil((dateFin - dateDebut) / (1000 * 60 * 60 * 24)) + ' jours' : 'En cours';
            
            return `
              <tr>
                <td><span class="badge bg-primary">${a.type}</span></td>
                <td>${a.date_debut}</td>
                <td>${a.date_fin || 'N/A'}</td>
                <td><span class="badge bg-${a.statut === 'active' ? 'success' : a.statut === 'expiree' ? 'warning' : 'secondary'}">${a.statut}</span></td>
                <td>${duree}</td>
              </tr>
            `;
          }).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucune adhésion</td></tr>';
        }
      }
    });
}

// Charger les publications
function loadPublications() {
  if (!currentMember) return;
  
  fetch(`/rdkq/api/membres/${currentMember.id}/publications`)
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector('#table-publications tbody');
      if (tbody) {
        if (data && data.length) {
          tbody.innerHTML = data.map(p => `
            <tr>
              <td>${p.titre}</td>
              <td><span class="badge bg-secondary">${p.type}</span></td>
              <td>${p.created_at || ''}</td>
              <td><span class="badge bg-${p.statut === 'publie' ? 'success' : p.statut === 'brouillon' ? 'warning' : 'secondary'}">${p.statut}</span></td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-1" onclick="editPublication(${p.id})">Modifier</button>
                <button class="btn btn-sm btn-outline-danger" onclick="deletePublication(${p.id})">Supprimer</button>
              </td>
            </tr>
          `).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucune publication</td></tr>';
        }
      }
    });
}

// Afficher le formulaire de nouvelle publication
function showNewPublicationForm() {
  const container = document.getElementById('form-publication-container');
  const title = document.getElementById('form-publication-title');
  const form = document.getElementById('form-publication');
  const idField = document.getElementById('publication-id');
  const porteeSelect = document.getElementById('pub-portee');
  const cercleSelect = document.getElementById('pub-cercle');
  
  if (container) container.classList.remove('d-none');
  if (title) title.textContent = 'Nouvelle Publication';
  if (form) form.reset();
  if (idField) idField.value = '';
  if (porteeSelect) porteeSelect.value = 'global';
  if (cercleSelect) {
    cercleSelect.disabled = true;
    cercleSelect.value = '';
  }
}

// Masquer le formulaire de publication
function hidePublicationForm() {
  const container = document.getElementById('form-publication-container');
  const result = document.getElementById('publication-result');
  
  if (container) container.classList.add('d-none');
  if (result) result.innerHTML = '';
}

// Gérer la soumission de publication
function handlePublicationSubmit(e) {
  e.preventDefault();
  
  const resultDiv = document.getElementById('publication-result');
  if (resultDiv) resultDiv.innerHTML = '';
  
  const payload = {
    titre: document.getElementById('pub-titre').value.trim(),
    type: document.getElementById('pub-type').value,
    contenu: document.getElementById('pub-contenu').value.trim(),
    portee: document.getElementById('pub-portee').value
  };
  
  // Validation
  if (!payload.titre || !payload.contenu) {
    if (resultDiv) {
      resultDiv.innerHTML = '<div class="alert alert-danger">Veuillez remplir tous les champs obligatoires.</div>';
    }
    return;
  }
  
  // Si portée cercle, vérifier la sélection
  if (payload.portee === 'cercle') {
    const cercleId = document.getElementById('pub-cercle').value;
    if (!cercleId) {
      if (resultDiv) {
        resultDiv.innerHTML = '<div class="alert alert-danger">Veuillez sélectionner un cercle.</div>';
      }
      return;
    }
    payload.cercle_id = cercleId;
  }
  
  const id = document.getElementById('publication-id').value;
  const url = id ? `/rdkq/api/publications/${id}` : '/rdkq/api/publications';
  const method = id ? 'PUT' : 'POST';
  
  fetch(url, {
    method: method,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(data => {
    if (resultDiv) {
      if (data.ok || data.id) {
        resultDiv.innerHTML = '<div class="alert alert-success">Publication enregistrée !</div>';
        setTimeout(() => {
          hidePublicationForm();
          loadPublications();
        }, 1500);
      } else {
        resultDiv.innerHTML = `<div class="alert alert-danger">${data.message || data.error || 'Erreur'}</div>`;
      }
    }
  })
  .catch(error => {
    console.error('Erreur:', error);
    if (resultDiv) {
      resultDiv.innerHTML = '<div class="alert alert-danger">Erreur réseau.</div>';
    }
  });
}

// Charger les décisions à voter
function loadDecisionsToVote() {
  if (!currentMember) return;
  
  fetch('/rdkq/api/decisions/available')
    .then(r => r.json())
    .then(data => {
      const tbody = document.querySelector('#table-decisions-vote tbody');
      if (tbody) {
        if (data && data.length) {
          tbody.innerHTML = data.map(d => {
            // Vérifier si le membre a déjà voté
            const hasVoted = d.member_vote ? true : false;
            const voteText = hasVoted ? d.member_vote : 'Pas encore voté';
            const voteBadge = hasVoted ? 
              `<span class="badge bg-${d.member_vote === 'pour' ? 'success' : d.member_vote === 'contre' ? 'danger' : 'warning'}">${voteText}</span>` :
              `<span class="badge bg-secondary">${voteText}</span>`;
              
            return `
              <tr>
                <td>${d.titre}</td>
                <td><span class="badge bg-info">${d.type}</span></td>
                <td style="max-width: 200px;">${d.description ? d.description.substring(0, 100) + '...' : ''}</td>
                <td>${d.date_vote || ''}</td>
                <td>${voteBadge}</td>
                <td>
                  <button class="btn btn-sm btn-primary" onclick="showVoteModal(${d.id}, '${d.titre}', '${d.description || ''}', '${d.member_vote || ''}')">
                    ${hasVoted ? 'Modifier vote' : 'Voter'}
                  </button>
                </td>
              </tr>
            `;
          }).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Aucune décision en attente</td></tr>';
        }
      }
    });
}

// Afficher le modal de vote
function showVoteModal(decisionId, titre, description, currentVote) {
  const idField = document.getElementById('vote-decision-id');
  const details = document.getElementById('vote-decision-details');
  
  if (idField) idField.value = decisionId;
  if (details) {
    details.innerHTML = `
      <h5>${titre}</h5>
      <p>${description}</p>
    `;
  }
  
  // Pré-sélectionner le vote actuel si existant
  if (currentVote) {
    const voteRadio = document.getElementById(`vote-${currentVote}`);
    if (voteRadio) voteRadio.checked = true;
  } else {
    document.querySelectorAll('input[name="vote"]').forEach(input => input.checked = false);
  }
  
  const modalEl = document.getElementById('modal-vote');
  if (modalEl && window.bootstrap) {
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  }
}

// Gérer la soumission du vote
function handleVoteSubmit() {
  const form = document.getElementById('form-vote');
  if (!form) return;
  
  const formData = new FormData(form);
  formData.append('membre_id', currentMember.id);
  
  fetch('/rdkq/api/votes', {
    method: 'POST',
    body: formData
  })
  .then(r => r.json())
  .then(data => {
    if (data.ok) {
      const modalEl = document.getElementById('modal-vote');
      if (modalEl && window.bootstrap) {
        bootstrap.Modal.getInstance(modalEl).hide();
      }
      loadDecisionsToVote(); // Recharger la liste
    } else {
      alert('Erreur lors du vote: ' + (data.error || 'Erreur inconnue'));
    }
  });
}

// Charger les paramètres
function loadSettings() {
  if (!currentMember) return;
  
  const fields = {
    'settings-prenom': currentMember.prenom || '',
    'settings-nom': currentMember.nom || '',
    'settings-email': currentMember.email || '',
    'settings-telephone': currentMember.telephone || '',
    'settings-organisation': currentMember.organisation || ''
  };
  
  Object.entries(fields).forEach(([id, value]) => {
    const el = document.getElementById(id);
    if (el) el.value = value;
  });
}

// Gérer la sauvegarde des paramètres
function handleSettingsSubmit(e) {
  e.preventDefault();
  const formData = new FormData(e.target);
  
  // Vérifier les mots de passe
  const password = formData.get('password');
  const passwordConfirm = formData.get('password_confirm');
  
  if (password && password !== passwordConfirm) {
    const resultDiv = document.getElementById('settings-result');
    if (resultDiv) {
      resultDiv.innerHTML = '<div class="alert alert-danger">Les mots de passe ne correspondent pas</div>';
    }
    return;
  }
  
  fetch(`/rdkq/api/membres/${currentMember.id}/settings`, {
    method: 'PUT',
    body: formData
  })
  .then(r => r.json())
  .then(data => {
    const resultDiv = document.getElementById('settings-result');
    if (resultDiv) {
      if (data.ok) {
        resultDiv.innerHTML = '<div class="alert alert-success">Paramètres sauvegardés !</div>';
        // Mettre à jour les données du membre
        currentMember = { ...currentMember, ...data.member };
        const memberName = document.getElementById('member-name');
        if (memberName) {
          memberName.textContent = `${currentMember.prenom} ${currentMember.nom}`;
        }
      } else {
        resultDiv.innerHTML = `<div class="alert alert-danger">${data.error || 'Erreur'}</div>`;
      }
    }
  });
}

// Fonctions pour éditer/supprimer les publications
function editPublication(id) {
  fetch(`/rdkq/api/publications/${id}`)
    .then(r => r.json())
    .then(publication => {
      const fields = {
        'publication-id': publication.id,
        'pub-titre': publication.titre,
        'pub-type': publication.type,
        'pub-contenu': publication.contenu
      };
      
      Object.entries(fields).forEach(([fieldId, value]) => {
        const el = document.getElementById(fieldId);
        if (el) el.value = value;
      });
      
      const title = document.getElementById('form-publication-title');
      const container = document.getElementById('form-publication-container');
      
      if (title) title.textContent = 'Modifier Publication';
      if (container) container.classList.remove('d-none');
    });
}

function deletePublication(id) {
  if (confirm('Supprimer cette publication ?')) {
    fetch(`/rdkq/api/publications/${id}`, { method: 'DELETE' })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          loadPublications();
        }
      });
  }
}

// Initialiser les données de démonstration
function initDemoData() {
  if (!confirm('Voulez-vous initialiser des données de démonstration riches pour votre profil ?')) {
    return;
  }
  
  fetch('/rdkq/api/init-demo', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        alert('✅ Données de démonstration initialisées avec succès !');
        // Recharger le tableau de bord pour voir les nouvelles données
        loadDashboard();
        loadHistory();
        loadPublications();
      } else {
        alert('❌ Erreur: ' + (data.error || 'Échec de l\'initialisation'));
      }
    })
    .catch(error => {
      console.error('Erreur:', error);
      alert('❌ Erreur lors de l\'initialisation des données');
    });
}

// Ajouter le bouton de démonstration pour Adam Menard
function addDemoButton() {
  const dashboard = document.getElementById('dashboard-content');
  if (dashboard && !document.getElementById('demo-button')) {
    const demoButton = document.createElement('div');
    demoButton.id = 'demo-button';
    demoButton.className = 'mt-3';
    demoButton.innerHTML = `
      <div class="alert alert-info">
        <h6>🎯 Mode Démonstration</h6>
        <p class="mb-2">Initialisez un profil riche avec des données d'exemple complètes :</p>
        <ul class="mb-2">
          <li>5 cercles et 3 rôles</li>
          <li>7 publications détaillées</li>
          <li>7 décisions avec 4 votes</li>
          <li>5 adhésions historiques</li>
        </ul>
        <button class="btn btn-warning btn-sm" onclick="initDemoData()">
          Initialiser les données de démonstration
        </button>
      </div>
    `;
    dashboard.appendChild(demoButton);
  }
}

// Au chargement, vérifier si c'est Adam pour ajouter le bouton démo
setTimeout(() => {
  if (currentMember && currentMember.prenom === 'Adam' && currentMember.nom === 'Menard') {
    addDemoButton();
  }
}, 1500);
