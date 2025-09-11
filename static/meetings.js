/**
 * MEETINGS COMPONENT JAVASCRIPT
 * =============================
 * Fonctionnalités JavaScript pour le système de réunions/meetings
 * Compatible avec l'architecture UMan API et les spécifications Decidim
 */

// Configuration globale
const MeetingsConfig = {
    autoSaveInterval: 30000, // 30 secondes
    calendarRefreshInterval: 60000, // 1 minute
    countdownRefreshInterval: 1000, // 1 seconde
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedFileTypes: ['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'],
    debounceDelay: 300
};

// Utilitaires généraux
const MeetingsUtils = {
    // Fonction de debounce pour optimiser les appels
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Formatage des dates
    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(date).toLocaleDateString('fr-FR', { ...defaultOptions, ...options });
    },

    // Formatage de la durée
    formatDuration(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        if (hours > 0) {
            return `${hours}h${mins > 0 ? ` ${mins}min` : ''}`;
        }
        return `${mins}min`;
    },

    // Validation des fichiers
    validateFile(file) {
        const extension = file.name.split('.').pop().toLowerCase();
        
        if (!MeetingsConfig.allowedFileTypes.includes(extension)) {
            return { valid: false, error: 'Type de fichier non autorisé' };
        }
        
        if (file.size > MeetingsConfig.maxFileSize) {
            return { valid: false, error: 'Fichier trop volumineux (max 10MB)' };
        }
        
        return { valid: true };
    },

    // Notification toast
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    },

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
};

/**
 * GESTIONNAIRE DE CALENDRIER
 */
class MeetingsCalendar {
    constructor(container) {
        this.container = container;
        this.currentDate = new Date();
        this.meetings = [];
        this.init();
    }

    init() {
        this.render();
        this.bindEvents();
        this.loadMeetings();
        this.startAutoRefresh();
    }

    render() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        let html = `
            <div class="calendar-header">
                <div class="calendar-navigation">
                    <button class="nav-btn prev-month" data-action="prev">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <h3 class="calendar-title">${this.formatMonthYear(year, month)}</h3>
                    <button class="nav-btn next-month" data-action="next">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
                <div class="calendar-actions">
                    <button class="btn-refonte btn-sm" onclick="window.location.href='/meetings/create'">
                        <i class="fas fa-plus"></i> Nouvelle réunion
                    </button>
                </div>
            </div>
            <div class="calendar-weekdays">
                ${['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map(day => `<div class="weekday">${day}</div>`).join('')}
            </div>
            <div class="calendar-days">
        `;
        
        const current = new Date(startDate);
        for (let i = 0; i < 42; i++) {
            const isCurrentMonth = current.getMonth() === month;
            const isToday = this.isToday(current);
            const dayMeetings = this.getMeetingsForDate(current);
            
            html += `
                <div class="calendar-day ${!isCurrentMonth ? 'empty' : ''} ${isToday ? 'today' : ''}" 
                     data-date="${current.toISOString().split('T')[0]}">
                    <div class="day-number">${current.getDate()}</div>
                    ${dayMeetings.map(meeting => this.renderCalendarMeeting(meeting)).join('')}
                </div>
            `;
            
            current.setDate(current.getDate() + 1);
        }
        
