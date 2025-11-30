document.addEventListener("DOMContentLoaded", () => {
	const form = document.getElementById("login-form");
	const usernameInput = form.querySelector('input[type="text"]');
	const checkBox = form.querySelector('input[type="checkbox"]');
	const title = document.querySelector(".login-title");
	
	const remember_form = new FormData(form);
	if(localStorage.getItem("remember_id")) {
		usernameInput.value = localStorage.getItem("remember_id");
		checkBox.checked = true;
	}

	form.addEventListener("submit", async (e) => {
		e.preventDefault();
		
		const formData = new FormData(form);
		const data = {
			username: formData.get("userName"),
			password: formData.get("userPassword")
		};
		
		const remember_id = formData.get("userName");

		// 5초 타이머: 5초 지나면 (그리고 아직 로컬에 firstLogin 기록이 없으면) 안내문구를 띄운다
		let noticeBox = null;
		const timerId = setTimeout(() => {
			if (!localStorage.getItem("firstLogin")) {
				noticeBox = document.createElement("div");
				noticeBox.className = "notice-box";
				noticeBox.innerText = "첫 로그인이시군요! 로그인이 30초 정도 소요될 수 있습니다.";
				// 제목 바로 아래에 삽입 (레이아웃 안정)
				title.insertAdjacentElement("afterend", noticeBox);
			}
			else {
				noticeBox = document.createElement("div");
				noticeBox.className = "notice-box";
				noticeBox.innerText = "데이터를 불러오는 중입니다. 로그인이 30초 정도 소요될 수 있습니다.";
				// 제목 바로 아래에 삽입 (레이아웃 안정)
				title.insertAdjacentElement("afterend", noticeBox);
			}
		}, 5000);

		try {
			// 개발/테스트용: URL에 ?simulateSlow=1 붙이면 의도적 지연(6초)을 넣어 테스트 가능
			const simulateSlow = window.location.search.includes("simulateSlow=1");
			if (simulateSlow) {
				await new Promise((r) => setTimeout(r, 6000));
			}

			const response = await fetch("https://nexcode.kr:16003/login", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(data)
			});

			const result = await response.json();

			if (result.status === "success") {
				if(formData.get("remember") === "on") {
					localStorage.setItem("remember_id", remember_id);
				}
				else if(localStorage.getItem("remember_id")) {
					localStorage.removeItem("remember_id");
				}
				
				// 최초 로그인 표시 여부: 로컬에 'firstLogin' 없으면 지금이 최초 성공 로그인으로 간주
				if (!localStorage.getItem("firstLogin")) {
					localStorage.setItem("firstLogin", "done");
				}

				// 학생 데이터 저장 및 이동
				if (result.data && result.data[0]) {
					sessionStorage.setItem("studentData", JSON.stringify(result.data[0]));
				}
				window.location.href = "/";
			} else {
				alert("로그인 실패: " + (result.message || "아이디/비밀번호 확인"));
			}
		} catch (err) {
			console.error("오류 발생:", err);
			alert("서버와 연결할 수 없습니다.");
		} finally {
			// 타이머 취소 (아직 안 찍혔다면 방지)
			clearTimeout(timerId);

			// 만약 안내문구가 표시되어 있으면 최소한 1.5초 더 보여준 뒤 제거 (사용자 눈에 보이도록)
			if (noticeBox) {
				setTimeout(() => {
					if (noticeBox && noticeBox.parentNode) noticeBox.parentNode.removeChild(noticeBox);
				}, 1500);
			}
		}
	});
});
