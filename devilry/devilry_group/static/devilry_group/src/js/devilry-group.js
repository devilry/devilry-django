(function() {
  var app;

  app = angular.module('devilryGroup', []);

  app = angular.module('devilryGroup.sidebar', []);

  app.controller('sidebarCollapseCtrl', [
    "$scope", function($scope) {
      $scope.collapse_variables = [];
      $scope.register_collapse = function(collapse_id, initial) {
        if (initial == null) {
          initial = false;
        }
        $scope.collapse_variables.push({
          name: collapse_id,
          value: initial
        });
        return $scope.collapse_variables[$scope.collapse_variables.length - 1];
      };
      $scope.toggle_collapse = function(collapse_id) {
        var collapse_var, _i, _len, _ref, _results;
        _ref = $scope.collapse_variables;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          collapse_var = _ref[_i];
          if (collapse_var.name === collapse_id) {
            _results.push(collapse_var.value = true);
          } else {
            _results.push(collapse_var.value = false);
          }
        }
        return _results;
      };
    }
  ]);

}).call(this);
