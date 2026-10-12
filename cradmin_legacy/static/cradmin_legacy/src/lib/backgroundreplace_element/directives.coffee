angular.module('cradminLegacy.backgroundreplace_element.directives', [])


.directive('cradminLegacyBgReplaceElementOnPageLoad', [
  '$window', 'cradminLegacyBgReplaceElement',
  ($window, cradminLegacyBgReplaceElement) ->
    ###
    This is just an example/debugging directive for cradminLegacyBgReplaceElement.
    ###
    return {
      restrict: 'A'

      controller: ($scope, $element) ->
        return

      link: ($scope, $element, attributes) ->
#        domId = $element.attr('id')
        remoteElementSelector = attributes.cradminLegacyRemoteElementSelector
        remoteUrl = attributes.cradminLegacyRemoteUrl
        if not remoteElementSelector?
          console?.error? "You must include the 'cradmin-legacy-remote-element-id' attribute."
        if not remoteUrl?
          console?.error? "You must include the 'cradmin-legacy-remote-url' attribute."
        angular.element(document).ready ->
          console.log 'load', remoteUrl, remoteElementSelector

          cradminLegacyBgReplaceElement.load({
            parameters: {
              method: 'GET'
              url: remoteUrl
            },
            remoteElementSelector: remoteElementSelector
            targetElement: $element
            $scope: $scope
            replace: true
            onHttpError: (response) ->
              console.log 'ERROR', response
            onSuccess: ->
              console.log 'Success!'
            onFinish: ->
              console.log 'Finish!'
          })
        return
    }
])
