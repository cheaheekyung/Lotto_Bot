
let isGetRequestSent = false; // 플래그 변수 추가
document.addEventListener("DOMContentLoaded", async function() {
    if (isGetRequestSent) return; // 이미 요청했다면 실행 안 함
    isGetRequestSent = true; // 요청 상태 변경
    console.log("초기 겟요청 실행됨")
    let token = localStorage.getItem("access_token");
    if (!token || token.trim() === "") {
        alert("로그인이 필요합니다.");
        window.location.href = "http://127.0.0.1:5500/Lotto_Bot/front/pages/login/login.html";
        return;
    }

    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatBox = document.getElementById("chat-box");

    console.log("폼 요소 확인:", chatForm); // ✅ chatForm이 정상적으로 가져와지는지 확인

    if (!chatForm) {
        console.error("❌ chatForm 요소를 찾을 수 없습니다.");
        return;
    }

    function appendMessage(sender, text) {
        const messageElem = document.createElement("div");
        messageElem.classList.add("chat-message", sender);
        const textElem = document.createElement("div");
        textElem.classList.add("message", sender);
        textElem.innerHTML = text.replace(/\n/g, "<br>");
        messageElem.appendChild(textElem);
        chatBox.appendChild(messageElem);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // 초기 GET 요청
    try {
        console.log("요청보낼거임");
        const getResponse = await axios.get("http://localhost:8000/api/chatbot/chat/", {
            headers: { Authorization: `Bearer ${token}` }
        });
        console.log("겟응답 받음", getResponse.data)
        if (getResponse.data && getResponse.data.response) {
            appendMessage("bot", getResponse.data.response);
        }
    } catch (error) {
        console.error("초기 GET 요청 에러:", error);
    }

    window.addEventListener("beforeunload", function () {
        console.log("❗ 페이지가 새로고침됨!");
    });

    // ✅ submit 이벤트 리스너 추가
    chatForm.addEventListener("submit", async function(e) {
        e.preventDefault(); // 🚀 페이지 리로드 방지
        console.log("폼 제출 이벤트 실행"); // 🚀 확인용 로그

        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        appendMessage("user", userMessage);
        chatInput.value = "";

        try {
            const postResponse = await axios.post(
                "http://localhost:8000/api/chatbot/chat/",
                { message: userMessage },
                {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`
                    }
                }
            );
            if (postResponse.data && postResponse.data.response) {
                appendMessage("bot", postResponse.data.response);
            }
        } catch (error) {
            console.error("POST 요청 에러:", error);
            appendMessage("bot", "네트워크 오류가 발생했습니다. 다시 시도해주세요.");
        }
    });
});