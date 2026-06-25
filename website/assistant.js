// Initialize Telegram Web App SDK
window.onerror = function(msg, url, line, col, error) {
    document.body.innerHTML += '<div style="position:fixed;top:0;left:0;z-index:99999;background:red;color:white;padding:20px;font-size:16px;">ERROR: ' + msg + '<br>Line: ' + line + '</div>';
};
const tg = window.Telegram.WebApp;
tg.expand();

// Base URL for all API calls - works with tunnels like Cloudflare
const API_BASE = window.location.origin;

// DOM elements
const chatHistory = document.getElementById('chat-history');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.getElementById('clear-btn');
const titleText = document.getElementById('chat-title-text');
const statusText = document.getElementById('chat-status-text');

// User settings & Localization
let userLang = localStorage.getItem('userLang') || 'de';
if (!localStorage.getItem('userLang') && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.language_code) {
    const code = tg.initDataUnsafe.user.language_code.toLowerCase();
    if (code === 'uz') userLang = 'uz';
    else if (code === 'ru') userLang = 'ru';
}

const LOCALIZATION = {
    de: {
        title: "ABDULAZIZ GERMAN AI",
        status: "DEUTSCH TUTOR // ONLINE",
        welcome: "Hallo! Ich bin dein Deutsch-Assistent. Wie kann ich dir heute beim Deutschlernen oder bei der Vorbereitung auf die B1-Prüfung helfen?",
        placeholder: "Schreibe eine Nachricht...",
        clearConfirm: "Möchtest du den Chat-Verlauf wirklich löschen?",
        dashboardTitle: "ABDULAZIZ GERMAN AI",
        dashboardStatus: "DEUTSCH TUTOR // ONLINE",
        welcomeUser: "Hallo, ",
        welcomeSub: "Lass uns gemeinsam das B1-Niveau in Deutsch erreichen!",
        progressLabel: "Niveau Fortschritt",
        lektionLabel: "Lektion",
        btnReadLessonTitle: "Heutige Lektion lesen",
        btnReadLessonDesc: "Grammatikregeln, Vokabeln und Übungen",
        btnChatTutorTitle: "Gespräch mit dem KI-Tutor",
        btnChatTutorDesc: "Fragen stellen und Konversation üben",
        btnTakeExamTitle: "Niveauprüfung ablegen",
        btnTakeExamDesc: "Verfügbar nach Abschluss von 60 Lektionen",
        backToMenu: "Zurück",
        completeLesson: "Lektion beenden",
        loadingLesson: "Lektion wird geladen...",
        lessonCompletedMsg: "Lektion abgeschlossen! Tolle Arbeit.",
        completeLessonConfirm: "Möchtest du diese Lektion wirklich als abgeschlossen markieren?",
        btnChangeLevel: "Niveaus // Stufen",
        ratingLabel: "Studienbewertung:"
    },
    uz: {
        title: "ABDULAZIZ NEMIS AI",
        status: "NEMIS TILI TUTORI // ONLINE",
        welcome: "Hallo! Men nemis tili bo'yicha AI-yordamchingizman. Nemis tilini o'rganishda va B1 imtihoniga (Ausbildung/ish) tayyorlanishda qanday yordam bera olaman?",
        placeholder: "Xabar yozing...",
        clearConfirm: "Chat tarixini o'chirishni xohlaysizmi?",
        dashboardTitle: "ABDULAZIZ NEMIS AI",
        dashboardStatus: "NEMIS TILI TUTORI // ONLINE",
        welcomeUser: "Salom, ",
        welcomeSub: "Nemis tili B1 darajasiga birgalikda erishamiz!",
        progressLabel: "Daraja progressi",
        lektionLabel: "Dars",
        btnReadLessonTitle: "Bugungi darsni o'qish",
        btnReadLessonDesc: "Barcha 60 ta darslar va mashqlar",
        btnChatTutorTitle: "AI Repetitor bilan suhbat",
        btnChatTutorDesc: "Savol-javob va mashq qilish",
        btnTakeExamTitle: "Daraja Imtihonini topshirish",
        btnTakeExamDesc: "60 ta dars tugagandan so'ng faollashadi",
        backToMenu: "Orqaga",
        completeLesson: "Darsni yakunlash",
        loadingLesson: "Dars yuklanmoqda...",
        lessonCompletedMsg: "Dars muvaffaqiyatli yakunlandi! Keyingi darsga o'tildi.",
        completeLessonConfirm: "Darsni yakunlashni xohlaysizmi?",
        btnChangeLevel: "Darajalar / Уровни",
        ratingLabel: "O'qish reytingi:"
    },
    ru: {
        title: "ABDULAZIZ NEMIS AI",
        status: "РЕПЕТИТОР НЕМЕЦКОГО // ОНЛАЙН",
        welcome: "Hallo! Я твой ИИ-помощник по немецкому языку. Чем я могу помочь тебе сегодня в изучении немецкого языка и подготовке к экзамену B1?",
        placeholder: "Напишите сообщение...",
        clearConfirm: "Вы уверены, что хотите очистить историю чата?",
        dashboardTitle: "ABDULAZIZ NEMIS AI",
        dashboardStatus: "РЕПЕТИТОР НЕМЕЦКОГО // ОНЛАЙН",
        welcomeUser: "Привет, ",
        welcomeSub: "Давайте вместе достигнем уровня B1 в немецком языке!",
        progressLabel: "Прогресс уровня",
        lektionLabel: "Урок",
        btnReadLessonTitle: "Читать сегодняшний урок",
        btnReadLessonDesc: "Все 60 уроков и упражнения",
        btnChatTutorTitle: "Чат с ИИ-репетитором",
        btnChatTutorDesc: "Вопросы, ответы и разговорная практика",
        btnTakeExamTitle: "Сдать экзамен уровня",
        btnTakeExamDesc: "Активируется после прохождения 60 уроков",
        backToMenu: "Назад",
        completeLesson: "Завершить урок",
        loadingLesson: "Загрузка урока...",
        lessonCompletedMsg: "Урок успешно завершен! Переходим к следующему уроку.",
        completeLessonConfirm: "Вы уверены, что хотите завершить текущий урок?",
        btnChangeLevel: "Уровни / Darajalar",
        ratingLabel: "Рейтинг обучения:"
    }
};

