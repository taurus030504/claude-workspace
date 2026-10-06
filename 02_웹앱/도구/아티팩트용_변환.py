"""02_웹앱/빌드/인물위키.html → 02_웹앱/빌드/아티팩트/인물위키.html

아티팩트 게시 규칙에 맞춘 사본을 만든다.
- <!DOCTYPE>, <html>, <head>, <body> 껍데기는 게시할 때 자동으로 붙으므로 뺀다.
- 글꼴 스타일시트는 Google Fonts만 허용되므로 Pretendard 대신 Noto Sans KR / Noto Serif KR을 불러온다.
원본(인물위키.html)은 그대로 두고, 고친 뒤에는 이 스크립트를 다시 돌려 사본을 갱신한다.

사용: python3 02_웹앱/도구/아티팩트용_변환.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "빌드" / "인물위키.html"
OUT = ROOT / "빌드" / "아티팩트" / "인물위키.html"

GOOGLE_FONTS = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Noto+Sans+KR:wght@400;500;700;800'
    '&family=Nanum+Brush+Script&family=Nanum+Pen+Script&display=swap" />'
)

src = SRC.read_text(encoding="utf-8")
head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)
body = re.search(r"<body>(.*?)</body>", src, re.S).group(1)

title = re.search(r"<title>.*?</title>", head, re.S).group(0)
styles = "\n".join(re.findall(r"<style>.*?</style>", head, re.S))
# 본문 글꼴 목록에서 Pretendard 다음에 Noto Sans KR가 오도록 (설치된 PC에서는 Pretendard 우선)
styles = styles.replace('"Pretendard","Pretendard JP",', '"Pretendard","Pretendard JP","Noto Sans KR",', 1)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(f"{title}\n{GOOGLE_FONTS}\n{styles}\n{body.strip()}\n", encoding="utf-8")
print(f"작성: {OUT.relative_to(ROOT.parent)} ({OUT.stat().st_size:,} bytes)")
