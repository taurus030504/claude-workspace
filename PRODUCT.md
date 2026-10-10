# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static HTML/CSS/JS in a single file, no build step. Published as a claude.ai Artifact link for students and committed to this repository. It must open on school Chromebooks and PCs without installing anything.

## Users

Vocational high school (특성화고) students in a digital literacy / fact-checking class. Each student works on their own Chromebook or PC, investigates on their own screen, and then agrees on verdicts with their group (모둠). The teacher runs the class and moves every group to the next turn at the same time.

## Product Purpose

문영 수사본부 (Munyeong Investigation Headquarters) is the students' investigation desk for a fact-checking game. Students read a fictional wiki (문영위키), news site (문영일보), and SNS about a fictional celebrity dating rumor. They pull out claims, attach dated evidence, and judge each claim as 사실이다 / 사실이 아니다 / 아직 모른다, writing down why.

Success means students make the judgment themselves and can give the evidence and reasoning behind it: they check where a claim came from, put events in the right time order, and say "아직 모른다" when the evidence is not enough. Getting the official "correct answer" is not the goal.

## Positioning

The case changes over time. Information is released turn by turn, so a judgment that was reasonable in turn 1 can be overturned in turn 3, and wiki paragraphs appear, get vandalized, and get reverted on a clock. The desk exists to make students reason about **when** something was known and **where** it came from, not just whether it is true.

## Operating Context

- **Sources (all fictional, separate artifacts):**
  - 문영위키 (https://claude.ai/artifact/JM9iRLeWXGpZZE3h4RTWDV): wiki documents with edit history, footnotes, [출처 필요] tags, and paragraphs that appear and disappear by time. It has its own scrap/memo panel (clip types 위키, 기사, SNS, 각주, 발췌) stored in the browser.
  - 문영일보 (https://claude.ai/artifact/FB262z41ts6fv9AuVNjSLB): the news site linked from wiki footnotes.
  - Fictional SNS: planned. The wiki's SNS base URL is still empty.
- **Case 2026-02, 이은호 김서진 열애설.** Three turns:
  - 1턴 2026-02-04 12:00: the day the rumor article appeared
  - 2턴 2026-03-06 12:00: a month later, spread to birthday photos, agency still silent
  - 3턴 2026-03-08 20:00: after the agency's denial notice and articles
- **Turn control:** the teacher advances turns for the whole class (teacher-only control in the wiki). Every group is always at the same point in time.
- **Class rhythm:** students work alone on their own device, then talk it through and settle verdicts as a group.

## Capabilities and Constraints

- Current desk prototype (https://claude.ai/artifact/NcmSp1afrSnTqXDe3Fj1Gz) has: case cover with group name, an evidence timeline by date with a "now" marker, a claim list with three verdicts and handwritten-style notes, an evidence box filtered by source (wiki/news/SNS), "출처 있음 / 원문 확인" checks, linking evidence to claims (button or drag), and adding new claims. State is saved only in that browser (localStorage).
- No backend. Work is not shared between students, groups, or the teacher's screen. **Undecided:** how a group combines individual work, and how the teacher collects results.
- The desk shows only the student's own verdicts. It never shows a correct answer.
- All people, agencies, albums, and media in the case are fictional, and must stay clearly labeled as classroom material.
- Terminology to keep: 사건 파일, 모둠, 턴, 주장, 증거, 판정 (사실이다 / 사실이 아니다 / 아직 모른다), 출처, 원문.
- **Undecided:** whether the desk reads the current turn from the wiki automatically or students set it themselves.

## Brand Commitments

- Name: 문영 수사본부. Sources: 문영위키, 문영일보.
- The teacher judges the current prototype's look as reading as AI-generated. Its content, terminology, and functions carry over; its visual treatment does not bind future work.
- Binding visual direction (set by the teacher 2026-10-10): follow Namuwiki's visual style (layout, typography, palette, navigation, document structure), as 문영위키 already does, so students work in one visual language across source and desk. Never use Namuwiki's own name or logo. Desk pages keep their own logo and the "수사:" namespace so students can tell the notebook from the wiki it cites.
- Students are fact-checkers, not detectives hunting a person. The interface must not frame the celebrities as suspects (inherited from the prototype's "do not use" list: no red string and dark detective board).

## Evidence on Hand

- The three artifacts above, with real case text, dates, and edit histories.
- Sample claims and evidence already written for turn 1 in the desk prototype.
- No real student work, outcomes, or testimonials exist. Do not invent any.

## Product Principles

1. The student decides. The interface organizes evidence and reasoning and never hands out the answer.
2. Time is evidence. Every piece of evidence carries a date and the turn it was found in, and the current turn is always visible.
3. Source is visible at a glance. Where a piece of evidence came from must be obvious before reading its text.
4. "아직 모른다" is a valid, respected verdict, not a failure state.
5. Reasoning is recorded. Writing down why counts as much as choosing a verdict.

## Accessibility & Inclusion

Mixed reading levels in a vocational high school class: plain Korean, short labels, no jargon. Usable by keyboard and touch (some Chromebooks have touchscreens). Must stay readable when projected and on small laptop screens (1366×768 is common).
