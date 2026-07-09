"""
Lightweight translation wrapper using deep-translator (free, no API key needed).
Translates arbitrary text at request time — supports any language the person asks for,
not a fixed set of pre-written translation files.
"""
from deep_translator import GoogleTranslator
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

# Small in-memory cache so repeated requests for the same text+language are instant
@lru_cache(maxsize=2000)
def _translate_single(text: str, target_lang: str) -> str:
    if not text.strip():
        return text
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation error for '{text[:40]}...' -> {target_lang}: {e}")
        return text  # fail gracefully — show original text rather than break the UI


def translate_batch(texts: list, target_lang: str) -> list:
    """Translate a list of strings in parallel — much faster than one-by-one."""
    if target_lang == "en":
        return texts
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda t: _translate_single(t, target_lang), texts))
    return results


SUPPORTED_LANGUAGES = {
    "en": "English", "es": "Español", "hi": "हिन्दी", "fr": "Français",
    "pt": "Português", "de": "Deutsch", "zh-CN": "中文", "ar": "العربية",
    "bn": "বাংলা", "id": "Bahasa Indonesia", "sw": "Kiswahili", "ja": "日本語",
}