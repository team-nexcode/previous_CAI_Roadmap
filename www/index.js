// sessionStorage에서 데이터 가져오기
const studentData = sessionStorage.getItem("studentData");
const idText = document.getElementById("idText");
const nameText = document.getElementById("nameText");
const loginInfo = document.getElementById("loginInfo");

if (studentData) {
	const parsed = JSON.parse(studentData);
	idText.textContent = parsed.STD_NO;
	nameText.textContent = parsed.STD_NM;
	loginInfo.textContent = "로그아웃";

	loginInfo.addEventListener("click", () => {
		sessionStorage.removeItem("studentData");
		window.location.href = "/login.html";
	});
} else {
	nameText.textContent = "";
	loginInfo.textContent = "로그인";
	window.location.href = "/login.html";
}

const tabs = document.querySelectorAll('.tab');
const tabContent = document.getElementById('tabContent');

/**
 * [V-Final with BSM Fix + Mobile-friendly] 모바일 반응형 개선
 */

function renderCoursePlan() {
	// --- 1. 데이터 정의 ---
	const modules = {
		1: { id: 'module-programming', title: '프로그래밍' },
		2: { id: 'module-pl', title: '프로그래밍 언어' },
		3: { id: 'module-ds-algo', title: '자료구조 및 알고리즘' },
		4: { id: 'module-db', title: '데이터베이스' },
		5: { id: 'module-network', title: '네트워크' },
		6: { id: 'module-architecture', title: '컴퓨터 구조' },
		7: { id: 'module-ai', title: '인공지능' },
		8: { id: 'module-vc', title: '비주얼컴퓨팅' },
		9: { id: 'module-system-sw', title: '시스템 소프트웨어' },
		10: { id: 'module-security', title: '컴퓨터 보안' },
		11: { id: 'module-vr', title: '가상현실' },
		12: { id: 'module-vision', title: '컴퓨터 비전' },
		13: { id: 'module-vc-advanced', title: '비주얼컴퓨팅 심화' },
		14: { id: 'module-ai-advanced', title: '인공지능 심화' },
		15: { id: 'module-security-advanced', title: '컴퓨터 보안 심화' },
		16: { id: 'module-game-advanced', title: '게임 심화' },
		'capstone': { id: 'module-capstone', title: '캡스톤 디자인' }
	};

	const trackData = {
		'선택 안 함': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 'capstone'],
		'비주얼컴퓨팅트랙': [1, 3, 7, 8, 11, 12, 13, 'capstone'],
		'AI/DS트랙': [1, 3, 4, 7, 12, 14, 'capstone'],
		'컴퓨터보안트랙': [1, 2, 3, 6, 9, 10, 15, 'capstone'],
		'게임트랙': [1, 3, 4, 7, 8, 10, 11, 12, 16, 'capstone'],
		'AIoT트랙': [1, 3, 5, 6, 7, 9, 10, 12, 'capstone'],
		'소프트웨어심화트랙': [1, 2, 3, 4, 5, 6, 7, 8, 9, 'capstone']
	};
	
	const allCourses = [
	// BSM (ID, 이름, 모듈, 선수과목, 타입)
		{ id: '미적분학및연습1', name: '미적분학및연습1', module: 5, prereqs: [], type: 'BSM' },
		{ id: '이산수학', name: '이산수학', module: 2, prereqs: [], type: 'BSM' },
		{ id: '확률및통계학', name: '확률및통계학', module: 5, prereqs: ['미적분학및연습1'], type: 'BSM' },
		{ id: '공학선형대수학', name: '공학선형대수학', module: 15, prereqs: [], type: 'BSM' },

		// 모듈 1: 프로그래밍
		{ id: '기초프로그래밍', name: '기초프로그래밍', module: 1, prereqs: [], type: '핵심' },
		{ id: '심화프로그래밍', name: '심화프로그래밍', module: 1, prereqs: ['기초프로그래밍'] },
		{ id: '객체지향프로그래밍', name: '객체지향프로그래밍', module: 1, prereqs: ['심화프로그래밍'] },
		{ id: '소프트웨어공학', name: '소프트웨어공학', module: 1, prereqs: ['객체지향프로그래밍'] },

		// 모듈 3: 자료구조 및 알고리즘
		{ id: '자료구조', name: '자료구조', module: 3, prereqs: ['심화프로그래밍'], type: '핵심' },
		{ id: '알고리즘', name: '알고리즘', module: 3, prereqs: ['자료구조'] }, // 'C++' 아이콘

		// 모듈 4: 데이터베이스
		{ id: '데이터베이스', name: '데이터베이스', module: 4, prereqs: ['자료구조'] }, // 'C++' 아이콘
		{ id: '데이터베이스설계', name: '데이터베이스설계', module: 4, prereqs: ['데이터베이스'] },

		// 모듈 5: 네트워크
		{ id: '데이터통신입문', name: '데이터통신입문', module: 5, prereqs: ['확률및통계학'] }, // 'S' 아이콘
		{ id: '컴퓨터네트워크', name: '컴퓨터네트워크', module: 5, prereqs: ['데이터통신입문'] },
		
		// 모듈 2: 프로그래밍 언어
		{ id: '프로그래밍언어론', name: '프로그래밍언어론', module: 2, prereqs: ['기초프로그래밍'] }, // 'C' 아이콘
		{ id: '형식언어', name: '형식언어', module: 2, prereqs: ['프로그래밍언어론'] },
		{ id: '컴파일러', name: '컴파일러', module: 2, prereqs: ['형식언어'] },

		// 모듈 6: 컴퓨터 구조
		{ id: '컴퓨터구성', name: '컴퓨터구성', module: 6, prereqs: ['이산수학'] },
		{ id: '컴퓨터구조', name: '컴퓨터구조', module: 6, prereqs: ['운영체제'] }, // 이미지 기준

		// 모듈 9: 시스템 소프트웨어
		{ id: '시스템소프트웨어', name: '시스템소프트웨어', module: 9, prereqs: ['컴퓨터구성', '자료구조'] }, // 화살표 + 'C++' 아이콘
		{ id: '운영체제', name: '운영체제', module: 9, prereqs: ['시스템소프트웨어'] },
		{ id: '임베디드시스템', name: '임베디드시스템', module: 9, prereqs: ['운영체제'] },
		{ id: '병렬처리', name: '병렬처리', module: 9, prereqs: ['임베디드시스템'] }, // 4-1에 위치

		// 모듈 7: 인공지능
		{ id: '인공지능', name: '인공지능', module: 7, prereqs: ['컴퓨터그래픽스'] }, // 이미지 기준
		{ id: '머신러닝', name: '머신러닝', module: 7, prereqs: ['인공지능'] },
		{ id: '딥러닝입문', name: '딥러닝입문', module: 7, prereqs: ['머신러닝'] },

		// 모듈 8: 비주얼컴퓨팅
		{ id: '컴퓨터그래픽스', name: '컴퓨터그래픽스', module: 8, prereqs: ['자료구조'] }, // 'C++' 아이콘
		{ id: '인간컴퓨터상호작용', name: '인간컴퓨터상호작용', module: 8, prereqs: ['컴퓨터그래픽스', '자료구조'] }, // 화살표 + 'C++' 아이콘
		
		// 모듈 10: 컴퓨터 보안
		{ id: '암호학과네트워크보안', name: '암호학과네트워크보안', module: 10, prereqs: ['시큐어코딩'] },
		{ id: '컴퓨터보안', name: '컴퓨터보안', module: 10, prereqs: ['암호학과네트워크보안'] },
		
		// 모듈 15: 컴퓨터 보안 심화
		{ id: '시큐어코딩', name: '시큐어코딩', module: 15, prereqs: ['공학선형대수학', '자료구조'] }, // 화살표 + 'C++' 아이콘
		{ id: '양자컴퓨팅', name: '양자컴퓨팅', module: 15, prereqs: ['임베디드시스템'] }, // 4-1에 위치
		{ id: '웹서비스보안', name: '웹서비스보안', module: 15, prereqs: ['암호학과네트워크보안'] }, // 4-1에 위치

		// 모듈 11, 12, 13, 14, 16 (심화)
		{ id: '가상현실', name: '가상현실', module: 11, prereqs: ['디지털영상처리'] }, // 3-2에 위치
		{ id: '컴퓨터비전입문', name: '컴퓨터비전입문', module: 12, prereqs: ['가상현실'] }, // 4-2에 위치
		{ id: '디지털신호처리', name: '디지털신호처리', module: 13, prereqs: ['공학선형대수학'] }, // 'S' 아이콘
		{ id: '디지털영상처리', name: '디지털영상처리', module: 13, prereqs: ['디지털신호처리'] },
		{ id: '인공지능수학', name: '인공지능수학', module: 14, prereqs: ['공학선형대수학'] },
		{ id: '다변량및시계열데이터분석', name: '다변량및시계열데이터분석', module: 14, prereqs: ['인공지능수학'] },
		{ id: '자연어처리개론', name: '자연어처리개론', module: 14, prereqs: ['다변량및시계열데이터분석'] },
		{ id: '게임프로그래밍', name: '게임프로그래밍', module: 16, prereqs: ['자료구조'] }, // 'C++' 아이콘
		{ id: '게임엔진프로그래밍', name: '게임엔진프로그래밍', module: 16, prereqs: ['게임프로그래밍'] },

		// 캡스톤
		{ id: '어드벤처디자인', name: '어드벤처디자인', module: 'capstone', prereqs: [], type: '설계' },
		{ id: '공개SW프로젝트', name: '공개SW프로젝트', module: 'capstone', prereqs: ['어드벤처디자인', '기초프로그래밍'], type: '설계' }, // 화살표 + 'C' 아이콘
		{ id: '종합설계1', name: '종합설계1', module: 'capstone', prereqs: ['공개SW프로젝트'], type: '설계' },
		{ id: '종합설계2', name: '종합설계2', module: 'capstone', prereqs: ['종합설계1'], type: '설계' }
	];

	// --- 2. 후수과목 자동 계산 ---
	const courseMap = new Map(allCourses.map(c => [c.id, { ...c, postreqs: [] }]));
	courseMap.forEach(course => {
		course.prereqs.forEach(prereqId => {
			const prereqCourse = courseMap.get(prereqId);
			if (prereqCourse) {
				prereqCourse.postreqs.push(course.id);
			}
		});
	});

	// --- 3. 헬퍼 함수 (카드 생성) ---
	const createCard = (course) => {
		let colors = 'bg-white border-gray-300 hover:bg-orange-50';
		if (course.type === 'BSM') {
			colors = 'bg-purple-50 border-purple-200 hover:bg-purple-100';
		} else if (course.type === '설계') {
			colors = 'bg-yellow-50 border-yellow-300 hover:bg-yellow-100';
		} else if (course.type === '핵심') {
			colors = 'bg-orange-50 border-orange-400 hover:bg-orange-100 font-bold';
		}
		
		return `
			<div class="course-card p-3 rounded-lg shadow-sm font-semibold text-sm
									${colors} border flex-1 break-words cursor-pointer transition-all
									min-w-[140px] max-w-full"
					data-course-id="${course.id}"
					data-prereqs="${course.prereqs.join(',')}"
					data-postreqs="${course.postreqs.join(',')}"
					data-module-id="${course.module}">
				<div class="text-center">${course.name}</div>
			</div>`;
	};

	// --- 4. 모듈 HTML 생성 ---
	const modulesHTML = Object.entries(modules).map(([moduleKey, moduleInfo]) => {
		const coursesInModule = Array.from(courseMap.values()).filter(c => c.module == moduleKey);
		if (coursesInModule.length === 0) return '';
		return `
			<div id="${moduleInfo.id}" class="module-container p-4 rounded-lg bg-gray-50 border">
				<h3 class="font-bold text-lg text-gray-800 mb-4 pb-2 border-b">${moduleInfo.title}</h3>
				<div class="flex flex-wrap items-start gap-2 md:gap-3">
					${coursesInModule.map(createCard).join('')}
				</div>
			</div>`;
	}).join('');

	// --- 5. 트랙 선택 드롭다운 HTML 생성 ---
	const trackOptions = Object.keys(trackData).map(trackName => {
		const moduleIds = trackData[trackName].map(num => modules[num]?.id).filter(Boolean).join(',');
		return `<a href="#" class="track-option-item block px-4 py-2 text-sm text-gray-700 hover:bg-orange-100" data-track-name="${trackName}" data-track-modules="${moduleIds}">${trackName}</a>`;
	}).join('');

	// --- 6. 최종 HTML 반환 ---
	return `
		<div class="flex items-center justify-between mb-4 flex-wrap gap-2">
			<h2 class='font-semibold text-xl'>컴퓨터ㆍAI학부 이수체계도</h2>
			<button id="guide-toggle-btn" class="text-sm text-orange-600 font-semibold hover:underline">이수체계도 안내 보기 ❓</button>
		</div>

		<div id="guide-details-box" class="hidden mb-6 p-4 bg-orange-50 rounded-lg border border-orange-200 text-sm space-y-3">
			<h3 class="font-bold text-orange-800 text-base">이수체계도 안내</h3>
			<p>과목 카드를 클릭하면 선수/후수 관계를 확인할 수 있습니다.</p>
			<div class="flex items-center gap-2"><div class="w-5 h-5 flex-shrink-0 rounded border-2 border-orange-500 bg-orange-50"></div><b>선택한 과목</b></div>
			<div class="flex items-center gap-2"><div class="w-5 h-5 flex-shrink-0 rounded border-2 border-blue-500 bg-blue-50"></div><b>선수 과목</b> (먼저 들어야 하는 과목)</div>
			<div class="flex items-center gap-2"><div class="w-5 h-5 flex-shrink-0 rounded border-2 border-green-500 bg-green-50"></div><b>후수 과목</b> (이후 들을 수 있는 과목)</div>
			<div class="flex items-center gap-2"><div class="w-5 h-5 flex-shrink-0 rounded border-2 border-gray-300 bg-white opacity-30"></div><b>관계 없는 과목</b></div>
			<div class="flex items-center gap-2"><div class="w-5 h-5 flex-shrink-0 rounded border-2 border-purple-200 bg-purple-50"></div><b>BSM 과목</b></div>
		</div>
		
		<div class="flex items-center gap-4 mb-6 flex-wrap">
			<div class="relative inline-block text-left" id="track-selector-container">
				<div>
					<button type="button" class="inline-flex justify-between w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none" id="track-selector-btn">
						<span id="track-selector-label">선택 안 함</span>
						<svg class="-mr-1 ml-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 0 010-1.414z" clip-rule="evenodd" /></svg>
					</button>
				</div>
				<div class="origin-top-right absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none hidden z-10" id="track-options-list">
					<div class="py-1" role="none">${trackOptions}</div>
				</div>
			</div>
			<button id="view-my-track-btn" class="px-3 py-1.5 bg-orange-500 text-white font-semibold rounded-md shadow-sm hover:bg-orange-600 transition">나의 트랙 보기</button>
		</div>

		<div id="module-wrapper" class="space-y-6 overflow-x-hidden">
			${modulesHTML}
		</div>
	`;
}

