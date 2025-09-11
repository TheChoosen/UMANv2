/**
 * Organizations Management JavaScript
 * Gestion des fonctionnalités interactives pour l'administration des organisations
 */

// Variables globales
let selectedOrganizations = new Set();

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    initializeOrganizationsTable();
    initializeFilters();
    initializeBulkActions();
});

/**
 * Initialisation du tableau des organisations
 */
function initializeOrganizationsTable() {
    // Gestion de la sélection multiple
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', toggleSelectAll);
    }
    
    // Gestion des checkboxes individuelles
    document.querySelectorAll('.org-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleOrgSelection);
    });
    
    // Fermeture des dropdowns au clic extérieur
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.admin-action-dropdown')) {
            document.querySelectorAll('.admin-dropdown-menu').forEach(menu => {
                menu.style.display = 'none';
            });
        }
    });
}

/**
 * Initialisation des filtres
 */
function initializeFilters() {
    const searchInput = document.getElementById('search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 3 || this.value.length === 0) {
                    applyFilters();
                }
            }, 500);
        });
    }
    
    // Auto-submit pour les selects
    document.querySelectorAll('#status, #created_after').forEach(select => {
        select.addEventListener('change', applyFilters);
    });
}

/**
 * Initialisation des actions en masse
 */
function initializeBulkActions() {
    updateBulkActionsVisibility();
}

/**
 * Sélection/Désélection de toutes les organisations
 */
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('select-all');
    const orgCheckboxes = document.querySelectorAll('.org-checkbox');
    
    orgCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
        const orgId = checkbox.value;
        
        if (selectAllCheckbox.checked) {
            selectedOrganizations.add(orgId);
        } else {
            selectedOrganizations.delete(orgId);
        }
    });
    
    updateBulkActionsVisibility();
}

/**
 * Gestion de la sélection d'une organisation
 */
function handleOrgSelection(event) {
    const orgId = event.target.value;
    const selectAllCheckbox = document.getElementById('select-all');
    
    if (event.target.checked) {
        selectedOrganizations.add(orgId);
    } else {
        selectedOrganizations.delete(orgId);
        selectAllCheckbox.checked = false;
    }
    
    // Vérifier si toutes les organisations sont sélectionnées
    const totalCheckboxes = document.querySelectorAll('.org-checkbox').length;
    const checkedCheckboxes = document.querySelectorAll('.org-checkbox:checked').length;
    
    if (totalCheckboxes === checkedCheckboxes && totalCheckboxes > 0) {
        selectAllCheckbox.checked = true;
    }
    
    updateBulkActionsVisibility();
}

/**
 * Mise à jour de la visibilité des actions en masse
 */
function updateBulkActionsVisibility() {
    const bulkActions = document.getElementById('bulk-actions');
    const bulkCount = document.querySelector('.admin-bulk-count');
    
    if (selectedOrganizations.size > 0) {
        bulkActions.style.display = 'block';
        bulkCount.textContent = `${selectedOrganizations.size} organisation(s) sélectionnée(s)`;
    } else {
        bulkActions.style.display = 'none';
    }
}

/**
 * Basculer l'affichage d'un dropdown
 */
function toggleDropdown(orgId) {
    const dropdown = document.getElementById(`dropdown-${orgId}`);
    const isVisible = dropdown.style.display === 'block';
    
    // Fermer tous les autres dropdowns
    document.querySelectorAll('.admin-dropdown-menu').forEach(menu => {
        menu.style.display = 'none';
    });
    
    // Basculer le dropdown actuel
    dropdown.style.display = isVisible ? 'none' : 'block';
}

/**
 * Se connecter en tant qu'organisation
 */
