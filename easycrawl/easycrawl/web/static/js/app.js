/**
 * EasyCrawl 웹 UI - 프론트엔드 로직
 */

// 전역 상태
const state = {
    crawlers: [],
    currentCrawler: null,
    currentRun: null,
    socket: null
};

// Socket.IO 연결
function initSocket() {
    state.socket = io();

    state.socket.on('connect', () => {
        console.log('WebSocket 연결됨');
        updateConnectionStatus(true);
    });

    state.socket.on('disconnect', () => {
        console.log('WebSocket 연결 해제됨');
        updateConnectionStatus(false);
    });

    state.socket.on('crawler_progress', (data) => {
        console.log('크롤러 진행상황:', data);
        updateRunProgress(data);
    });

    state.socket.on('crawler_finished', (data) => {
        console.log('크롤러 완료:', data);
        showNotification('크롤러 실행 완료!', 'success');
        loadCrawlers();
    });
}

// 연결 상태 업데이트
function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connection-status');
    if (connected) {
        statusEl.innerHTML = `
            <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span class="text-gray-400">연결됨</span>
        `;
    } else {
        statusEl.innerHTML = `
            <div class="w-2 h-2 rounded-full bg-red-500"></div>
            <span class="text-gray-400">연결 끊김</span>
        `;
    }
}

// 크롤러 목록 로드
async function loadCrawlers(search = '') {
    try {
        const response = await fetch(`/api/crawlers?search=${encodeURIComponent(search)}`);
        const data = await response.json();

        state.crawlers = data.crawlers;
        renderCrawlerList();
    } catch (error) {
        console.error('크롤러 목록 로드 실패:', error);
        showNotification('크롤러 목록을 불러올 수 없습니다', 'error');
    }
}