function renderTab(tab) {
	if (tab === 'courses') {
		tabContent.innerHTML = renderCoursePlan();

		const guideToggleBtn = document.getElementById('guide-toggle-btn');
		const guideDetailsBox = document.getElementById('guide-details-box');
		const container = document.getElementById('track-selector-container');
		const btn = document.getElementById('track-selector-btn');
		const label = document.getElementById('track-selector-label');
		const optionsList = document.getElementById('track-options-list');
		const allModules = document.querySelectorAll('.module-container');
		const viewMyTrackBtn = document.getElementById('view-my-track-btn');

		guideToggleBtn.addEventListener('click', () => {
			const isHidden = guideDetailsBox.classList.toggle('hidden');
			guideToggleBtn.innerHTML = isHidden ? '이수체계도 안내 보기 ❓' : '이수체계도 안내 닫기 ❌';
		});
		
		btn.addEventListener('click', () => {
			optionsList.classList.toggle('hidden');
		});

		optionsList.addEventListener('click', (e) => {
			e.preventDefault();
			const target = e.target.closest('.track-option-item');
			if (!target) return;

			const trackName = target.dataset.trackName;
			const modulesToShow = target.dataset.trackModules.split(',');

			label.textContent = trackName;
			optionsList.classList.add('hidden');

			allModules.forEach(module => {
				module.style.display = modulesToShow.includes(module.id) ? 'block' : 'none';
			});
		});

		viewMyTrackBtn.addEventListener('click', () => {
			fetch("https://nexcode.kr:16003/data/mydata", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ student_id: studentId })
			})
			.then(res => res.json())
			.then(json => {
				const profileDataString = json.data.track;
				const myTrack = profileDataString || '선택 안 함';
				const trackOption = document.querySelector(`.track-option-item[data-track-name="${myTrack}"]`);
				if (trackOption) {
					trackOption.click();
					alert(`'${myTrack}'에 맞는 모듈을 표시합니다.`);
				} else {
					document.querySelector('.track-option-item[data-track-name="선택 안 함"]')?.click();
				}
			})
			.catch(error => {
				console.error("Error fetching completed courses:", error);
				tabContent.innerHTML = `<p class="p-4 text-red-500">데이터를 불러오는 중 오류가 발생했습니다.</p>`;
			});
		});

		window.addEventListener('click', (e) => {
			if (!container.contains(e.target)) {
				optionsList.classList.add('hidden');
			}
		});

		const moduleWrapper = document.getElementById('module-wrapper');
		if (moduleWrapper) {
			const allCards = moduleWrapper.querySelectorAll('.course-card');

			moduleWrapper.addEventListener('click', (e) => {
				const card = e.target.closest('.course-card');
				if (!card) {
					allCards.forEach(c => {
						c.classList.remove('opacity-30', 'selected', 'prereq', 'postreq');
					});
					return;
				}

				const selectedId = card.dataset.courseId;
				const prereqIds = card.dataset.prereqs.split(',').filter(Boolean);
				const postreqIds = card.dataset.postreqs.split(',').filter(Boolean);
				const isAlreadySelected = card.classList.contains('selected');

				allCards.forEach(c => {
					c.classList.remove('selected', 'prereq', 'postreq');
					c.classList.add('opacity-30');
				});

				if (isAlreadySelected) {
					allCards.forEach(c => c.classList.remove('opacity-30'));
					return;
				}

				allCards.forEach(c => {
					const id = c.dataset.courseId;

					if (id === selectedId) {
						c.classList.remove('opacity-30');
						c.classList.add('selected');
					} else if (prereqIds.includes(id)) {
						c.classList.remove('opacity-30');
						c.classList.add('prereq');
					} else if (postreqIds.includes(id)) {
						c.classList.remove('opacity-30');
						c.classList.add('postreq');
					}
				});
			});
		}
	} else if (tab === 'recommend') {
		const studentId = idText.textContent;
		tabContent.innerHTML = `<div class="p-6 text-center text-gray-500">
			<p>추천 데이터를 불러오는 중입니다...</p>
			<p class="text-sm">(학생 ID: ${studentId})</p>
		</div>`;

		async function loadRecommendations() {
			try {
				const now = new Date();
			    const currentMonth = now.getMonth()
			
			    let next_term_num;
			
			    // 1학기 신청 기간 (11월, 12월, 1월, 2월)
			    if (currentMonth >= 3 || currentMonth <= 8) {
			        next_term_num = 1;
			    }
			    else {
			        next_term_num = 2;
			    }
			
				const response = await fetch('https://nexcode.kr:16003/recommendations', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ student_id: studentId, next_term: next_term_num })
				});
				if (!response.ok) {
					const errorData = await response.json();
					throw new Error(errorData.message || '데이터를 불러오는 데 실패했습니다.');
				}
				const data = await response.json();
				if (data.status !== 'success') {
					throw new Error(data.message || 'API 응답 오류');
				}

				const backendMajors = data.recommendations.majors;
				const backendLiberalArts = data.recommendations.liberal_arts;

				const majorCourses = backendMajors.map(c => ({
					type: ((c.sbj_no[0] != 'C') ? 'BSM' : ((c.sbj_no[3] == '2') ? '전공기초' : '전공전문')),
					name: c.name,
					sbj_no: c.sbj_no,
					credit: c.credit,
					description: ((c.description != null) ? c.description : ''),
					note: `트랙: ${c.track.join(', ') || '없음'}`
				}));

				const otherCourses = backendLiberalArts.map(c => ({
					type: c.category,
					name: c.name,
					sbj_no: c.sbj_no,
					credit: c.credit,
					description: c.description,
					note: ((c.min_grade > 1) ? `최소 학년: ${c.min_grade}학년` : ``)
				}));

				// ====== 변경점: (1) 각 항목에 번호, (2) 초기 4개만 보이기 + 드롭다운 ======
				function generateRecommendSectionHTML(title, courses, idPrefix) {
					const total = (courses?.length || 0);
					const previewCount = Math.min(4, total);
					const extraCount = Math.max(0, total - previewCount);

					if (!courses || total === 0) {
						return `
						<div id="${idPrefix}-recommend-section" class="mb-8">
							<h3 class='font-semibold text-lg'>${title} <span class="text-sm text-gray-500">(0)</span></h3>
							<p class="text-gray-500 text-sm px-2">추천 강의가 없습니다.</p>
						</div>
						`;
					}

					return `
					<div id="${idPrefix}-recommend-section" class="mb-8">
						<div class="flex flex-wrap justify-between items-center gap-4 mb-4">
							<h3 class='font-semibold text-lg'>
								${title} <span class="text-sm text-gray-500">(${total})</span>
							</h3>
							<div class="view-toggle-buttons text-sm font-medium border border-gray-300 rounded-lg overflow-hidden flex" role="tablist" aria-label="${title} 보기 전환">
								<button role="tab" aria-selected="true" data-view="list" class="toggle-btn px-3 py-1 bg-orange-500 text-white">전체 보기</button>
								<button role="tab" aria-selected="false" data-view="detail" class="toggle-btn px-3 py-1 bg-white text-gray-700 hover:bg-gray-100">자세히 보기</button>
							</div>
						</div>

						<div class="recommend-grid-view">
							<div class="grid gap-4 md:grid-cols-2">
								${courses.map((c, index) => `
									<div class="course-card border border-orange-200 rounded-xl p-4 shadow-sm bg-orange-50 text-gray-800
											hover:bg-orange-100 hover:border-orange-300 hover:shadow-md
											transition-all duration-200 ease-in-out cursor-pointer ${index >= previewCount ? 'hidden' : ''}"
											data-name="${c.name}" data-index="${index}" ${index >= previewCount ? 'data-extra="1"' : ''}>
										<div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 mb-2">
											<div class="flex items-center gap-2 min-w-0">
												<span class="inline-flex items-center justify-center w-6 h-6 text-xs rounded-full border border-orange-300 bg-white/70"> ${index + 1} </span>
												<span class="font-bold text-gray-900 text-lg truncate" title="${c.name}">${c.name}</span>
											</div>
											<div class="flex items-baseline gap-x-3 text-sm flex-shrink-0">
												<span class="text-gray-600 font-medium">${c.type}</span>
												<span class="text-orange-600 font-medium">학점: ${c.credit}</span>
											</div>
										</div>
										<p class="text-sm text-gray-700">${c.note || ''}</p>
									</div>
								`).join("")}
							</div>
							${extraCount > 0 ? `
								<div class="mt-3 text-center">
									<button type="button" class="show-more-btn inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border text-sm hover:bg-gray-50"
										aria-expanded="false" aria-controls="${idPrefix}-extra"
									>더 보기 ${extraCount}개</button>
								</div>
							` : ``}
						</div>

						<div class="recommend-detail-view hidden">
							<div class="relative">
								<div class="swiper ${idPrefix}-swiper overflow-hidden rounded-xl border border-orange-200 bg-orange-50 mx-4 md:mx-12">
									<div class="swiper-wrapper flex transition-transform duration-300 ease-in-out">
										${courses.map((c, idx) => `
											<div class="swiper-slide w-full flex-shrink-0 p-8">
												<div class="flex flex-wrap justify-between items-baseline gap-x-4 gap-y-1 mb-3">
													<div class="flex items-center gap-2 min-w-0">
														<span class="inline-flex items-center justify-center w-7 h-7 text-xs rounded-full border border-orange-300 bg-white/70"> ${idx + 1} </span>
														<span class="font-bold text-gray-900 text-xl truncate" title="${c.name}">${c.name}</span>
													</div>
													<div class="flex items-baseline gap-x-3 text-base flex-shrink-0">
														<span class="text-black-600 font-medium">${c.sbj_no}</span>
														<span class="text-gray-600 font-medium">${c.type}</span>
														<span class="text-orange-600 font-medium">학점: ${c.credit}</span>
													</div>
												</div>
												<p class="text-base text-gray-700">${c.description || ''}</p>
												<p class="text-base text-gray-700 mb-6">${c.note || ''}</p>
											</div>
										`).join("")}
									</div>
									<div class="swiper-pagination ${idPrefix}-pagination"></div>
								</div>
								
								<button class="swiper-button-prev ${idPrefix}-prev absolute top-1/2 -translate-y-1/2 text-orange-600 transition duration-150 ease-in-out bg-transparent hover:scale-110 disabled:opacity-50" aria-label="이전 강의">
								    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" /></svg>
								</button>
								<button class="swiper-button-next ${idPrefix}-next absolute top-1/2 -translate-y-1/2 text-orange-600 transition duration-150 ease-in-out bg-transparent hover:scale-110 disabled:opacity-50" aria-label="다음 강의">
								    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" /></svg>
								</button>
							</div>
							<div class="text-center text-sm text-gray-600 mt-2">
								<span class="detail-page-counter"></span>
							</div>
						</div>
					</div>
					`;
				}
				
				function initializeDetailSwiper() {
					
					// 1. 'major' 섹션 Swiper 초기화
					const majorSwiperElement = document.querySelector(".major-swiper");
					if (majorSwiperElement && !majorSwiperElement.swiper) {
						new Swiper(majorSwiperElement, {
							autoHeight: true, 
							slidesPerView: 1,
							spaceBetween: 0, 
							// 고유 클래스 지정
							pagination: {
								el: ".major-pagination",
								clickable: true,
							},
							navigation: {
								nextEl: ".major-next",
								prevEl: ".major-prev",
							},
							watchSlidesProgress: true,
						});
					}

					// 2. 'other' 섹션 Swiper 초기화
					const otherSwiperElement = document.querySelector(".other-swiper");
					if (otherSwiperElement && !otherSwiperElement.swiper) {
						new Swiper(otherSwiperElement, {
							autoHeight: true, 
							slidesPerView: 1,
							spaceBetween: 0, 
							// 고유 클래스 지정
							pagination: {
								el: ".other-pagination",
								clickable: true,
							},
							navigation: {
								nextEl: ".other-next",
								prevEl: ".other-prev",
							},
							watchSlidesProgress: true,
						});
					}
				}

				function initializeRecommendSection(containerSelector, courses) {
					const sectionContainer = tabContent.querySelector(containerSelector);
					if (!sectionContainer || !courses || courses.length === 0) {
						return;
					}

					const gridView = sectionContainer.querySelector(".recommend-grid-view");
					const detailView = sectionContainer.querySelector(".recommend-detail-view");
					const toggleButtonsContainer = sectionContainer.querySelector(".view-toggle-buttons");
					const toggleButtons = toggleButtonsContainer.querySelectorAll(".toggle-btn");
					const gridCards = gridView.querySelectorAll(".course-card");
					
					// 기존 수동 슬라이더 관련 변수 제거 (주석 처리)
					// const sliderWrapper = detailView.querySelector(".detail-slider-wrapper");
					// const prevBtn = detailView.querySelector(".detail-prev-btn");
					// const nextBtn = detailView.querySelector(".detail-next-btn");
					// const pageCounter = detailView.querySelector(".detail-page-counter");
					
					const showMoreBtn = sectionContainer.querySelector(".show-more-btn");
					const extraItems = sectionContainer.querySelectorAll('.course-card[data-extra="1"]');

					let gridExpanded = false; // 초기에는 상위 4개만
					
					// 수동 슬라이더 위치 업데이트 함수 제거 (주석 처리)
					// function updateSliderPosition(index) { ... }


					function switchView(viewName, slideIndex = -1) {
						if (viewName === 'detail') {
							gridView.classList.add('hidden');
							detailView.classList.remove('hidden');
							toggleButtons[0].classList.replace('bg-orange-500', 'bg-white');
							toggleButtons[0].classList.replace('text-white', 'text-gray-700');
							toggleButtons[0].classList.add('hover:bg-gray-100');
							toggleButtons[0].setAttribute('aria-selected', 'false');
							toggleButtons[1].classList.replace('bg-white', 'bg-orange-500');
							toggleButtons[1].classList.replace('text-gray-700', 'text-white');
							toggleButtons[1].classList.remove('hover:bg-gray-100');
							toggleButtons[1].setAttribute('aria-selected', 'true');
							
							// 예: "#major-recommend-section" -> "major-swiper"
							const prefix = containerSelector.substring(1).split('-')[0]; // "major" 또는 "other"
							const swiperClass = `.${prefix}-swiper`;
							const currentSwiper = document.querySelector(swiperClass)?.swiper;
							
							if (currentSwiper && slideIndex !== -1) {
								currentSwiper.slideTo(slideIndex);
							}
							
						} else {
							detailView.classList.add('hidden');
							gridView.classList.remove('hidden');
							toggleButtons[1].classList.replace('bg-orange-500', 'bg-white');
							toggleButtons[1].classList.replace('text-white', 'text-gray-700');
							toggleButtons[1].classList.add('hover:bg-gray-100');
							toggleButtons[1].setAttribute('aria-selected', 'false');
							toggleButtons[0].classList.replace('bg-white', 'bg-orange-500');
							toggleButtons[0].classList.replace('text-gray-700', 'text-white');
							toggleButtons[0].classList.remove('hover:bg-gray-100');
							toggleButtons[0].setAttribute('aria-selected', 'true');
						}
					}

					// 드롭다운(더 보기) 토글
					if (showMoreBtn && extraItems.length > 0) {
						showMoreBtn.addEventListener('click', () => {
							gridExpanded = !gridExpanded;
							extraItems.forEach(el => el.classList.toggle('hidden', !gridExpanded));
							showMoreBtn.textContent = gridExpanded ? '접기' : `더 보기 ${extraItems.length}개`;
							showMoreBtn.setAttribute('aria-expanded', gridExpanded ? 'true' : 'false');
						});
					}

					toggleButtonsContainer.addEventListener('click', (e) => {
						const btn = e.target.closest('.toggle-btn');
						if (btn) {
							switchView(btn.dataset.view);
						}
					});

					gridCards.forEach((card) => {
						card.addEventListener('click', () => {
							const index = parseInt(card.dataset.index, 10);
							switchView('detail', index);
						});
					});

					// 수동 버튼 이벤트 리스너 제거 (Swiper가 처리)
					// prevBtn.addEventListener('click', () => { updateSliderPosition(currentDetailIndex - 1); });
					// nextBtn.addEventListener('click', () => { updateSliderPosition(currentDetailIndex + 1); });
					// updateSliderPosition(0);

					initializeDetailSwiper();
				}

				const majorHTML = generateRecommendSectionHTML("전공 및 선이수", majorCourses, "major");
				const otherHTML = generateRecommendSectionHTML("기타", otherCourses, "other");
				
				tabContent.innerHTML = majorHTML + '<hr class="my-6 border-gray-200">' + otherHTML;
				initializeRecommendSection("#major-recommend-section", majorCourses);
				initializeRecommendSection("#other-recommend-section", otherCourses);

			} catch (error) {
				console.error("추천 로드 실패:", error);
				tabContent.innerHTML = `<div class="p-6 text-center text-red-500">
					<p>추천을 불러오는 중 오류가 발생했습니다.</p>
					<p class="text-sm">${error.message}</p>
				</div>`;
			}
		}

		loadRecommendations();
	} else if (tab === 'progress') {
		const studentId = idText.textContent;
		if (!studentId) return;

		fetch("https://nexcode.kr:16003/data/completed", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ student_id: studentId })
		})
		.then(res => res.json())
		.then(json => {
			if (json.status !== "success" || !json.data || !json.data.length) {
				tabContent.innerHTML = `<p class="p-4 text-gray-500">수강 완료 강의 정보가 없습니다.</p>`;
				return;
			}

			const nestedGroupedCourses = json.data.reduce((acc, course) => {
				const semester = course.open_yy_sem;
				if (!semester) return acc;

				if (!acc[semester]) {
					acc[semester] = {};
				}

				let category;
				switch (course.cpdv_nm) {
					case '일교': category = '일반교양'; break;
					case '공교': category = '공통교양'; break;
					case '전공': category = '전공'; break;
					default: category = '기타';
				}

				if (!acc[semester][category]) {
					acc[semester][category] = [];
				}
				
				acc[semester][category].push({
					code: course.sbj_no,
					name: course.name,
					dvcls: course.dvcls,
					professor: course.main_prof_nm,
					credit: course.credit,
					grade: course.grade_cd
				});

				return acc;
			}, {});

			const sortedSemesters = Object.keys(nestedGroupedCourses).sort((a, b) => b.localeCompare(a));
			const categoryOrder = ['전공', '공통교양', '일반교양', '기타'];

			tabContent.innerHTML = `
				<h3 class='font-semibold text-lg mb-3'>수강 완료 강의</h3>
				<div class="space-y-8">
					${sortedSemesters.map(semester => `
						<div class="semester-group">
							<h2 class="text-xl font-bold text-gray-800 pb-2 mb-4 border-b border-orange-300">${semester}</h2>
							<div class="space-y-6">
								
								${categoryOrder.map(category => {
									if (nestedGroupedCourses[semester][category]) {
										return `
											<div>
												<h4 class="font-semibold text-orange-600 mb-2">${category}</h4>
												<table class="w-full text-sm border-collapse table-auto">
													<colgroup>
														<col style="width: 10%;">
														<col style="width: 43%;">
														<col style="width: 10%;">
														<col style="width: 17%;">
														<col style="width: 10%;">
														<col style="width: 10%;">
													</colgroup>
													<thead>
														<tr class="bg-orange-100 text-left">
															<th class="p-2 font-medium">과목코드</th>
															<th class="p-2 font-medium">과목명</th>
															<th class="p-2 font-medium">분반</th>
															<th class="p-2 font-medium">교수</th>
															<th class="p-2 font-medium">학점</th>
															<th class="p-2 font-medium">성취도</th>
														</tr>
													<thead>
													<tbody>
														${nestedGroupedCourses[semester][category].map(c => `
															<tr class="border-b border-gray-200">
																<td class="p-2">${c.code || '-'}</td>
																<td class="p-2">${c.name || '-'}</td>
																<td class="p-2">${c.dvcls || '-'}</td>
																<td class="p-2">${c.professor || '-'}</td>
																<td class="p-2">${c.credit !== null && c.credit !== undefined ? c.credit : '-'}</td>
																<td class="p-2">${c.grade || '-'}</td>
															</tr>
														`).join("")}
													</tbody>
												</table>
											</div>
										`;
									}
									return ''; 
								}).join("")}
							</div>
						</div>
					`).join("")}
				</div>
			`;
		})
		.catch(error => {
			console.error("Error fetching completed courses:", error);
			tabContent.innerHTML = `<p class="p-4 text-red-500">데이터를 불러오는 중 오류가 발생했습니다.</p>`;
		});
	} else if (tab === 'grade') {
		const studentId = idText.textContent;
		if (!studentId) return;

		tabContent.innerHTML = `
			<h3 class='font-semibold text-lg mb-3'>나의 학점</h3>
			<canvas id="gradeChart" class="w-full h-64"></canvas>
		`;

		const parseSem = (s) => {
			const str = String(s||'');
			let m = /(\d{4}).*([12])/.exec(str);
			if (m) return { y:+m[1], h:+m[2], raw:str };
			m = /(\d{4})[-_. ]?([12])/.exec(str);
			if (m) return { y:+m[1], h:+m[2], raw:str };
			return { y:0, h:0, raw:str };
		};
		const cmpSem = (a,b)=> (a.y!==b.y? a.y-b.y : a.h-b.h);

		const letterToPoint = (g)=>{
			if (g==null) return null;
			const L = String(g).replace(/\s+/g,'').toUpperCase();
			const map = { 'A+':4.5,'A0':4.0,'A':4.0,'B+':3.5,'B0':3.0,'B':3.0,'C+':2.5,'C0':2.0,'C':2.0,'D+':1.5,'D0':1.0,'D':1.0,'F':0,'P':null,'NP':0 };
			return map[L] ?? null;
		};
		const gpaWeighted = (rows)=> {
			return rows.reduce((acc,r)=>{
				const p = letterToPoint(r.grade_cd);
				const c = Number(r.credit)||0;
				if (p===null || c<=0) return acc;
				acc.n += p*c; acc.d += c; return acc;
			},{n:0,d:0});
		};

		fetch("https://nexcode.kr:16003/data/term", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ student_id: studentId })
		})
		.then(res => res.json())
		.then(async (json) => {
			if (json.status !== "success" || !json.data.length) {
				tabContent.innerHTML = `<p class="p-4 text-red-500">학점 정보가 없습니다.</p>`;
				return;
			}
			
			const termRows = json.data.slice();
			const labels = termRows.map(item => item.yy_sem_name);
			const values = termRows.map(item => Number(item.gpa));

			const pointLabelPlugin = {
				id: 'pointLabelPlugin',
				afterDatasetsDraw(chart, args, pluginOptions) {
					const { ctx } = chart;
					const dataset = chart.data.datasets[0];
					const meta = chart.getDatasetMeta(0);

					ctx.save();
					ctx.textAlign = 'center';
					ctx.textBaseline = 'bottom';
					ctx.fillStyle = pluginOptions.color || 'rgb(249,115,22)';
					ctx.font = `${pluginOptions.fontSize || 12}px sans-serif`;

					dataset.data.forEach((val, i) => {
						const dp = meta.data[i];
						if (!dp) return;
						const num = Number(val);
						if (!Number.isFinite(num)) return;

						const { x, y } = dp.getProps(['x', 'y'], true);
						const label = pluginOptions.formatter ? pluginOptions.formatter(num) : num;
						ctx.fillText(label, x, y - (pluginOptions.offset || 8));
					});

					ctx.restore();
				}
			};
			Chart.register(pointLabelPlugin);

			const ctx = document.getElementById("gradeChart").getContext("2d");
			new Chart(ctx, {
				type: 'line',
				data: {
					labels,
					datasets: [{
						label: '평균 학점',
						data: values,
						borderColor: 'rgb(249,115,22)',
						backgroundColor: 'rgba(249,115,22,0.2)',
						fill: true,
						tension: 0.3,
						pointRadius: 5,
						pointBackgroundColor: 'rgb(249,115,22)'
					}]
				},
				options: {
					responsive: true,
					plugins: {
						legend: { display: true },
						pointLabelPlugin: {
							color: 'rgb(249,115,22)',
							fontSize: 14,
							offset: 11,
							formatter: (v) => v.toFixed(2)
						}
					},
					scales: {
						y: { min: 0, max: 4.5, ticks: { stepSize: 0.5, autoSkip: false } }
					}
				}
			});

			// 요약 카드 값 계산
			const latest = termRows
				.map(r => ({ ...parseSem(r.yy_sem_name), gpa: Number(r.gpa) }))
				.sort(cmpSem).at(-1);
			const lastSemGpa = (latest && Number.isFinite(latest.gpa)) ? latest.gpa : null;

			// 총 누적: 학기별 GPA 산술평균
			const termGpas = termRows.map(r => Number(r.gpa)).filter(n => Number.isFinite(n));
			const overallGpa = termGpas.length ? termGpas.reduce((a,b)=>a+b,0) / termGpas.length : null;

			// 전공 가중 평균
			let majorGpa = null;
			try {
				const resCompleted = await fetch("https://nexcode.kr:16003/data/completed", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ student_id: studentId })
				});
				const j2 = await resCompleted.json();
				if (j2.status === 'success' && Array.isArray(j2.data) && j2.data.length){
					const majorOnly = j2.data
						.filter(r => r.cpdv_nm === '전공')
						.map(r => ({ grade_cd: r.grade_cd, credit: r.credit }));
					const W = gpaWeighted(majorOnly);
					if (W.d > 0) majorGpa = W.n / W.d;
				}
			} catch(e) {
				console.warn('completed 데이터 계산 중 오류', e);
			}

			if (typeof window.updateGradeSummary === 'function') {
				window.updateGradeSummary({
					last_sem_gpa: lastSemGpa,
					major_gpa: majorGpa,
					overall_gpa: overallGpa
				});
			} else {
				const mount = document.createElement('div');
				mount.className = 'mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3';
				const fmt = v => (typeof v==='number' ? v.toFixed(2)+' / 4.5' : '—');
				mount.innerHTML = `
					<div class="rounded-xl border p-4"><p class="text-xs text-gray-500">직전 학기</p><p class="text-2xl font-bold">${fmt(lastSemGpa)}</p></div>
					<div class="rounded-xl border p-4"><p class="text-xs text-gray-500">전공 과목</p><p class="text-2xl font-bold">${fmt(majorGpa)}</p></div>
					<div class="rounded-xl border p-4"><p class="text-xs text-gray-500">총 누적(학기 산술평균)</p><p class="text-2xl font-bold">${fmt(overallGpa)}</p></div>
				`;
				tabContent.appendChild(mount);
			}
		});
	} else if (tab === 'timetable') {
		const studentId = idText.textContent;
		const today = new Date();
		const year = today.getFullYear();
		const month = today.getMonth() + 1;
		const term = (month >= 3 && month <= 8) ? 1 : 2;
		if (!studentId) return;

		fetch("https://nexcode.kr:16003/data/curcourses", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ student_id: studentId, year: year, term: term })
		})
		.then(res => res.json())
		.then(json => {
			if (json.status !== "success" || !json.data || !json.data.length) {
				tabContent.innerHTML = `<p class="p-4 text-gray-500">현재 수강 강의 정보가 없습니다.</p>`;
				return;
			}

			const groupedCourses = json.data.reduce((acc, course) => {
				let category;
				switch (course.cpdv_nm) {
					case '일교': category = '일반교양'; break;
					case '공교': category = '공통교양'; break;
					case '전공': category = '전공'; break;
					default: category = '기타';
				}

				if (!acc[category]) {
					acc[category] = [];
				}
				
				acc[category].push({
					code: course.sbj_no,
					name: course.name,
					professor: course.main_prof_nm,
					credit: course.credit,
					time: course.timetable,
					location: course.ROOM_KOR_DSC
				});

				return acc;
			}, {});

			const categoryOrder = ['전공', '공통교양', '일반교양', '기타'];

			tabContent.innerHTML = `
				<h3 class='font-semibold text-lg mb-4'>현재 수강 강의</h3>
				<div class="space-y-8">
					<div>
						<h2 class="text-xl font-bold text-gray-800 pb-2 mb-4 border-b border-orange-300">${year}-${term}학기</h2>
						<div class="space-y-6">
							${categoryOrder.map(category => {
								if (groupedCourses[category] && groupedCourses[category].length > 0) {
									return `
										<div>
											<h4 class="font-semibold text-orange-600 mb-2">${category}</h4>
											<table class="w-full text-sm border-collapse table-auto">
												<colgroup>
													<col style="width: 10%;">
													<col style="width: 21%;">
													<col style="width: 17%;">
													<col style="width: 10%;">
													<col style="width: 21%;">
													<col style="width: 21%;">
												</colgroup>
												<thead>
													<tr class="bg-orange-100 text-left">
														<th class="p-2 font-medium">과목코드</th>
														<th class="p-2 font-medium">과목명</th>
														<th class="p-2 font-medium">교수</th>
														<th class="p-2 font-medium">학점</th>
														<th class="p-2 font-medium">강의시간</th>
														<th class="p-2 font-medium">강의실</th>
													</tr>
												</thead>
												<tbody>
													${groupedCourses[category].map(c => `
														<tr class="border-b border-gray-200">
															<td class="p-2">${c.code || '-'}</td>
															<td class="p-2">${c.name || '-'}</td>
															<td class="p-2">${c.professor || '-'}</td>
															<td class="p-2">${c.credit !== null ? c.credit : '-'}</td>
															<td class="p-2">${c.time || '-'}</td>
															<td class="p-2">${c.location || '-'}</td>
														</tr>
													`).join("")}
												</tbody>
											</table>
										</div>
									`;
								}
								return '';
							}).join("")}
						</div>
					</div>
				</div>
			`;
		})
		.catch(error => {
			console.error("Error fetching current courses:", error);
			tabContent.innerHTML = `<p class="p-4 text-red-500">데이터를 불러오는 중 오류가 발생했습니다.</p>`;
		});
	}
	// ===== [복구] 학사일정 탭 =====
	else if (tab === 'calendar') {
		const year = new Date().getFullYear();
		tabContent.innerHTML = `
			<h3 class='font-semibold text-lg mb-3'>학사일정</h3>
			<p class="text-sm text-gray-500 px-2">불러오는 중…</p>
		`;

		const fmtDate = (d) => {
			if (!(d instanceof Date) || isNaN(d)) return '-';
			const w = ['일','월','화','수','목','금','토'][d.getDay()];
			return `${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')}(${w})`;
		};

		fetch("https://nexcode.kr:16003/data/calendar", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ year })
		})
		.then(res => res.json())
		.then(json => {
			if (json.status !== "success" || !Array.isArray(json.data) || json.data.length === 0) {
				tabContent.innerHTML = `<p class="p-4 text-gray-500">학사일정 데이터가 없습니다.</p>`;
				return;
			}

			// 다양한 필드명 대응
			const events = json.data.map(ev => {
				const title = ev.title || ev.name || ev.event || '일정';
				const s = ev.start || ev.start_date || ev.date || ev.begin || ev.from;
				const e = ev.end || ev.end_date || ev.to || ev.finish || s;
				const loc = ev.location || ev.place || '';
				const sd = new Date(s);
				const ed = new Date(e);
				return { title, start: sd, end: ed, location: loc };
			}).filter(ev => !isNaN(ev.start)).sort((a,b)=>a.start - b.start);

			// 월별 그룹화
			const byMonth = events.reduce((acc, ev) => {
				const key = `${ev.start.getFullYear()}-${String(ev.start.getMonth()+1).padStart(2,'0')}`;
				(acc[key] ||= []).push(ev);
				return acc;
			}, {});
			const months = Object.keys(byMonth).sort();

			tabContent.innerHTML = `
				<h3 class='font-semibold text-lg mb-3'>학사일정 (${year})</h3>
				<div class="space-y-8">
					${months.map(m => {
						const [yy, mm] = m.split('-');
						const rows = byMonth[m].map(ev => `
							<tr class="border-b border-gray-200">
								<td class="p-2 whitespace-nowrap">
									${fmtDate(ev.start)}${(ev.end && ev.end > ev.start) ? ` ~ ${fmtDate(ev.end)}` : ''}
								</td>
								<td class="p-2">${ev.title}</td>
								<td class="p-2">${ev.location || '-'}</td>
							</tr>
						`).join('');
						return `
							<div>
								<h4 class="text-base font-bold text-gray-800 pb-2 mb-2 border-b border-orange-300">${yy}년 ${mm}월</h4>
								<table class="w-full text-sm border-collapse table-auto">
									<colgroup>
										<col style="width: 30%;">
										<col style="width: 50%;">
										<col style="width: 20%;">
									</colgroup>
									<thead>
										<tr class="bg-orange-100 text-left">
											<th class="p-2 font-medium">날짜</th>
											<th class="p-2 font-medium">일정</th>
											<th class="p-2 font-medium">장소</th>
										</tr>
									</thead>
									<tbody>${rows}</tbody>
								</table>
							</div>
						`;
					}).join('')}
				</div>
			`;
		})
		.catch(err => {
			console.error('학사일정 로드 오류:', err);
			tabContent.innerHTML = `<p class="p-4 text-red-500">학사일정을 불러오는 중 오류가 발생했습니다.</p>`;
		});
	}
}

