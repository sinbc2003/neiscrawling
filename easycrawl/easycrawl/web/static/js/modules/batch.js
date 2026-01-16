/**
 * 일괄 실행 관리 모듈
 */

import { API } from './api.js';
import { UI } from './ui.js';

export class BatchManager {
    constructor() {
        this.selectedCrawlers = new Set();
        this.runningRuns = new Map(); // crawler_id -> run_id
    }

    // 크롤러 선택/해제
    toggleSelection(crawlerId) {
        if (this.selectedCrawlers.has(crawlerId)) {
            this.selectedCrawlers.delete(crawlerId);
        } else {
            this.selectedCrawlers.add(crawlerId);
        }

        // UI 업데이트
        UI.renderBatchControls(this.selectedCrawlers.size);

        // 체크박스 상태 업데이트
        const checkbox = document.querySelector(`input[data-crawler-id="${crawlerId}"]`);
        if (checkbox) {
            checkbox.checked = this.selectedCrawlers.has(crawlerId);
        }
    }

    // 전체 선택 해제
    clearSelection() {
        this.selectedCrawlers.clear();
        document.querySelectorAll('.crawler-checkbox').forEach(cb => {
            cb.checked = false;
        });
        UI.renderBatchControls(0);
    }

    // 일괄 실행
    async startBatch(collectionMode = 'incremental') {
        if (this.selectedCrawlers.size === 0) {
            UI.showNotification('선택된 크롤러가 없습니다', 'warning');
            return;
        }

        const crawlerIds = Array.from(this.selectedCrawlers);

        UI.showNotification(`${crawlerIds.length}개 크롤러 시작 중...`, 'info');

        try {
            const result = await API.startBatch(crawlerIds, collectionMode);

            if (result.successful > 0) {
                UI.showNotification(
                    `${result.successful}개 크롤러가 시작되었습니다!`,
                    'success'
                );

                // run_id 저장
                result.results.forEach(r => {
                    if (r.success) {
                        this.runningRuns.set(r.crawler_id, r.run_id);
                    }
                });
            }

            if (result.failed > 0) {
                UI.showNotification(
                    `${result.failed}개 크롤러 시작 실패`,
                    'error'
                );
            }

            // 목록 새로고침
            if (window.loadCrawlers) {
                setTimeout(() => window.loadCrawlers(), 1000);
            }

        } catch (error) {
            console.error('일괄 실행 오류:', error);
            UI.showNotification('일괄 실행 중 오류가 발생했습니다', 'error');
        }
    }

    // 일괄 중지
    async stopBatch() {
        if (this.selectedCrawlers.size === 0) {
            UI.showNotification('선택된 크롤러가 없습니다', 'warning');
            return;
        }

        if (!confirm(`${this.selectedCrawlers.size}개 크롤러를 중지하시겠습니까?`)) {
            return;
        }

        // 실행 중인 run_id 찾기
        const runIds = [];
        for (const crawlerId of this.selectedCrawlers) {
            if (this.runningRuns.has(crawlerId)) {
                runIds.push(this.runningRuns.get(crawlerId));
            }
        }

        if (runIds.length === 0) {
            UI.showNotification('실행 중인 크롤러가 없습니다', 'warning');
            return;
        }

        try {
            const result = await API.stopBatch(runIds);

            if (result.successful > 0) {
                UI.showNotification(
                    `${result.successful}개 크롤러가 중지되었습니다`,
                    'success'
                );

                // run_id 제거
                runIds.forEach(runId => {
                    for (const [crawlerId, rId] of this.runningRuns.entries()) {
                        if (rId === runId) {
                            this.runningRuns.delete(crawlerId);
                        }
                    }
                });
            }

            if (result.failed > 0) {
                UI.showNotification(
                    `${result.failed}개 크롤러 중지 실패`,
                    'error'
                );
            }

            // 목록 새로고침
            if (window.loadCrawlers) {
                setTimeout(() => window.loadCrawlers(), 1000);
            }

        } catch (error) {
            console.error('일괄 중지 오류:', error);
            UI.showNotification('일괄 중지 중 오류가 발생했습니다', 'error');
        }
    }

    // 일괄 일시정지
    async pauseBatch() {
        if (this.selectedCrawlers.size === 0) {
            UI.showNotification('선택된 크롤러가 없습니다', 'warning');
            return;
        }

        const runIds = [];
        for (const crawlerId of this.selectedCrawlers) {
            if (this.runningRuns.has(crawlerId)) {
                runIds.push(this.runningRuns.get(crawlerId));
            }
        }

        if (runIds.length === 0) {
            UI.showNotification('실행 중인 크롤러가 없습니다', 'warning');
            return;
        }

        try {
            const result = await API.pauseBatch(runIds);

            if (result.successful > 0) {
                UI.showNotification(
                    `${result.successful}개 크롤러가 일시정지되었습니다`,
                    'success'
                );
            }

            // 목록 새로고침
            if (window.loadCrawlers) {
                setTimeout(() => window.loadCrawlers(), 1000);
            }

        } catch (error) {
            console.error('일괄 일시정지 오류:', error);
            UI.showNotification('일괄 일시정지 중 오류가 발생했습니다', 'error');
        }
    }

    // 일괄 재개
    async resumeBatch() {
        if (this.selectedCrawlers.size === 0) {
            UI.showNotification('선택된 크롤러가 없습니다', 'warning');
            return;
        }

        const runIds = [];
        for (const crawlerId of this.selectedCrawlers) {
            if (this.runningRuns.has(crawlerId)) {
                runIds.push(this.runningRuns.get(crawlerId));
            }
        }

        if (runIds.length === 0) {
            UI.showNotification('일시정지된 크롤러가 없습니다', 'warning');
            return;
        }

        try {
            const result = await API.resumeBatch(runIds);

            if (result.successful > 0) {
                UI.showNotification(
                    `${result.successful}개 크롤러가 재개되었습니다`,
                    'success'
                );
            }

            // 목록 새로고침
            if (window.loadCrawlers) {
                setTimeout(() => window.loadCrawlers(), 1000);
            }

        } catch (error) {
            console.error('일괄 재개 오류:', error);
            UI.showNotification('일괄 재개 중 오류가 발생했습니다', 'error');
        }
    }

    // 수집 모드 선택 모달 표시
    showModeModal() {
        UI.showCollectionModeModal((mode) => {
            this.startBatch(mode);
        });
    }
}
