function dtranslate(key) {
    if(window.document.i18n) {
        var translation = window.document.i18n[key];
        if(translation) {
            return translation;
        }
    }
    return key;
}
