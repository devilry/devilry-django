app = angular.module 'cradminLegacy.forms.filewidget', []

app.controller 'CradminFileFieldController', ($scope, $filter) ->

  $scope.init = ->
    $scope.$watch 'cradmin_filefield_has_value', (newValue) ->
      if newValue?
        if newValue
          $scope.cradmin_filefield_clearcheckbox_value = ''
        else
          $scope.cradmin_filefield_clearcheckbox_value = 'checked'
    return

  $scope.cradminClearFileField = ->
    $scope.cradmin_filefield_clear_value = true

  $scope.init()
  return


app.directive 'cradminFilefieldValue', ->
  {
    scope: false

    link: ($scope, element, attributes) ->
      $scope.cradmin_filefield_clear_value = false
      fileFieldElement = element

      if attributes.cradminFilefieldValue? and attributes.cradminFilefieldValue != ""
        $scope.cradmin_filefield_has_value = true
        $scope.cradmin_filefield_has_original_value = true

      setupFileFieldChangeListener = ->
        fileFieldElement.bind 'change', (changeEvent) ->
          reader = new FileReader

          reader.onload = (loadEvent) ->
            $scope.$apply ->
              #value = loadEvent.target.result
              $scope.cradmin_filefield_has_value = true
              $scope.cradmin_filefield_has_original_value = false
              return
            return

          reader.readAsDataURL changeEvent.target.files[0]
          return

      $scope.$watch 'cradmin_filefield_clear_value', (newValue) ->
        if newValue
          $scope.cradmin_filefield_has_value = false
          $scope.cradmin_filefield_clear_value = false
          $scope.cradmin_filefield_has_original_value = false
          newFileFieldElement = fileFieldElement.clone()
          jQuery(fileFieldElement).replaceWith(newFileFieldElement)
          fileFieldElement = newFileFieldElement
          setupFileFieldChangeListener()

      setupFileFieldChangeListener()
      return
  }
