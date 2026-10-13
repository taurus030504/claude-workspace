import unicodedata

from app.services.markdown_tools import chunk_markdown, excerpt, extract_wiki_links, normalize_text
from app.services.text_analysis import analyze_query, strip_korean_suffix


def test_chunks_follow_headings_and_keep_offsets():
    text = "intro line\n\n# 게임 설계\n본문 A\n\n## 조작\n점프와 창 고정\n\n# 스테이지\n1단계"
    chunks = chunk_markdown(text, max_chars=500)
    assert [c.heading for c in chunks] == ["", "게임 설계", "게임 설계 > 조작", "스테이지"]
    for c in chunks:
        assert text[c.start : c.end] == c.content
    assert chunks[2].content.startswith("## 조작")


def test_headings_inside_code_fences_are_ignored():
    text = "# A\n```\n# not a heading\n```\ntext"
    chunks = chunk_markdown(text)
    assert len(chunks) == 1 and chunks[0].heading == "A"


def test_long_sections_are_split_below_limit():
    para = "가나다라마바사 " * 30
    text = "# 긴 글\n" + "\n\n".join([para] * 6)
    chunks = chunk_markdown(text, max_chars=300)
    assert len(chunks) > 3
    assert all(len(c.content) <= 300 for c in chunks)
    assert all(text[c.start : c.end] == c.content for c in chunks)


def test_empty_document_yields_one_empty_chunk():
    chunks = chunk_markdown("")
    assert len(chunks) == 1 and chunks[0].content == ""


def test_wiki_links():
    text = "see [[창 물리 시스템]] and [[게임 설계 문서|GDD]] and [[창 물리 시스템#반동]] [[ ]]"
    assert extract_wiki_links(text) == ["창 물리 시스템", "게임 설계 문서"]


def test_normalize_composes_hangul_and_line_endings():
    decomposed = unicodedata.normalize("NFD", "한글") + "\r\nx\ry"
    assert normalize_text(decomposed) == "한글\nx\ny"


def test_excerpt_strips_markdown():
    assert excerpt("# 제목\n**굵게** `code`") == "제목 굵게 code"


def test_particles_and_stopwords_removed():
    assert strip_korean_suffix("프로젝트를") == "프로젝트"
    assert strip_korean_suffix("게임에서는") == "게임"
    assert strip_korean_suffix("필요") == "필요"  # would leave 1 char -> untouched
    assert analyze_query("창 고정 기능을 어떻게 구현하는지 알려줘") == ["고정", "기능", "구현"]
    assert analyze_query("What is the spear physics?") == ["spear", "physics"]
    assert analyze_query("??? !!") == []


def test_query_terms_are_deduplicated_and_capped():
    terms = analyze_query("게임 게임을 게임의 " + " ".join(f"단어{i}" for i in range(20)))
    assert terms[0] == "게임" and terms.count("게임") == 1
    assert len(terms) == 8
