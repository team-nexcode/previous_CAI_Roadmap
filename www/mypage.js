// ===================================================================
// 1. 공통 로직 (헤더의 로그인 정보, 네비게이션 등)
// ===================================================================

const studentData = sessionStorage.getItem("studentData");
const idText = document.getElementById("idText");
const nameText = document.getElementById("nameText");
const loginInfo = document.getElementById("loginInfo");
let major = "";

if (studentData) {
	const parsed = JSON.parse(studentData);
	if (idText) idText.textContent = parsed.STD_NO;
	if (nameText) nameText.textContent = parsed.STD_NM;
	if (loginInfo) loginInfo.textContent = "로그아웃";
	major = parsed.DPTMJR_NM;

	loginInfo?.addEventListener("click", () => {
		sessionStorage.removeItem("studentData");
		window.location.href = "/login.html";
	});
} else {
	window.location.href = "/login.html";
}

const logoHome = document.getElementById('logoHome');
logoHome?.addEventListener('click', () => {
	window.location.href = "/";
});

const myInfoTab = document.getElementById('myInfoTab');
myInfoTab?.addEventListener('click', (e) => {
	e.preventDefault();
	location.reload();
});


// ===================================================================
// 2. '나의 정보' 페이지 전용 로직
// ===================================================================

// '나의 정보' 페이지에만 존재하는 요소(info-name)가 있을 때만 아래 코드를 실행
if (document.getElementById('info-name')) {
	const studentId = idText.textContent;

	// 2-1. 화면 렌더 함수
	function renderStudentInfo(data) {
		document.getElementById('info-name').textContent = data.name || '-';
		document.getElementById('info-id').textContent = data.id || '-';
		document.getElementById('info-department').textContent = data.department || '-';
		document.getElementById('info-email').textContent = data.email || '-';
		document.getElementById('info-phone').textContent = data.phone || '-';
		document.getElementById('info-track').textContent = data.track || '-';
		document.getElementById('info-updated-at').textContent = data.lastUpdatedAt || '-';
	}
	
	// 2-2. 서버에서 최신 데이터를 가져오는 함수
	async function fetchUpdatedStudentData() {
		console.log("서버에서 최신 정보를 가져오는 중...");
		try {
			const response = await fetch("https://nexcode.kr:16003/data/mydata", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ student_id: studentId })
			});
			const result = await response.json();

			if (result.status === "success") {
				console.log("최신 정보를 성공적으로 가져왔습니다.");
				const newDataFromServer = {
					name: nameText.textContent,
					id: studentId,
					department: major,
					email: result.data.mail || "hong.g.d@university.ac.kr",
					phone: result.data.phone || "010-8765-4321",
					track: result.data.track || "선택 안 함",
					lastUpdatedAt: new Date().toISOString().slice(0, 19).replace('T', ' ')
				};
				return newDataFromServer;
			} else {
				alert("정보 불러오기 실패: " + (result.message || '서버 오류'));
				return null;
			}
		} catch (err) {
			console.error("요청 오류:", err);
			alert("서버와 통신할 수 없습니다.");
			return null;
		}
	}

	// 최초 진입 시 1회 불러오기
	fetchUpdatedStudentData().then(updatedData => {
		if (updatedData) renderStudentInfo(updatedData);
	});

	// --- 트랙 수정 UI ---
	const editButton = document.getElementById('edit-track-button');
	const cancelButton = document.getElementById('cancel-track-button');
	const updateButton = document.getElementById('update-track-button');
	const viewModeDiv = document.getElementById('track-view-mode');
	const editModeDiv = document.getElementById('track-edit-mode');
	const infoTrack = document.getElementById('info-track');
	const trackSelect = document.getElementById('track-select');

	editButton?.addEventListener('click', () => {
		trackSelect.value = infoTrack.textContent;
		viewModeDiv.classList.add('hidden');
		editModeDiv.classList.remove('hidden');
	});

	updateButton?.addEventListener('click', async () => {
		const newTrack = trackSelect.value;
		infoTrack.textContent = newTrack;
		viewModeDiv.classList.remove('hidden');
		editModeDiv.classList.add('hidden');
		
		try {
			const response = await fetch("https://nexcode.kr:16003/update/track", {
				method: "PATCH",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ student_id: studentId, track: newTrack })
			});
			const result = await response.json();
			if (result.status === "success") {
				alert('트랙 정보가 수정되었습니다.');
			} else {
				alert("업데이트 실패: " + (result.message || '서버 오류'));
			}
		} catch (err) {
			console.error("요청 오류:", err);
			alert("서버와 통신할 수 없습니다.");
		}
	});

	cancelButton?.addEventListener('click', () => {
		viewModeDiv.classList.remove('hidden');
		editModeDiv.classList.add('hidden');
	});
}


