"""
Lightweight translation wrapper using deep-translator (free, no API key).
Runs translations in parallel with a timeout per-call, so a single slow
or failing request can't stall the whole batch.
"""
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from functools import lru_cache

REQUEST_TIMEOUT_SECONDS = 4
MAX_WORKERS = 16

@lru_cache(maxsize=5000)
def _translate_single(text: str, target_lang: str) -> str:
    if not text.strip():
        return text
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation error for '{text[:40]}...' -> {target_lang}: {e}")
        return text


def _translate_with_timeout(text: str, target_lang: str) -> str:
    with ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(_translate_single, text, target_lang)
        try:
            return future.result(timeout=REQUEST_TIMEOUT_SECONDS)
        except FutureTimeoutError:
            print(f"Translation timed out for '{text[:40]}...' -> {target_lang}, returning original.")
            return text


def translate_batch(texts: list, target_lang: str) -> list:
    if target_lang == "en":
        return texts
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(lambda t: _translate_with_timeout(t, target_lang), texts))
    return results


SUPPORTED_LANGUAGES = {
    "en": "English", "es": "Español", "hi": "हिन्दी", "fr": "Français",
    "pt": "Português", "de": "Deutsch", "zh-CN": "中文", "ar": "العربية",
    "bn": "বাংলা", "id": "Bahasa Indonesia", "sw": "Kiswahili", "ja": "日本語",
}