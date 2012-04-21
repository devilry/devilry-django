/** Lookup a translation for the given ``key``.
 *
 * If the key is not found, the ``fallback`` is returned. As a last resort, the
 * key is returned.
 *
 * **Usage:** Only use fallback when the UI will break (I.E. for date
 * formatting strings etc..). In any other case it is easier to test and spot
 * untranslated UI widgets when the key is displayed by default.
 */
function dtranslate(key, fallback) {
    if(window.document.i18n) {
        var translation = window.document.i18n[key];
        if(translation) {
            return translation;
        } 
    }
    if(fallback !== undefined) {
        return fallback;
    }
    return key;
}
