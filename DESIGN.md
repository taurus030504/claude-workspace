---
name: 문영 수사본부
description: 증거를 지하철 노선도로 읽는 사실 확인 수업용 수사 책상
colors:
  signage-navy: "#18233A"
  signage-navy-raised: "#24324F"
  on-signage: "#FFFFFF"
  on-signage-soft: "#C3CCDB"
  platform-grey: "#EDF0F4"
  panel-white: "#FFFFFF"
  panel-hover: "#F5F7FA"
  ink: "#18233A"
  muted: "#556074"
  rule: "#D3D9E2"
  rule-strong: "#A9B3C2"
  selected: "#E3E9F3"
  line-wiki: "#009D74"
  line-wiki-pill: "#00805F"
  line-news: "#2156C2"
  line-sns: "#CC3A7A"
  line-sns-pill: "#B8306B"
  now-yellow: "#FFC93C"
  on-now: "#18233A"
  false-red: "#D2352B"
  false-red-text: "#B92D24"
  focus-blue: "#2156C2"
typography:
  headline:
    fontFamily: "Do Hyeon, Gothic A1, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "24px"
    fontWeight: 400
    lineHeight: 1.2
  title:
    fontFamily: "Do Hyeon, Gothic A1, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
    fontSize: "22px"
    fontWeight: 400
    lineHeight: 1.3
    letterSpacing: "-0.005em"
  claim-title:
    fontFamily: "Gothic A1, Apple SD Gothic Neo, Malgun Gothic, Noto Sans KR, system-ui, sans-serif"
    fontSize: "21px"
    fontWeight: 800
    lineHeight: 1.45
  subhead:
    fontFamily: "Gothic A1, Apple SD Gothic Neo, Malgun Gothic, Noto Sans KR, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 800
    lineHeight: 1.4
  body:
    fontFamily: "Gothic A1, Apple SD Gothic Neo, Malgun Gothic, Noto Sans KR, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Gothic A1, Apple SD Gothic Neo, Malgun Gothic, Noto Sans KR, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.3
  line-number:
    fontFamily: "Gothic A1, Apple SD Gothic Neo, Malgun Gothic, Noto Sans KR, system-ui, sans-serif"
    fontSize: "13.5px"
    fontWeight: 800
    lineHeight: 1
rounded:
  hairline: "3px"
  tag: "4px"
  control: "6px"
  row: "8px"
  panel: "10px"
  pill: "14px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "22px"
components:
  button:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 14px"
    height: "40px"
  button-small:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 11px"
    height: "34px"
  button-primary:
    backgroundColor: "{colors.signage-navy}"
    textColor: "{colors.on-signage}"
    rounded: "{rounded.control}"
    padding: "0 14px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.signage-navy-raised}"
    textColor: "{colors.on-signage}"
  input:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "40px"
  input-signage:
    backgroundColor: "{colors.signage-navy-raised}"
    textColor: "{colors.on-signage}"
    rounded: "{rounded.control}"
    padding: "0 10px"
    height: "36px"
  now-select:
    backgroundColor: "{colors.now-yellow}"
    textColor: "{colors.on-now}"
    rounded: "{rounded.control}"
    padding: "0 6px 0 10px"
    height: "36px"
  line-pill-wiki:
    backgroundColor: "{colors.line-wiki-pill}"
    textColor: "{colors.on-signage}"
    typography: "{typography.line-number}"
    rounded: "{rounded.pill}"
    padding: "0 10px"
    height: "28px"
  line-pill-news:
    backgroundColor: "{colors.line-news}"
    textColor: "{colors.on-signage}"
    typography: "{typography.line-number}"
    rounded: "{rounded.pill}"
    padding: "0 10px"
    height: "28px"
  line-pill-sns:
    backgroundColor: "{colors.line-sns-pill}"
    textColor: "{colors.on-signage}"
    typography: "{typography.line-number}"
    rounded: "{rounded.pill}"
    padding: "0 10px"
    height: "28px"
  turn-marker-now:
    backgroundColor: "{colors.now-yellow}"
    textColor: "{colors.on-now}"
    rounded: "{rounded.pill}"
    padding: "0 11px"
    height: "28px"
  verdict-button:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.row}"
    padding: "6px 12px"
    height: "48px"
  verdict-true-pressed:
    backgroundColor: "{colors.signage-navy}"
    textColor: "{colors.on-signage}"
  verdict-false-pressed:
    backgroundColor: "{colors.false-red}"
    textColor: "{colors.on-signage}"
  verdict-open-pressed:
    backgroundColor: "{colors.now-yellow}"
    textColor: "{colors.on-now}"
  tab:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
    padding: "0 12px"
    height: "34px"
  tab-active:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.panel-white}"
  panel:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
  top-bar:
    backgroundColor: "{colors.signage-navy}"
    textColor: "{colors.on-signage}"
    height: "60px"