let texts = LOCALIZATION[userLang] || LOCALIZATION['de'];

function applyLanguage(lang) {
    userLang = lang;
    texts = LOCALIZATION[userLang] || LOCALIZATION['de'];
    
    // Update global UI Elements if they exist
    if (titleText) titleText.textContent = texts.title;
    if (statusText) statusText.textContent = texts.status;
    if (messageInput) messageInput.placeholder = texts.placeholder;
    
    // If dashboard is visible, re-render to update text
    if (views && views.dashboard && !views.dashboard.classList.contains('hidden')) {
        renderDashboard();
    }
}

// Initial application will be called at the bottom after initialization


// Apply Telegram theme colors dynamically
document.documentElement.style.setProperty('--tg-theme-bg-color', tg.backgroundColor || '#111215');
document.documentElement.style.setProperty('--tg-theme-text-color', tg.textColor || '#ffffff');
document.documentElement.style.setProperty('--tg-theme-hint-color', tg.hintColor || '#8e9297');
document.documentElement.style.setProperty('--tg-theme-button-color', tg.buttonColor || '#e63946');
document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.buttonTextColor || '#ffffff');

// Local storage session key
const STORAGE_KEY = 'nemis_chat_history';

// Modal Elements
const welcomeModal = document.getElementById('welcome-modal');
const screenLevel = document.getElementById('screen-level');
const screenWarning = document.getElementById('screen-warning');
const warningTextContent = document.getElementById('warning-text-content');
const acceptChallengeBtn = document.getElementById('accept-challenge-btn');
const declineChallengeBtn = document.getElementById('decline-challenge-btn');

let selectedLevel = localStorage.getItem('nemis_selected_level') || '';
let challengeAccepted = localStorage.getItem('nemis_challenge_accepted') === 'true';

// Load history or initialize
let history = [];
try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        history = JSON.parse(saved);
    }
} catch (e) {
    console.error("Error reading from localStorage", e);
}

// Render history
function renderChat() {
    chatHistory.innerHTML = '';
    
    // If empty history, add default welcome message
    if (history.length === 0) {
        let msg = texts.welcome;
        if (selectedLevel) {
            msg += ` (Niveau: ${selectedLevel})`;
        }
        addMessage(msg, 'bot', false);
    } else {
        history.forEach(msg => {
            addMessage(msg.text, msg.sender, false);
        });
    }
    scrollToBottom();
}

// Add message element to chat screen
function addMessage(text, sender, save = true) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'user' ? 'message-user' : 'message-bot');
    
    const bubble = document.createElement('div');
    bubble.classList.add('message-bubble');
    
    // Render text with markdown format linebreaks
    bubble.innerHTML = formatMarkdown(text);
    
    msgDiv.appendChild(bubble);
    chatHistory.appendChild(msgDiv);
    
    if (save) {
        history.push({ text, sender });
        saveHistory();
    }
    scrollToBottom();
}

// Simple markdown formatter
function formatMarkdown(text) {
    if (!text) return '';
    let escaped = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    
    // Code blocks
    escaped = escaped.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    // Inline code
    escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Bold
    escaped = escaped.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    escaped = escaped.replace(/\*([^*]+)\*/g, '<strong>$1</strong>');
    // Linebreaks
    return escaped.replace(/\n/g, '<br>');
}

function saveHistory() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
        console.error("Error saving to localStorage", e);
    }
}

function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Show/Hide typing indicator
let typingIndicator = null;
function showTyping() {
    if (typingIndicator) return;
    
    typingIndicator = document.createElement('div');
    typingIndicator.classList.add('message', 'message-bot');
    
    const bubble = document.createElement('div');
    bubble.classList.add('message-bubble', 'typing-bubble');
    bubble.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    
    typingIndicator.appendChild(bubble);
    chatHistory.appendChild(typingIndicator);
    scrollToBottom();
}

function hideTyping() {
    if (typingIndicator) {
        typingIndicator.remove();
        typingIndicator = null;
    }
}

// Handle message submission
async function handleSubmit() {
    const question = messageInput.value.trim();
    if (!question) return;
    
    // Send feedback vibration
    if (tg.HapticFeedback && typeof tg.HapticFeedback.impactOccurred === 'function') {
        try { tg.HapticFeedback.impactOccurred('light'); } catch(e){}
    }
    
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    addMessage(question, 'user');
    showTyping();
    
    try {
        const response = await fetch('/assistant/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, lang: userLang })
        });
        
        hideTyping();
        
        if (response.ok) {
            const data = await response.json();
            addMessage(data.answer || 'Fehler beim Laden der Antwort.', 'bot');
        } else {
            addMessage('Fehler bei der Verbindung mit dem Server.', 'bot');
        }
    } catch (e) {
        hideTyping();
        addMessage('Netzwerkfehler.', 'bot');
    }
}

