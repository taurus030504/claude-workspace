---
name: 문영 수사본부
description: 문영위키와 같은 위키 문서 양식으로 쓰는 사실 확인 수업용 수사 기록장
colors:
  top-bar-deep: "#08857A"
  top-bar-green: "#2CB27C"
  wiki-teal: "#0E9F92"
  teal-ink: "#0A7A70"
  table-head-teal: "#0B7D73"
  link-blue: "#0275D8"
  page-grey: "#F5F5F5"
  card-white: "#FFFFFF"
  border-grey: "#CCCCCC"
  border-soft: "#DDDDDD"
  hover-grey: "#F2F2F2"
  text-ink: "#212529"
  muted-grey: "#666666"
  selected-mint: "#EEFAF7"
  flash-yellow: "#FFF3B0"
  now-black: "#222222"
  source-wiki: "#0A7A70"
  source-news: "#2F6FB5"
  source-sns: "#C2477F"
  verdict-true: "#212529"
  verdict-false: "#C0392B"
  verdict-open: "#E0A800"
typography:
  logo:
    fontFamily: "Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "21px"
    fontWeight: 800
    lineHeight: 1.6
    letterSpacing: "-0.04em"
  display:
    fontFamily: "Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "36px"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "27px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "21px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  box-title:
    fontFamily: "Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.6
  body:
    fontFamily: "Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
  control:
    fontFamily: "Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.6
  meta:
    fontFamily: "Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "13.5px"
    fontWeight: 400
    lineHeight: 1.6
  tag:
    fontFamily: "Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "12.5px"
    fontWeight: 800
    lineHeight: 1.6
rounded:
  tag: "3px"
  control: "4px"
  card: "5px"
  chip: "15px"
spacing:
  hair: "4px"
  tight: "8px"
  row: "12px"
  gutter: "16px"
  card: "24px"
  section: "30px"
  page: "36px"
components:
  top-bar:
    backgroundColor: "{colors.top-bar-deep}"
    textColor: "{colors.card-white}"
    height: "56px"
    padding: "0 36px"
  team-field:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.text-ink}"
    rounded: "{rounded.tag}"
    height: "40px"
    width: "250px"
  turn-select:
    backgroundColor: "{colors.teal-ink}"
    textColor: "{colors.card-white}"
    rounded: "{rounded.control}"
    padding: "0 8px"
    height: "36px"
  document-card:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.text-ink}"
    rounded: "{rounded.card}"
    padding: "24px 24px 0"
  sidebar-card:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.text-ink}"
    rounded: "{rounded.card}"
    padding: "16px 20px"
  button:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.text-ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "36px"
  button-hover:
    backgroundColor: "{colors.hover-grey}"
    textColor: "{colors.text-ink}"
  button-primary:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.teal-ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "36px"
  input:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.text-ink}"
    rounded: "{rounded.control}"
    padding: "0 10px"
    height: "38px"
  verdict-button:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.text-ink}"
    padding: "0 14px"
    height: "38px"
  verdict-true-pressed:
    backgroundColor: "{colors.verdict-true}"
    textColor: "{colors.card-white}"
  verdict-false-pressed:
    backgroundColor: "{colors.verdict-false}"
    textColor: "{colors.card-white}"
  verdict-open-pressed:
    backgroundColor: "{colors.verdict-open}"
    textColor: "{colors.text-ink}"
  filter-chip:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.muted-grey}"
    rounded: "{rounded.chip}"
    padding: "0 12px"
    height: "30px"
  filter-chip-active:
    backgroundColor: "{colors.text-ink}"
    textColor: "{colors.card-white}"
  source-tag-wiki:
    backgroundColor: "{colors.source-wiki}"
    textColor: "{colors.card-white}"
    typography: "{typography.tag}"
    rounded: "{rounded.tag}"
    padding: "0 8px"
    height: "24px"
  source-tag-news:
    backgroundColor: "{colors.source-news}"
    textColor: "{colors.card-white}"
    typography: "{typography.tag}"
    rounded: "{rounded.tag}"
    padding: "0 8px"
    height: "24px"
  source-tag-sns:
    backgroundColor: "{colors.source-sns}"
    textColor: "{colors.card-white}"
    typography: "{typography.tag}"
    rounded: "{rounded.tag}"
    padding: "0 8px"
    height: "24px"
  table-head:
    backgroundColor: "{colors.table-head-teal}"
    textColor: "{colors.card-white}"
    padding: "6px 10px"
  turn-marker-now:
    backgroundColor: "{colors.now-black}"
    textColor: "{colors.card-white}"
    rounded: "{rounded.tag}"
    padding: "0 9px"
    height: "26px"
  selected-heading:
    backgroundColor: "{colors.selected-mint}"
    textColor: "{colors.text-ink}"
    padding: "6px 8px 8px"
