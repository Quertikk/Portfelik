"""F11: odczyt paragonu z atrapą modelu; NF6 (brak zapisu pliku), NF9 (klucz tylko ze środowiska)."""
import io
import json

import pytest

import receipts
from conftest import WALLET, query

PNG = b"\x89PNG\r\n\x1a\n" + b"x" * 100
MINE = WALLET["Filip"]
GOOD = {"amount": "12,50 zł", "date": "2026-11-06", "shop": "Biedronka", "category": "Transport"}


def fake_model(monkeypatch, answer):
    calls = []

    def provider(image, mime):
        calls.append((image, mime))
        if isinstance(answer, Exception):
            raise answer
        return answer if isinstance(answer, str) else json.dumps(answer)

    monkeypatch.setitem(receipts.PROVIDERS, "gemini", provider)
    return calls


def upload(client, content=PNG, wallet=MINE, name="paragon.png"):
    return client.post(f"/portfel/{wallet}/paragon", follow_redirects=True,
                       data={"receipt": (io.BytesIO(content), name)}, content_type="multipart/form-data")


def amount_field(html):
    """Wartość pola kwoty w formularzu dodawania."""
    tag = html[html.index('name="amount"'):].split(">", 1)[0]
    return tag.split('value="', 1)[1].split('"', 1)[0] if 'value="' in tag else ""


def test_good_answer_fills_form_without_saving(client, monkeypatch):
    calls = fake_model(monkeypatch, GOOD)
    before = len(query("SELECT * FROM expenses"))
    html = upload(client).get_data(as_text=True)
    assert amount_field(html) == "12,50"
    assert 'value="Biedronka"' in html and 'value="2026-11-06"' in html
    assert '<option value="3" selected>' in html  # Transport
    assert calls == [(PNG, "image/png")]
    assert len(query("SELECT * FROM expenses")) == before  # zapis dopiero po kliknięciu „Dodaj”


def test_jpeg_accepted(client, monkeypatch):
    calls = fake_model(monkeypatch, GOOD)
    upload(client, b"\xff\xd8\xff\xe0" + b"x" * 50, name="a.jpg")
    assert calls[0][1] == "image/jpeg"


def test_invalid_json_gives_message(client, monkeypatch):
    fake_model(monkeypatch, "to nie jest json")
    html = upload(client).get_data(as_text=True)
    assert "nieczytelną odpowiedź" in html and 'value="Biedronka"' not in html


def test_json_that_is_not_object_gives_message(client, monkeypatch):
    fake_model(monkeypatch, "[1, 2]")
    assert "nieczytelną odpowiedź" in upload(client).get_data(as_text=True)


@pytest.mark.parametrize("amount", ["abc", "", "0", "-5", "inf", "1e999", "99999999"])
def test_bad_amount_asks_for_manual_entry_but_keeps_other_fields(client, monkeypatch, amount):
    fake_model(monkeypatch, dict(GOOD, amount=amount))
    html = upload(client).get_data(as_text=True)
    assert "Nie udało się odczytać kwoty" in html and 'value="Biedronka"' in html
    assert amount_field(html) == ""


def test_bad_date_and_unknown_category_are_dropped(client, monkeypatch):
    fake_model(monkeypatch, dict(GOOD, date="wczoraj", category="Kosmos"))
    html = upload(client).get_data(as_text=True)
    assert amount_field(html) == "12,50" and "wczoraj" not in html and "selected" not in html


def test_missing_fields_do_not_crash(client, monkeypatch):
    fake_model(monkeypatch, {"amount": None})
    assert "Nie udało się odczytać kwoty" in upload(client).get_data(as_text=True)


@pytest.mark.parametrize("content", [b"GIF89a....", b"%PDF-1.4", b"", b"<html>"])
def test_wrong_file_type_is_rejected_before_model(client, monkeypatch, content):
    calls = fake_model(monkeypatch, GOOD)
    assert "JPG lub PNG" in upload(client, content).get_data(as_text=True)
    assert calls == []


def test_png_name_does_not_make_html_an_image(client, monkeypatch):
    calls = fake_model(monkeypatch, GOOD)
    assert "JPG lub PNG" in upload(client, b"<script>", name="x.png").get_data(as_text=True)
    assert calls == []


def test_missing_file_field(client):
    resp = client.post(f"/portfel/{MINE}/paragon", follow_redirects=True)
    assert "JPG lub PNG" in resp.get_data(as_text=True)


def test_too_big_file_is_rejected(client, monkeypatch):
    calls = fake_model(monkeypatch, GOOD)
    html = upload(client, PNG + b"x" * receipts.MAX_BYTES).get_data(as_text=True)
    assert "za duży" in html and calls == []