// Event listeners
sendBtn.addEventListener('click', handleSubmit);

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
    }
});

// Auto-expand textarea height
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = (messageInput.scrollHeight) + 'px';
});

clearBtn.addEventListener('click', () => {
    if (confirm(texts.clearConfirm)) {
        if (tg.HapticFeedback && typeof tg.HapticFeedback.notificationOccurred === 'function') {
            try { tg.HapticFeedback.notificationOccurred('warning'); } catch(e){}
        }
        history = [];
        saveHistory();
        renderChat();
    }
});

// Fetch Telegram User Info
const tgUser = (tg.initDataUnsafe && tg.initDataUnsafe.user) || { id: "12345678", first_name: "Local User", username: "localuser" };
const userId = tgUser.id;
const userName = tgUser.first_name || 'User';
const userUsername = tgUser.username || '';

// Current state from DB
let currentLesson = 1;
const screenExam = document.getElementById('screen-exam');
const submitExamBtn = document.getElementById('submit-exam-btn');

// Modal Warning Screen helper
let currentWarningLang = userLang; // default to tg language

function showWarningScreen() {
    if (tg.HapticFeedback && typeof tg.HapticFeedback.notificationOccurred === 'function') {
        try { tg.HapticFeedback.notificationOccurred('warning'); } catch(e){}
    }
    screenLevel.classList.add('hidden');
    screenWarning.classList.remove('hidden');
    screenExam.classList.add('hidden');
    updateWarningText(currentWarningLang);
}

function updateWarningText(lang) {
    // Update active state of toggle buttons
    const langBtns = document.querySelectorAll('.modal-lang-btn');
    langBtns.forEach(btn => {
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // The user provided custom text in Uzbek/Russian hybrid
    let template = `
        <div style="text-align: left; font-size: 0.95rem; line-height: 1.5;">
            <strong>📜 Abdulaziz Nemis AI — Foydalanish Qoidalari va Ommaviy Oferta</strong><br><br>
            DIQQAT! Botdan foydalanishni boshlashdan oldin ushbu qoidalar va shartlar bilan to‘liq tanishib chiqing. "Да, я согласен" tugmasini bosish orqali siz ushbu qoidalarga so‘zsiz rozilik bildirasiz va ularni buzmaslik majburiyatini olasiz.<br><br>
            
            <strong>1. 🛡️ Kiberxavfsizlik va O‘zbekiston Respublikasi Qonunchiligi</strong><br>
            Ushbu botning dasturiy kodi, ma'lumotlar bazasi va unga ulangan Gemini Pro sun'iy intellekt tizimi mualliflik huquqi hamda O‘zbekiston Respublikasi qonunlari bilan qattiq himoyalangan. Botni buzishga (vzlom), dekompilyatsiya qilishga, ma'lumotlar bazasiga ruxsatsiz kirishga, tizimni o‘zgartirishga yoki serverga zararli hujumlar (DDoS/Spam) uyushtirishga bo‘lgan har qanday urinish mutlaqo taqiqlanadi. Qoidabuzarlik aniqlangan taqdirda, foydalanuvchining hisobi (ID) hech qanday ogohlantirishsiz va to‘langan pul qaytarilmasdan butunlay bloklanadi, uning IP-manzili hamda barcha tarmoq ma'lumotlari qayd etilib, huquqni muhofaza qilish organlariga topshiriladi. O‘zbekiston Respublikasi Jinoyat Kodeksining 278-moddasi, 278-1-moddasi va 278-6-moddasiga muvofiq jiddiy jinoiy javobgarlikka tortiladilar.<br><br>

            <strong>2. 🎴 Temir Intizom, Progress Tizimi va Jarimalar</strong><br>
            Nemis tilini noldan boshlab mukammal o‘rganish va real testlarga tayyorlanish faqat har kungi tinimsiz hamda tizimli mehnatni talab qiladi. Shu sababli, Abdulaziz Nemis AI botida qat'iy "Temir intizom" va jarima tizimi joriy etilgan. Agar siz 1 kun davomida kirmasa, darslarni qoldirsa yoki berilgan kunlik uy vazifasini topshirmasa, progress avtomatik raqishda 4 ta darsga orqaga qaytariladi. Masalan, 59-darajadan dars qoldirsangiz, progress darhol 55-darajaga tushirib yuboradi. Ushbu qoida barcha darajalar (A1, A2, B1, B2) uchun amal qiladi. Har bir bosqich yakunida faqat qattiq imtihon orqali keyingi darajaga o‘tiladi.<br><br>

            <strong>3. 💳 Obuna bo‘lish va To‘lov Shartlari</strong><br>
            Botdan to‘liq va cheksiz foydalanish muddati to‘lov tasdiqlangan kundan boshlab to‘g‘ri 1 oy (30 kun) etib belgilanadi. Oylik obuna narxi 100 000 so‘mni tashkil etadi. Hech qanday vositachilar va ortiqcha komissiyalarsiz, to‘lov to‘g‘ridan-to‘g‘ri Humo yoki Uzcard plastik kartasiga o‘tkaziladi hamda to‘lov amalga oshirilganligini tasdiqlovchi chek (skrinshot) tekshirish uchun botga yuboriladi. Intizomsizlik qilib belgilangan 30 kun ichida o‘z darajasini tugata olmagan o‘quvchilar keyingi oyga ham to‘lovni to‘liq amalga oshirishlari shart.
        </div>
    `;
    
    warningTextContent.innerHTML = template;
    document.getElementById('accept-btn-text').textContent = '🟢 Да, я согласен';
    
    // Check if decline btn exists
    const declineBtnText = document.getElementById('decline-btn-text');
    if(declineBtnText) declineBtnText.textContent = '❌ Нет, я не согласен';
    
    document.getElementById('warning-disclaimer-text').textContent = 'Qoidalarni diqqat bilan o\'qing';
}

// Bind language toggle buttons click
const langToggleBtns = document.querySelectorAll('.modal-lang-btn');
langToggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const selectedLang = btn.getAttribute('data-lang');
        currentWarningLang = selectedLang;
        updateWarningText(currentWarningLang);
        // Apply the language choice globally for the bot
        applyLanguage(selectedLang);
        // Optional: save to local storage so it remembers next time
        localStorage.setItem('userLang', selectedLang);
        if (tg.HapticFeedback && typeof tg.HapticFeedback.selectionChanged === 'function') {
            try { tg.HapticFeedback.selectionChanged(); } catch(e){}
        }
    });
});

