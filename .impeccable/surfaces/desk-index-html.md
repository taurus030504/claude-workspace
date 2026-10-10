---
version: 1
slug: "desk-index-html"
primary_target: "desk/index.html"
related_targets: []
---

## Scope

Operate mode: the student investigation desk (수사 데스크), the main screen of 문영 수사본부. One student on their own Chromebook or PC, school computer room under fluorescent light, 1366x768 is common; light theme first. Task: link dated evidence to each claim, judge it (사실이다 / 사실이 아니다 / 아직 모른다), write the reason, and judge again when the teacher opens the next turn.

History: the 교정지와 형광펜 prototype, then a metro-map direction (2026-10-10). The user then pinned a new direction: match Namuwiki's visual style in layout, typography, palette, navigation, and document structure. The metro-map look is replaced. Its mechanisms are kept: the dated evidence timeline with the "now" marker and dashed future, and the per-turn verdict record.

## Direction contract

THESIS: The desk is a wiki document. The investigation is written up the way 문영위키 (a Namuwiki-style wiki) writes up a person, so students move between source and notebook in one visual language. Refuses the dashboard-of-cards layout. The "수사:" namespace, the notice line, and the logo keep the desk distinct from the wiki it cites.
OWN-WORLD: The Namuwiki / 문영위키 skin, with tokens taken from the 문영위키 artifact. Teal-to-green gradient top bar (#0E9F92 to #2CB27C), #F5F5F5 ground, white document card with a #CCC border and 5px corners, #212529 text, #0275D8 links, Pretendard / Noto Sans KR. A 36px title with a bordered action button group, a 분류 bar, round-icon notices, a gradient-headed infobox, a 목차 box, numbered blue section headings with fold toggles, wiki tables with teal headers, and a right sidebar (판정 현황 like 실시간 검색어, 최근 기록 like 최근 변경). Floating 목차/up/down buttons. Source colours are the wiki's clip colours (위키 #0A7A70, 기사 #2F6FB5, SNS #C2477F).
STORY: The student reads the case like a wiki article. The timeline section shows where evidence sits in time. Each claim is its own numbered subsection, holding its verdict, reason, and linked evidence. The 증거함 table lists every piece of evidence with its source checks.
FIRST VIEWPORT: Gradient top bar (logo 문영 수사본부, nav 문영위키 / 문영일보, 모둠 field in the search-box slot). The 현재 시점 turn bar with the turn select. Then the document card (title "수사:이은호 김서진 열애설", action buttons, last-saved line, 분류 bar, notice, infobox floated right, 목차) and the sidebar on the right.
FORM: User-pinned direction ("Namuwiki's visual style"). No concept roll. Seed key: none (pinned).
SELECTED STATE: The claim being worked on gets a tinted heading row (--sel, with a teal rule), and its evidence is drawn dark on the timeline.
SIGNATURE: Section 2's evidence timeline. Changing the turn moves the "지금" marker, and the passed dashed section draws solid once.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Open decisions

- How a group merges individual work, and how the teacher collects results (for now, a "기록 복사" text export).
- Whether the desk reads the turn from 문영위키. For now the student sets it when the teacher announces.
