# 아티팩트 (게시용 사본)

| 화면 | 주소 | 원본 |
|---|---|---|
| 문영위키 (인물위키) | https://claude.ai/artifact/JM9iRLeWXGpZZE3h4RTWDV | `02_웹앱/빌드/인물위키.html` |
| 문영TV (가사 영상, 라디오) | https://claude.ai/artifact/CkW6BpMk5EkZJAYYNVsZC1 | `02_웹앱/빌드/문영TV.html` |
| 문영일보 (뉴스) | https://claude.ai/artifact/FB262z41ts6fv9AuVNjSLB | 브랜치 `claude/zen-gauss-smepeo`의 `news-article/index.html` |

- 공유 설정은 각 페이지의 Share 메뉴에서 한다.
- 이 폴더의 html은 게시용 사본이다. 직접 고치지 않는다. 내용 수정은 원본에서.
- 위키의 `site.videoBase`에 문영TV 주소가, `site.newsBase`에 문영일보 주소가 들어 있다. 주소가 바뀌면 여기를 고친다.

## 수정 후 다시 게시하기

1. `02_웹앱/빌드/` 안의 원본을 고친다.
2. `python3 02_웹앱/도구/아티팩트용_변환.py` 로 사본을 다시 만든다. (`python3 … 문영TV` 처럼 이름을 주면 하나만)
3. 사본을 위 주소로 다시 게시한다. 다른 대화에서 게시할 때는 위 주소를 `url`로 넘겨야 같은 주소가 유지된다.

## 문영TV 영상 id (위키 `{{영상:id|라벨}}`에서 쓰는 값)

| id | 내용 |
|---|---|
| v-lyric-second-window | 이은호 《두 번째 창》 가사 영상 |
| v-lyric-focus | 김서진 《초점》 가사 영상 |
| v-lyric-low-long | 이은호 《낮게, 오래》 가사 영상 (사진 표지) |
| v-lyric-slowly | 김서진 《천천히 말해》 가사 영상 (사진 표지) |
| v-eunho-radio-2025 | 문영FM 밤의 음악실 이은호 편 (2025.08.20) |
| v-seojin-radio-2025 | 문영FM 밤의 음악실 김서진 편 (2025.12.19) |
| v-namgung-interview | 뮤직노트 남궁현 오디오 인터뷰 (2026.03.12) |
| v-eunho-height, v-seojin-short-answers, v-namgung-ending | 삭제 또는 비공개 안내 화면 |

별칭(옛 id): v-eunho-radio-euno, v-seojin-radio-height, v-seojin-webshow-mbti 는 모두 해당 라디오 편으로 연결된다.

## 위키 시점(턴)

- 문영일보와 같은 3턴(10.04 12:00 / 10.05 12:00 / 10.06 23:59). 위쪽 "현재 시점" 줄의 "다음 턴"으로 넘긴다.
- 교사는 특수 기능 > 시점 바꾸기(교사 학번 1444)로 아무 턴으로나 이동.
- 턴은 브라우저마다 저장된다. 게임 웹앱에 합칠 때는 `window.MOONYOUNG_TURN` 또는 `setWikiTurn(n)`으로 넘긴다.
- 시점별 내용과 편집 기록 설계는 `02_웹앱/원본/위키_타임라인_초안.md`.

## 기획사 설정 (2026-10-09)

- 소속사는 **제이엘컴퍼니 (JL COMPANY)**. 2018년 설립, 대표 남궁현(1981년생), 소속 아티스트는 이은호와 김서진 둘.
- 예전 이름 리버노트 엔터테인먼트와 그 소속 가상 아티스트(한소율, 노트포 등)는 모두 뺐다.
- 위키 문서 이름은 `제이엘컴퍼니`. JL Company, JL COMPANY, JL컴퍼니, 제이엘 컴퍼니로 검색해도 이 문서로 간다.
- 로고: 정보상자에는 JL COMPANY 워드마크(`infobox.imageSrc`), 상단 틀에는 흰색 JL 심볼(`navbox.logoSrc`). 원본과 웹용은 `02_웹앱/원본/제이엘컴퍼니/`.
- 교사용 비공개 설정(대표의 동기 등)은 공개 위키, 문영TV 어디에도 넣지 않는다.
