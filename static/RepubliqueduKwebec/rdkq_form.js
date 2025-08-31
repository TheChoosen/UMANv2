// JS AJAX pour le formulaire de participation République du Kwébec

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('form-participer');
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const nom = document.getElementById('nom')?.value.trim();
      const email = document.getElementById('email')?.value.trim();
      const sujet = document.getElementById('sujet')?.value.trim();
      const message = document.getElementById('message')?.value.trim();
      const rgpd = document.getElementById('rgpd')?.checked;
      if (!nom || !email || !sujet || !message || !rgpd) {
        document.getElementById('resultat-form').innerHTML = '<div class="alert alert-danger">Veuillez remplir tous les champs requis</div>';
        return;
      }
      const formData = new FormData(form);
      fetch('/rdkq/submit-form', {
        method: 'POST',
        body: formData
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          document.getElementById('resultat-form').innerHTML = '<div class="alert alert-success">' + data.message + '</div>';
          form.reset();
        } else {
          document.getElementById('resultat-form').innerHTML = '<div class="alert alert-danger">' + (data.message || 'Erreur') + '</div>';
        }
      })
      .catch(() => {
        document.getElementById('resultat-form').innerHTML = '<div class="alert alert-danger">Erreur réseau</div>';
      });
    });
  }
});