tabs.forEach(btn => {
	btn.addEventListener('click', () => {
		tabs.forEach(b => b.classList.remove('bg-orange-500','text-white'));
		btn.classList.add('bg-orange-500','text-white');
		renderTab(btn.dataset.tab);
	});
});

// 초기 렌더링
renderTab('recommend');
document.querySelector('[data-tab="recommend"]').classList.add('bg-orange-500','text-white');

// [추가] 로고 클릭 시 초기 화면(추천 강의)로 이동
const logoHome = document.getElementById('logoHome');
if (logoHome) {
	logoHome.addEventListener('click', () => {
		window.location.href = "/";
	});
}

// [추가] '나의 정보' 탭 클릭 시 mypage.html로 이동 (이후 IIFE에서 모달로 대체됨)
const myInfoTab = document.getElementById('myInfoTab');
if (myInfoTab) {
	myInfoTab.addEventListener('click', (e) => {
		e.preventDefault();
		window.location.href = "/mypage.html";
	});
}

/* ========= 체크리스트 로직 ========= */
const dummyStatus = {
	common: 14, basic: 6, bsm: 21, major: 70, total: 128,
	gpa: 2.3, toeic: null, eng_course: 3,
	design1: false, design2: false, individual: true
};

const goals = {
	common: 25, basic: 6, bsm: 21, major: 72, total: 130,
	gpa: 2.0, toeic: 700, eng_course: 4,
	design1: 1, design2: 1, individual: 1
};

