angular.module('cradminLegacy.wysihtml', [])

.directive 'cradminLegacyWysihtml', () ->
  return {
    restrict: 'A'
    transclude: true
    template: '<div><p>Stuff is awesome!</p><div ng-transclude></div></div>'
  }