---

# Design System: 문영 수사본부

## Overview

**Creative North Star: "수사 노트도 위키 문서다 (The Case as a Wiki Article)"**

수사 데스크는 대시보드가 아니라 한 편의 위키 문서다. 학생이 근거를 찾으러 읽는 문영위키(나무위키 양식의 가상 위키)와 똑같은 화면 언어로, 사건을 인물 문서처럼 써 내려간다. 청록에서 초록으로 넘어가는 상단 바, 연회색 바닥 위의 흰 문서 상자, 36px 문서 제목과 테두리 단추 묶음, 분류 줄, 동그란 아이콘 안내문, 오른쪽에 뜬 정보상자, 목차, 번호가 파랗게 붙은 문단 제목과 접기 단추, 청록 머리의 위키 표, 오른쪽 사이드바. 학생은 출처와 노트 사이를 오가며 다른 화면 문법을 다시 익히지 않아도 된다.

그러나 이 문서는 문영위키가 아니다. 돋보기 로고와 "문영 수사본부"라는 이름, 제목 앞의 "수사:" 이름공간, 그리고 "이 문서는 모둠의 수사 기록입니다"라는 안내문 한 줄이 노트와 원본을 구분한다. 나무위키의 이름과 로고는 쓰지 않는다. 밀도는 위키 문서처럼 높다. 장식 색은 없고, 색은 링크(파랑), 출처(문영위키의 스크랩 색 세 가지), 학생의 판정(검정, 빨강, 노랑), 그리고 위키의 청록 틀에만 쓴다.

움직임은 하나가 대표다. 선생님이 턴을 넘기면 2절 증거 시간선의 "지금" 표시가 다음 경계로 미끄러지고, 지나온 점선 구간이 한 번 실선으로 그려진다. 나머지는 접기 화살표 회전과 짧은 하이라이트뿐이다. 인물을 용의자처럼 보이게 하는 붉은 실이나 어두운 수사 게시판 연출은 쓰지 않는다.

**Key Characteristics:**
- 청록-초록 그라데이션 상단 바, #F5F5F5 바닥, 1px 회색 테두리의 흰 문서 상자와 사이드바 상자
- 문서 구조는 위키 그대로: 제목, 분류 줄, 안내문, 정보상자, 목차, 번호 붙은 문단과 접기
- 글꼴은 Noto Sans KR 하나, 위계는 크기와 굵기로
- 출처 = 문영위키 스크랩 색(위키 청록, 기사 파랑, SNS 자홍)과 글자 표시
- 판정 = 학생이 고른 색과 모양(체크, 사선, 점 세 개)
- 대표 부품은 증거 시간선: 출처별 줄, 날짜 순 점, 검은 "지금" 표시, 그 뒤의 점선

## Colors

문영위키의 청록 틀과 회색 문서 바탕 위에, 뜻이 정해진 몇 가지 색만 얹는 위키 팔레트다.

### Primary
- **상단 바 진한 청록** (`top-bar-deep`): 상단 바 그라데이션의 왼쪽 35% 구간과 돋보기 로고의 선. 흰 글자(로고, 문영위키·문영일보 메뉴)가 놓이는 자리다.
- **상단 바 초록** (`top-bar-green`): 상단 바 오른쪽 끝. 문영위키와 같은 초록이다. 정보상자 제목 띠는 흰 부제(13.5px)의 대비를 지키려고 상단 바 진한 청록(`top-bar-deep`)에서 표 머리 청록(`table-head-teal`)으로 넘어간다.
- **위키 청록** (`wiki-teal`): 문영위키 고유의 청록. 현재 시점 줄의 왼쪽 4px 띠, 고른 주장 제목의 밑줄, 정보상자 테두리와 제목 띠의 왼쪽 끝. 선과 면에만 쓰고, 그 위에 작은 흰 글자를 올리지 않는다.
- **청록 글자** (`teal-ink`): 흰 바탕 위의 청록 글자와 채움. 주요 단추("증거 연결", "증거 추가")의 글자와 테두리, 턴 선택칸 바탕, 체크된 확인 상자.
- **표 머리 청록** (`table-head-teal`): 위키 표의 머리 칸과 정보상자의 왼쪽 항목 칸. 흰 굵은 글자를 올린다.

