function dtranslate(key) {
    var translation = i18n[key];
    if(translation) {
        return translation;
    } else {
        return key;
    }
}
