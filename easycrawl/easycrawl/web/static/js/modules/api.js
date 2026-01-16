/**
 * API 호출 모듈
 * 모든 서버 API 호출을 담당
 */

export const API = {
    // 크롤러 목록
    async getCrawlers(search = '') {
        const response = await fetch(`/api/crawlers?search=${encodeURIComponent(search)}`);
        return await response.json();
    },

    // 크롤러 상세
    async getCrawler(id) {
        const response = await fetch(`/api/crawlers/${id}`);
        return await response.json();
    },

    // 크롤러 생성
    async createCrawler(data) {
        const response = await fetch('/api/crawlers', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        return await response.json();
    },

    // 크롤러 삭제
    async deleteCrawler(id) {
        const response = await fetch(`/api/crawlers/${id}`, {method: 'DELETE'});
        return await response.json();
    },

    // 크롤러 시작
    async startCrawler(id, collectionMode = 'from_scratch') {
        const response = await fetch(`/api/crawlers/${id}/start`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({collection_mode: collectionMode})
        });
        return await response.json();
    },

    // 코드 보기
    async getCode(id) {
        const response = await fetch(`/api/crawlers/${id}/code`);
        return await response.json();
    },

    // 데이터 다운로드
    downloadData(id) {
        window.location.href = `/api/crawlers/${id}/download`;
    },

    // 실행 제어
    async pauseRun(runId) {
        const response = await fetch(`/api/runs/${runId}/pause`, {method: 'POST'});
        return await response.json();
    },

    async resumeRun(runId) {
        const response = await fetch(`/api/runs/${runId}/resume`, {method: 'POST'});
        return await response.json();
    },

    async stopRun(runId) {
        const response = await fetch(`/api/runs/${runId}/stop`, {method: 'POST'});
        return await response.json();
    },

    // 일괄 실행
    async startBatch(crawlerIds, collectionMode = 'from_scratch') {
        const response = await fetch('/api/batch/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                crawler_ids: crawlerIds,
                collection_mode: collectionMode
            })
        });
        return await response.json();
    },

    async stopBatch(runIds) {
        const response = await fetch('/api/batch/stop', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({run_ids: runIds})
        });
        return await response.json();
    },

    async pauseBatch(runIds) {
        const response = await fetch('/api/batch/pause', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({run_ids: runIds})
        });
        return await response.json();
    },

    async resumeBatch(runIds) {
        const response = await fetch('/api/batch/resume', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({run_ids: runIds})
        });
        return await response.json();
    }
};