// 서버에서 받아온 주요 과목 리스트 보관 (필수/이수 여부 판정용)
let MAIN_COURSES = null;
// 미이수 필수과목 리스트
let MISSING_REQUIRED = [];

// 필수과목 추출 & 미이수 산정 (다양한 응답 포맷에 대응)
function computeMissingRequired(courseData) {
	try {
		const missing = new Set();

		// 1) 과목 배열 형태: [{name, required, completed/grade/...}, ...]
		if (Array.isArray(courseData)) {
			for (const c of courseData) {
				const name = c.name || c.course_name || c.title;
				const isRequired = c.required === true || c.req === true || c.is_required === true;
				const completed = !!(c.completed || c.done || c.passed || c.grade || c.is_completed);
				if (isRequired) {
					if (!completed && name) missing.add(name);
				}
			}
		}

		// 2) 별도 키 존재: { required: [names], completed: [names] } 또는 codes 등
		if (courseData && typeof courseData === 'object' && !Array.isArray(courseData)) {
			const reqArr = courseData.required || courseData.requiredCourses || [];
			const compArr = courseData.completed || courseData.completedCourses || [];
			const compSet = new Set(compArr);
			if (Array.isArray(reqArr)) {
				for (const name of reqArr) {
					if (name && !compSet.has(name)) missing.add(name);
				}
			}
		}

		// 3) 종합설계 필수 반영(백엔드 불일치 대비): checklist 설계 플래그 사용
		if (dummyStatus.design1 === false) missing.add('종합설계1');
		if (dummyStatus.design2 === false) missing.add('종합설계2/개별연구');

		return Array.from(missing);
	} catch(e) {
		console.warn('필수과목 계산 중 예외:', e);
		return [];
	}
}