        html += '</div>';
        this.container.innerHTML = html;
    }

    formatMonthYear(year, month) {
        return new Date(year, month).toLocaleDateString('fr-FR', { 
            year: 'numeric', 
            month: 'long' 
        });
    }

    isToday(date) {
        const today = new Date();
        return date.toDateString() === today.toDateString();
    }

    getMeetingsForDate(date) {
        const dateStr = date.toISOString().split('T')[0];
        return this.meetings.filter(meeting => 
            meeting.date.startsWith(dateStr)
        );
    }

    renderCalendarMeeting(meeting) {
        const time = new Date(meeting.date).toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        return `
            <div class="calendar-meeting" data-meeting-id="${meeting.id}" title="${meeting.title}">
                <div class="meeting-time">${time}</div>
                <div class="meeting-title">${meeting.title}</div>
            </div>
        `;
    }

    bindEvents() {
        this.container.addEventListener('click', (e) => {
            if (e.target.matches('.nav-btn[data-action="prev"]') || 
                e.target.closest('.nav-btn[data-action="prev"]')) {
                this.previousMonth();
            } else if (e.target.matches('.nav-btn[data-action="next"]') || 
                       e.target.closest('.nav-btn[data-action="next"]')) {
                this.nextMonth();
            } else if (e.target.matches('.calendar-meeting') || 
                       e.target.closest('.calendar-meeting')) {
                const meetingElement = e.target.closest('.calendar-meeting');
                const meetingId = meetingElement.dataset.meetingId;
                window.location.href = `/meetings/${meetingId}`;
            }
        });
    }

    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.render();
        this.loadMeetings();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.render();
        this.loadMeetings();
    }

    async loadMeetings() {
        try {
            const year = this.currentDate.getFullYear();
            const month = this.currentDate.getMonth() + 1;
            
            const response = await fetch(`/api/meetings/calendar?year=${year}&month=${month}`);
            if (response.ok) {
                this.meetings = await response.json();
                this.render();
            }
        } catch (error) {
            console.error('Erreur lors du chargement des réunions:', error);
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            this.loadMeetings();
        }, MeetingsConfig.calendarRefreshInterval);
    }
}

/**
 * GESTIONNAIRE DE FILTRES ET RECHERCHE
 */
class MeetingsFilters {
    constructor(container) {
        this.container = container;
        this.filters = {
            search: '',
            status: '',
            type: '',
            organization: '',
            dateFrom: '',
            dateTo: '',
            tags: []
        };
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSavedFilters();
    }

