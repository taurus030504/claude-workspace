# 문영일보 로고 (v3, 2026-10-09)

- `문영일보_로고_v3_원본.webp`: 교사가 준 원본(2000×669, 투명 바탕).
- `문영일보_로고_v3.webp`: 글자 둘레를 딱 맞게 자르고 960×210으로 줄인 게시용(37KB). 문영일보 페이지의 CSS 변수 `--logo`에 data URI로 들어 있다.

함께 바꾼 값 (문영일보 페이지 CSS)
- `.logo-img { aspect-ratio: 960 / 210; }` (예전 2000 / 574)
- 머리글 로고 너비 200px → 240px, 휴대폰 140px → 170px (새 로고가 더 가로로 길어서 높이를 맞춤)

게시본(https://claude.ai/artifact/FB262z41ts6fv9AuVNjSLB, 버전 38)에는 반영했다.
문영일보 원본 파일은 다른 브랜치(`claude/zen-gauss-smepeo`의 `news-article/index.html`)에 있어서 그쪽은 아직 예전 로고다.
그 브랜치에서 다시 게시하기 전에 위 세 값과 로고 그림을 옮겨야 한다. (`python3 tools/embed_image.py` 같은 도구가 아니라 `--logo` 변수를 직접 바꾸면 된다.)