// Fallback for cached HTML
if (!document.getElementById('lessons-list-view')) {
    const listHtml = `
    <div class="chat-container hidden" id="lessons-list-view">
        <header class="chat-header">
            <div class="header-left">
                <button class="action-btn back-btn" id="lessons-list-back-btn" title="Back to Menu" style="margin-right: 10px; font-size: 1.3rem;">
                    <i class="fa-solid fa-chevron-left"></i>
                </button>
                <div class="header-info">
                    <h1 class="header-title" id="lessons-list-title-text">DARSLAR RO'YXATI</h1>
                    <div class="header-status">
                        <span class="status-dot"></span>
                        <span class="status-text" id="lessons-list-status-text">60 LEKTIONEN</span>
                    </div>
                </div>
            </div>
        </header>
        <main class="dashboard-content" style="flex: 1; overflow-y: auto; padding: 20px;">
            <div class="level-grid" id="lessons-grid" style="grid-template-columns: repeat(4, 1fr); gap: 10px;">
            </div>
        </main>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', listHtml);
}

// View Navigation Map
const views = {
    dashboard: document.getElementById('dashboard-view'),
    chat: document.getElementById('chat-view'),
    lesson: document.getElementById('lesson-view'),
    lessonsList: document.getElementById('lessons-list-view')
};

function switchView(viewName) {
    Object.keys(views).forEach(key => {
        if (!views[key]) return;
        if (key === viewName) {
            views[key].classList.remove('hidden');
        } else {
            views[key].classList.add('hidden');
        }
    });
    
    if (viewName === 'dashboard') {
        renderDashboard();
    }
}

// Render Dashboard values dynamically
function renderDashboard() {
    const progressLabelText = document.getElementById('progress-label-text');
    const progressValueText = document.getElementById('progress-value-text');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const levelBadgeVal = document.getElementById('level-badge-val');
    
    const dashboardTitleText = document.getElementById('dashboard-title-text');
    const dashboardStatusText = document.getElementById('dashboard-status-text');
    
    const cardReadTitle = document.getElementById('card-read-title');
    const cardReadDesc = document.getElementById('card-read-desc');
    const cardChatTitle = document.getElementById('card-chat-title');
    const cardChatDesc = document.getElementById('card-chat-desc');
    const cardExamTitle = document.getElementById('card-exam-title');
    const cardExamDesc = document.getElementById('card-exam-desc');
    
    const completeBtnLbl = document.getElementById('complete-btn-lbl');
    const lessonLoadingText = document.getElementById('lesson-loading-text');

    // Populate localized dashboard elements
    dashboardTitleText.textContent = texts.dashboardTitle || "ABDULAZIZ GERMAN AI";
    dashboardStatusText.textContent = texts.dashboardStatus || "DEUTSCH TUTOR // ONLINE";
    
    // Populate profile details
    const nameEl = document.getElementById('profile-name');
    const usernameEl = document.getElementById('profile-username');
    const phoneEl = document.getElementById('profile-phone');
    
    if (nameEl) nameEl.textContent = userDetails.name;
    if (usernameEl) usernameEl.textContent = userDetails.username ? `@${userDetails.username.replace('@', '')}` : '';
    if (phoneEl) phoneEl.textContent = userDetails.phone || '';
    
    // Calculate and populate rating percentage
    const maxL = 60;
    const ratingPct = Math.min(100, Math.round(((currentLesson - 1) / maxL) * 100));
    const ratingValEl = document.getElementById('profile-rating-val');
    if (ratingValEl) {
        ratingValEl.textContent = `${ratingPct}%`;
    }
    
    // Localize rating label text
    const ratingLblText = document.getElementById('rating-lbl-text');
    if (ratingLblText) {
        ratingLblText.textContent = texts.ratingLabel || "O'qish reytingi / Рейтинг обучения:";
    }
    
    // Localize change level button
    const changeLevelBtnText = document.getElementById('change-level-btn-text');
    if (changeLevelBtnText) {
        changeLevelBtnText.textContent = texts.btnChangeLevel || "Darajalar / Уровни";
    }

    // Determine status badge
    let statusText = '';
    if (userLang === 'uz') {
        if (ratingPct >= 90) statusText = "Mukammal 👑";
        else if (ratingPct >= 70) statusText = "A'lochi 🌟";
        else if (ratingPct >= 40) statusText = "Yaxshi 👍";
        else if (ratingPct >= 15) statusText = "Harakatda 🚀";
        else statusText = "Boshlang'ich 🐣";
    } else if (userLang === 'ru') {
        if (ratingPct >= 90) statusText = "В совершенстве 👑";
        else if (ratingPct >= 70) statusText = "Отличник 🌟";
        else if (ratingPct >= 40) statusText = "Хорошо 👍";
        else if (ratingPct >= 15) statusText = "Активный 🚀";
        else statusText = "Начинающий 🐣";
    } else {
        if (ratingPct >= 90) statusText = "Perfekt 👑";
        else if (ratingPct >= 70) statusText = "Ausgezeichnet 🌟";
        else if (ratingPct >= 40) statusText = "Gut 👍";
        else if (ratingPct >= 15) statusText = "Aktiver Student 🚀";
        else statusText = "Anfänger 🐣";
    }

    const statusBadgeEl = document.getElementById('profile-status-badge');
    if (statusBadgeEl) {
        statusBadgeEl.textContent = statusText;
        if (ratingPct < 15) {
            statusBadgeEl.style.color = '#ff9900';
            statusBadgeEl.style.backgroundColor = 'rgba(255, 153, 0, 0.1)';
            statusBadgeEl.style.borderColor = 'rgba(255, 153, 0, 0.25)';
        } else if (ratingPct >= 90) {
            statusBadgeEl.style.color = 'var(--accent-gold)';
            statusBadgeEl.style.backgroundColor = 'rgba(255, 204, 0, 0.1)';
            statusBadgeEl.style.borderColor = 'rgba(255, 204, 0, 0.25)';
        } else {
            statusBadgeEl.style.color = '#00ff66';
            statusBadgeEl.style.backgroundColor = 'rgba(0, 255, 102, 0.1)';
            statusBadgeEl.style.borderColor = 'rgba(0, 255, 102, 0.25)';
        }
    }
    
    progressLabelText.textContent = texts.progressLabel || "Daraja progressi";
    progressValueText.textContent = `${texts.lektionLabel || "Lektion"}: ${currentLesson}/${maxL}`;
    
    const pct = Math.min(100, Math.floor(((currentLesson - 1) / maxL) * 100));
    progressBarFill.style.width = `${pct}%`;
    
    // Display level to users
    let cleanLevelName = selectedLevel;
    levelBadgeVal.textContent = cleanLevelName;
    
    cardReadTitle.textContent = texts.btnReadLessonTitle || "Darslar ro'yxati";
    cardReadDesc.textContent = texts.btnReadLessonDesc || "Barcha 60 ta darslar va mashqlar";
    cardChatTitle.textContent = texts.btnChatTutorTitle || "AI Repetitor bilan suhbat";
    cardChatDesc.textContent = texts.btnChatTutorDesc || "Savol-javob va mashq qilish";
    cardExamTitle.textContent = texts.btnTakeExamTitle || "Daraja Imtihonini topshirish";
    cardExamDesc.textContent = texts.btnTakeExamDesc || "60 ta dars tugagandan so'ng faollashadi";
    
    if (completeBtnLbl) completeBtnLbl.textContent = texts.completeLesson || "Darsni yakunlash";
    if (lessonLoadingText) lessonLoadingText.textContent = texts.loadingLesson || "Dars yuklanmoqda...";
    
    // Handle exam button enablement
    const btnTakeExam = document.getElementById('btn-take-exam');
    const examLockIcon = document.getElementById('exam-lock-icon');
    if (currentLesson >= maxL) {
        btnTakeExam.removeAttribute('disabled');
        if (examLockIcon) {
            examLockIcon.className = "fa-solid fa-chevron-right";
        }
    } else {
        btnTakeExam.setAttribute('disabled', 'true');
        if (examLockIcon) {
            examLockIcon.className = "fa-solid fa-lock";
        }
    }
}

// Timer for lesson
let timerInterval = null;
let lessonCompleteEnabled = false;

function startLessonTimer() {
    const timerBadge = document.getElementById('lesson-timer-badge');
    const completeBtn = document.getElementById('lesson-complete-btn');
    
    if (timerBadge) {
        timerBadge.style.display = 'none';
    }
    
    if (completeBtn) {
        completeBtn.style.opacity = '1';
        completeBtn.style.cursor = 'pointer';
    }
    lessonCompleteEnabled = true;
    
    if (timerInterval) clearInterval(timerInterval);
}

// Load Lesson Text dynamically
async function loadLesson(lessonNum = null) {
    const lessonTitleText = document.getElementById('lesson-title-text');
    const lessonStatusText = document.getElementById('lesson-status-text');
    const lessonLoading = document.getElementById('lesson-loading');
    const lessonTextContent = document.getElementById('lesson-text-content');
    const lessonFooter = document.getElementById('lesson-footer');
    
    const loadNum = lessonNum || currentLesson;
    
    // Set headers
    let displayLevel = selectedLevel;
    lessonTitleText.textContent = `${displayLevel} // Lektion ${loadNum}`;
    lessonStatusText.textContent = texts.loadingLesson;
    
    // Show spinner, hide content & footer
    lessonLoading.style.display = 'flex';
    lessonTextContent.style.display = 'none';
    lessonFooter.style.display = 'none';
    
    try {
        const response = await fetch(API_BASE + '/api/get_lesson', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, lesson_number: loadNum })
        });
        
        if (response.ok) {
            const data = await response.json();
            lessonTextContent.innerHTML = formatMarkdown(data.lesson_text);
            
            // Show content, hide spinner
            lessonLoading.style.display = 'none';
            lessonTextContent.style.display = 'block';
            
            // Only show complete button and timer if it's the current lesson we are supposed to finish
            if (loadNum === currentLesson) {
                lessonFooter.style.display = 'block';
                startLessonTimer();
            } else {
                lessonFooter.style.display = 'none';
                document.getElementById('lesson-timer-badge').style.display = 'none';
            }
            
            lessonStatusText.textContent = "LEARNING";
        } else {
            lessonLoading.style.display = 'none';
            lessonTextContent.innerHTML = `<p style="color: var(--accent-red); font-weight: bold; text-align: center;">Error loading lesson. Please try again.</p>`;
            lessonTextContent.style.display = 'block';
            lessonStatusText.textContent = "ERROR";
        }
    } catch (e) {
        console.error("Error loading lesson", e);
        lessonLoading.style.display = 'none';
        lessonTextContent.innerHTML = `<p style="color: var(--accent-red); font-weight: bold; text-align: center;">Network error. Please check your connection.</p>`;
        lessonTextContent.style.display = 'block';
        lessonStatusText.textContent = "ERROR";
    }
}

