document.getElementById('logout-button').addEventListener('click', function () {
    const refreshToken = localStorage.getItem('refresh'); // 저장된 refresh 토큰 가져오기

    if (!refreshToken) {
        alert("이미 로그아웃된 상태입니다.");
        return;
    }

    axios.post('http://localhost:8000/api/logout/', { refresh: refreshToken }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
    })
    .then(response => {
        alert("로그아웃 되었습니다.");
        localStorage.removeItem('access');  // 액세스 토큰 삭제
        localStorage.removeItem('refresh'); // 리프레시 토큰 삭제
        window.location.href = '/login.html'; // 로그인 페이지로 이동
    })
    .catch(error => {
        console.error("로그아웃 실패:", error);
        alert("로그아웃 중 오류 발생");
    });
});