/* ====== (NEW) 미이수 패널 렌더/토글 ====== */
function renderMissingPanel() {
	const container = document.getElementById('missingPanel');
	if (!container) return;

	if (!MISSING_REQUIRED.length) {
		container.innerHTML = `
			<div class="rounded-xl border border-emerald-200 bg-emerald-50 text-emerald-800 p-3">
				<div class="flex items-center justify-between">
					<p class="font-semibold">미이수 필수 과목 없음</p>
					<button id="missingPanelCloseOk" class="text-xs px-2 py-1 rounded-md bg-white border">닫기</button>
				</div>
				<p class="text-sm mt-1">모든 필수 과목을 충족했습니다. ✅</p>
			</div>`;
		document.getElementById('missingPanelCloseOk')?.addEventListener('click', () => container.classList.add('hidden'));
		return;
	}

	container.innerHTML = `
		<div class="rounded-xl border border-amber-200 bg-amber-50 p-3">
			<div class="flex items-center justify-between">
				<p class="font-semibold text-amber-800">미이수 필수 과목</p>
				<button id="missingPanelClose" class="text-xs px-2 py-1 rounded-md bg-white border">닫기</button>
			</div>
			<ul class="mt-2 list-disc pl-5 text-sm text-amber-900">
				${MISSING_REQUIRED.map(n => `<li>${n}</li>`).join('')}
			</ul>
		</div>`;
	document.getElementById('missingPanelClose')?.addEventListener('click', () => container.classList.add('hidden'));
}