// User details global state
let userDetails = {
    name: userName,
    username: userUsername,
    phone: '',
    sub: 'none'
};

// Fetch progress from API
async function loadUserData() {
    try {
        const apiUrl = API_BASE + '/api/user_data';
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                name: userName,
                username: userUsername
            })
        });
        if (response.ok) {
            const data = await response.json();
            currentLesson = data.current_lesson || 1;
            selectedLevel = data.selected_level || '';
            userDetails.name = data.name || userName;
            userDetails.username = data.username || userUsername;
            userDetails.phone = data.phone || '';
            userDetails.sub = data.sub || 'none';
            
            // Har doim avval qoidalar (warning) oynasini ko'rsat
            welcomeModal.classList.remove('hidden');
            showWarningScreen();
        }
    } catch (e) {
        console.error("Error fetching user data", e);
        // API ishlamasa ham warning ko'rsat
        welcomeModal.classList.remove('hidden');
        showWarningScreen();
    }
}

// Bind level button clicks
const levelBtns = document.querySelectorAll('.level-btn');
levelBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
        const levelVal = btn.getAttribute('data-level');
        if (tg.HapticFeedback && typeof tg.HapticFeedback.selectionChanged === 'function') {
            try { tg.HapticFeedback.selectionChanged(); } catch(e){}
        }
        
        try {
            const response = await fetch(API_BASE + '/api/save_level', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    level: levelVal
                })
            });
            if (response.ok) {
                const resData = await response.json();
                selectedLevel = resData.selected_level;
                welcomeModal.classList.add('hidden');
                currentLesson = 1;
                switchView('dashboard');
            }
        } catch (e) {
            console.error("Error saving level", e);
        }
    });
});

