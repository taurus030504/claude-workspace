#!/usr/bin/env python3
"""교사가 만든 이미지 파일을 기사 이미지로 넣는다 (data URI로 내장).

사용법:
  python3 tools/embed_image.py <기사 아이디> <이미지 파일> [설명]
예:
  python3 tools/embed_image.py a1 assets/a1_단톡방캡처.png "두 사람의 예고 동창이 올린 메시지 캡처. 사진=SNS 캡처"

- 기사 '이미지' 칸을 { "종류": "사진", "자료": "data:...", "설명": ... } 로 바꾼다.
- 설명을 생략하면 기존 설명을 유지한다. 바꾸기 전 이미지 칸은 '이미지(이전)' 에 남겨 둔다.
- webp/png/jpg 모두 됨. 1MB가 넘으면 경고만 하고 계속 진행.
"""
import base64, json, mimetypes, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
OPEN = '<script type="application/json" id="site-data">\n'

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
    i = html.index(OPEN) + len(OPEN); j = html.index('</script>', i)
    data = json.loads(html[i:j])
    art = [a for a in data['기사'] if a['아이디'] == aid]
    if not art:
        print('없는 기사 아이디:', aid); sys.exit(1)
    a = art[0]
    old = a.get('이미지')
    if old and old.get('종류') != '사진':
        a['이미지(이전)'] = old
    a['이미지'] = { '종류': '사진', '자료': uri, '설명': desc or (old or {}).get('설명', '[교사 입력]') }
    out = json.dumps(data, ensure_ascii=False, indent=2)
    open(HTML, 'w', encoding='utf-8').write(html[:i] + out + '\n' + html[j:])
    print(f'{aid} 이미지를 {os.path.basename(path)} ({len(raw)//1024}KB, {mime}) 로 바꿨어요.')

if __name__ == '__main__':
    main()
