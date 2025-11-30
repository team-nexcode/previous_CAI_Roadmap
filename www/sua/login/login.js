document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
    const usernameInput = form.querySelector('input[type="text"]');
    const passwordInput = form.querySelector('input[type="password"]');
    const checkBox = form.querySelector('input[type="checkbox"]');
    const submitBtn = form.querySelector('input[type="submit"]');

	// 버튼 클릭 이벤트
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {
            username: formData.get("userName"),
            password: formData.get("userPassword"),
            remember: formData.get("remember") === "on"
        };
        
        // 버튼 비활성화 및 텍스트 변경
        usernameInput.disabled = true;
        passwordInput.disabled = true;
        checkBox.disabled = true;
        submitBtn.disabled = true;
        const originalText = submitBtn.value;
        submitBtn.value = "로그인 중...";

		// api 서버에 post 요청
        try {
            const response = await fetch("https://nexcode.kr:16003/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.status === "success") {
                sessionStorage.setItem("loginResult", JSON.stringify(result));
                alert("로그인 성공!");
                window.location.href = "/heo/heo.html"; // 로그인 전 메인페이지로 이동
            } else {
                alert("로그인 실패: " + (result.message || "아이디/비밀번호 확인"));
            }
        } catch (err) {
            console.error("오류 발생:", err);
            alert("서버와 연결할 수 없습니다.");
        } finally {
            // 요청 완료 후 버튼 원래 상태로 복구
            usernameInput.disabled = false;
        	passwordInput.disabled = false;
        	checkBox.disabled = false;
            submitBtn.disabled = false;
            submitBtn.value = originalText;
        }
    });
});