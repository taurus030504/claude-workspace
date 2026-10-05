#!/usr/bin/env python3
"""교사가 만든 이미지 파일을 기사 이미지로 넣는다 (data URI로 내장).

사용법:
  python3 tools/embed_image.py <기사 아이디> <이미지 파일> [설명]
예:
  python3 tools/embed_image.py a1 assets/a1_단톡방캡처.webp "두 사람의 예고 동창이 올린 메시지 캡처. 사진=SNS 캡처"

- 기사 '이미지' 칸을 { "종류": "사진", "자료": "data:...", "설명": ... } 로 바꾼다.
- 설명을 생략하면 기존 설명을 유지한다. 바꾸기 전 이미지 칸은 '이미지(이전)' 에 남겨 둔다.
- 데이터 블록의 다른 줄은 건드리지 않는다(댓글 한 줄 서식 유지).
- webp/png/jpg 모두 됨. 1MB가 넘으면 경고만 하고 계속 진행.
"""
import base64, json, mimetypes, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
OPEN = '<script type="application/json" id="site-data">\n'

def find_value_end(text, start):
    """text[start]가 { 또는 [ 또는 " 또는 null/숫자일 때 그 값이 끝나는 위치(끝 다음 인덱스)를 돌려준다."""
    c = text[start]
    if c in '{[':
        depth, i, in_str = 0, start, False
        while i < len(text):
            ch = text[i]
            if in_str:
                if ch == '\\': i += 1
                elif ch == '"': in_str = False
            elif ch == '"': in_str = True
            elif ch in '{[': depth += 1
            elif ch in '}]':
                depth -= 1
                if depth == 0: return i + 1
            i += 1
    if c == '"':
        i = start + 1
        while i < len(text):
            if text[i] == '\\': i += 2; continue
            if text[i] == '"': return i + 1
            i += 1
    i = start
    while i < len(text) and text[i] not in ',\n': i += 1
    return i

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    aid, path = sys.argv[1], sys.argv[2]
    desc = sys.argv[3] if len(sys.argv) > 3 else None
    mime = mimetypes.guess_type(path)[0] or 'image/png'
    raw = open(path, 'rb').read()
    if len(raw) > 1_000_000:
        print(f'경고: {len(raw)//1024}KB. 1MB가 넘으면 공유 링크가 느려질 수 있어요. 줄여서 다시 넣는 걸 권해요.')
    uri = 'data:' + mime + ';base64,' + base64.b64encode(raw).decode()

    html = open(HTML, encoding='utf-8').read()
    bi = html.index(OPEN) + len(OPEN); bj = html.index('</script>', bi)
    block = html[bi:bj]
    key = '"아이디": ' + json.dumps(aid, ensure_ascii=False)
    if key not in block:
        print('없는 기사 아이디:', aid); sys.exit(1)
    a0 = block.index(key)
    k = block.index('"이미지":', a0)
    v = k + len('"이미지":')
    while block[v] == ' ': v += 1
    e = find_value_end(block, v)
    old_text = block[v:e]
    old = json.loads(old_text)
    indent = ' ' * (k - block.rfind('\n', 0, k) - 1)
    new = {'종류': '사진', '자료': uri, '설명': desc or (old or {}).get('설명', '[교사 입력]')}
    new_text = json.dumps(new, ensure_ascii=False, indent=2).replace('\n', '\n' + indent)
    out = block[:v] + new_text
    if old and old.get('종류') != '사진':
        out += ',\n' + indent + '"이미지(이전)": ' + old_text.replace('\n', '\n')
    out += block[e:]
    json.loads(out)
    open(HTML, 'w', encoding='utf-8').write(html[:bi] + out + html[bj:])
    print(f'{aid} 이미지를 {os.path.basename(path)} ({len(raw)//1024}KB, {mime}) 로 바꿨어요.')

if __name__ == '__main__':
    main()
