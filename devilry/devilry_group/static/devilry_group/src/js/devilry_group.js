(function() {
  var app;

  app = angular.module('devilryGroupTestApp', ['ui.bootstrap']);

  app.controller('devilryGroupSidebarContentCollapse', function($scope) {
    $scope.isUploadedFilesCollapsed = false;
    $scope.isTextFormattingCollapsed = true;
    $scope.isCodeFormattingCollapsed = true;
    $scope.isMathFormattingCollapsed = true;
    return $scope.toggleSidebarContentCollapse = function(collapseElement) {
      if (collapseElement === 'isUploadedFilesCollapsed') {
        $scope.isUploadedFilesCollapsed = !$scope.isUploadedFilesCollapsed;
        $scope.isTextFormattingCollapsed = true;
        $scope.isCodeFormattingCollapsed = true;
        return $scope.isMathFormattingCollapsed = true;
      } else if (collapseElement === 'isTextFormattingCollapsed') {
        $scope.isTextFormattingCollapsed = !$scope.isTextFormattingCollapsed;
        $scope.isUploadedFilesCollapsed = true;
        $scope.isCodeFormattingCollapsed = true;
        return $scope.isMathFormattingCollapsed = true;
      } else if (collapseElement === 'isCodeFormattingCollapsed') {
        $scope.isCodeFormattingCollapsed = !$scope.isCodeFormattingCollapsed;
        $scope.isUploadedFilesCollapsed = true;
        $scope.isTextFormattingCollapsed = true;
        return $scope.isMathFormattingCollapsed = true;
      } else if (collapseElement === 'isMathFormattingCollapsed') {
        $scope.isMathFormattingCollapsed = !$scope.isMathFormattingCollapsed;
        $scope.isUploadedFilesCollapsed = true;
        $scope.isTextFormattingCollapsed = true;
        return $scope.isCodeFormattingCollapsed = true;
      }
    };
  });

  app.directive('devilryGroupTestDirective', [
    function() {
      return {
        restrict: 'A',
        scope: {
          settings: '=?devilryGroupTestDirective'
        }
      };
    }
  ]);

}).call(this);