// Accept challenge button handler
acceptChallengeBtn.addEventListener('click', () => {
    if (tg.HapticFeedback && typeof tg.HapticFeedback.notificationOccurred === 'function') {
        try { tg.HapticFeedback.notificationOccurred('success'); } catch(e){}
    }
    // Hide warning screen
    screenWarning.classList.add('hidden');
    
    // The user requested: "srazu menuga kirishi kerak" (immediately open dashboard)
    welcomeModal.classList.add('hidden');
    switchView('dashboard');
    renderDashboard();
});

// Decline challenge button handler
if (declineChallengeBtn) {
    declineChallengeBtn.addEventListener('click', () => {
        if (tg.HapticFeedback && typeof tg.HapticFeedback.notificationOccurred === 'function') {
            try { tg.HapticFeedback.notificationOccurred('error'); } catch(e){}
        }
        
        // Hide the action buttons and replace the content with the rejection text
        const warningActions = document.querySelector('.warning-actions');
        if (warningActions) warningActions.style.display = 'none';
        
        const disclaimer = document.getElementById('warning-disclaimer-text');
        if (disclaimer) disclaimer.style.display = 'none';
        
        document.getElementById('warning-title-text').textContent = "❌ RAD ETILDI";
        document.getElementById('warning-title-text').style.color = "#ef4444";
        
        warningTextContent.innerHTML = `
            <div style="text-align: center; font-size: 1.1rem; line-height: 1.6; padding: 20px 0; color: #f87171;">
                Biz tushunamiz, sizga shunchaki dangasalik qilyapti. Lekin unutmang, bu qoidalarning barchasi faqat va faqat sizning foydangiz uchun!<br><br>
                Nemis tilini temir intizomsiz o‘rganib bo‘lmaydi. Qachonki o‘zingizda kuch topib, dangasalikni yengib, natijaga erishishni chin dildan xohlasangiz — qaytib keling va qoidalarni qabul qiling!
            </div>
            <button onclick="tg.close()" style="margin-top: 20px; background: #3b82f6; border: none; color: white; border-radius: 12px; padding: 14px; width: 100%; font-weight: bold; cursor: pointer;">
                Chiqish
            </button>
        `;
    });
}