function loginAsOrg(orgId) {
    if (confirm('Voulez-vous vous connecter en tant qu\'administrateur de cette organisation ?')) {
        showLoading('Connexion en cours...');
        
        fetch(`/admin/system/organizations/${orgId}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.open(data.redirect_url, '_blank');
                showNotification('Connexion réussie', 'success');
            } else {
                showNotification(data.message || 'Erreur lors de la connexion', 'error');
            }
        })
        .catch(error => {
            showNotification('Erreur lors de la connexion', 'error');
        })
        .finally(() => {
            hideLoading();
        });
    }
}

/**
 * Suspendre une organisation
 */
function suspendOrg(orgId) {
    if (confirm('Voulez-vous vraiment suspendre cette organisation ? Les utilisateurs ne pourront plus y accéder.')) {
        updateOrgStatus(orgId, 'suspended');
    }
}

/**
 * Activer une organisation
 */
function activateOrg(orgId) {
    updateOrgStatus(orgId, 'active');
}

/**
 * Mettre à jour le statut d'une organisation
 */
function updateOrgStatus(orgId, status) {
    showLoading('Mise à jour...');
    
    fetch(`/admin/system/organizations/${orgId}/status`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Organisation ${status === 'active' ? 'activée' : 'suspendue'}`, 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showNotification(data.message || 'Erreur lors de la mise à jour', 'error');
        }
    })
    .catch(error => {
        showNotification('Erreur lors de la mise à jour', 'error');
    })
    .finally(() => {
        hideLoading();
    });
}

/**
 * Supprimer une organisation
 */
