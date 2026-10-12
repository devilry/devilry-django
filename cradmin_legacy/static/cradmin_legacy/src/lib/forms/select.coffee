angular.module('cradminLegacy.forms.select', [])

.directive('cradminLegacyOpenUrlStoredInSelectedOption', [
  ->
    return {
      restrict: 'A',
      link: ($scope, $element, attributes) ->
        getValue = ->
          $element.find("option:selected").attr('value')

        $element.on 'change', ->
          remoteUrl = getValue()
          window.location = value
    }
])