function toggleMissingPanel() {
	const panel = document.getElementById('missingPanel');
	if (!panel) return;
	renderMissingPanel();
	panel.classList.toggle('hidden');
}

function bindMissingPanelToggle() {
	const warnBtn = document.getElementById('progressWarn');
	const majorItem = document.getElementById('majorTodoItem');
	if (warnBtn) {
		warnBtn.addEventListener('click', toggleMissingPanel);
	}
	if (majorItem) {
		majorItem.addEventListener('click', (e) => {
			// 체크박스는 disabled라 클릭해도 변화 없음, 패널만 토글
			toggleMissingPanel();
		});
	}
}

/* ====== 경고/체크 표시에 대한 정책 ======
 * - 경고는 "전공 학점 충족 && 필수 미이수 존재"일 때만 노출
 * - 전공 체크박스는 (전공 학점 충족 && 필수 미이수 없음)일 때만 체크
 */
function applyRequiredWarnings() {
	const progressWarn = document.getElementById('progressWarn');
	const majorWarn = document.getElementById('majorWarn');

	const creditOk = Number(dummyStatus.major) >= Number(goals.major);
	const hasMissing = MISSING_REQUIRED.length > 0;
	const showWarn = creditOk && hasMissing;

	// 상단 진행률 왼쪽 경고
	if (progressWarn) {
		progressWarn.classList.toggle('hidden', !showWarn);
		progressWarn.title = showWarn ? `전공 필수 미이수: ${MISSING_REQUIRED.join(', ')}` : '';
	}

	// 전공 항목 라인 경고: 없으면 완전 숨김(display:none) -> 여백 제거
	if (majorWarn) {
		if (showWarn) {
			majorWarn.textContent = '⚠️';
			majorWarn.title = `미이수 필수과목: ${MISSING_REQUIRED.join(', ')}`;
			majorWarn.classList.remove('hidden');
			majorWarn.classList.add('cursor-pointer');
		} else {
			majorWarn.textContent = '';
			majorWarn.removeAttribute('title');
			majorWarn.classList.add('hidden'); // ← 여백 사라지게
			majorWarn.classList.remove('cursor-pointer');
		}
	}

	// 전공 체크박스는 "학점충족 && 미이수없음" 일 때만 완료 처리
	const majorCheckbox = document.querySelector('.todo[data-key="major"]');
	if (majorCheckbox) {
		majorCheckbox.checked = creditOk && !hasMissing;
	}

	// 진행률/정렬 재계산
	refreshChecklistProgress();

	// 경고/전공 클릭 토글 바인딩
	bindMissingPanelToggle();
}