### Secondary
- **링크 파랑** (`link-blue`): 링크, 문단 번호("2.", "3.1."), 목차 번호, [출처 필요] 각주 표시, 입력 커서. 파랑은 "누를 수 있다"는 뜻이다.
- **위키 / 기사 / SNS 출처색** (`source-wiki`, `source-news`, `source-sns`): 문영위키 스크랩 패널의 색을 그대로 가져왔다. 시간선의 출처 줄과 점 테두리, 출처 꼬리표(위키 / 기사 / SNS)에만 쓴다.

### Tertiary
- **판정 검정 / 빨강 / 노랑** (`verdict-true`, `verdict-false`, `verdict-open`): 학생이 고른 "사실이다 / 사실이 아니다 / 아직 모른다". 판정 단추의 눌린 상태, 판정 기록 점, 사이드바 판정 현황 꼬리표. 빨강은 입력 오류 문구와 "처음 상태로" 경고 상태에도 쓴다. 노랑 위의 글자는 `text-ink`다.
- **지금 검정** (`now-black`): 시간선의 "지금 N턴" 표시와 지금 경계선. 문영위키의 말풍선 검정과 같은 값이다.
- **하이라이트 노랑** (`flash-yellow`): 텍스트 선택 색, 시간선 점을 눌러 이동한 증거 줄이 잠깐 비치는 색, 지금 고른 점의 이름표 바탕.
- **고른 주장 민트** (`selected-mint`): 지금 다루는 주장 제목 줄의 바탕.

### Neutral
- **바닥 회색** (`page-grey`): 페이지 바탕.
- **문서 흰색** (`card-white`): 문서 상자, 사이드바 상자, 입력칸, 단추, 모둠 입력칸, 그리고 색 위의 흰 글자.
- **테두리 회색 / 옅은 테두리** (`border-grey`, `border-soft`): 상자 테두리, 단추 묶음 사이 칸막이, 문단 제목 밑줄, 표 칸은 `border-grey`. 표 안 줄 구분, 사이드바 기둥, 현재 시점 줄 테두리는 `border-soft`.
- **hover 회색** (`hover-grey`): 단추, 접기 단추, 떠 있는 단추의 hover 바탕.
- **본문 먹색** (`text-ink`): 본문 글자.
- **보조 회색** (`muted-grey`): 날짜, 출처 위치, 설명, 저장 시각. 회색 바닥 위에서도 5.27:1이다.

어두운 화면(시스템 설정 또는 `data-theme="dark"`)에서는 같은 이름의 변수를 다시 정의한다. 바닥 #1C1D1F, 상자 #27292D, 출처색과 링크는 밝아지고, 밝아진 색 위의 글자(출처 꼬리표, 턴 선택칸, 판정 단추)는 흰색 대신 #1C1D1F로 바뀐다. 어두운 값은 `.impeccable/design.json`의 `colorMeta.*.dark`에 있다.