def test_model_error_message_is_shown(client, monkeypatch):
    fake_model(monkeypatch, receipts.ReceiptError("Nie udało się odczytać paragonu. Wpisz wydatek ręcznie."))
    assert "Wpisz wydatek ręcznie" in upload(client).get_data(as_text=True)


def test_missing_api_key_gives_message(client, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert "nie jest skonfigurowany" in upload(client).get_data(as_text=True)


def test_other_users_wallet_is_404(client):
    assert client.post(f"/portfel/{WALLET['Daria']}/paragon", data={}).status_code == 404


def test_requires_login(anon):
    assert anon.post(f"/portfel/{MINE}/paragon").status_code == 302


def test_nothing_written_to_disk(client, monkeypatch, tmp_path):
    fake_model(monkeypatch, GOOD)
    before = sorted(p.name for p in tmp_path.iterdir())
    upload(client)
    assert sorted(p.name for p in tmp_path.iterdir()) == before


def test_prefilled_form_posts_like_manual_entry(client, monkeypatch):
    """Zapis idzie zwykłą trasą dodawania, więc próg i walidacja działają tak samo jak przy ręcznym wpisie."""
    fake_model(monkeypatch, GOOD)
    upload(client)
    client.post(f"/portfel/{MINE}/dodaj", data={"amount": "12,50", "category_id": 3, "spent_on": "2026-11-06",
                                               "description": "Biedronka"})
    assert tuple(query("SELECT amount, description FROM expenses ORDER BY id DESC LIMIT 1")[0]) == (1250, "Biedronka")


def test_upload_form_warns_about_external_model(client):
    html = client.get(f"/portfel/{MINE}").get_data(as_text=True)
    assert "zewnętrznego modelu AI" in html and 'accept="image/jpeg,image/png"' in html


# dostawca Gemini bez sieci
class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_gemini_sends_key_in_header_and_returns_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "sekret-klucz")
    seen = {}

    def urlopen(req, timeout):
        seen["url"], seen["headers"] = req.full_url, dict(req.header_items())
        return FakeResponse(json.dumps({"candidates": [{"content": {"parts": [{"text": '{"amount": "1"}'}]}}]}).encode())

    monkeypatch.setattr(receipts.urllib.request, "urlopen", urlopen)
    assert receipts.gemini(PNG, "image/png") == '{"amount": "1"}'
    assert "sekret-klucz" not in seen["url"] and seen["headers"]["X-goog-api-key"] == "sekret-klucz"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(receipts.time, "sleep", lambda s: None)


@pytest.mark.parametrize("failure", [receipts.urllib.error.URLError("brak sieci"), TimeoutError(), ValueError()])
def test_gemini_network_errors_become_receipt_error(monkeypatch, failure):
    monkeypatch.setenv("GEMINI_API_KEY", "k")

    def urlopen(req, timeout):
        raise failure

    monkeypatch.setattr(receipts.urllib.request, "urlopen", urlopen)
    with pytest.raises(receipts.ReceiptError):
        receipts.gemini(PNG, "image/png")


def test_gemini_unexpected_reply_shape(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(receipts.urllib.request, "urlopen", lambda req, timeout: FakeResponse(b'{"candidates": []}'))
    with pytest.raises(receipts.ReceiptError):
        receipts.gemini(PNG, "image/png")


def test_image_mime():
    assert receipts.image_mime(PNG) == "image/png"
    assert receipts.image_mime(b"\xff\xd8\xff\xdb") == "image/jpeg"
    assert receipts.image_mime(b"GIF89a") is None


def http_error(code):
    return receipts.urllib.error.HTTPError("http://x", code, "err", {}, io.BytesIO(b"{}"))


def test_gemini_retries_after_overload(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    answers = [http_error(503), TimeoutError(), FakeResponse(
        json.dumps({"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}).encode())]

    def urlopen(req, timeout):
        a = answers.pop(0)
        if isinstance(a, Exception):
            raise a
        return a

    monkeypatch.setattr(receipts.urllib.request, "urlopen", urlopen)
    assert receipts.gemini(PNG, "image/png") == "ok" and not answers


def test_gemini_gives_up_after_three_tries(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    calls = []

    def urlopen(req, timeout):
        calls.append(1)
        raise http_error(503)

    monkeypatch.setattr(receipts.urllib.request, "urlopen", urlopen)
    with pytest.raises(receipts.ReceiptError):
        receipts.gemini(PNG, "image/png")
    assert len(calls) == receipts.TRIES


def test_gemini_does_not_retry_bad_request(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    calls = []

    def urlopen(req, timeout):
        calls.append(1)
        raise http_error(404)

    monkeypatch.setattr(receipts.urllib.request, "urlopen", urlopen)
    with pytest.raises(receipts.ReceiptError):
        receipts.gemini(PNG, "image/png")
    assert len(calls) == 1