---

# Design System: 문영 수사본부

## Overview

**Creative North Star: "서울 지하철 노선도 (The Evidence Metro)"**

이 시스템은 서울 지하철 안내 사인을 빌려 온다. 시간은 왼쪽에서 오른쪽으로 흐르고, 출처 하나가 노선 하나이며, 증거 하나가 역 하나다. 지금 턴은 열차가 서 있는 자리다. 학생은 "누가 범인인가"를 쫓는 탐정이 아니라 "언제, 어디서 나온 말인가"를 확인하는 승객이자 안내원이다. 그래서 화면은 수사 게시판처럼 어둡고 극적이지 않고, 역 안내판처럼 밝고 정돈되어 있으며 한눈에 읽힌다.

밀도는 중간이다. 상단에는 남색 안내판 바가 있고, 그 아래로 승강장 회색 바닥 위에 흰 판이 놓인다. 판 안의 내용은 카드로 다시 쪼개지 않고 가는 선(rule)으로 나눈 줄로 정리한다. 색은 대부분 무채색에 가깝게 두고, 노선 세 가지 색과 "지금" 노랑, "사실이 아니다" 빨강만 의미를 가진 색으로 쓴다. 장식 색은 없다.

움직임은 하나뿐이다. 교사가 턴을 넘기면 열차 표시(지금 마커)가 다음 경계로 미끄러지고, 지나온 구간이 실선으로 이어진다. 그 밖의 전환은 짧은 상태 변화에 그친다. 확인된 거부는 하나다. 붉은 실과 어두운 탐정 게시판처럼 인물을 용의자로 보이게 하는 연출은 쓰지 않는다.

**Key Characteristics:**
- 남색 안내판 바, 승강장 회색 바닥, 흰 작업 판의 세 층
- 출처 = 노선 색(위키 초록, 기사 파랑, SNS 자홍), 노선 번호처럼 생긴 알약 표시
- 증거 = 흰 점에 색 테두리를 두른 역, 고른 주장에 연결되면 환승역 고리
- 지금 = 노랑, 아직 = 점선
- 제목은 Do Hyeon, 나머지는 모두 Gothic A1
- 판 안은 카드 대신 줄과 선으로 나눈다

## Colors

거의 무채색인 안내판 남색과 회색 위에, 의미가 정해진 몇 가지 신호색만 올리는 팔레트다.

### Primary
- **안내판 남색 (Signage Navy)** (`signage-navy`): 상단 바 배경, 본문 글자, 주요 버튼, "사실이다" 판정의 눌린 상태. 화면의 뼈대이자 "확정"의 색이다. 같은 값이 `ink`로 본문 글자에 쓰인다.
- **안내판 남색, 한 단 밝게** (`signage-navy-raised`): 상단 바 안의 입력칸과 주요 버튼의 hover.

### Secondary
- **위키 노선 초록** (`line-wiki`, 알약은 `line-wiki-pill`): 문영위키에서 나온 증거의 노선, 역 테두리, 출처 알약.
- **기사 노선 파랑** (`line-news`): 문영일보 기사 노선과 알약. 같은 파랑이 `focus-blue`로 키보드 초점 테두리와 입력 커서에 쓰인다.
- **SNS 노선 자홍** (`line-sns`, 알약은 `line-sns-pill`): SNS 노선과 알약.

