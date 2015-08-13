app = angular.module 'devilryGroupTestApp', []

app.controller 'devilryGroupTestController', ($scope) ->
  alert "I am testController, and I am here to kill you all!!"

app.directive 'devilryGroupTestDirective', [
  ->
    return {
      restrict: 'A'
      scope:
        settings: '=?devilryGroupTestDirective'

      controller: ($scope, $element, $attrs) ->
        console.log "I am a controller function on devilryGroupTestDirective"

      link: ($scope, $element, $attrs) ->
        console.log "I am a link function on devilryGroupTestDirective"
    }

]

