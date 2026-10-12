angular.module('cradminLegacy.messages', [])


.controller('DjangoCradminMessagesCtrl', [
  '$scope', '$timeout'
  ($scope, $timeout) ->
    $scope.loading = true
    $timeout(->
      $scope.loading = false
    , 650)
    $scope.messageHidden = {}
    $scope.hideMessage = (index) ->
      $scope.messageHidden[index] = true
    $scope.messageIsHidden = (index) ->
      return $scope.messageHidden[index]
    return
])