노선 선과 역 테두리는 밝은 노선 색을, 흰 글자가 올라가는 알약은 한 단 어두운 `-pill` 색을 쓴다. 글자 대비를 지키기 위한 구분이다.

### Tertiary
- **지금 노랑 (Now Yellow)** (`now-yellow`, 글자는 `on-now`): 지금 턴 마커, 지금 경계선, 상단의 "지금 시점" 선택칸, 노선도에서 고른 역의 이름표, 증거로 이동했을 때 잠깐 비치는 강조, 텍스트 선택 색, 그리고 "아직 모른다" 판정. 노랑 위의 글자는 언제나 남색이다.
- **판정 빨강 (False Red)** (`false-red`, 글자용 `false-red-text`): "사실이 아니다" 판정, 입력 오류 문구, [출처 필요] 표시, 되돌릴 수 없는 동작 직전의 경고 버튼.

### Neutral
- **승강장 회색 (Platform Grey)** (`platform-grey`): 페이지 바닥.
- **흰 판 (Panel White)** (`panel-white`): 노선도와 작업 영역의 판, 입력칸, 기본 버튼, 역 점 안쪽.
- **판 hover** (`panel-hover`): 목록 줄과 펼침 영역의 hover 바탕.
- **고른 줄** (`selected`): 지금 고른 주장의 줄 바탕.
- **보조 글자** (`muted`): 설명, 날짜, 메타 정보, 흐려진 역 이름. 흰 판과 회색 바닥 모두에서 본문 대비를 지킨다.
- **안내판 위 보조 글자** (`on-signage-soft`): 상단 바의 브랜드명, 라벨, 수업용 표시 테두리.
- **가는 선 / 굵은 선** (`rule`, `rule-strong`): 줄 사이 구분선과 입력칸·버튼 테두리, 지나지 않은 턴 마커 테두리.

어두운 화면(시스템 설정 또는 `data-theme="dark"`)에서는 같은 역할의 토큰을 다시 정의한다. 노선 색은 밝아지고 판은 남회색이 되지만, 지금 노랑은 그대로다. 어두운 값은 `.impeccable/design.json`의 `colorMeta.*.dark`에 있다.

### Named Rules
**The One Yellow Rule (노랑은 "지금"뿐이다).** 노랑은 현재 시점과 "아직 모른다"에만 쓴다. 둘 다 "아직 열려 있는 상태"라는 같은 뜻이다. 강조나 장식으로 노랑을 쓰면 학생이 지금 위치를 잃는다. 예외는 브랜드 표시의 노란 역 고리 하나다.

**The Line Is the Source Rule (노선 색은 출처다).** 초록, 파랑, 자홍은 각각 위키, 기사, SNS만 뜻한다. 다른 정보에 이 세 색을 빌려 쓰지 않는다. 출처 알약에는 반드시 글자(위키 / 기사 / SNS)를 함께 쓴다.

**The Red Means False Rule (빨강은 "사실이 아니다"다).** 빨강은 판정과 오류에만 쓴다. 인물, 사건 제목, 위험 분위기를 꾸미는 데 쓰지 않는다.

## Typography

**Display Font:** Do Hyeon (대체: Gothic A1, Apple SD Gothic Neo, Malgun Gothic)
**Body Font:** Gothic A1 400 / 600 / 800 (대체: Apple SD Gothic Neo, Malgun Gothic, Noto Sans KR)

**Character:** Do Hyeon은 역 이름판처럼 굵고 납작한 한 가지 굵기의 제목 글꼴이고, Gothic A1은 안내문처럼 중립적인 본문 글꼴이다. 위계는 크기보다 굵기(400, 600, 800)로 만든다.

