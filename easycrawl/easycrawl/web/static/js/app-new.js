/**
 * EasyCrawl 웹 UI - 메인 애플리케이션
 * 모듈화된 구조
 */

import { API } from './modules/api.js';
import { UI } from './modules/ui.js';
import { BatchManager } from './modules/batch.js';

// 전역 상태
const state = {
    crawlers: [],
    currentCrawler: null,
    currentRun: null,
    socket: null,
    batchManager: new BatchManager()
};

// 전역 함수로 노출 (HTML onclick에서 사용)
window.selectCrawler = selectCrawler;
window.toggleCrawlerSelection = (id) => state.batchManager.toggleSelection(id);
window.clearSelection = () => state.batchManager.clearSelection();
window.showBatchModeModal = () => state.batchManager.showModeModal();
window.batchStop = () => state.batchManager.stopBatch();
window.batchPause = () => state.batchManager.pauseBatch();
window.deleteCrawler = deleteCrawler;
window.startCrawler = startCrawler;
window.pauseCrawler = pauseCrawler;
window.resumeCrawler = resumeCrawler;
window.stopCrawler = stopCrawler;
window.viewCode = viewCode;
window.downloadData = downloadData;
window.loadCrawlers = loadCrawlers;

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
        updateRunProgress(data);
    });

    state.socket.on('crawler_finished', (data) => {
        UI.showNotification('크롤러 실행 완료!', 'success');
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
        const data = await API.getCrawlers(search);
        state.crawlers = data.crawlers;
        UI.renderCrawlerList(
            state.crawlers,
            state.batchManager.selectedCrawlers,
            state.currentCrawler?.id
        );
    } catch (error) {
        console.error('크롤러 목록 로드 실패:', error);
        UI.showNotification('크롤러 목록을 불러올 수 없습니다', 'error');
    }
}

// 크롤러 선택
async function selectCrawler(crawlerId) {
    try {
        const data = await API.getCrawler(crawlerId);
        state.currentCrawler = data.crawler;
        renderCrawlerDetail();
    } catch (error) {
        console.error('크롤러 로드 실패:', error);
        UI.showNotification('크롤러를 불러올 수 없습니다', 'error');
    }
}

// 크롤러 상세 화면
function renderCrawlerDetail() {
    // 기존 app.js의 renderCrawlerDetail 함수 로직 유지
    const createForm = document.getElementById('create-form');
    const detailView = document.getElementById('crawler-detail');

    createForm.classList.add('hidden');
    detailView.classList.remove('hidden');

    const crawler = state.currentCrawler;
    const latestRun = crawler.recent_runs && crawler.recent_runs[0];

    document.getElementById('main-title').textContent = crawler.name;
    document.getElementById('main-subtitle').textContent = crawler.description || '설명 없음';

    detailView.innerHTML = `
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
            </div>
        </div>

        <div class="bg-zinc-900 rounded-xl p-6 border border-zinc-800">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                <i data-lucide="play-circle" class="w-6 h-6 text-green-500"></i>
                크롤러 실행
            </h3>
            <div id="run-controls" class="space-y-4">
                ${renderRunControls(latestRun, crawler.id)}
            </div>
            ${latestRun ? renderRunStatus(latestRun) : ''}
        </div>
    `;

    lucide.createIcons();
}

