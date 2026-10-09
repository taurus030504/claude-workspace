"""news-article/index.html → 아티팩트(공유 링크)용 사본 만들기.

아티팩트는 게시할 때 <!doctype>/<html>/<head>/<body> 뼈대를 스스로 씌우므로
원본에서 그 태그와 charset/viewport meta만 빼서 사본을 만든다. 원본은 건드리지 않는다.

사용: python3 news-article/tools/build_artifact.py <출력 경로> [--live <공유 링크에서 읽어 저장된 html>]

--live 를 주면 지금 공유 링크의 "현재 턴"과 "턴 시작 시각"을 사본에 그대로 옮긴다.
교사가 수업 중에 턴을 바꿔 둔 상태에서 다시 올려도 반이 1턴으로 되돌아가지 않게 하려는 것.
"""
import re
import sys
from pathlib import Path

# (이름, 앞부분, 값) — 앞부분은 그대로 두고 값만 공유 링크 것으로 바꾼다
TURN_KEYS = [('현재 턴', r'"현재 턴":\s*', r'\d+'), ('턴 시작 시각', r'"턴 시작 시각":\s*', r'\{[^}]*\}')]

SRC = Path(__file__).resolve().parent.parent / 'index.html'
STRIP = [
    '<!doctype html>\n', '<html lang="ko">\n', '<head>\n', '</head>\n',
    '<body>\n', '</body>\n', '</html>\n',
    '<meta charset="utf-8">\n',
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
]


def main():
    args = sys.argv[1:]
    live = None
    if '--live' in args:
        i = args.index('--live')
        live = Path(args[i + 1]).read_text(encoding='utf-8')
        del args[i:i + 2]
    if len(args) != 1:
        sys.exit('사용: python3 news-article/tools/build_artifact.py <출력 경로> [--live <저장된 html>]')
    s = SRC.read_text(encoding='utf-8')
    for tag in STRIP:
        if tag not in s:
            sys.exit('원본에서 찾지 못한 태그: ' + tag.strip())
        s = s.replace(tag, '', 1)
    if 'window.print' in s or 'confirm(' in s:
        sys.exit('아티팩트에서 동작하지 않는 window.print/confirm 이 들어 있습니다.')
    carried = False
    for name, head, val in TURN_KEYS:
        if not re.search(head + val, s):
            sys.exit('원본 데이터에 턴 값이 없습니다: ' + name)
        if live is not None:
            m = re.search(head + '(' + val + ')', live)
            if not m:   # 턴 기능을 넣기 전 판이면 원본 값(1턴)으로 올린다
                print('주의: 공유 링크 판에 "' + name + '" 값이 없어 원본 값을 씁니다.')
                continue
            s = re.sub('(' + head + ')' + val, lambda mm: mm.group(1) + m.group(1), s, count=1)
            carried = True
    out = Path(args[0])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding='utf-8')
    turn = re.search(r'"현재 턴":\s*(\d+)', s).group(1)
    print('만듦:', out, f'({len(s):,}자, 현재 턴 {int(turn) + 1}턴' + (' = 공유 링크 값' if carried else ' = 원본 값') + ')')


if __name__ == '__main__':
    main()