// ===================================================================
// 3. 비밀번호 모달 로직 (나의 정보 업데이트 / 서비스 탈퇴 공용)
// ===================================================================
(() => {
	const studentId = idText.textContent;
	
	// 버튼들
	const updateBtn = document.getElementById('update-info-button');
	const withdrawBtn = document.getElementById('withdraw-button');

	// 모달 요소들
	const modal = document.getElementById('pwModal');
	const overlay = document.getElementById('pwModalOverlay');
	const closeBtn = document.getElementById('pwModalClose');
	const cancelBtn = document.getElementById('pwCancel');
	const form = document.getElementById('pwForm');
	const pwInput = document.getElementById('pwInput');
	const pwError = document.getElementById('pwError');
	const pwToggle = document.getElementById('pwToggle');
	const eyeOn = document.getElementById('eyeOn');
	const eyeOff = document.getElementById('eyeOff');
	const actionField = document.getElementById('pwAction');

	// >>> ADDED: 진행률 모달 요소 참조
	const progModal = document.getElementById('progressModal');   // >>> ADDED
	const progBar = document.getElementById('progressBar');       // >>> ADDED
	const progText = document.getElementById('progressText');     // >>> ADDED

	// 필수 요소가 없으면 바로 종료(다른 페이지에 영향 X)
	if (!modal || !form || !pwInput) return;

	let lastFocused = null;

	// 접근성/포커스 유틸
	const getFocusable = () =>
		modal.querySelectorAll(
			'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
		);

	const keepFocusWithinModal = (e) => {
		const focusables = Array.from(getFocusable());
		if (!focusables.length) return;

		const first = focusables[0];
		const last = focusables[focusables.length - 1];

		if (e.shiftKey && document.activeElement === first) {
			e.preventDefault();
			last.focus();
		} else if (!e.shiftKey && document.activeElement === last) {
			e.preventDefault();
			first.focus();
		}
	};

	const trapFocus = (e) => {
		if (!modal.classList.contains('hidden') && !modal.contains(e.target)) {
			e.stopPropagation();
			const focusables = getFocusable();
			if (focusables.length) focusables[0].focus();
		}
	};

	const onKeydown = (e) => {
		if (e.key === 'Escape') {
			e.preventDefault();
			closeModal();
		} else if (e.key === 'Tab') {
			keepFocusWithinModal(e);
		}
	};

	const openModal = (action) => {
		lastFocused = document.activeElement;
		if (actionField) actionField.value = action || '';

		modal.classList.remove('hidden');
		modal.classList.add('flex');
		document.body.style.overflow = 'hidden';

		if (pwError) pwError.classList.add('hidden');
		pwInput.value = '';
		setTimeout(() => pwInput.focus(), 0);

		document.addEventListener('keydown', onKeydown);
		document.addEventListener('focus', trapFocus, true);
	};

	const closeModal = () => {
		modal.classList.add('hidden');
		modal.classList.remove('flex');
		document.body.style.overflow = '';

		document.removeEventListener('keydown', onKeydown);
		document.removeEventListener('focus', trapFocus, true);

		if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
	};

	// >>> ADDED: 진행률 모달 제어 함수 3종
	function openProgress() {                                              // >>> ADDED
		if (!progModal) return;
		progModal.classList.remove('hidden');
		progModal.classList.add('flex');
		if (progBar) progBar.style.width = '0%';
		if (progText) progText.textContent = '준비 중…';
	}
	function updateProgress(step, total, msg) {                             // >>> ADDED
		const pct = (step && total) ? Math.floor((step / total) * 100) : 0;
		if (progBar) progBar.style.width = pct + '%';
		if (progText) progText.textContent = msg || `진행 중… (${pct}%)`;
	}
	function closeProgress() {                                              // >>> ADDED
		if (!progModal) return;
		progModal.classList.add('hidden');
		progModal.classList.remove('flex');
	}

	// 버튼 → 모달 오픈
	updateBtn?.addEventListener('click', () => openModal('update'));
	withdrawBtn?.addEventListener('click', () => openModal('withdraw'));

	// 닫기/취소/오버레이
	overlay?.addEventListener('click', closeModal);
	closeBtn?.addEventListener('click', closeModal);
	cancelBtn?.addEventListener('click', closeModal);

	// 비밀번호 표시/숨김 토글
	pwToggle?.addEventListener('click', () => {
		const isText = pwInput.type === 'text';
		pwInput.type = isText ? 'password' : 'text';
		eyeOn?.classList.toggle('hidden', !isText);
		eyeOff?.classList.toggle('hidden', isText);
		pwInput.focus();
	});

	// >>> CHANGED: 제출 처리 로직 전체 교체 (백엔드 작업 시작 + 폴링 + 진행률 반영)
	form.addEventListener('submit', async (e) => {                           // >>> CHANGED
		e.preventDefault();

		if (!pwInput.value.trim()) {
			pwError?.classList.remove('hidden');
			pwInput.focus();
			return;
		}

		const action = actionField?.value || '';

		// 비번 모달 닫고 → 진행률 모달 오픈
		closeModal();                                                        // >>> CHANGED                                                      // >>> CHANGED

		if (action === 'update') {
			openProgress();
			
			try {
				// 1) 작업 시작 (job_id 발급)
				const start = await fetch("https://nexcode.kr:16003/update/ndrims_start", {   // >>> CHANGED
					method: "POST",
					headers: { "Content-Type":"application/json" },
					body: JSON.stringify({
						student_id: idText.textContent,
						password: pwInput.value
					})
				});
				const init = await start.json();
				if (start.status !== 202 || init.status !== 'accepted') {
					closeProgress();
					alert("업데이트 시작 실패: " + (init.message || '서버 오류'));
					return;
				}
				const jobId = init.job_id;

				// 2) 상태 폴링(1초 간격)
				const timer = setInterval(async () => {                       // >>> CHANGED
					try {
						const r = await fetch(`https://nexcode.kr:16003/update/ndrims_status?job_id=${jobId}`);
						const j = await r.json();
						if (j.status !== 'success') return;

						const p = j.progress; // {step,total,msg,done,error}
						updateProgress(p.step, p.total, p.msg);               // >>> CHANGED

						if (p.error) {
							clearInterval(timer);
							closeProgress();
							alert("업데이트 실패: " + p.error);
						} else if (p.done) {
							clearInterval(timer);
							setTimeout(async () => {
								closeProgress();
								// 최신 정보 재로딩
								if (document.getElementById('info-name')) {
									const updated = await fetchUpdatedStudentData(); // >>> CHANGED
									if (updated) renderStudentInfo(updated);        // >>> CHANGED
								}
								alert('업데이트가 완료되었습니다.');
							}, 500);
						}
					} catch (e) {
						console.error(e);
					}
				}, 1000);

			} catch (err) {
				console.error(err);
				closeProgress();                                              // >>> CHANGED
				alert('업데이트 요청 실패');                                     // >>> CHANGED
			}
		} else if (action === 'withdraw') {
			try {
				const response = await fetch("https://nexcode.kr:16003/delete", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ student_id: studentId, password: pwInput.value })
				});
				const result = await response.json();
	
				if (result.status === "success") {
					alert("다음에 또 만나요.")
					sessionStorage.removeItem("studentData");
					window.location.href = "/login.html";
				} else {
					alert("탈퇴 실패: " + (result.message || '서버 오류'));
					return null;
				}
			} catch (err) {
				console.error("요청 오류:", err);
				alert("서버와 통신할 수 없습니다.");
				return null;
			}
		} else {
			alert('알 수 없는 동작입니다.');
		}
	});
})();