// 실행 컨트롤 버튼
function renderRunControls(latestRun, crawlerId) {
    if (!latestRun || ['completed', 'failed', 'cancelled'].includes(latestRun.status)) {
        return `
            <div class="flex gap-3">
                <button
                    onclick="showStartModeModal(${crawlerId})"
                    class="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-4 rounded-lg font-semibold btn-hover flex items-center justify-center gap-2">
                    <i data-lucide="play" class="w-5 h-5"></i>
                    실행하기
                </button>
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
                <span>${UI.getStatusText(run.status)}</span>
            </div>
        </div>
    `;
}

// 수집 모드 선택 후 시작
window.showStartModeModal = function(crawlerId) {
    UI.showCollectionModeModal((mode) => {
        startCrawler(crawlerId, mode);
    });
};

// 크롤러 시작
async function startCrawler(crawlerId, collectionMode = 'incremental') {
    try {
        UI.showNotification('크롤러를 시작합니다...', 'info');
        const data = await API.startCrawler(crawlerId, collectionMode);

        if (data.success) {
            UI.showNotification('크롤러가 시작되었습니다!', 'success');
            setTimeout(() => selectCrawler(crawlerId), 1000);
        } else {
            UI.showNotification(`오류: ${data.error}`, 'error');
        }
    } catch (error) {
        UI.showNotification('크롤러 시작 실패', 'error');
    }
}

// 실행 제어
async function pauseCrawler(runId) {
    try {
        await API.pauseRun(runId);
        UI.showNotification('일시정지되었습니다', 'success');
        selectCrawler(state.currentCrawler.id);
    } catch (error) {
        UI.showNotification('일시정지 실패', 'error');
    }
}

async function resumeCrawler(runId) {
    try {
        await API.resumeRun(runId);
        UI.showNotification('재개되었습니다', 'success');
        selectCrawler(state.currentCrawler.id);
    } catch (error) {
        UI.showNotification('재개 실패', 'error');
    }
}

async function stopCrawler(runId) {
    if (!confirm('정말 크롤러를 중지하시겠습니까?')) return;

    try {
        await API.stopRun(runId);
        UI.showNotification('중지되었습니다', 'success');
        selectCrawler(state.currentCrawler.id);
    } catch (error) {
        UI.showNotification('중지 실패', 'error');
    }
}

async function deleteCrawler(crawlerId) {
    if (!confirm('정말 이 크롤러를 삭제하시겠습니까?')) return;

    try {
        await API.deleteCrawler(crawlerId);
        UI.showNotification('삭제되었습니다', 'success');
        showCreateForm();
        loadCrawlers();
    } catch (error) {
        UI.showNotification('삭제 실패', 'error');
    }
}

async function viewCode(crawlerId) {
    try {
        const data = await API.getCode(crawlerId);

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
                    <pre class="text-sm text-gray-300 bg-zinc-950 p-4 rounded-lg overflow-x-auto"><code>${UI.escapeHtml(data.code)}</code></pre>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        lucide.createIcons();
    } catch (error) {
        UI.showNotification('코드를 불러올 수 없습니다', 'error');
    }
}

function downloadData(crawlerId) {
    API.downloadData(crawlerId);
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
        UI.showNotification('필수 항목을 모두 입력해주세요', 'error');
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
        const result = await API.createCrawler({
            name,
            description,
            api_key: apiKey,
            curl_command: curlCommand,
            output_format: outputFormat,
            request_delay: requestDelay,
            additional_info: additionalInfo
        });

        if (result.success) {
            UI.showNotification('크롤러가 생성되었습니다!', 'success');
            loadCrawlers();
            selectCrawler(result.crawler.id);
        } else {
            UI.showNotification(`오류: ${result.error}`, 'error');
            statusEl.classList.add('hidden');
        }
    } catch (error) {
        UI.showNotification('크롤러 생성 실패', 'error');
        statusEl.classList.add('hidden');
    }
}

// 진행 상황 업데이트 (WebSocket)
function updateRunProgress(data) {
    if (!state.currentRun || state.currentRun.id !== data.run_id) return;

    const progressBar = document.getElementById('progress-bar');
    if (progressBar) {
        progressBar.style.width = `${data.progress}%`;
    }

    if (data.collected % 100 === 0) {
        selectCrawler(state.currentCrawler.id);
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    initSocket();
    loadCrawlers();

    document.getElementById('btn-new-crawler').addEventListener('click', showCreateForm);
    document.getElementById('btn-create').addEventListener('click', createCrawler);

    let searchTimeout;
    document.getElementById('search-input').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadCrawlers(e.target.value);
        }, 300);
    });
});
