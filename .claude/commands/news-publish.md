---
description: 문영일보 기사 사이트를 기존 공유 링크(아티팩트)에 업데이트
---

`news-article/index.html` 의 현재 상태를 기존 공유 링크에 올린다. 새 링크를 만들지 않는다.

1. 원본이 마지막으로 브라우저 테스트를 통과했는지 확인한다. 안 했으면 Playwright로 기사·기자 프로필·전체기사·시작 화면을 열어 콘솔 오류가 없는지 본다.
2. 사본을 만든다: `python3 news-article/tools/build_artifact.py <스크래치패드>/artifact/munyoung-news.html`
3. 이 대화에서 아직 이 링크를 읽거나 올린 적이 없으면 먼저 Artifact `action: "read"`, `url: https://claude.ai/artifact/FB262z41ts6fv9AuVNjSLB` 로 읽는다.
4. Artifact publish: `file_path` = 2번 사본, `url` = 위 링크, `label` = 이번 변경을 몇 단어로. `icon` 은 넣지 않는다.
5. 교사에게 링크와 바뀐 점을 짧게 알린다.

$ARGUMENTS