### Named Rules
**The Dark Stop Rule (흰 글자 밑은 진한 청록으로).** 상단 바 그라데이션은 왼쪽 0 ~ 35%를 `top-bar-deep`(#08857A)으로 붙잡아 둔 뒤에야 `top-bar-green`으로 넘어간다. 흰 메뉴 글자가 4.52:1을 넘기기 위해서다. 문영위키 원래의 #0E9F92는 흰 글자와 3.28:1이라 본문 크기 글자에 모자란다. 문영위키와 값이 다른 것은 의도된 차이다. 흰 글자를 올리는 모든 그라데이션은 글자가 놓이는 구간을 4.5:1 이상의 진한 쪽으로 붙잡는다.

**The Clip Colour Is the Source Rule (스크랩 색은 출처다).** 청록, 파랑, 자홍은 각각 위키, 기사, SNS만 뜻한다. 출처 꼬리표에는 언제나 글자(위키 / 기사 / SNS)를 함께 쓴다.

**The Blue Means Clickable Rule (파랑은 누를 수 있는 것).** `link-blue`는 링크와 문단 번호처럼 이동할 수 있는 글자에만 쓴다. 강조를 위해 파랑을 칠하지 않는다.

**The Student's Verdict Rule (판정 색은 학생의 것).** 검정, 빨강, 노랑은 학생이 고른 판정만 나타낸다. 정답 여부를 암시하는 색이나 표시는 어디에도 없다.

## Typography

**Body Font:** Noto Sans KR 400 / 500 / 700 / 800 (대체: Apple SD Gothic Neo, Malgun Gothic, sans-serif)

**Character:** 위키 문서의 중립적인 한글 고딕 하나로 제목부터 꼬리표까지 쓴다. 위계는 크기(36 / 27 / 21 / 18 / 15px)와 굵기로 만든다. 줄바꿈은 `word-break: keep-all`로 낱말 단위다.

### Hierarchy
- **Logo** (800, 21px, -0.04em; 768px 이하 19px): 상단 바의 "문영 수사본부".
- **Display** (600, 36px, 1.25, -0.02em; 768px 이하 28px): 문서 제목 "수사:…" 한 줄. Noto Sans KR 600을 함께 불러 그대로 그려진다.
- **Headline** (700, 27px, 1.3, -0.02em; 768px 이하 23px): 1단계 문단 제목("2. 증거 시간선").
- **Title** (700, 21px, 1.3; 768px 이하 18.5px): 2단계 문단 제목, 곧 주장 하나("3.1. …").
- **Box Title** (700, 18px): 사이드바 상자 제목("판정 현황", "최근 기록"). 목차 머리도 18px이지만 400이다. 정보상자 제목은 19px 700.
- **Body** (400, 15px, 1.6): 문서 본문, 사이드바 목록, 안내문. 증거 본문은 14px.
- **Control** (400, 14px): 단추, 입력칸, 분류 줄, 저장 시각. 판정 단추는 14.5px 500, 눌리면 700.
- **Meta** (400, 13.5px): 날짜, 근거 칸의 도움말, 시간선 아래 설명. 출처 위치는 13px, 시간선 날짜 라벨과 턴 표시는 12.5px.
- **Tag** (800, 12.5px): 시간선의 출처 꼬리표. 문서 안 출처 꼬리표는 12px 800, 판정 꼬리표는 12px 700.

### Named Rules
**The One Face Rule (글꼴은 Noto Sans KR 하나).** 로드하는 글꼴은 Google Fonts의 Noto Sans KR(400, 500, 700, 800) 하나뿐이다. 나무위키의 글꼴인 Pretendard는 허용된 글꼴 호스트에서 받을 수 없고, 출처 없이 글꼴 목록에만 적어 두면 기기마다 다르게 그려졌다. 그래서 글꼴 목록에 Pretendard를 넣지 않는다. 문영위키와 글꼴이 다른 것은 의도된 차이다.

**The Tabular Time Rule (날짜와 숫자는 같은 폭으로).** 날짜, 시각, 턴, 개수, 문단 번호는 `font-variant-numeric: tabular-nums`로 써서 값이 바뀌어도 자리가 흔들리지 않게 한다.

## Layout

위에서부터 상단 바(최소 56px, 화면에 붙어 따라옴), 현재 시점 줄, 그리고 본문 틀. 본문 틀은 최대 1520px, 좌우 여백 36px의 두 칸 격자로, 왼쪽은 문서 상자(나머지 폭), 오른쪽은 320px 사이드바, 사이 16px이다. 사이드바는 상단 바 아래(72px)에 붙어 따라온다.

문서 안의 흐름은 위키 문서 그대로다. 제목과 오른쪽 단추 묶음, 저장 시각, 분류 줄, 안내문, 오른쪽으로 띄운 360px 정보상자, 개요 글, 목차 상자, 그리고 1 ~ 5절. 문단 제목은 위 30px, 아래 14px 간격에 밑줄 1px, 2단계 제목은 위 24px. 문서 상자 안쪽 여백 24px, 사이드바 상자 16 / 20px.

증거 시간선은 높이 290px, 최소 폭 780px의 도식이다. 출처 줄 세 개(세로 104 / 168 / 232px)와 날짜 축(260px). 출처 꼬리표는 왼쪽 76px 기둥에 고정되어 가로 스크롤해도 따라오고, 스크롤할 수 있는 쪽 가장자리는 흐려진다. 턴 구간의 폭은 그 구간에 든 증거 수에 비례한다. 같은 날의 증거는 날짜 라벨 하나와 얕은 괄호선을 나눠 쓴다.

반응형: 1100px 이하에서 한 칸으로 쌓이고 사이드바는 문서 아래 두 칸 격자, 좌우 여백 16px. 1000px 이하에서 상단 메뉴는 아이콘만 보인다(이름은 화면 읽기용으로 남김). 768px 이하에서 문서 상자는 테두리 없이 화면 폭을 다 쓰고, 상단 바가 접혀 모둠 입력칸이 한 줄을 차지하며, 정보상자는 띄우지 않고 폭 전체, 판정 단추 묶음은 폭 전체로 나뉜다. 터치 화면(`pointer: coarse`)에서는 단추와 판정 단추의 최소 높이가 44px, 확인 상자의 누르는 영역이 44px이다.

## Elevation & Depth

깊이는 그림자가 아니라 테두리로 나눈다. 회색 바닥 위에 1px `border-grey` 테두리의 흰 상자가 놓이고, 상자 안의 정보상자, 목차, 시간선, 표, 증거 고르기 목록도 각자 1px 테두리 상자다. 위키 문서처럼 테두리 상자가 겹겹이 들어가는 것은 이 세계의 본래 모양이다.

### Shadow Vocabulary
- **떠 있는 단추** (`box-shadow: 0 2px 6px rgba(0, 0, 0, .12)`): 오른쪽 아래의 목차 / 맨 위로 / 맨 아래로 단추 묶음에만 쓴다.
- **고른 점 고리** (`box-shadow: 0 0 0 2px <상자 색>, 0 0 0 4px <본문 색>`): 시간선에서 고른 주장에 연결된 증거 점의 두 겹 고리. 그림자가 아니라 테두리 역할이다.

### Named Rules
**The Border, Not Shadow Rule (상자는 테두리로).** 문서 안의 상자에는 그림자를 쓰지 않는다. 그림자는 화면 위에 떠 있는 단추 묶음에만 있다.

## Shapes

모서리는 작다. 문서 상자, 사이드바 상자, 떠 있는 단추 묶음 5px. 단추, 단추 묶음, 입력칸, 현재 시점 줄, 증거 고르기 목록 4px. 꼬리표, 턴 표시, 모둠 입력칸, 확인 상자 3px. 정보상자와 목차는 모서리가 없다. 둥근 알약은 증거함의 출처 거르기 단추 하나(30px 높이에 15px)뿐이다.

원은 뜻이 있는 곳에만 쓴다. 안내문 앞의 동그란 아이콘, 시간선의 증거 점(16px, 4px 출처색 테두리, 연결되면 출처색으로 꽉 차고 두 겹 고리), 판정 표시(원 안에 체크, 사선, 점 세 개), 판정 기록의 턴별 점.

굵은 점선은 "아직"을 뜻한다. 지금 이후의 출처 줄(4px, 8 / 7 간격, 35% 투명도), 아직 오지 않은 턴 표시의 점선 테두리, 판정 기록에서 아직 오지 않은 턴의 점선 원. 턴 경계의 1px 회색 4 / 4 점선은 눈금일 뿐이고, 지금 경계만 3px 검은 실선이다.

### Named Rules
**The Dashed Means Not Yet Rule (점선은 아직이다).** 출처 줄의 점선, 점선 테두리, 점선 원은 아직 열리지 않은 시간에만 쓴다. 턴이 열리면 그 구간은 실선으로 그려진다.

## Components

### Buttons
위키의 테두리 단추처럼 담백하다.
- **Shape:** 4px 모서리, 높이 36px, 좌우 12px, 1px `border-grey` 테두리, 흰 바탕, 14px 글자. 앞에 1em 선 아이콘을 둔다.
- **Primary:** 바탕은 흰색 그대로, 글자와 테두리를 `teal-ink`로, 글자 700. "증거 연결", "증거 추가"처럼 이 절의 주된 동작 하나에만 쓴다.
- **Button Group:** 문서 제목 오른쪽의 "기록 복사 | 처음 상태로". 바깥만 테두리와 4px 모서리, 안쪽은 1px 칸막이.
- **Hover / Focus:** hover는 `hover-grey` 바탕. 초점은 2px 파란 외곽선(#1B6EC2), 2px 띄움.
- **Warning:** "처음 상태로"는 한 번 누르면 글자가 `verdict-false`로 바뀌고 "모두 지워집니다. 한 번 더 누르세요"가 되며, 4초 안에 다시 눌러야 실행된다.

### Verdict Buttons (판정)
단추 묶음 하나 안의 세 칸(높이 38px, 칸막이 1px). 각 칸은 20px 판정 표시 원과 글자를 함께 쓴다. 눌리면 그 칸이 판정 색으로 꽉 차고 글자가 700이 된다. 다시 누르면 판정이 지워진다. 옆에는 58 x 18px 판정 기록(턴별 점 세 개, 지난 구간 실선, 아직 오지 않은 구간 점선)과 "이전 판정: 1턴 아직 모른다"가 붙는다.

### Chips
- **출처 꼬리표:** 출처색 바탕, 흰 글자 800, 3px 모서리. 시간선 기둥(24px 높이, 최소 50px 폭), 문서 안 목록과 표(12px, 한 줄 높이).
- **판정 꼬리표:** 사이드바 판정 현황 줄 끝. 판정 색 바탕 12px 700, 판정 전은 테두리만.
- **출처 거르기:** 30px 알약, 흰 바탕 보조 회색 글자. 고르면 먹색 바탕에 흰 글자. 뒤에 개수.

### Cards / Containers
- **Corner Style:** 5px.
- **Background:** `card-white` 위 `page-grey` 바닥.
- **Shadow Strategy:** 없음(Elevation & Depth 참고).
- **Border:** 1px `border-grey`.
- **Internal Padding:** 문서 24px, 사이드바 16 / 20px. 사이드바의 "최근 기록" 상자는 위에 5px 회색 띠를 두른다(문영위키의 최근 변경 상자와 같은 모양).

### Inputs / Fields
- **Style:** 흰 바탕, 1px `border-grey`, 4px 모서리, 높이 38px, 여러 줄은 최소 76px. 라벨은 위에 14.5px 700, 옆에 도움말 13.5px 보조 회색.
- **Hover / Focus:** hover는 테두리 #999, 초점은 2px 파란 외곽선.
- **Team Field:** 상단 바의 검색칸 자리에 놓인 250 x 40px 흰 칸, 3px 모서리, 앞에 사람 아이콘. 초점은 안쪽 2px 파란 테두리.
- **Turn Select:** 현재 시점 줄 오른쪽의 36px 선택칸, `teal-ink` 바탕에 흰 굵은 글자.
- **Error:** 폼 아래에 `verdict-false` 글자로 무엇이 틀렸는지 문장으로 알린다.

### Navigation
- **Top Bar:** 왼쪽부터 돋보기 로고와 "문영 수사본부", 문영위키 / 문영일보 메뉴(16px 흰 글자, 20px 선 아이콘, hover는 14% 흰 바탕), 오른쪽 끝에 모둠 입력칸.
- **Current Turn Bar:** 흰 줄에 왼쪽 4px `wiki-teal` 띠. "현재 시점 1턴 2026-02-04 12:00 설명", 오른쪽에 "선생님이 알려 준 턴" 선택칸.
- **Section Heading:** 접기 화살표(24px, 접히면 -90도 회전), 파란 번호, 제목, 오른쪽 끝에 13px 보조 정보. 아래 1px 밑줄.
- **TOC:** 1px 테두리 상자, "목차" 18px와 접기 화살표, 파란 번호 목록, 2단계는 26px 들여쓰기.
- **Floating Buttons:** 오른쪽 아래, 40px 정사각 단추. 목차 하나, 맨 위로 / 맨 아래로 한 묶음. 768px 이하에서는 목차 단추를 숨긴다.

### Infobox (정보상자)
오른쪽에 띄운 360px 상자, 2px `wiki-teal` 테두리. 제목 띠는 `wiki-teal`에서 `top-bar-green`으로 넘어가는 그라데이션에 흰 19px 700 제목과 13.5px 부제. 아래는 왼쪽 92px `table-head-teal` 항목 칸과 오른쪽 값 칸의 표.

### Wiki Table (증거함)
칸마다 1px `border-grey`, 머리 칸은 `table-head-teal` 바탕에 흰 700 글자 가운데 정렬. 출처, 날짜, 증거, 출처 있음, 원문 확인, 연결한 주장. 확인 상자는 18px, 체크되면 `teal-ink`로 꽉 찬다. 시간선 점을 누르면 해당 줄로 이동해 `flash-yellow`로 비쳤다가 1.2초 동안 사라진다.

### Evidence Timeline (증거 시간선)
이 시스템의 대표 부품이다. 출처 줄은 지금까지 5px 실선, 지금 이후는 4px 흐린 점선. 턴 표시는 경계 위 26px 꼬리표로, 지난 턴은 먹색 글자, 지금 턴은 `now-black` 바탕에 흰 굵은 글자, 다음 턴은 점선 테두리다. 주장을 고르면 연결된 점은 출처색으로 꽉 차고 두 겹 고리와 굵은 이름이 되며, 나머지 점의 이름은 보조 회색이 된다. 턴이 바뀌면 지금 표시와 경계선이 700ms 동안 `cubic-bezier(.16, 1, .3, 1)`로 미끄러지고, 새로 지난 구간이 실선으로 한 번 그려진다. 동작 줄이기 설정에서는 즉시 바뀐다.

### Selected Claim (고른 주장)
지금 다루는 주장의 2단계 제목 줄은 `selected-mint` 바탕에 밑줄이 `wiki-teal`로 바뀌고, 그 주장의 증거가 시간선에서 진하게 그려진다.

## Do's and Don'ts

### Do:
- **Do** 돋보기 로고, "문영 수사본부", 제목 앞의 "수사:" 이름공간, 수사 기록임을 밝히는 안내문 한 줄을 모든 데스크 문서에 둔다.
- **Do** 흰 글자를 올리는 그라데이션은 글자가 놓이는 구간을 4.5:1 이상의 진한 쪽(`top-bar-deep`, #08857A)으로 붙잡는다.
- **Do** 출처는 스크랩 색과 꼬리표 글자(위키 / 기사 / SNS)를 함께 써서 나타낸다.
- **Do** 판정은 색과 모양(체크, 사선, 점 세 개)을 함께 써서 색만으로 구분하지 않게 한다.
- **Do** 상자는 1px `border-grey` 테두리로 나누고, 그림자는 떠 있는 단추에만 쓴다.
- **Do** 날짜, 시각, 턴, 개수는 같은 폭 숫자로 쓴다.
- **Do** 아직 오지 않은 시간은 점선으로 그리고, 턴이 열리면 실선으로 잇는다.
- **Do** 터치 화면에서 누를 수 있는 것은 최소 44px를 지킨다.

### Don't:
- **Don't** 나무위키의 이름이나 로고를 쓰지 않는다.
- **Don't** 글꼴 목록에 Pretendard나 출처 없는 글꼴을 넣지 않는다. Noto Sans KR 하나로 쓴다.
- **Don't** 문영위키의 #0E9F92나 #2CB27C 위에 본문 크기의 흰 글자를 올리지 않는다(각각 3.28:1, 2.7:1).
- **Don't** 스크랩 색 세 가지를 출처가 아닌 정보나 장식에 쓰지 않는다.
- **Don't** 파랑을 링크와 문단 번호가 아닌 강조에 쓰지 않는다.
- **Don't** 정답 여부를 색이나 표시로 암시하지 않는다. 판정 색은 학생이 고른 판정만 나타낸다.
- **Don't** 붉은 실, 어두운 코르크 게시판, 용의자 사진처럼 인물을 수사 대상으로 보이게 하는 연출을 쓰지 않는다.
- **Don't** 문서를 카드 대시보드로 쪼개지 않는다. 내용은 번호 붙은 문단과 위키 표로 쓴다.