    bindEvents() {
        // Recherche avec debounce
        const searchInput = this.container.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', 
                MeetingsUtils.debounce((e) => {
                    this.filters.search = e.target.value;
                    this.applyFilters();
                }, MeetingsConfig.debounceDelay)
            );
        }

        // Filtres par sélection
        const filterSelects = this.container.querySelectorAll('.filter-select');
        filterSelects.forEach(select => {
            select.addEventListener('change', (e) => {
                const filterType = e.target.dataset.filter;
                this.filters[filterType] = e.target.value;
                this.applyFilters();
            });
        });

        // Filtres par date
        const dateInputs = this.container.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const filterType = e.target.dataset.filter;
                this.filters[filterType] = e.target.value;
                this.applyFilters();
            });
        });

        // Reset des filtres
        const resetBtn = this.container.querySelector('.filters-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetFilters();
            });
        }
    }

    applyFilters() {
        const params = new URLSearchParams();
        
        Object.entries(this.filters).forEach(([key, value]) => {
            if (value && value !== '') {
                if (Array.isArray(value)) {
                    value.forEach(v => params.append(key, v));
                } else {
                    params.set(key, value);
                }
            }
        });

        this.updateResults(params.toString());
        this.saveFilters();
    }

    async updateResults(queryString) {
        try {
            const response = await fetch(`/api/meetings/filter?${queryString}`);
            if (response.ok) {
                const data = await response.json();
                this.renderResults(data);
                this.updateResultsCount(data.total);
            }
        } catch (error) {
            console.error('Erreur lors de la filtration:', error);
            MeetingsUtils.showToast('Erreur lors de la recherche', 'error');
        }
    }

    renderResults(data) {
        const resultsContainer = document.querySelector('.meetings-container');
        if (!resultsContainer) return;

        if (data.meetings.length === 0) {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search fa-3x"></i>
                    <h3>Aucune réunion trouvée</h3>
                    <p>Modifiez vos critères de recherche ou créez une nouvelle réunion.</p>
                    <a href="/meetings/create" class="btn-refonte">
                        <i class="fas fa-plus"></i> Créer une réunion
                    </a>
                </div>
            `;
            return;
        }

        resultsContainer.innerHTML = data.meetings.map(meeting => 
            this.renderMeetingCard(meeting)
        ).join('');
    }

    renderMeetingCard(meeting) {
        return `
            <div class="meeting-card" data-meeting-id="${meeting.id}">
                <div class="meeting-header">
                    <div class="status-badges">
                        <span class="status-badge status-${meeting.status}">
                            <i class="fas fa-${this.getStatusIcon(meeting.status)}"></i>
                            ${this.getStatusText(meeting.status)}
                        </span>
                        <span class="type-badge type-${meeting.type}">
                            <i class="fas fa-${this.getTypeIcon(meeting.type)}"></i>
                            ${this.getTypeText(meeting.type)}
                        </span>
                    </div>
                    <div class="meeting-actions">
                        <button class="action-btn" title="Partager" onclick="shareMeeting(${meeting.id})">
                            <i class="fas fa-share-alt"></i>
                        </button>
                        <button class="action-btn" title="Favoris" onclick="toggleFavorite(${meeting.id})">
                            <i class="fas fa-heart"></i>
                        </button>
                    </div>
                </div>
                
                <div class="meeting-content">
                    <h3 class="meeting-title">
                        <a href="/meetings/${meeting.id}">${meeting.title}</a>
                    </h3>
                    <p class="meeting-description">${meeting.description}</p>
                    
                    <div class="meeting-meta">
                        <div class="meeting-timing">
                            <div class="meeting-date">${MeetingsUtils.formatDate(meeting.date)}</div>
                            <div class="meeting-duration">Durée: ${MeetingsUtils.formatDuration(meeting.duration)}</div>
                        </div>
                        
                        <div class="meeting-location">
                            ${meeting.type !== 'online' ? `
                                <div class="location-info">
                                    <i class="fas fa-map-marker-alt"></i>
                                    <span>${meeting.location}</span>
                                </div>
                            ` : ''}
                            ${meeting.type !== 'in-person' ? `
                                <div class="online-info">
                                    <i class="fas fa-video"></i>
                                    <span>Réunion en ligne</span>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    ${meeting.registrationEnabled ? `
                        <div class="registration-info">
                            <div class="registration-stats">
                                <span class="registered-count">
                                    <i class="fas fa-users"></i>
                                    ${meeting.registeredCount}/${meeting.maxParticipants || '∞'} inscrits
                                </span>
                                <div class="capacity-bar">
                                    <div class="capacity-fill" style="width: ${(meeting.registeredCount / (meeting.maxParticipants || meeting.registeredCount + 10)) * 100}%"></div>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="meeting-footer">
                    <div class="meeting-organizer">
                        <div class="organizer-info">
                            <div class="organizer-avatar">
                                ${meeting.organizer.avatar ? 
                                    `<img src="${meeting.organizer.avatar}" alt="${meeting.organizer.name}">` :
                                    `<span class="avatar-placeholder">${meeting.organizer.name.charAt(0)}</span>`
                                }
                            </div>
                            <div class="organizer-details">
                                <div class="organizer-name">${meeting.organizer.name}</div>
                                <div class="meeting-created">Créée le ${MeetingsUtils.formatDate(meeting.createdAt, { hour: undefined, minute: undefined })}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="meeting-indicators">
                        ${meeting.hasAgenda ? '<div class="indicator-item verified" title="Ordre du jour disponible"><i class="fas fa-list"></i></div>' : ''}
                        ${meeting.hasMinutes ? '<div class="indicator-item verified" title="Compte-rendu disponible"><i class="fas fa-file-alt"></i></div>' : ''}
                        ${meeting.isVerified ? '<div class="indicator-item verified" title="Réunion vérifiée"><i class="fas fa-check"></i></div>' : ''}
                    </div>
                </div>
                
                <div class="traceability-indicator">
                    <div class="trace-info">
                        <i class="fas fa-shield-alt"></i>
                        <span>Score de traçabilité: <span class="trace-score">${meeting.traceabilityScore}%</span></span>
                    </div>
                    <div class="signature-verified">
                        <i class="fas fa-certificate"></i>
                        <span>Signature vérifiée</span>
                    </div>
                </div>
            </div>
        `;
    }

    getStatusIcon(status) {
        const icons = {
            upcoming: 'clock',
            ongoing: 'play-circle',
            finished: 'check-circle',
            cancelled: 'times-circle'
        };
        return icons[status] || 'question-circle';
    }

    getStatusText(status) {
        const texts = {
            upcoming: 'À venir',
            ongoing: 'En cours',
            finished: 'Terminée',
            cancelled: 'Annulée'
        };
        return texts[status] || 'Inconnu';
    }

    getTypeIcon(type) {
        const icons = {
            'in-person': 'users',
            'online': 'video',
            'hybrid': 'globe'
        };
        return icons[type] || 'question-circle';
    }

    getTypeText(type) {
        const texts = {
            'in-person': 'Présentiel',
            'online': 'En ligne',
            'hybrid': 'Hybride'
        };
        return texts[type] || 'Inconnu';
    }

    updateResultsCount(total) {
        const countElement = document.querySelector('.results-count');
        if (countElement) {
            countElement.textContent = `${total} réunion${total !== 1 ? 's' : ''} trouvée${total !== 1 ? 's' : ''}`;
        }
    }

    resetFilters() {
        this.filters = {
            search: '',
            status: '',
            type: '',
            organization: '',
            dateFrom: '',
            dateTo: '',
            tags: []
        };

        // Reset des inputs
        const inputs = this.container.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });

        this.applyFilters();
        localStorage.removeItem('meetingsFilters');
    }

    saveFilters() {
        localStorage.setItem('meetingsFilters', JSON.stringify(this.filters));
    }

    loadSavedFilters() {
        const saved = localStorage.getItem('meetingsFilters');
        if (saved) {
            try {
                this.filters = { ...this.filters, ...JSON.parse(saved) };
                this.restoreFilterInputs();
            } catch (error) {
                console.error('Erreur lors du chargement des filtres sauvegardés:', error);
            }
        }
    }

    restoreFilterInputs() {
        Object.entries(this.filters).forEach(([key, value]) => {
            const input = this.container.querySelector(`[data-filter="${key}"]`);
            if (input && value) {
                input.value = value;
            }
        });
    }
}

/**
 * GESTIONNAIRE DE FORMULAIRE DE RÉUNION
 */
class MeetingForm {
    constructor(form) {
        this.form = form;
        this.autoSaveTimer = null;
        this.isDirty = false;
        this.originalData = {};
        this.agenda = [];
        this.init();
    }

    init() {
        this.captureOriginalData();
        this.bindEvents();
        this.initializeComponents();
        this.startAutoSave();
    }

    captureOriginalData() {
        const formData = new FormData(this.form);
        this.originalData = Object.fromEntries(formData.entries());
    }

    bindEvents() {
        // Détection des changements
        this.form.addEventListener('input', () => {
            this.isDirty = true;
            this.updateSaveStatus('modified');
        });

        this.form.addEventListener('change', () => {
            this.isDirty = true;
            this.updateSaveStatus('modified');
        });

        // Gestion du format de réunion
        const formatRadios = this.form.querySelectorAll('input[name="format"]');
        formatRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.toggleFormatFields(e.target.value);
            });
        });

        // Gestion des dates
        const startDateInput = this.form.querySelector('#start_date');
        const endDateInput = this.form.querySelector('#end_date');
        
        if (startDateInput && endDateInput) {
            startDateInput.addEventListener('change', () => {
                this.updateDuration();
            });
            endDateInput.addEventListener('change', () => {
                this.updateDuration();
            });
        }

        // Validation avant soumission
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
            } else {
                this.updateSaveStatus('saving');
            }
        });

        // Prévention de la perte de données
        window.addEventListener('beforeunload', (e) => {
            if (this.isDirty) {
                e.preventDefault();
                e.returnValue = 'Vous avez des modifications non sauvegardées. Êtes-vous sûr de vouloir quitter ?';
            }
        });
    }

    initializeComponents() {
        // Initialisation des sélecteurs de date/heure
        this.initDateTimePickers();
        
        // Initialisation de l'éditeur WYSIWYG
        this.initRichEditor();
        
        // Initialisation du constructeur d'agenda
        this.initAgendaBuilder();
        
        // Définition du format initial
        const checkedFormat = this.form.querySelector('input[name="format"]:checked');
        if (checkedFormat) {
            this.toggleFormatFields(checkedFormat.value);
        }
    }

    initDateTimePickers() {
        // Utilisation de flatpickr pour les sélecteurs de date/heure
        const dateTimeInputs = this.form.querySelectorAll('.datetime-picker');
        dateTimeInputs.forEach(input => {
            flatpickr(input, {
                enableTime: true,
                dateFormat: "Y-m-d H:i",
                time_24hr: true,
                locale: "fr",
                minDate: "today"
            });
        });
    }

    initRichEditor() {
        const descriptionTextarea = this.form.querySelector('#description');
        if (descriptionTextarea && typeof CKEDITOR !== 'undefined') {
            CKEDITOR.replace('description', {
                height: 200,
                toolbar: [
                    { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline'] },
                    { name: 'paragraph', items: ['NumberedList', 'BulletedList'] },
                    { name: 'links', items: ['Link', 'Unlink'] },
                    { name: 'insert', items: ['Image', 'Table'] }
                ],
                language: 'fr'
            });
        }
    }

    initAgendaBuilder() {
        const agendaContainer = this.form.querySelector('.agenda-builder');
        if (agendaContainer) {
            this.bindAgendaEvents();
            this.loadExistingAgenda();
        }
    }

    bindAgendaEvents() {
        const addItemBtn = this.form.querySelector('.add-agenda-item');
        if (addItemBtn) {
            addItemBtn.addEventListener('click', () => {
                this.addAgendaItem();
            });
        }

        // Templates d'agenda prédéfinis
        const templateBtns = this.form.querySelectorAll('.agenda-template');
        templateBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const template = e.target.dataset.template;
                this.loadAgendaTemplate(template);
            });
        });
    }

    addAgendaItem(data = {}) {
        const itemId = Date.now();
        const itemHtml = `
            <div class="agenda-item" data-item-id="${itemId}">
                <div class="agenda-item-header">
                    <span class="item-handle"><i class="fas fa-grip-vertical"></i></span>
                    <span class="item-number">${this.agenda.length + 1}</span>
                    <input type="text" class="item-title" placeholder="Titre du point" value="${data.title || ''}" required>
                    <button type="button" class="item-remove" onclick="this.closest('.agenda-item').remove(); meetingForm.updateAgendaNumbers();">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="agenda-item-content">
                    <div class="item-meta">
                        <input type="number" class="item-duration form-control" placeholder="Durée (min)" value="${data.duration || 15}" min="5" max="180">
                        <select class="item-type form-control">
                            <option value="presentation" ${data.type === 'presentation' ? 'selected' : ''}>Présentation</option>
                            <option value="discussion" ${data.type === 'discussion' ? 'selected' : ''}>Discussion</option>
                            <option value="decision" ${data.type === 'decision' ? 'selected' : ''}>Décision</option>
                            <option value="vote" ${data.type === 'vote' ? 'selected' : ''}>Vote</option>
                            <option value="break" ${data.type === 'break' ? 'selected' : ''}>Pause</option>
                        </select>
                    </div>
                    <textarea class="item-description form-control" rows="2" placeholder="Description détaillée...">${data.description || ''}</textarea>
                </div>
            </div>
        `;

        const agendaItems = this.form.querySelector('.agenda-items');
        agendaItems.insertAdjacentHTML('beforeend', itemHtml);
        
        this.agenda.push({
            id: itemId,
            title: data.title || '',
            duration: data.duration || 15,
            type: data.type || 'presentation',
            description: data.description || ''
        });

        this.updateAgendaSummary();
        this.makeSortable();
    }

    updateAgendaNumbers() {
        const items = this.form.querySelectorAll('.agenda-item');
        items.forEach((item, index) => {
            const numberSpan = item.querySelector('.item-number');
            numberSpan.textContent = index + 1;
        });
        this.updateAgendaSummary();
    }

    updateAgendaSummary() {
        const items = this.form.querySelectorAll('.agenda-item');
        const totalDuration = Array.from(items).reduce((total, item) => {
            const duration = parseInt(item.querySelector('.item-duration').value) || 0;
            return total + duration;
        }, 0);

        const summaryElement = this.form.querySelector('.agenda-summary');
        if (summaryElement) {
            summaryElement.innerHTML = `
                <div class="summary-item">
                    <strong>${items.length}</strong> point${items.length !== 1 ? 's' : ''}
                </div>
                <div class="summary-item">
                    Durée totale: <strong>${MeetingsUtils.formatDuration(totalDuration)}</strong>
                </div>
            `;
        }
    }

    makeSortable() {
        const agendaItems = this.form.querySelector('.agenda-items');
        if (agendaItems && typeof Sortable !== 'undefined') {
            new Sortable(agendaItems, {
                handle: '.item-handle',
                animation: 150,
                onEnd: () => {
                    this.updateAgendaNumbers();
                }
            });
        }
    }

    loadAgendaTemplate(template) {
        const templates = {
            standard: [
                { title: 'Ouverture de séance', duration: 5, type: 'presentation' },
                { title: 'Approbation de l\'ordre du jour', duration: 10, type: 'decision' },
                { title: 'Rapport d\'activité', duration: 30, type: 'presentation' },
                { title: 'Discussion générale', duration: 45, type: 'discussion' },
                { title: 'Décisions', duration: 30, type: 'decision' },
                { title: 'Questions diverses', duration: 15, type: 'discussion' },
                { title: 'Clôture', duration: 5, type: 'presentation' }
            ],
            workshop: [
                { title: 'Accueil et présentations', duration: 15, type: 'presentation' },
                { title: 'Introduction du sujet', duration: 20, type: 'presentation' },
                { title: 'Travail en groupes', duration: 60, type: 'discussion' },
                { title: 'Pause', duration: 15, type: 'break' },
                { title: 'Restitution des groupes', duration: 45, type: 'presentation' },
                { title: 'Synthèse et prochaines étapes', duration: 25, type: 'decision' }
            ]
        };

        const templateData = templates[template];
        if (templateData) {
            // Vider l'agenda existant
            this.form.querySelector('.agenda-items').innerHTML = '';
            this.agenda = [];
            
            // Ajouter les éléments du template
            templateData.forEach(item => {
                this.addAgendaItem(item);
            });
        }
    }

    toggleFormatFields(format) {
        const locationFields = this.form.querySelector('.location-fields');
        const onlineFields = this.form.querySelector('.online-fields');

        if (locationFields) locationFields.style.display = 'none';
        if (onlineFields) onlineFields.style.display = 'none';

        switch (format) {
            case 'in-person':
                if (locationFields) locationFields.style.display = 'block';
                break;
            case 'online':
                if (onlineFields) onlineFields.style.display = 'block';
                break;
            case 'hybrid':
                if (locationFields) locationFields.style.display = 'block';
                if (onlineFields) onlineFields.style.display = 'block';
                break;
        }
    }

    updateDuration() {
        const startDate = this.form.querySelector('#start_date').value;
        const endDate = this.form.querySelector('#end_date').value;

        if (startDate && endDate) {
            const start = new Date(startDate);
            const end = new Date(endDate);
            const durationMs = end - start;
            const durationMinutes = Math.round(durationMs / (1000 * 60));

            const durationField = this.form.querySelector('#duration');
            if (durationField) {
                durationField.value = durationMinutes;
            }
        }
    }

    validateForm() {
        const errors = [];

        // Validation du titre
        const title = this.form.querySelector('#title').value.trim();
        if (!title) {
            errors.push('Le titre est requis');
        }

        // Validation des dates
        const startDate = this.form.querySelector('#start_date').value;
        const endDate = this.form.querySelector('#end_date').value;
        
        if (!startDate) {
            errors.push('La date de début est requise');
        }
        
        if (!endDate) {
            errors.push('La date de fin est requise');
        }
        
        if (startDate && endDate && new Date(startDate) >= new Date(endDate)) {
            errors.push('La date de fin doit être postérieure à la date de début');
        }

        // Validation selon le format
        const format = this.form.querySelector('input[name="format"]:checked')?.value;
        
        if (format === 'in-person' || format === 'hybrid') {
            const location = this.form.querySelector('#location').value.trim();
            if (!location) {
                errors.push('Le lieu est requis pour les réunions en présentiel');
            }
        }

        // Affichage des erreurs
        if (errors.length > 0) {
            const errorContainer = this.form.querySelector('.form-errors');
            if (errorContainer) {
                errorContainer.innerHTML = errors.map(error => 
                    `<div class="alert alert-danger">${error}</div>`
                ).join('');
                errorContainer.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Erreurs de validation:\n' + errors.join('\n'));
            }
            return false;
        }

        return true;
    }

    startAutoSave() {
        this.autoSaveTimer = setInterval(() => {
            if (this.isDirty) {
                this.autoSave();
            }
        }, MeetingsConfig.autoSaveInterval);
    }

    async autoSave() {
        try {
            const formData = new FormData(this.form);
            formData.append('auto_save', 'true');
            
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                this.isDirty = false;
                this.updateSaveStatus('saved');
            } else {
                this.updateSaveStatus('error');
            }
        } catch (error) {
            console.error('Erreur lors de la sauvegarde automatique:', error);
            this.updateSaveStatus('error');
        }
    }

    updateSaveStatus(status) {
        const statusElement = this.form.querySelector('.save-status');
        if (!statusElement) return;

        const statusConfig = {
            saved: {
                icon: 'check-circle',
                text: 'Sauvegardé automatiquement',
                class: 'status-saved'
            },
            saving: {
                icon: 'spinner fa-spin',
                text: 'Sauvegarde en cours...',
                class: 'status-saving'
            },
            modified: {
                icon: 'edit',
                text: 'Modifications non sauvegardées',
                class: 'status-modified'
            },
            error: {
                icon: 'exclamation-triangle',
                text: 'Erreur de sauvegarde',
                class: 'status-error'
            }
        };

        const config = statusConfig[status];
        if (config) {
            statusElement.className = `save-status ${config.class}`;
            statusElement.innerHTML = `
                <i class="fas fa-${config.icon}"></i>
                <span>${config.text}</span>
            `;
        }
    }
}

/**
 * GESTIONNAIRE DE COMPTEURS (COUNTDOWNS)
 */
class MeetingCountdowns {
    constructor() {
        this.countdowns = new Map();
        this.init();
    }

    init() {
        this.findCountdownElements();
        this.startCountdowns();
    }

    findCountdownElements() {
        const elements = document.querySelectorAll('[data-countdown]');
        elements.forEach(element => {
            const targetDate = element.dataset.countdown;
            if (targetDate) {
                this.countdowns.set(element, new Date(targetDate));
            }
        });
    }

    startCountdowns() {
        setInterval(() => {
            this.updateCountdowns();
        }, MeetingsConfig.countdownRefreshInterval);
        
        // Mise à jour immédiate
        this.updateCountdowns();
    }

    updateCountdowns() {
        this.countdowns.forEach((targetDate, element) => {
            const now = new Date();
            const diff = targetDate - now;

            if (diff <= 0) {
                element.textContent = 'Terminée';
                element.classList.add('countdown-expired');
                return;
            }

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            let text = '';
            if (days > 0) {
                text = `${days}j ${hours}h ${minutes}min`;
            } else if (hours > 0) {
                text = `${hours}h ${minutes}min ${seconds}s`;
            } else {
                text = `${minutes}min ${seconds}s`;
            }

            element.textContent = text;
        });
    }
}

/**
 * FONCTIONS GLOBALES ET UTILITAIRES
 */

// Partage de réunion
function shareMeeting(meetingId) {
    const url = `${window.location.origin}/meetings/${meetingId}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Réunion - UMan API',
            url: url
        }).catch(console.error);
    } else {
        // Fallback: copier dans le presse-papiers
        navigator.clipboard.writeText(url).then(() => {
            MeetingsUtils.showToast('Lien copié dans le presse-papiers', 'success');
        }).catch(() => {
            // Fallback du fallback
            prompt('Copiez ce lien:', url);
        });
    }
}

