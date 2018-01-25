/*
Fallback implementations for the Django i18n translation catalog
functions.

See:
https://docs.djangoproject.com/en/2.0/topics/i18n/translation/

We only add the translation functions to ``window`` if they
are not already there. This means that this can be included
both before and after loading the Django i18n javascript catalog.
*/

if (!window.gettext) {
  window.gettext = function (msgid) {
    return msgid
  }
  if (process.env.NODE_ENV !== 'test') {
    console.warn(
      'window.gettext is not defined. Patching window.gettext and related ' +
      'functions with noop fallbacks. ' +
      'Make sure you import/include a full gettext translation system like ' +
      'the Django JavascriptCatalog view before ievv_jsbase or any javascript using ' +
      'ievv_jsbase to get translations.'
    )
  }
}

if (!window.pluralidx) {
  window.pluralidx = function (count) {
    return (count === 1) ? 0 : 1
  }
}

if (!window.ngettext) {
  window.ngettext = function (singular, plural, count) {
    return (count === 1) ? singular : plural
  }
}

if (!window.gettext_noop) {
  window.gettext_noop = function (msgid) {
    return msgid
  }
}

if (!window.pgettext) {
  window.pgettext = function (context, msgid) {
    return msgid
  }
}

if (!window.npgettext) {
  window.npgettext = function (context, singular, plural, count) {
    return (count === 1) ? singular : plural
  }
}

if (!window.interpolate) {
  window.interpolate = function (fmt, obj, named) {
    if (named) {
      return fmt.replace(/%\(\w+\)s/g, function (match) {
        return String(obj[match.slice(2, -2)])
      })
    } else {
      return fmt.replace(/%s/g, function (match) {
        return String(obj.shift())
      })
    }
  }
}

if (!window.get_format) {
  window.get_format = function (format_type) {
    return format_type
  }
}