const EXAM_QUESTIONS = {
    'A1': [
        {
            q: "1. What does 'Guten Morgen' mean?",
            options: ["Good morning", "Good evening", "Good night"],
            correct: 0
        },
        {
            q: "2. How do you say 'Thank you' in German?",
            options: ["Bitte", "Danke", "Tschüss"],
            correct: 1
        },
        {
            q: "3. What is 'Wasser'?",
            options: ["Bread", "Water", "Milk"],
            correct: 1
        }
    ],
    'A1': [
        {
            q: "1. Translate: 'Ich wohne in Berlin.'",
            options: ["I live in Berlin", "I work in Berlin", "I am visiting Berlin"],
            correct: 0
        },
        {
            q: "2. Which is the correct article for 'Apfel' (Apple)?",
            options: ["der", "die", "das"],
            correct: 0
        },
        {
            q: "3. Translate: 'Wie alt bist du?'",
            options: ["How are you?", "How old are you?", "What is your name?"],
            correct: 1
        }
    ],
    'A2': [
        {
            q: "1. What is the past participle of 'machen'?",
            options: ["gemacht", "gemach", "gemachen"],
            correct: 0
        },
        {
            q: "2. Complete: 'Ich habe ein ____ Auto gekauft.'",
            options: ["neues", "neu", "neuen"],
            correct: 0
        },
        {
            q: "3. Which preposition requires the dative case?",
            options: ["mit", "für", "ohne"],
            correct: 0
        }
    ],
    'B1': [
        {
            q: "1. Which conjunction requires subordinate clause word order (verb at the end)?",
            options: ["weil", "aber", "denn"],
            correct: 0
        },
        {
            q: "2. Complete: 'Wenn ich reich ____, würde ich ein Haus kaufen.'",
            options: ["wäre", "bin", "wurde"],
            correct: 0
        },
        {
            q: "3. Translate: 'Ich freue mich auf die B1-Prüfung.'",
            options: ["I am looking forward to the B1 exam", "I am afraid of the B1 exam", "I passed the B1 exam"],
            correct: 0
        }
    ],
    'B2': [
        {
            q: "1. Complete: 'Je mehr ich lerne, ____ besser werde ich.'",
            options: ["desto", "umso", "als"],
            correct: 0
        },
        {
            q: "2. Complete: 'Es ist wichtig, ____ die Hausaufgaben zu machen.'",
            options: ["um", "ohne", "zu"],
            correct: 2
        },
        {
            q: "3. What is the meaning of 'ausgezeichnet'?",
            options: ["Excellent", "Average", "Bad"],
            correct: 0
        }
    ]
};

function renderExam(lvl) {
    const qContent = document.getElementById('exam-questions-content');
    qContent.innerHTML = '';
    const qList = EXAM_QUESTIONS[lvl] || EXAM_QUESTIONS['A1'];
    
    qList.forEach((q, idx) => {
        const qDiv = document.createElement('div');
        qDiv.style.marginBottom = '20px';
        qDiv.innerHTML = `<p style="font-weight: 700; margin-bottom: 8px; color: var(--text-bright);">${q.q}</p>`;
        
        q.options.forEach((opt, optIdx) => {
            qDiv.innerHTML += `
                <label style="display: block; margin-bottom: 6px; cursor: pointer;">
                    <input type="radio" name="q_${idx}" value="${optIdx}" style="margin-right: 8px;">
                    ${opt}
                </label>
            `;
        });
        qContent.appendChild(qDiv);
    });
}

// Complete current lesson action
const lessonCompleteBtn = document.getElementById('lesson-complete-btn');
lessonCompleteBtn.addEventListener('click', async () => {
    if (!lessonCompleteEnabled) {
        alert(userLang === 'uz' ? "Iltimos, darsni yakunlash uchun 10 daqiqalik vaqt tugashini kuting!" : (userLang === 'ru' ? "Пожалуйста, подождите 10 минут, чтобы завершить урок!" : "Please wait 10 minutes to complete the lesson!"));
        return;
    }
    if (!confirm(texts.completeLessonConfirm || "Darsni yakunlashni tasdiqlaysizmi?")) {
        return;
    }
    
    if (tg.HapticFeedback && typeof tg.HapticFeedback.notificationOccurred === 'function') {
        try { tg.HapticFeedback.notificationOccurred('success'); } catch(e){}
    }
    
    if (timerInterval) clearInterval(timerInterval);
    
    try {
        const response = await fetch(API_BASE + '/api/complete_lesson', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.status === 'exam_ready') {
                alert(userLang === 'uz' ? "🎉 Dars yakunlandi! Darajani oshirish imtihonini topshirish vaqti keldi." : (userLang === 'ru' ? "🎉 Урок завершен! Время сдать экзамен на повышение уровня." : "🎉 Lesson completed! Time to take the level promotion exam."));
                
                // Show Exam Modal!
                welcomeModal.classList.remove('hidden');
                screenWarning.classList.add('hidden');
                screenLevel.classList.add('hidden');
                screenExam.classList.remove('hidden');
                renderExam(selectedLevel);
            } else {
                currentLesson = data.current_lesson;
                alert(texts.lessonCompletedMsg || "Dars yakunlandi!");
                switchView('dashboard');
            }
        } else {
            alert("Error completing lesson.");
        }
    } catch (e) {
        console.error("Error completing lesson", e);
        alert("Network error.");
    }
});