// 진행률 바/레이블 재계산만 수행
function refreshChecklistProgress() {
	const progressBar = document.getElementById('progressBar');
	const progressLabel = document.getElementById('progressLabel');
	const todoCheckboxes = document.querySelectorAll('.todo');

	let completedCount = 0;
	todoCheckboxes.forEach(chk => { if (chk.checked) completedCount++; });

	const progressPercentage = (completedCount / todoCheckboxes.length) * 100;
	if (progressBar) progressBar.style.width = `${progressPercentage}%`;
	if (progressLabel) progressLabel.innerText = `${completedCount}/${todoCheckboxes.length} 완료`;

	// 미완료 먼저 보이도록 정렬
	const todoListContainer = document.getElementById('todoList');
	if (todoListContainer) {
		const listItems = Array.from(todoListContainer.children);
		listItems.sort((a, b) => {
			const aIsChecked = a.querySelector('.todo').checked;
			const bIsChecked = b.querySelector('.todo').checked;
			return aIsChecked - bIsChecked;
		});
		listItems.forEach(item => todoListContainer.appendChild(item));
	}
}

// 체크리스트 표시/체크 로직 (필수과목 반영 포함)
function updateChecklist() {
	const todoCheckboxes = document.querySelectorAll('.todo');

	todoCheckboxes.forEach(chk => {
		const key = chk.dataset.key;
		let done = dummyStatus[key];
		const total = goals[key];
		let progressText = "";

		if (typeof done === 'number') {
			// 숫자 항목은 "현재/목표" 형식 표기
			if (key === "gpa") {
				progressText = `${done?.toFixed?.(1) ?? '-'}/${total?.toFixed?.(1) ?? '-'}`;
				chk.checked = done >= total;
			} else if (key === "toeic") {
				progressText = `${done ?? 0}/${total}`;
				chk.checked = Number(done) >= Number(total);
			} else {
				progressText = `${done ?? 0}/${total}`;
				chk.checked = Number(done) >= Number(total);
			}
		} else if (typeof done === 'boolean') {
			progressText = done ? "완료" : "미완료";
			chk.checked = done;
		} else {
			progressText = "정보 없음";
			chk.checked = false;
		}

		// 전공 항목 체크는 applyRequiredWarnings에서 최종 보정
		const progressEl = document.getElementById(`${key}Progress`);
		if (progressEl) progressEl.innerText = progressText;
	});

	// 경고/체크 보정 및 진행률 갱신
	applyRequiredWarnings();
}

