document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    // 메시지 요소는 폼 외부에 위치하는 것이 좋습니다.
    const messageDiv = document.getElementById('signup-message');

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const password2 = document.getElementById('password2').value;

            if (password !== password2) {
                messageDiv.textContent = '비밀번호가 일치하지 않습니다.';
                messageDiv.style.color = 'red';
                return;
            }

            try {
                const response = await axios.post('http://localhost:8000/api/accounts/signup/', {
                    username: username,
                    email: email,
                    password: password,
                    password2: password2,
                }, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                console.log("응답 상태:", response.status);

                if (response.status >= 200 && response.status < 300) {
                    // 회원가입 성공 메시지 출력
                    messageDiv.textContent = '회원가입 성공!';
                    messageDiv.style.color = 'green';
                    
                    // 입력창 리셋 (messageDiv가 폼 외부에 있다면 내용은 유지됨)
                    signupForm.reset();
                    console.log("회원가입 성공, 리다이렉트 준비 중");

                    // 2초 후 로그인 페이지로 리다이렉트
                    setTimeout(() => {
                        window.location.href = 'http://127.0.0.1:5500/Lotto_Bot/front/pages/login/login.html';
                        console.log("리다이렉트 성공");
                    }, 2000);
                }
            } catch (error) {
                console.error("에러 발생:", error);
                if (error.response) {
                    messageDiv.textContent = error.response.data.detail || '회원가입 실패';
                } else {
                    messageDiv.textContent = '서버와 연결할 수 없습니다.';
                }
                messageDiv.style.color = 'red';
            }
        });
    }
});