### Hierarchy
- **Headline** (Do Hyeon 400, 24px, 1.2; 좁은 화면 21px): 상단 바의 사건 제목 한 줄.
- **Title** (Do Hyeon 400, 22px, 1.3): 판 제목. "증거 노선도", "판단할 주장".
- **Claim Title** (Gothic A1 800, 21px, 1.45): 고른 주장의 문장. 학생이 쓴 문장이므로 제목 글꼴이 아니라 본문 글꼴의 가장 굵은 단계로 쓴다.
- **Subhead** (Gothic A1 800, 15px, 1.4): 블록 제목("2턴 판정", "내 근거", "증거함"). 옆에 붙는 설명은 400, `muted`, 13.5px.
- **Body** (Gothic A1 400, 15px, 1.6): 기본 글자. 증거 본문은 14.5px, 한 줄 최대 72ch.
- **Label** (Gothic A1 600, 13px, 1.3): 역 이름, 메타 정보, 폼 라벨. 날짜 라벨은 12.5px.
- **Line Number** (Gothic A1 800, 13.5px): 노선 알약과 턴 마커 안의 글자.

### Named Rules
**The Signage Voice Rule (제목 글꼴은 안내판에만).** Do Hyeon은 상단 바 제목과 판 제목에만 쓴다. 본문, 라벨, 버튼, 숫자, 학생이 쓴 문장에는 쓰지 않는다.

**The Tabular Time Rule (날짜와 숫자는 같은 폭으로).** 날짜, 턴, 개수는 `font-variant-numeric: tabular-nums`로 써서 줄이 바뀌어도 자리가 흔들리지 않게 한다.

## Layout

화면은 위에서 아래로 세 층이다. 남색 상단 바(최소 높이 60px), 화면 폭 전체를 쓰는 노선도 판, 그 아래 작업 영역. 내용 폭은 최대 1440px, 좌우 여백 16px이다.

노선도는 높이 268px의 고정 도식이다. 노선 세 개를 가로로 놓고(세로 위치 84 / 146 / 208px), 날짜 축은 그 아래에 둔다. 노선 알약은 왼쪽 84px 기둥에 고정되어 가로 스크롤해도 따라온다. 노선도의 최소 폭은 980px이고, 그보다 좁으면 가로 스크롤하며 지금 위치나 연결된 첫 역에서 시작한다. 턴 구간의 폭은 그 구간에 든 역의 수에 비례한다. 같은 날의 역들은 날짜 라벨 하나를 나눠 쓰고, 아래에 얕은 괄호선으로 묶는다.

작업 영역은 두 칸 격자다. 왼쪽 주장 목록(300 ~ 380px)과 오른쪽 고른 주장(나머지 폭), 사이 간격 16px. 1001px 이상에서는 주장 목록이 화면에 붙어 따라오고, 1000px 이하에서는 한 칸으로 쌓인다. 640px 이하에서는 판정 버튼이 세로로 쌓이고 증거 줄의 노선 알약이 본문 위로 올라간다.

간격은 4 / 8 / 12 / 16 / 22px 단계를 쓴다. 판과 판 사이 16px, 판 안 블록 사이 22px, 줄 안 요소 사이 8 ~ 12px. 터치 화면(`pointer: coarse`)에서는 작은 버튼, 탭, 체크 항목의 최소 높이를 44px로 올린다.

## Elevation & Depth

깊이는 두 평면뿐이다. 승강장 회색 바닥과 그 위에 놓인 흰 판. 판에는 하나의 부드러운 그림자만 쓰고, 판 안에서는 그림자를 다시 쓰지 않는다. 판 안의 구분은 가는 선과 바탕색 변화(hover, 고른 줄)로 한다.

### Shadow Vocabulary
- **판 그림자** (`box-shadow: 0 1px 2px rgba(24, 35, 58, .08), 0 4px 14px rgba(24, 35, 58, .06)`): 노선도 판, 작업 판, 알림 토스트. 어두운 화면에서는 검정 기반 값으로 바뀐다.
- **환승 고리** (`box-shadow: 0 0 0 3px <노선 색>`): 연결된 역 점의 바깥 고리. 그림자가 아니라 테두리 역할이다.

### Named Rules
**The Two Planes Rule (바닥과 판, 두 층뿐이다).** 판 안에 카드를 다시 넣지 않는다. 증거, 주장처럼 반복되는 항목은 선으로 나눈 줄로 쓴다.

