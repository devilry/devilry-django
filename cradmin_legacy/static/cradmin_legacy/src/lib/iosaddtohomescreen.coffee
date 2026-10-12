angular.module('cradminLegacy.iosaddtohomescreen', [])

.directive 'iosAddToHomeScreen', ['$window', 'cradminDetectize', ($window, cradminDetectize) ->
  {
    transclude: true
    template: '<div ng-transclude>This is my directive content</div>'

    link: ($scope, $element, attrs) ->
      if attrs.forceOs?
        $scope.os = attrs.forceOs
      else
        $scope.os = cradminDetectize.os.name

      if attrs.forceBrowser?
        $scope.browser = attrs.forceBrowser
      else
        $scope.browser = cradminDetectize.browser.name

      if attrs.forceDeviceModel?
        $scope.deviceModel = attrs.forceDeviceModel
      else
        $scope.deviceModel = cradminDetectize.device.model

#      console.log 'Detected os:', $scope.os
#      console.log 'Detected browser:', $scope.browser
#      console.log 'Detected deviceModel:', $scope.deviceModel
#
#      console.log $window.navigator.standalone

      if $scope.os == 'ios' and $scope.browser == 'safari'
        $element.show()
      else
        $element.hide()
      return
  }
]
