document.getElementById("login-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await axios.post("http://localhost:8000/api/accounts/login/", {
            username: username,
            password: password
        });

        console.log("로그인 응답:", response.data);

        if (response.data.access) {
            localStorage.setItem("access_token", response.data.access);
            localStorage.setItem("refresh_token", response.data.refresh);

            // ✅ 바로 페이지 이동 (alert 제거)
            window.location.href = 'http://127.0.0.1:5500/Lotto_Bot/front/pages/main/main.html';
        } else {
            alert("로그인 실패!");
        }
    } catch (error) {
        alert("로그인 실패! 아이디 또는 비밀번호를 확인하세요.");
        console.error(error.response?.data || error);
    }
});