// 크롤러 목록 렌더링
function renderCrawlerList() {
    const listEl = document.getElementById('crawler-list');

    if (state.crawlers.length === 0) {
        listEl.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-2 opacity-50"></i>
                <p class="text-sm">크롤러가 없습니다</p>
                <p class="text-xs mt-1">새 크롤러를 만들어보세요!</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    listEl.innerHTML = state.crawlers.map(crawler => `
        <div
            class="sidebar-item p-3 rounded-lg cursor-pointer ${state.currentCrawler?.id === crawler.id ? 'bg-zinc-800' : ''}"
            onclick="selectCrawler(${crawler.id})">
            <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-semibold text-white truncate">${escapeHtml(crawler.name)}</h4>
                    <p class="text-xs text-gray-500 truncate mt-1">${escapeHtml(crawler.description || '설명 없음')}</p>
                    <p class="text-xs text-gray-600 mt-1">${formatDate(crawler.created_at)}</p>
                </div>
                <div class="ml-2">
                    <i data-lucide="chevron-right" class="w-4 h-4 text-gray-600"></i>
                </div>
            </div>
        </div>
    `).join('');

    lucide.createIcons();
}

// 크롤러 선택
async function selectCrawler(crawlerId) {
    try {
        const response = await fetch(`/api/crawlers/${crawlerId}`);
        const data = await response.json();

        state.currentCrawler = data.crawler;
        renderCrawlerDetail();
    } catch (error) {
        console.error('크롤러 로드 실패:', error);
        showNotification('크롤러를 불러올 수 없습니다', 'error');
    }
}

// 크롤러 상세 화면 렌더링
function renderCrawlerDetail() {
    const createForm = document.getElementById('create-form');
    const detailView = document.getElementById('crawler-detail');

    createForm.classList.add('hidden');
    detailView.classList.remove('hidden');

    const crawler = state.currentCrawler;
    const latestRun = crawler.recent_runs && crawler.recent_runs[0];

    document.getElementById('main-title').textContent = crawler.name;
    document.getElementById('main-subtitle').textContent = crawler.description || '설명 없음';

    detailView.innerHTML = `
        <!-- 기본 정보 -->
        <div class="bg-zinc-900 rounded-xl p-6 border border-zinc-800">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-bold flex items-center gap-2">
                    <i data-lucide="info" class="w-6 h-6 text-blue-500"></i>
                    크롤러 정보
                </h3>
                <button
                    onclick="deleteCrawler(${crawler.id})"
                    class="text-red-500 hover:text-red-400 flex items-center gap-1 text-sm">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                    삭제
                </button>
            </div>

            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <p class="text-gray-500">출력 형식</p>
                    <p class="text-white font-semibold mt-1">${crawler.output_format.toUpperCase()}</p>
                </div>
                <div>
                    <p class="text-gray-500">요청 딜레이</p>
                    <p class="text-white font-semibold mt-1">${crawler.request_delay}ms</p>
                </div>
                <div>
                    <p class="text-gray-500">생성일</p>
                    <p class="text-white font-semibold mt-1">${formatDate(crawler.created_at)}</p>
                </div>
                <div>
                    <p class="text-gray-500">기본 URL</p>
                    <p class="text-white font-semibold mt-1 truncate">${crawler.spec?.base_url || 'N/A'}</p>
                </div>
            </div>
        </div>

        <!-- 실행 컨트롤 -->
        <div class="bg-zinc-900 rounded-xl p-6 border border-zinc-800">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                <i data-lucide="play-circle" class="w-6 h-6 text-green-500"></i>
                크롤러 실행
            </h3>

            <div id="run-controls" class="space-y-4">
                ${renderRunControls(latestRun)}
            </div>

            ${latestRun ? renderRunStatus(latestRun) : ''}
        </div>

        <!-- 최근 실행 기록 -->
        ${crawler.recent_runs && crawler.recent_runs.length > 0 ? `
            <div class="bg-zinc-900 rounded-xl p-6 border border-zinc-800">
                <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                    <i data-lucide="history" class="w-6 h-6 text-purple-500"></i>
                    최근 실행 기록
                </h3>

                <div class="space-y-2">
                    ${crawler.recent_runs.map(run => `
                        <div class="flex items-center justify-between p-3 bg-zinc-800 rounded-lg">
                            <div class="flex items-center gap-3">
                                ${getStatusBadge(run.status)}
                                <div>
                                    <p class="text-sm text-white">수집: ${run.collected_items}개</p>
                                    <p class="text-xs text-gray-500">${formatDate(run.started_at)}</p>
                                </div>
                            </div>
                            <div class="text-sm text-gray-400">
                                ${run.progress}%
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}

        <!-- 생성된 코드 보기 -->
        <div class="bg-zinc-900 rounded-xl p-6 border border-zinc-800">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                <i data-lucide="file-code" class="w-6 h-6 text-yellow-500"></i>
                생성된 코드
            </h3>

            <button
                onclick="viewCode(${crawler.id})"
                class="w-full bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-3 rounded-lg flex items-center justify-center gap-2 transition">
                <i data-lucide="eye" class="w-5 h-5"></i>
                코드 보기
            </button>
        </div>

        <!-- 데이터 다운로드 -->
        <div class="bg-zinc-900 rounded-xl p-6 border border-zinc-800">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                <i data-lucide="download" class="w-6 h-6 text-blue-500"></i>
                데이터 다운로드
            </h3>

            <button
                onclick="downloadData(${crawler.id})"
                class="w-full bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-3 rounded-lg flex items-center justify-center gap-2 transition">
                <i data-lucide="download" class="w-5 h-5"></i>
                수집 데이터 다운로드
            </button>
        </div>
    `;

    lucide.createIcons();
}

// 실행 컨트롤 버튼 렌더링
function renderRunControls(latestRun) {
    if (!latestRun || latestRun.status === 'completed' || latestRun.status === 'failed' || latestRun.status === 'cancelled') {
        return `
            <div class="flex gap-3">
                <button
                    onclick="startCrawler(${state.currentCrawler.id}, false)"
                    class="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-4 rounded-lg font-semibold btn-hover flex items-center justify-center gap-2">
                    <i data-lucide="play" class="w-5 h-5"></i>
                    ${latestRun ? '이어서 실행' : '실행하기'}
                </button>
                ${latestRun ? `
                    <button
                        onclick="startCrawler(${state.currentCrawler.id}, true)"
                        class="flex-1 bg-zinc-800 hover:bg-zinc-700 text-white px-6 py-4 rounded-lg font-semibold btn-hover flex items-center justify-center gap-2">
                        <i data-lucide="refresh-cw" class="w-5 h-5"></i>
                        처음부터 다시
                    </button>
                ` : ''}
            </div>
        `;
    } else if (latestRun.status === 'running') {
        return `
            <div class="flex gap-3">
                <button
                    onclick="pauseCrawler(${latestRun.id})"
                    class="flex-1 bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-4 rounded-lg font-semibold btn-hover flex items-center justify-center gap-2">
                    <i data-lucide="pause" class="w-5 h-5"></i>
                    일시정지
                </button>
                <button
                    onclick="stopCrawler(${latestRun.id})"
                    class="flex-1 bg-red-600 hover:bg-red-700 text-white px-6 py-4 rounded-lg font-semibold btn-hover flex items-center justify-center gap-2">
                    <i data-lucide="square" class="w-5 h-5"></i>
                    중지하기
                </button>
            </div>
        `;
    } else if (latestRun.status === 'paused') {
        return `
            <div class="flex gap-3">
                <button
                    onclick="resumeCrawler(${latestRun.id})"
                    class="flex-1 bg-green-600 hover:bg-green-700 text-white px-6 py-4 rounded-lg font-semibold btn-hover flex items-center justify-center gap-2">
                    <i data-lucide="play" class="w-5 h-5"></i>
                    재개하기
                </button>
                <button
                    onclick="stopCrawler(${latestRun.id})"
                    class="flex-1 bg-red-600 hover:bg-red-700 text-white px-6 py-4 rounded-lg font-semibold btn-hover flex items-center justify-center gap-2">
                    <i data-lucide="square" class="w-5 h-5"></i>
                    중지하기
                </button>
            </div>
        `;
    }

    return '';
}

// 실행 상태 렌더링
function renderRunStatus(run) {
    return `
        <div class="mt-6 p-4 bg-zinc-800 rounded-lg">
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm text-gray-400">진행 상황</span>
                <span class="text-sm font-semibold text-white">${run.progress}%</span>
            </div>
            <div class="w-full bg-zinc-700 rounded-full h-2 mb-3">
                <div
                    id="progress-bar"
                    class="progress-bar bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                    style="width: ${run.progress}%"></div>
            </div>
            <div class="flex items-center justify-between text-xs text-gray-500">
                <span>수집: ${run.collected_items || 0}개</span>
                <span>${getStatusText(run.status)}</span>
            </div>
        </div>
    `;
}

// 상태 배지
function getStatusBadge(status) {
    const badges = {
        'draft': '<span class="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">대기</span>',
        'running': '<span class="px-2 py-1 bg-green-700 text-green-300 rounded text-xs">실행 중</span>',
        'paused': '<span class="px-2 py-1 bg-yellow-700 text-yellow-300 rounded text-xs">일시정지</span>',
        'completed': '<span class="px-2 py-1 bg-blue-700 text-blue-300 rounded text-xs">완료</span>',
        'failed': '<span class="px-2 py-1 bg-red-700 text-red-300 rounded text-xs">실패</span>',
        'cancelled': '<span class="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">취소</span>'
    };
    return badges[status] || badges['draft'];
}

// 상태 텍스트
function getStatusText(status) {
    const texts = {
        'draft': '대기 중',
        'running': '실행 중...',
        'paused': '일시정지됨',
        'completed': '완료됨',
        'failed': '실패',
        'cancelled': '취소됨'
    };
    return texts[status] || '알 수 없음';
}

// 크롤러 시작
async function startCrawler(crawlerId, fromScratch) {
    try {
        showNotification('크롤러를 시작합니다...', 'info');

        const response = await fetch(`/api/crawlers/${crawlerId}/start`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({from_scratch: fromScratch})
        });

        const data = await response.json();

        if (data.success) {
            showNotification('크롤러가 시작되었습니다!', 'success');
            state.currentRun = {id: data.run_id};
            setTimeout(() => selectCrawler(crawlerId), 1000);
        } else {
            showNotification(`오류: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('크롤러 시작 실패', 'error');
    }
}

// 크롤러 일시정지
async function pauseCrawler(runId) {
    try {
        const response = await fetch(`/api/runs/${runId}/pause`, {method: 'POST'});
        const data = await response.json();

        if (data.success) {
            showNotification('일시정지되었습니다', 'success');
            selectCrawler(state.currentCrawler.id);
        }
    } catch (error) {
        showNotification('일시정지 실패', 'error');
    }
}

// 크롤러 재개
async function resumeCrawler(runId) {
    try {
        const response = await fetch(`/api/runs/${runId}/resume`, {method: 'POST'});
        const data = await response.json();

        if (data.success) {
            showNotification('재개되었습니다', 'success');
            selectCrawler(state.currentCrawler.id);
        }
    } catch (error) {
        showNotification('재개 실패', 'error');
    }
}

// 크롤러 중지
async function stopCrawler(runId) {
    if (!confirm('정말 크롤러를 중지하시겠습니까?')) return;

    try {
        const response = await fetch(`/api/runs/${runId}/stop`, {method: 'POST'});
        const data = await response.json();

        if (data.success) {
            showNotification('중지되었습니다', 'success');
            selectCrawler(state.currentCrawler.id);
        }
    } catch (error) {
        showNotification('중지 실패', 'error');
    }
}

// 크롤러 삭제
async function deleteCrawler(crawlerId) {
    if (!confirm('정말 이 크롤러를 삭제하시겠습니까? 실행 기록도 모두 삭제됩니다.')) return;

    try {
        const response = await fetch(`/api/crawlers/${crawlerId}`, {method: 'DELETE'});
        const data = await response.json();

        if (data.success) {
            showNotification('삭제되었습니다', 'success');
            showCreateForm();
            loadCrawlers();
        }
    } catch (error) {
        showNotification('삭제 실패', 'error');
    }
}

// 코드 보기
async function viewCode(crawlerId) {
    try {
        const response = await fetch(`/api/crawlers/${crawlerId}/code`);
        const data = await response.json();

        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4';
        modal.innerHTML = `
            <div class="bg-zinc-900 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
                <div class="p-4 border-b border-zinc-800 flex items-center justify-between">
                    <h3 class="text-lg font-bold text-white">생성된 크롤러 코드</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-white">
                        <i data-lucide="x" class="w-6 h-6"></i>
                    </button>
                </div>
                <div class="p-4 overflow-y-auto max-h-[calc(90vh-80px)]">
                    <pre class="text-sm text-gray-300 bg-zinc-950 p-4 rounded-lg overflow-x-auto"><code>${escapeHtml(data.code)}</code></pre>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        lucide.createIcons();
    } catch (error) {
        showNotification('코드를 불러올 수 없습니다', 'error');
    }
}

// 데이터 다운로드
function downloadData(crawlerId) {
    window.location.href = `/api/crawlers/${crawlerId}/download`;
}

// 실행 진행상황 업데이트 (WebSocket)
function updateRunProgress(data) {
    if (!state.currentRun || state.currentRun.id !== data.run_id) return;

    const progressBar = document.getElementById('progress-bar');
    if (progressBar) {
        progressBar.style.width = `${data.progress}%`;
    }

    // 필요시 전체 화면 갱신
    if (data.collected % 100 === 0) {  // 100개마다 새로고침
        selectCrawler(state.currentCrawler.id);
    }
}

// 새 크롤러 생성 폼 표시
function showCreateForm() {
    const createForm = document.getElementById('create-form');
    const detailView = document.getElementById('crawler-detail');

    createForm.classList.remove('hidden');
    detailView.classList.add('hidden');

    state.currentCrawler = null;

    document.getElementById('main-title').textContent = '크롤러 만들기';
    document.getElementById('main-subtitle').textContent = 'AI가 자동으로 웹 크롤러를 만들어드립니다';
}

// 크롤러 생성
async function createCrawler() {
    const name = document.getElementById('crawler-name').value.trim();
    const description = document.getElementById('crawler-description').value.trim();
    const apiKey = document.getElementById('api-key').value.trim();
    const curlCommand = document.getElementById('curl-command').value.trim();
    const outputFormat = document.getElementById('output-format').value;
    const requestDelay = parseInt(document.getElementById('request-delay').value);
    const additionalInfo = document.getElementById('additional-info').value.trim();

    if (!name || !apiKey || !curlCommand) {
        showNotification('필수 항목을 모두 입력해주세요', 'error');
        return;
    }

    const statusEl = document.getElementById('create-status');
    statusEl.classList.remove('hidden');
    statusEl.innerHTML = `
        <div class="bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg p-4 text-center">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-2"></div>
            <p class="text-sm text-blue-300">AI가 분석하고 있습니다...</p>
        </div>
    `;

    try {
        const response = await fetch('/api/crawlers', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name,
                description,
                api_key: apiKey,
                curl_command: curlCommand,
                output_format: outputFormat,
                request_delay: requestDelay,
                additional_info: additionalInfo
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('크롤러가 생성되었습니다!', 'success');
            loadCrawlers();
            selectCrawler(data.crawler.id);
        } else {
            showNotification(`오류: ${data.error}`, 'error');
            statusEl.classList.add('hidden');
        }
    } catch (error) {
        showNotification('크롤러 생성 실패', 'error');
        statusEl.classList.add('hidden');
    }
}

// 알림 표시
function showNotification(message, type = 'info') {
    const colors = {
        'info': 'bg-blue-600',
        'success': 'bg-green-600',
        'error': 'bg-red-600',
        'warning': 'bg-yellow-600'
    };

    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 fade-in`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// 유틸리티 함수들
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 이벤트 리스너
document.addEventListener('DOMContentLoaded', () => {
    // Socket.IO 초기화
    initSocket();

    // 크롤러 목록 로드
    loadCrawlers();

    // 새 크롤러 만들기 버튼
    document.getElementById('btn-new-crawler').addEventListener('click', showCreateForm);

    // 생성 버튼
    document.getElementById('btn-create').addEventListener('click', createCrawler);

    // 검색
    let searchTimeout;
    document.getElementById('search-input').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadCrawlers(e.target.value);
        }, 300);
    });
});