function deleteOrg(orgId) {
    const orgRow = document.querySelector(`input[value="${orgId}"]`).closest('tr');
    const orgName = orgRow.querySelector('.admin-org-info strong').textContent;
    
    if (confirm(`Voulez-vous vraiment SUPPRIMER définitivement l'organisation "${orgName}" ?\n\nCette action est IRRÉVERSIBLE et supprimera :\n- Tous les utilisateurs\n- Tous les espaces participatifs\n- Toutes les données\n\nTapez "SUPPRIMER" pour confirmer.`)) {
        const confirmText = prompt('Tapez "SUPPRIMER" pour confirmer la suppression :');
        
        if (confirmText === 'SUPPRIMER') {
            showLoading('Suppression en cours...');
            
            fetch(`/admin/system/organizations/${orgId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Organisation supprimée', 'success');
                    orgRow.remove();
                    selectedOrganizations.delete(orgId);
                    updateBulkActionsVisibility();
                } else {
                    showNotification(data.message || 'Erreur lors de la suppression', 'error');
                }
            })
            .catch(error => {
                showNotification('Erreur lors de la suppression', 'error');
            })
            .finally(() => {
                hideLoading();
            });
        }
    }
}

/**
 * Exporter les données d'une organisation
 */
function exportOrgData(orgId) {
    showLoading('Préparation de l\'export...');
    
    fetch(`/admin/system/organizations/${orgId}/export`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Erreur lors de l\'export');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `organisation_${orgId}_export_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Export téléchargé', 'success');
    })
    .catch(error => {
        showNotification('Erreur lors de l\'export', 'error');
    })
    .finally(() => {
        hideLoading();
    });
}

/**
 * Exporter toutes les organisations
 */
function exportOrganizations() {
    showLoading('Préparation de l\'export...');
    
    fetch('/admin/system/organizations/export', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Erreur lors de l\'export');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `organisations_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Export téléchargé', 'success');
    })
    .catch(error => {
        showNotification('Erreur lors de l\'export', 'error');
    })
    .finally(() => {
        hideLoading();
    });
}

/**
 * Actions en masse
 */
function bulkAction(action) {
    const orgIds = Array.from(selectedOrganizations);
    
    if (orgIds.length === 0) {
        showNotification('Aucune organisation sélectionnée', 'warning');
        return;
    }
    
    let confirmMessage = '';
    let actionText = '';
    
    switch (action) {
        case 'activate':
            confirmMessage = `Activer ${orgIds.length} organisation(s) ?`;
            actionText = 'Activation';
            break;
        case 'suspend':
            confirmMessage = `Suspendre ${orgIds.length} organisation(s) ?`;
            actionText = 'Suspension';
            break;
        case 'export':
            confirmMessage = `Exporter les données de ${orgIds.length} organisation(s) ?`;
            actionText = 'Export';
            break;
        case 'delete':
            confirmMessage = `SUPPRIMER définitivement ${orgIds.length} organisation(s) ?\n\nCette action est IRRÉVERSIBLE !`;
            actionText = 'Suppression';
            break;
    }
    
    if (confirm(confirmMessage)) {
        if (action === 'delete') {
            const confirmText = prompt('Tapez "SUPPRIMER" pour confirmer :');
            if (confirmText !== 'SUPPRIMER') {
                return;
            }
        }
        
        showLoading(`${actionText} en cours...`);
        
        fetch(`/admin/system/organizations/bulk/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ organization_ids: orgIds })
        })
        .then(response => {
            if (action === 'export' && response.ok) {
                return response.blob();
            }
            return response.json();
        })
        .then(data => {
            if (action === 'export' && data instanceof Blob) {
                const url = window.URL.createObjectURL(data);
                const a = document.createElement('a');
                a.href = url;
                a.download = `bulk_organizations_export_${new Date().toISOString().split('T')[0]}.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                showNotification('Export téléchargé', 'success');
            } else if (data.success) {
                showNotification(data.message || `${actionText} réussie`, 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showNotification(data.message || `Erreur lors de ${actionText.toLowerCase()}`, 'error');
            }
        })
        .catch(error => {
            showNotification(`Erreur lors de ${actionText.toLowerCase()}`, 'error');
        })
        .finally(() => {
            hideLoading();
        });
    }
}

/**
 * Appliquer les filtres
 */
function applyFilters() {
    document.querySelector('.admin-filters-form').submit();
}

/**
 * Afficher un indicateur de chargement
 */
function showLoading(message = 'Chargement...') {
    // Créer ou mettre à jour l'overlay de chargement
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'admin-loading-overlay';
        overlay.innerHTML = `
            <div class="admin-loading-content">
                <i class="fas fa-spinner fa-spin"></i>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('span').textContent = message;
    }
    
    overlay.style.display = 'flex';
}

/**
 * Masquer l'indicateur de chargement
 */
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Afficher une notification
 */
function showNotification(message, type = 'info') {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `admin-notification admin-notification-${type}`;
    
    let icon = 'fas fa-info-circle';
    switch (type) {
        case 'success':
            icon = 'fas fa-check-circle';
            break;
        case 'warning':
            icon = 'fas fa-exclamation-triangle';
            break;
        case 'error':
            icon = 'fas fa-times-circle';
            break;
    }
    
    notification.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Ajouter au conteneur de notifications
    let container = document.getElementById('notifications-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notifications-container';
        container.className = 'admin-notifications-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Animation d'entrée
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Suppression automatique après 5 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Styles CSS pour les notifications et le loading (à ajouter à admin.css)
const additionalStyles = `
.admin-loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 10000;
}

.admin-loading-content {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    color: var(--text-primary);
    font-size: 1.1rem;
}

.admin-loading-content i {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: var(--primary-color);
}

.admin-notifications-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    max-width: 400px;
}

.admin-notification {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    color: var(--text-primary);
    transform: translateX(100%);
    opacity: 0;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.admin-notification.show {
    transform: translateX(0);
    opacity: 1;
}

.admin-notification button {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    margin-left: auto;
    padding: 0.25rem;
}

.admin-notification-success {
    border-left: 4px solid var(--success-color);
}

.admin-notification-error {
    border-left: 4px solid var(--danger-color);
}

.admin-notification-warning {
    border-left: 4px solid var(--warning-color);
}

.admin-notification-info {
    border-left: 4px solid var(--primary-color);
}
`;

// Injecter les styles additionnels
if (!document.getElementById('admin-organizations-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'admin-organizations-styles';
    styleSheet.textContent = additionalStyles;
    document.head.appendChild(styleSheet);
}