## Shapes

모서리는 작고 일정하다. 판 10px, 판정 버튼·목록 줄·빈 상태 상자 8px, 버튼과 입력칸 6px, 작은 표시와 체크 상자 4px. 노선 알약, 턴 마커, 출처 탭은 높이의 절반을 반지름으로 써서 완전한 알약 모양이다(28px 높이에 14px).

원은 역과 판정 표시에만 쓴다. 역은 18px 흰 점에 4px 노선 색 테두리, 연결되면 5px 남색 테두리에 3px 노선 색 고리를 더한 환승역이 된다. 판정 표시는 원 안에 모양을 넣는다. 사실이다는 체크, 사실이 아니다는 사선, 아직 모른다는 점 세 개, 판정 전은 점선 원이다.

점선은 "아직"을 뜻한다. 지금 이후의 노선(굵기 5px, 10 / 8 간격, 흐리게), 아직 오지 않은 턴 마커의 테두리, 판정 기록 속 다음 턴 자리, 비어 있는 목록 상자가 모두 점선이다. 지나간 턴 경계는 가는 점선, 지금 경계는 4px 노란 실선이다.

### Named Rules
**The Dashed Means Not Yet Rule (점선은 아직이다).** 점선은 아직 열리지 않은 시간과 아직 채워지지 않은 자리에만 쓴다. 장식용 점선 테두리는 없다.

## Components

### Buttons
안내판처럼 담백하고 단단하다.
- **Shape:** 살짝 둥근 모서리(6px), 높이 40px, 작은 버튼 34px.
- **Primary:** 남색 바탕에 흰 글자. 폼을 제출하는 한 자리("증거 추가")에만 쓴다.
- **Default:** 흰 바탕, `rule-strong` 테두리, 남색 글자 600.
- **Hover / Focus:** hover는 테두리가 남색으로 진해지고, 누르면 1px 내려간다. 초점은 3px 파란 외곽선, 2px 띄움. 상단 바 안에서는 초점 외곽선이 노랑이다.
- **Warning:** 되돌릴 수 없는 동작은 한 번 누르면 빨간 테두리와 확인 문구로 바뀌고, 4초 안에 다시 눌러야 실행된다.

