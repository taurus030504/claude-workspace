---
version: 1
slug: "desk-index-html"
primary_target: "desk/index.html"
related_targets: []
---

## Scope

Operate mode: the student investigation desk (수사 데스크), the main screen of 문영 수사본부. One student on their own Chromebook or PC, school computer room under fluorescent light, 1366x768 is common; light theme first. Replaces the 교정지와 형광펜 prototype (https://claude.ai/artifact/NcmSp1afrSnTqXDe3Fj1Gz): keep its content, terminology, and functions, and drop its look.

Task: pick a claim, link dated evidence, judge it (사실이다 / 사실이 아니다 / 아직 모른다), write the reason, and judge again when the teacher opens the next turn.

## Direction contract

THESIS: Evidence is a metro map. Time runs left to right, each source is a line, each piece of evidence is a station, and the current turn is where the train is. Refuses both the detective cork board and the generic card dashboard.
OWN-WORLD: Seoul metro signage. Signage navy bar, platform-grey ground, white work panels. Source lines in wiki green, news blue, and SNS magenta. "Now" yellow is shared with 아직 모른다, and false is red. Do Hyeon for headings only, Gothic A1 for everything else. Line-number pills mark sources. Stations are white dots with coloured rings, and linked evidence becomes a transfer-station ring. Lines past the current turn are dashed, like a section still under construction.
STORY: The student sees where the case stands in time, picks a claim, sees which stations hold its evidence, judges it, and records why. Each turn adds a judgment, so revisions stay visible.
FIRST VIEWPORT: Navy top bar with the brand, case title, group name, current-turn select, and wiki link. A full-width schematic map below it (3 lines, stations in date order, turn boundaries, yellow "지금" marker, dashed future). Below that, the claim list on the left (verdict trail per claim) and the selected claim on the right: verdict control, reason, linked evidence, evidence box.
FORM: Candidate 1 of 7 (지하철 노선도). Seed key: none (waiver). concept-seed could not run in this session because the engine binary was blocked, so the direction round ran through the structured question tool instead: A 지하철 노선도, B OMR 답안지, C 택배 배송조회, D standard dashboard (canon). The user picked A, and that pick stands in for the roll.
SIGNATURE: Changing the turn moves the train, and the dashed segment it passes draws solid once. Each claim row carries a three-stop mini line of its verdict per turn.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Open decisions

- How a group merges individual work, and how the teacher collects results (for now, a "copy my record" text export).
- Whether the desk reads the turn from 문영위키. For now the student sets it when the teacher announces.
