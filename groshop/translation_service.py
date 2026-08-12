import boto3
from django.conf import settings

_client = None


def get_translate_client():
    global _client
    if _client is None:
        _client = boto3.client(
            'translate',
            aws_access_key_id=settings.AWS_TRANSLATE_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_TRANSLATE_SECRET_KEY,
            region_name=settings.AWS_TRANSLATE_REGION,
        )
    return _client


def translate_text(text, source_lang, target_lang):
    """
    Traduit un texte. source_lang/target_lang: 'fr', 'en', 'ar'
    Amazon Translate utilise les mêmes codes ISO, donc pas de mapping nécessaire.
    """
    if not text or not text.strip():
        return ''

    client = get_translate_client()
    response = client.translate_text(
        Text=text,
        SourceLanguageCode=source_lang,
        TargetLanguageCode=target_lang,
    )
    return response['TranslatedText']