### Verdict Buttons (판정)
세 칸이 나란히 놓인 큰 선택 버튼(최소 높이 48px, 8px 모서리, 1.5px 테두리). 각 버튼은 판정 표시 원과 글자를 함께 쓴다. 눌리면 사실이다는 남색, 사실이 아니다는 빨강, 아직 모른다는 노랑으로 꽉 찬다. 어두운 테마에서 빨강이 밝아지면(#FF6B5E) 그 위 글자는 흰색 대신 어두운 남색(`--on-false`)으로 바꿔 대비를 지킨다. 다시 누르면 판정이 지워진다.

### Chips
- **노선 알약:** 노선 색 바탕(`-pill` 단계)에 흰 글자 800, 28px 높이. 노선도 왼쪽 기둥과 증거 줄의 머리에 쓴다.
- **출처 탭:** 34px 알약, 앞에 10px 노선 색 점, 뒤에 개수. 고르면 남색 바탕에 흰 글자.
- **수업용 표시:** 사건 제목 옆의 얇은 테두리 표시(4px 모서리). 가상 사건임을 밝히는 필수 표시다.

### Cards / Containers
- **Corner Style:** 10px.
- **Background:** 흰 판.
- **Shadow Strategy:** 판 그림자 하나(Elevation & Depth 참고).
- **Border:** 없음.
- **Internal Padding:** 판 머리 16 / 18px, 고른 주장 영역 18 / 22px.

### Inputs / Fields
- **Style:** 흰 바탕, `rule-strong` 1px 테두리, 6px 모서리, 높이 40px. 여러 줄 입력은 최소 92px.
- **Hover / Focus:** hover는 테두리가 `muted`로, 초점은 3px 파란 외곽선.
- **On signage:** 상단 바 안의 입력칸은 한 단 밝은 남색 바탕, 테두리 없음, 높이 36px. "지금 시점" 선택칸만 노랑 바탕에 남색 굵은 글자다.
- **Error:** 폼 아래에 빨간 글자로 무엇이 빠졌는지 문장으로 알린다.

### Navigation
상단 바 하나가 내비게이션 전부다. 왼쪽부터 브랜드(노란 역 고리 표시와 이름), 사건 제목과 수업용 표시, 모둠 이름, 지금 시점, 문영위키 바로가기(테두리 버튼). 좁은 화면에서는 제목이 한 줄을 다 차지하고 도구가 그 아래로 내려간다.

### Evidence Metro Map (노선도)
이 시스템의 대표 부품이다. 노선은 지금까지 7px 실선, 지금 이후는 5px 흐린 점선이다. 턴 마커는 경계 위의 알약이다. 지나간 턴은 남색 테두리, 지금 턴은 노랑, 다음 턴은 점선 테두리다. 역 이름표는 흰 바탕을 깔아 선 위에서도 읽힌다. 주장을 고르면 연결된 역은 환승역 고리와 굵은 이름이 되고, 나머지 역은 이름이 `muted`로, 점 테두리가 바탕 쪽으로 옅어진다. 역을 누르면 아래 증거 줄로 이동해 잠깐 노랗게 비친다. 턴이 바뀌면 지금 마커와 경계선이 700ms 동안 `cubic-bezier(.16, 1, .3, 1)`로 미끄러지고, 새로 지난 구간이 실선으로 그려진다. 동작 줄이기 설정에서는 즉시 바뀐다.

### Verdict Trail (판정 기록 노선)
주장 목록의 각 줄 앞에 58 x 18px 작은 노선을 둔다. 턴마다 판정 표시 색의 원 하나, 판정 전은 빈 원, 아직 오지 않은 턴은 점선 원이다. 판정이 바뀐 흔적이 목록에서 바로 보인다.

### Evidence Row (증거 줄)
증거는 카드가 아니라 선으로 나눈 줄이다. 왼쪽 60px 칸에 노선 알약, 오른쪽에 짧은 이름(800), 날짜, 찾은 턴, 본문, 출처 위치, 그리고 "출처 있음 / 원문 확인함" 체크와 연결 버튼이 온다.

## Do's and Don'ts

### Do:
- **Do** 출처를 나타낼 때 노선 색과 노선 알약 글자를 함께 쓴다(위키 초록, 기사 파랑, SNS 자홍).
- **Do** "지금"과 "아직 모른다"에만 노랑(`now-yellow`)을 쓰고, 노랑 위 글자는 언제나 남색(`on-now`)으로 쓴다.
- **Do** 아직 오지 않은 시간과 비어 있는 자리를 점선으로 그린다.
- **Do** 판정은 색과 모양(체크, 사선, 점 세 개)을 함께 써서 색만으로 구분하지 않게 한다.
- **Do** 흐리게 보여야 하는 글자는 `muted` 색으로 낮추고, 투명도로 낮추지 않는다.
- **Do** 같은 날짜의 역은 날짜 라벨 하나를 나눠 쓰고 괄호선으로 묶는다.
- **Do** 판 안의 반복 항목은 `rule` 선으로 나눈 줄로 쓴다.
- **Do** 터치 화면에서 누를 수 있는 것은 최소 44px 높이를 지킨다.

### Don't:
- **Don't** 붉은 실, 어두운 코르크 게시판, 용의자 사진처럼 인물을 수사 대상으로 보이게 하는 연출을 쓰지 않는다.
- **Don't** 흰 판 안에 그림자 있는 카드를 다시 넣지 않는다.
- **Don't** Do Hyeon을 본문, 라벨, 버튼, 숫자에 쓰지 않는다.
- **Don't** 노선 색 세 가지를 출처가 아닌 정보나 장식에 쓰지 않는다.
- **Don't** 빨강을 "사실이 아니다"와 오류가 아닌 곳에 쓰지 않는다.
- **Don't** 정답 여부를 색이나 표시로 암시하지 않는다. 판정 색은 학생이 고른 판정만 나타낸다.
