console.log("accessToken from localStorage:", localStorage.getItem('access_token'));
document.addEventListener('DOMContentLoaded', () => {
    // localStorage에서 JWT access token을 가져옴
    const token = localStorage.getItem('access_token');
    console.log("Access Token:", token);
    if (!token) {
      alert('로그인이 필요한 서비스입니다. 로그인 페이지로 이동합니다.');
      window.location.href = 'http://127.0.0.1:5500/Lotto_Bot/front/pages/login/login.html';  
    }
  
    // axios를 사용해 API 호출
    axios.get('http://127.0.0.1:8000/api/main/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        // 'Content-Type': 'application/json'
      }
    })
    .then(response => {
      console.log("API 응답 데이터:", response.data);
      const data = response.data;
      // 회차 및 추첨일자 표시
      const roundText = `${data["회차"]}회 (${data["추첨 일자"]})`;
      document.getElementById('round-info').textContent = roundText;
  
      // 각 번호 업데이트
      document.getElementById('num1').textContent = data["번호1"];
      document.getElementById('num2').textContent = data["번호2"];
      document.getElementById('num3').textContent = data["번호3"];
      document.getElementById('num4').textContent = data["번호4"];
      document.getElementById('num5').textContent = data["번호5"];
      document.getElementById('num6').textContent = data["번호6"];
      document.getElementById('bonus').textContent = data["보너스번호"];
    })
    .catch(error => {
        console.error("API 호출 에러:", error);
        if (error.response) {
          console.error("응답 상태:", error.response.status);
          console.error("응답 데이터:", error.response.data);
          if (error.response.status === 401 || error.response.status === 403) {
            alert('인증이 만료되었거나 권한이 없습니다. 다시 로그인해주세요.');
            window.location.href = 'http://127.0.0.1:5500/Lotto_Bot/front/pages/login/login.html';  // 로그인 페이지의 실제 경로로 수정하세요.
          }
        } else {
          alert('네트워크 오류가 발생했습니다.');
        }
      });
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