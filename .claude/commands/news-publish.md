---
description: 문영일보 기사 사이트를 기존 공유 링크(아티팩트)에 업데이트
---

`news-article/index.html` 의 현재 상태를 기존 공유 링크에 올린다. 새 링크를 만들지 않는다.

1. 원본이 마지막으로 브라우저 테스트를 통과했는지 확인한다. 안 했으면 Playwright로 기사·기자 프로필·전체기사·시작 화면을 열어 콘솔 오류가 없는지 본다.
2. **올리기 직전에 매번** Artifact `action: "read"`, `url: https://claude.ai/artifact/FB262z41ts6fv9AuVNjSLB` 로 읽는다. 교사가 수업 중에 턴을 바꾸면 페이지가 새 판으로 올라가므로, 이 대화에서 읽은 적이 있어도 다시 읽어야 지금 반의 턴을 안다. 결과에 나오는 저장 파일 경로를 기억한다.
3. 사본을 만든다: `python3 news-article/tools/build_artifact.py <스크래치패드>/artifact/munyoung-news.html --live <2번 저장 파일>`. 공유 링크의 "현재 턴"과 "턴 시작 시각"을 그대로 옮긴다(출력 끝에 "= 공유 링크 값"). 교사가 턴을 처음으로 되돌려 달라고 할 때만 `--live` 를 뺀다.
4. Artifact publish: `file_path` = 3번 사본, `url` = 위 링크, `label` = 이번 변경을 몇 단어로. `icon` 은 넣지 않는다. `capabilities` 는 넣지 않는다(이미 저장된 `{artifact: {}}` 가 그대로 이어짐. 빼먹고 `{}` 를 넣으면 교사의 턴 바꾸기가 멈춘다).
5. 교사에게 링크와 바뀐 점을 짧게 알린다.

$ARGUMENTS
