"""news-article/index.html → 아티팩트(공유 링크)용 사본 만들기.

아티팩트는 게시할 때 <!doctype>/<html>/<head>/<body> 뼈대를 스스로 씌우므로
원본에서 그 태그와 charset/viewport meta만 빼서 사본을 만든다. 원본은 건드리지 않는다.

사용: python3 news-article/tools/build_artifact.py <출력 경로>
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / 'index.html'
STRIP = [
    '<!doctype html>\n', '<html lang="ko">\n', '<head>\n', '</head>\n',
    '<body>\n', '</body>\n', '</html>\n',
    '<meta charset="utf-8">\n',
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
]


def main():
    if len(sys.argv) != 2:
        sys.exit('사용: python3 news-article/tools/build_artifact.py <출력 경로>')
    s = SRC.read_text(encoding='utf-8')
    for tag in STRIP:
        if tag not in s:
            sys.exit('원본에서 찾지 못한 태그: ' + tag.strip())
        s = s.replace(tag, '', 1)
    if 'window.print' in s or 'confirm(' in s:
        sys.exit('아티팩트에서 동작하지 않는 window.print/confirm 이 들어 있습니다.')
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding='utf-8')
    print('만듦:', out, f'({len(s):,}자)')


if __name__ == '__main__':
    main()
