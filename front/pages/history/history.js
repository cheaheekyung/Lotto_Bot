document.addEventListener("DOMContentLoaded", async function() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("로그인이 필요합니다.");
        window.location.href = 'http://127.0.0.1:5500/Lotto_Bot/front/pages/login/login.html';
        return;
    }

    try {
        const response = await axios.get('http://localhost:8000/api/mypage/', {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        const historyList = document.getElementById('history-list');

        // ✅ 추천 기록이 없을 때 메시지 표시
        if (!Array.isArray(response.data) || response.data.length === 0) {
            historyList.innerHTML = "<p>추천 기록이 없습니다.</p>";
            return;
        }

        response.data.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.classList.add('history-item');

            const createdAt = new Date(item.created_at);
            const createdAtFormatted = createdAt.toISOString().split('T')[0];

            const createdAtCell = document.createElement('div');
            createdAtCell.textContent = createdAtFormatted;
            historyItem.appendChild(createdAtCell);

            const strategyCell = document.createElement('div');
            strategyCell.textContent = `전략 ${item.strategy || "없음"}`;
            historyItem.appendChild(strategyCell);

            const numbersCell = document.createElement('div');
            numbersCell.textContent = item.numbers;
            historyItem.appendChild(numbersCell);

            const drawDateCell = document.createElement('div');
            drawDateCell.textContent = item.draw_date || "아직 추천이후 최신회차가 진행되지 않았습니다.";
            historyItem.appendChild(drawDateCell);

            const isPrizedCell = document.createElement('div');
            isPrizedCell.textContent = item.is_prized || "미당첨";
            historyItem.appendChild(isPrizedCell);

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