// Gestion des favoris
async function toggleFavorite(meetingId) {
    try {
        const response = await fetch(`/api/meetings/${meetingId}/favorite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            const data = await response.json();
            const button = document.querySelector(`[onclick="toggleFavorite(${meetingId})"]`);
            if (button) {
                const icon = button.querySelector('i');
                icon.className = data.favorited ? 'fas fa-heart' : 'far fa-heart';
            }
            MeetingsUtils.showToast(
                data.favorited ? 'Ajouté aux favoris' : 'Retiré des favoris', 
                'success'
            );
        }
    } catch (error) {
        console.error('Erreur lors de la gestion des favoris:', error);
        MeetingsUtils.showToast('Erreur lors de la gestion des favoris', 'error');
    }
}

// Export des réunions
function exportMeetings(format = 'pdf') {
    const params = new URLSearchParams(window.location.search);
    params.set('export', format);
    
    window.open(`/meetings/export?${params.toString()}`, '_blank');
}

// Inscription à une réunion
async function registerForMeeting(meetingId, action = 'register') {
    try {
        const response = await fetch(`/api/meetings/${meetingId}/register`, {
            method: action === 'register' ? 'POST' : 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            const data = await response.json();
            
            // Recharger la page pour mettre à jour l'affichage
            window.location.reload();
        } else {
            const error = await response.json();
            MeetingsUtils.showToast(error.message || 'Erreur lors de l\'inscription', 'error');
        }
    } catch (error) {
        console.error('Erreur lors de l\'inscription:', error);
        MeetingsUtils.showToast('Erreur lors de l\'inscription', 'error');
    }
}

/**
 * INITIALISATION AUTOMATIQUE
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation du calendrier
    const calendarContainer = document.querySelector('.calendar-container');
    if (calendarContainer) {
        new MeetingsCalendar(calendarContainer);
    }

    // Initialisation des filtres
    const filtersSection = document.querySelector('.filters-section');
    if (filtersSection) {
        new MeetingsFilters(filtersSection);
    }

    // Initialisation du formulaire de réunion
    const meetingForm = document.querySelector('.meeting-form');
    if (meetingForm) {
        window.meetingForm = new MeetingForm(meetingForm);
    }

    // Initialisation des compteurs
    new MeetingCountdowns();

    // Gestion des vues (grille/liste)
    const viewToggles = document.querySelectorAll('.view-toggle');
    viewToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            const view = e.target.dataset.view || e.target.closest('.view-toggle').dataset.view;
            switchView(view);
        });
    });

    // Initialisation des tooltips Bootstrap si disponible
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Fonction de changement de vue
function switchView(view) {
    const container = document.querySelector('.meetings-container');
    const toggles = document.querySelectorAll('.view-toggle');
    
    if (container) {
        container.className = `meetings-container view-${view}`;
    }
    
    toggles.forEach(toggle => {
        toggle.classList.toggle('active', toggle.dataset.view === view);
    });
    
    // Sauvegarder la préférence
    localStorage.setItem('meetingsView', view);
}

// Restaurer la vue sauvegardée
const savedView = localStorage.getItem('meetingsView');
if (savedView) {
    switchView(savedView);
}
