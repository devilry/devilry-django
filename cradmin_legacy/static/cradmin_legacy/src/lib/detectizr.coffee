angular.module('cradminLegacy.detectizr', [])


.factory 'cradminDetectize', ->
  Detectizr.detect({
    # option for enabling HTML classes of all features (not only the true features) to be added
    addAllFeaturesAsClass: false,
    # option for enabling detection of device
    detectDevice: true,
    # option for enabling detection of device model
    detectDeviceModel: true,
    # option for enabling detection of screen size
    detectScreen: true,
    # option for enabling detection of operating system type and version
    detectOS: true,
    # option for enabling detection of browser type and version
    detectBrowser: true,
    # option for enabling detection of common browser plugins
    detectPlugins: false
  })
  return Detectizr
