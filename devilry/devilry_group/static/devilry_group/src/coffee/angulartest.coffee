app = angular.module 'devilryGroupTestApp', []

app.controller 'devilryGroupSidebarContentCollapse', ($scope) ->
  # Keep UPLOADED FILES not collapsed and the rest
  # collapsed as default
  $scope.isUploadedFilesCollapsed = false
  $scope.isTextFormattingCollapsed = true
  $scope.isCodeFormattingCollapsed = true
  $scope.isMathFormattingCollapsed = true

  $scope.toggleSidebarContentCollapse = (collapseElement) ->
#    console.log collapseElement
    if collapseElement == 'isUploadedFilesCollapsed'
      $scope.isUploadedFilesCollapsed = !$scope.isUploadedFilesCollapsed
      $scope.isTextFormattingCollapsed = true
      $scope.isCodeFormattingCollapsed = true
      $scope.isMathFormattingCollapsed = true
    else if collapseElement == 'isTextFormattingCollapsed'
      $scope.isTextFormattingCollapsed = !$scope.isTextFormattingCollapsed
      $scope.isUploadedFilesCollapsed = true
      $scope.isCodeFormattingCollapsed = true
      $scope.isMathFormattingCollapsed = true
    else if collapseElement == 'isCodeFormattingCollapsed'
      $scope.isCodeFormattingCollapsed = !$scope.isCodeFormattingCollapsed
      $scope.isUploadedFilesCollapsed = true
      $scope.isTextFormattingCollapsed = true
      $scope.isMathFormattingCollapsed = true
    else if collapseElement == 'isMathFormattingCollapsed'
      $scope.isMathFormattingCollapsed = !$scope.isMathFormattingCollapsed
      $scope.isUploadedFilesCollapsed = true
      $scope.isTextFormattingCollapsed = true
      $scope.isCodeFormattingCollapsed = true

app.directive 'devilryGroupTestDirective', [
  ->
    return {
      restrict: 'A'
      scope:
        settings: '=?devilryGroupTestDirective'

#      controller: ($scope, $element, $attrs) ->
#        console.log "I am a controller function on devilryGroupTestDirective"
#
#      link: ($scope, $element, $attrs) ->
#        console.log "I am a link function on devilryGroupTestDirective"
    }

]