// Submit exam button handler
submitExamBtn.addEventListener('click', async () => {
    const qList = EXAM_QUESTIONS[selectedLevel] || EXAM_QUESTIONS['A1'];
    let passed = true;
    
    for (let i = 0; i < qList.length; i++) {
        const checked = document.querySelector(`input[name="q_${i}"]:checked`);
        if (!checked || parseInt(checked.value) !== qList[i].correct) {
            passed = false;
            break;
        }
    }
    
    if (!passed) {
        if (tg.HapticFeedback && typeof tg.HapticFeedback.notificationOccurred === 'function') {
            try { tg.HapticFeedback.notificationOccurred('error'); } catch(e){}
        }
        
        try {
            await fetch(API_BASE + '/api/fail_exam', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
        } catch (err) {
            console.error("Error reporting failed exam", err);
        }
        
        alert(userLang === 'uz' ? 
            "Imtihondan o'ta olmadingiz! Sizning progresingiz ushbu darajaning 1-darsiga qaytarildi." : 
            (userLang === 'ru' ? 
                "Вы завалили экзамен! Ваш прогресс сброшен на 1-й урок текущего уровня." : 
                "You failed the exam! Your progress has been reset to lesson 1 of this level."));
        
        currentLesson = 1;
        welcomeModal.classList.add('hidden');
        switchView('dashboard');
        return;
    }
    
    if (tg.HapticFeedback && typeof tg.HapticFeedback.notificationOccurred === 'function') {
        try { tg.HapticFeedback.notificationOccurred('success'); } catch(e){}
    }
    
    // Save passed exam to advance level
    try {
        const response = await fetch(API_BASE + '/api/pass_exam', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });
        if (response.ok) {
            const data = await response.json();
            const prevLevelDisplay = selectedLevel;
            selectedLevel = data.selected_level;
            currentLesson = 1;
            welcomeModal.classList.add('hidden');
            
            let levelUpMsg = userLang === 'uz' ? `🎓 Ajoyib! Siz ${prevLevelDisplay} imtihonidan muvaffaqiyatli o'tdingiz. Yangi darajangiz: ${selectedLevel}!` : (userLang === 'ru' ? `🎓 Отлично! Вы успешно сдали экзамен ${prevLevelDisplay}. Ваш новый уровень: ${selectedLevel}!` : `🎓 Great job! You successfully passed the exam for ${prevLevelDisplay}. Your new level is: ${selectedLevel}!`);
            alert(levelUpMsg);
            switchView('dashboard');
        }
    } catch (e) {
        console.error("Error passing exam", e);
    }
});

function renderLessonsList() {
    const grid = document.getElementById('lessons-grid');
    if (!grid) return;
    grid.innerHTML = '';
    const maxL = 60;
    
    const titleText = document.getElementById('lessons-list-title-text');
    if (titleText) titleText.textContent = (texts.btnReadLessonTitle || "Darslar ro'yxati").toUpperCase();
    
    for (let i = 1; i <= maxL; i++) {
        const btn = document.createElement('button');
        btn.classList.add('level-btn');
        btn.style.width = '100%';
        btn.style.height = '60px';
        btn.style.padding = '0';
        btn.style.display = 'flex';
        btn.style.alignItems = 'center';
        btn.style.justifyContent = 'center';
        btn.style.fontSize = '1.2rem';
        btn.textContent = i;
        
        if (i < currentLesson) {
            btn.style.background = 'rgba(0, 150, 255, 0.15)';
            btn.style.borderColor = '#0096ff';
            btn.style.color = '#0096ff';
            btn.onclick = () => {
                switchView('lesson');
                loadLesson(i);
            };
        } else if (i === currentLesson) {
            btn.style.background = 'linear-gradient(135deg, var(--accent-gold) 0%, #cc9900 100%)';
            btn.style.borderColor = 'var(--accent-gold)';
            btn.style.color = '#000';
            btn.style.boxShadow = '0 0 10px rgba(255, 204, 0, 0.4)';
            btn.onclick = () => {
                switchView('lesson');
                loadLesson(i);
            };
        } else {
            btn.style.background = 'rgba(255, 255, 255, 0.05)';
            btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            btn.style.color = 'rgba(255, 255, 255, 0.3)';
            btn.style.cursor = 'not-allowed';
        }
        grid.appendChild(btn);
    }
}

// Dashboard button clicks
document.getElementById('btn-read-lesson').addEventListener('click', () => {
    switchView('lessonsList');
    renderLessonsList();
});

document.getElementById('btn-chat-tutor').addEventListener('click', () => {
    switchView('chat');
    renderChat();
});

document.getElementById('change-level-btn').addEventListener('click', () => {
    if (tg.HapticFeedback && typeof tg.HapticFeedback.notificationOccurred === 'function') {
        try { tg.HapticFeedback.notificationOccurred('success'); } catch(e){}
    }
    welcomeModal.classList.remove('hidden');
    screenWarning.classList.add('hidden');
    screenLevel.classList.remove('hidden');
    screenExam.classList.add('hidden');
});

document.getElementById('btn-take-exam').addEventListener('click', () => {
    welcomeModal.classList.remove('hidden');
    screenWarning.classList.add('hidden');
    screenLevel.classList.add('hidden');
    screenExam.classList.remove('hidden');
    renderExam(selectedLevel);
});

document.getElementById('rules-btn').addEventListener('click', () => {
    welcomeModal.classList.remove('hidden');
    screenWarning.classList.remove('hidden');
    screenLevel.classList.add('hidden');
    screenExam.classList.add('hidden');
    updateWarningText(currentWarningLang);
});

// Back buttons
document.getElementById('chat-back-btn').addEventListener('click', () => {
    switchView('dashboard');
});

const lessonsListBackBtn = document.getElementById('lessons-list-back-btn');
if (lessonsListBackBtn && !lessonsListBackBtn.hasAttribute('data-listener')) {
    lessonsListBackBtn.setAttribute('data-listener', 'true');
    lessonsListBackBtn.addEventListener('click', () => {
        switchView('dashboard');
    });
}

document.getElementById('lesson-back-btn').addEventListener('click', () => {
    switchView('lessonsList');
});

// Init
applyLanguage(userLang);
loadUserData();
