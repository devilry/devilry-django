app = angular.module 'devilryGroup.sidebar', []

app.controller 'sidebarCollapseCtrl', ["$scope", ($scope) ->
  $scope.collapse_variables = []

  $scope.register_collapse = (collapse_id, initial=false) ->
    $scope.collapse_variables.push {name: collapse_id, value: initial}
    return $scope.collapse_variables[$scope.collapse_variables.length-1]


  $scope.toggle_collapse = (collapse_id) ->
    console.log "asd"
    for collapse_var in $scope.collapse_variables
      if collapse_var.name == collapse_id
        collapse_var.value = true
      else
        collapse_var.value = false

  return
]