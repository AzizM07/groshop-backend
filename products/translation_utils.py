from groshop.translation_service import translate_text

LANGUAGES = ['fr', 'en', 'ar']
SOURCE_LANG = 'fr'

# Quels champs traduire pour chaque modèle
TRANSLATE_CONFIG = {
    'Product': ['name', 'description', 'specs_raw'],
    'Category': ['name'],
    'ProductVariant': ['name'],
    'ProductChoiceGroup': ['name'],
}


def auto_translate_fields(model_cls, pk, fields, source_lang=SOURCE_LANG):
    """
    Remplit les champs _en / _ar manquants à partir du champ _fr.
    N'écrase JAMAIS une traduction déjà présente (manuelle ou automatique).
    Utilise .update() pour éviter de redéclencher les signals (pas de boucle infinie).
    """
    try:
        instance = model_cls.objects.get(pk=pk)
    except model_cls.DoesNotExist:
        return

    updates = {}
    for field in fields:
        source_value = getattr(instance, f'{field}_{source_lang}', None)
        if not source_value:
            continue

        for lang in LANGUAGES:
            if lang == source_lang:
                continue
            target_attr = f'{field}_{lang}'
            current_value = getattr(instance, target_attr, None)
            if current_value:
                continue  # déjà traduit, on ne touche pas

            try:
                translated = translate_text(source_value, source_lang, lang)
            except Exception:
                translated = None  # AWS down / erreur réseau → on ignore, pas de crash

            if translated:
                updates[target_attr] = translated

    if updates:
        model_cls.objects.filter(pk=pk).update(**updates)