// 서버 통신: checklist + maincourses
const studentId = idText.textContent;
if (!studentId) {
	updateChecklist();
} else {
	// checklist(학점/설계/GPA/영강 등)
	fetch("https://nexcode.kr:16003/data/checklist", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ student_id: studentId }),
	})
	.then((res) => res.json())
	.then((json) => {
		if (json.status === "success" && json.data) {
			dummyStatus.basic = json.data.basic;
			dummyStatus.bsm = json.data.bsm;
			dummyStatus.common = json.data.common;
			dummyStatus.design1 = !!json.data.design1;
			dummyStatus.design2 = !!json.data.design2;
			dummyStatus.eng_course = json.data.eng_credit;
			dummyStatus.gpa = json.data.gpa;
			dummyStatus.major = json.data.major;
			dummyStatus.total = json.data.total_credit;
		}
	})
	.catch((error) => console.error("Error fetching checklist data:", error))
	.finally(() => {
		updateChecklist();
	});

	// maincourses(필수/이수 현황)
	updateCourseData(studentId).then(courseData => {
		MAIN_COURSES = courseData;
		MISSING_REQUIRED = computeMissingRequired(MAIN_COURSES);
		applyRequiredWarnings(); // 경고/체크 보정
	}).catch(() => {
		MAIN_COURSES = null;
		MISSING_REQUIRED = [];
		applyRequiredWarnings();
	});
}

// maincourses 요청 함수 (원본 유지 + 반환값 사용)
function updateCourseData(studentId) {
	return fetch("https://nexcode.kr:16003/data/maincourses", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ student_id: studentId }),
	})
	.then(res => res.json())
	.then(json => {
		if (json.status === "success" && json.data) {
			return json.data;
		} else {
			return null;
		}
	})
	.catch(error => {
		console.error("데이터 요청 중 오류:", error);
		return null;
	});
}

// --- '나의 정보' 클릭 시 모달로 비밀번호 확인 후 이동 (이전 리스너 무효화) ---
(() => {
	const modal = document.getElementById("pwModal");
	const overlay = document.getElementById("pwModalOverlay");
	const closeBtn = document.getElementById("pwModalClose");
	const cancelBtn = document.getElementById("pwCancel");
	const form = document.getElementById("pwForm");
	const pwInput = document.getElementById("pwInput");
	const pwError = document.getElementById("pwError");
	const pwToggle = document.getElementById("pwToggle");
	const eyeOn = document.getElementById("eyeOn");
	const eyeOff = document.getElementById("eyeOff");
	const submitBtn = form ? form.querySelector('button[type="submit"]') : null;

	const oldLink = document.getElementById("myInfoTab");
	if (!oldLink || !modal || !form || !submitBtn) return;

	const newLink = oldLink.cloneNode(true);
	oldLink.parentNode.replaceChild(newLink, oldLink);

	let lastFocused = null;

	const onKeydown = (e) => {
	if (e.key === "Escape") {
			e.preventDefault();
			closeModal();
		}
	};

	const openModal = () => {
		lastFocused = document.activeElement;
		modal.classList.remove("hidden");
		modal.classList.add("flex");
		if (pwError) pwError.classList.add("hidden");
		if (pwInput) {
			pwInput.value = "";
			setTimeout(() => pwInput.focus(), 0);
		}
		document.body.style.overflow = "hidden";
		document.addEventListener("keydown", onKeydown);
	};

	const closeModal = () => {
		modal.classList.add("hidden");
		modal.classList.remove("flex");
		document.body.style.overflow = "";
		document.removeEventListener("keydown", onKeydown);
		if (lastFocused) lastFocused.focus();
	};

	newLink.addEventListener("click", (e) => {
		e.preventDefault();
		openModal();
	});

	if (overlay) overlay.addEventListener("click", closeModal);
	if (closeBtn) closeBtn.addEventListener("click", closeModal);
	if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

	if (pwToggle && pwInput && eyeOn && eyeOff) {
		pwToggle.addEventListener("click", () => {
			const isText = pwInput.type === "text";
			pwInput.type = isText ? "password" : "text";
			eyeOn.classList.toggle("hidden", isText);
			eyeOff.classList.toggle("hidden", !isText);
			pwInput.focus();
		});
	}

	form.addEventListener("submit", async (e) => {
		e.preventDefault();
		const password = pwInput.value.trim();
		const studentId = document.getElementById("idText").textContent;

		if (!password) {
			if (pwError) pwError.classList.remove("hidden");
			if (pwInput) pwInput.focus();
			return;
		}
		
		if (pwError) pwError.classList.add("hidden");

		const originalBtnText = submitBtn.innerHTML;
		submitBtn.disabled = true;
		submitBtn.innerHTML = `<span class="spinner"></span> 확인 중...`;

		try {
			const response = await fetch("https://nexcode.kr:16003/login", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					username: studentId,
					password: password
				})
			});

			const result = await response.json();

			if (result.status === "success") {
				window.location.href = "/mypage.html";
			} else {
				alert("비밀번호가 일치하지 않습니다. 다시 확인해주세요.");
				pwInput.value = "";
				pwInput.focus();
			}
		} catch (err) {
			console.error("비밀번호 확인 중 오류:", err);
			alert("서버와 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
		} finally {
			submitBtn.disabled = false;
			submitBtn.innerHTML = originalBtnText;
		}
	});
})();
