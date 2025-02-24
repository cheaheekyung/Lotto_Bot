document.addEventListener("DOMContentLoaded", async function() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("로그인이 필요합니다.");
        window.location.href = 'http://127.0.0.1:5500/Lotto_Bot/front/pages/login/login.html'; // 로그인 페이지로 리다이렉트
        return;
    }

    try {
        // 추천 히스토리 API 호출
        const response = await axios.get('http://localhost:8000/api/mypage/', {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        const historyList = document.getElementById('history-list');

        response.data.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.classList.add('history-item');

            // 추천 날짜 포맷 (예: 2025-01-01)
            const createdAt = new Date(item.created_at); // ISO 문자열을 Date 객체로 변환
            const createdAtFormatted = createdAt.toISOString().split('T')[0]; // 'YYYY-MM-DD' 형식으로 포맷

            const createdAtCell = document.createElement('div');
            createdAtCell.textContent = createdAtFormatted;
            historyItem.appendChild(createdAtCell);

            // 전략 (예: 전략 A) - "전략: " 추가
            const strategyCell = document.createElement('div');
            strategyCell.textContent = `전략 ${item.strategy || "없음"}`; // 전략이 없으면 '없음'으로 표시
            historyItem.appendChild(strategyCell);

            // 추천 번호 (예: 12, 13, 18, 28, 33, 39)
            const numbersCell = document.createElement('div');
            numbersCell.textContent = item.numbers;
            historyItem.appendChild(numbersCell);

            // 추첨일 (예: 아직 추천 이후 최신 회차가 진행되지 않았습니다.)
            const drawDateCell = document.createElement('div');
            drawDateCell.textContent = item.draw_date || "아직 추천이후 최신회차가 진행되지 않았습니다.";
            historyItem.appendChild(drawDateCell);

            // 당첨 여부 (예: 미당첨, 1등, 2등 등)
            const isPrizedCell = document.createElement('div');
            isPrizedCell.textContent = item.is_prized || "미당첨";
            historyItem.appendChild(isPrizedCell);

            // 히스토리 항목을 리스트에 추가
            historyList.appendChild(historyItem);
        });
    } catch (error) {
        console.error('데이터를 가져오는 데 실패했습니다.', error);
        alert("히스토리 데이터를 가져오는 데 실패했습니다.");
    }
});

function logout() {
    if (confirm("정말 로그아웃 하시겠습니까?")) {
        // localStorage에서 토큰 삭제
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        // 로그아웃 후 로그인 페이지로 리다이렉트
        window.location.href = 'http://127.0.0.1:5500/Lotto_Bot/front/pages/login/login.html';
    }
}