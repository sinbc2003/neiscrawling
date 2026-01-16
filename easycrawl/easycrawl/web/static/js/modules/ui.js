/**
 * UI 렌더링 모듈
 */

export const UI = {
    // 유틸리티
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('ko-KR');
    },

    // 상태 배지
    getStatusBadge(status) {
        const badges = {
            'draft': '<span class="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">대기</span>',
            'running': '<span class="px-2 py-1 bg-green-700 text-green-300 rounded text-xs">실행 중</span>',
            'paused': '<span class="px-2 py-1 bg-yellow-700 text-yellow-300 rounded text-xs">일시정지</span>',
            'completed': '<span class="px-2 py-1 bg-blue-700 text-blue-300 rounded text-xs">완료</span>',
            'failed': '<span class="px-2 py-1 bg-red-700 text-red-300 rounded text-xs">실패</span>',
            'cancelled': '<span class="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">취소</span>'
        };
        return badges[status] || badges['draft'];
    },

    getStatusText(status) {
        const texts = {
            'draft': '대기 중',
            'running': '실행 중...',
            'paused': '일시정지됨',
            'completed': '완료됨',
            'failed': '실패',
            'cancelled': '취소됨'
        };
        return texts[status] || '알 수 없음';
    },

    // 알림
    showNotification(message, type = 'info') {
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
    },

    // 크롤러 목록 렌더링
    renderCrawlerList(crawlers, selectedIds = new Set(), currentCrawlerId = null) {
        const listEl = document.getElementById('crawler-list');

        if (crawlers.length === 0) {
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

        listEl.innerHTML = crawlers.map(crawler => `
            <div class="sidebar-item p-3 rounded-lg ${currentCrawlerId === crawler.id ? 'bg-zinc-800' : ''}">
                <div class="flex items-start gap-2">
                    <input
                        type="checkbox"
                        class="crawler-checkbox mt-1 w-4 h-4 rounded border-gray-600 text-blue-600 focus:ring-blue-500 focus:ring-offset-gray-900"
                        data-crawler-id="${crawler.id}"
                        ${selectedIds.has(crawler.id) ? 'checked' : ''}
                        onclick="window.toggleCrawlerSelection(${crawler.id})">
                    <div class="flex-1 min-w-0 cursor-pointer" onclick="window.selectCrawler(${crawler.id})">
                        <h4 class="text-sm font-semibold text-white truncate">${this.escapeHtml(crawler.name)}</h4>
                        ${crawler.website_url ? `
                            <p class="text-xs text-blue-400 truncate mt-1 flex items-center gap-1">
                                <i data-lucide="link" class="w-3 h-3"></i>
                                ${this.escapeHtml(crawler.website_url)}
                            </p>
                        ` : ''}
                        ${crawler.description ? `
                            <p class="text-xs text-gray-400 truncate mt-1">${this.escapeHtml(crawler.description)}</p>
                        ` : ''}
                        <p class="text-xs text-gray-600 mt-1">${this.formatDate(crawler.created_at)}</p>
                    </div>
                </div>
            </div>
        `).join('');

        lucide.createIcons();
    },

    // 일괄 컨트롤 바 렌더링
    renderBatchControls(selectedCount) {
        const controlBar = document.getElementById('batch-control-bar');

        if (selectedCount === 0) {
            controlBar.classList.add('hidden');
            return;
        }

        controlBar.classList.remove('hidden');
        controlBar.innerHTML = `
            <div class="bg-zinc-800 border-b border-zinc-700 p-4">
                <div class="max-w-7xl mx-auto flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <span class="text-sm text-gray-400">${selectedCount}개 선택됨</span>
                        <button
                            onclick="window.clearSelection()"
                            class="text-xs text-gray-500 hover:text-gray-300">
                            선택 해제
                        </button>
                    </div>
                    <div class="flex items-center gap-2">
                        <button
                            onclick="window.showBatchModeModal()"
                            class="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-semibold btn-hover flex items-center gap-2">
                            <i data-lucide="play" class="w-4 h-4"></i>
                            일괄 실행
                        </button>
                        <button
                            onclick="window.batchPause()"
                            class="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm font-semibold btn-hover flex items-center gap-2">
                            <i data-lucide="pause" class="w-4 h-4"></i>
                            일괄 일시정지
                        </button>
                        <button
                            onclick="window.batchStop()"
                            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-semibold btn-hover flex items-center gap-2">
                            <i data-lucide="square" class="w-4 h-4"></i>
                            일괄 중지
                        </button>
                    </div>
                </div>
            </div>
        `;

        lucide.createIcons();
    },

    // 수집 모드 선택 모달
    showCollectionModeModal(onSelect) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-zinc-900 rounded-xl max-w-md w-full mx-4 border border-zinc-800">
                <div class="p-6 border-b border-zinc-800">
                    <h3 class="text-xl font-bold text-white">수집 모드 선택</h3>
                    <p class="text-sm text-gray-400 mt-1">어떤 방식으로 데이터를 수집할까요?</p>
                </div>
                <div class="p-6 space-y-3">
                    <button
                        class="mode-option w-full p-4 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-left transition"
                        data-mode="from_scratch">
                        <div class="flex items-start gap-3">
                            <div class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 mt-1">
                                <i data-lucide="rotate-cw" class="w-4 h-4 text-white"></i>
                            </div>
                            <div class="flex-1">
                                <h4 class="text-white font-semibold">처음부터 수집</h4>
                                <p class="text-xs text-gray-400 mt-1">기존 데이터는 유지하고 처음부터 다시 수집합니다.</p>
                            </div>
                        </div>
                    </button>

                    <button
                        class="mode-option w-full p-4 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-left transition"
                        data-mode="fresh_start">
                        <div class="flex items-start gap-3">
                            <div class="w-6 h-6 rounded-full bg-red-600 flex items-center justify-center flex-shrink-0 mt-1">
                                <i data-lucide="trash-2" class="w-4 h-4 text-white"></i>
                            </div>
                            <div class="flex-1">
                                <h4 class="text-white font-semibold">모두 삭제 후 수집</h4>
                                <p class="text-xs text-gray-400 mt-1">기존 데이터를 모두 삭제하고 완전히 새로 시작합니다.</p>
                            </div>
                        </div>
                    </button>

                    <button
                        class="mode-option w-full p-4 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-left transition"
                        data-mode="incremental">
                        <div class="flex items-start gap-3">
                            <div class="w-6 h-6 rounded-full bg-green-600 flex items-center justify-center flex-shrink-0 mt-1">
                                <i data-lucide="arrow-right" class="w-4 h-4 text-white"></i>
                            </div>
                            <div class="flex-1">
                                <h4 class="text-white font-semibold">이어서 수집 (권장)</h4>
                                <p class="text-xs text-gray-400 mt-1">마지막 수집 시점 이후의 새로운 데이터만 수집합니다.</p>
                                <p class="text-xs text-yellow-500 mt-1">💡 예: 1/15 크롤링 → 1/19 실행 시 15일 이후만 수집</p>
                            </div>
                        </div>
                    </button>
                </div>
                <div class="p-6 border-t border-zinc-800">
                    <button
                        onclick="this.closest('.fixed').remove()"
                        class="w-full bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-2 rounded-lg">
                        취소
                    </button>
                </div>
            </div>
        `;

        modal.querySelectorAll('.mode-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.dataset.mode;
                modal.remove();
                onSelect(mode);
            });
        });

        document.body.appendChild(modal);
        lucide.createIcons();
    }
};
