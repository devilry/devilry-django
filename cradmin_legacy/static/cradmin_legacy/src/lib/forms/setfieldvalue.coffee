app = angular.module 'cradminLegacy.forms.setfieldvalue', ['cfp.hotkeys']

###*
Directive for setting the value of a form field to specified value.

Example:

```
  <button type="button"
          cradmin-legacy-setfieldvalue="2015-12-24 12:30"
          cradmin-legacy-setfieldvalue-field-id="my_datetimefield_id">
      Set value to 2015-12-24 12:30
  </button>
```

You can make the directive change the focus on click after applying the
value with ``cradmin-legacy-setfieldvalue-move-focus-on-click="<id>"``:

```
  <button type="button"
          cradmin-legacy-setfieldvalue="2015-12-24 12:30"
          cradmin-legacy-setfieldvalue-field-id="my_datetimefield_id"
          cradmin-legacy-setfieldvalue-move-focus-on-click="my_datetimefield_id">
      Set value to 2015-12-24 12:30
  </button>
```


Can also be used on ``<a>``-elements. The directive uses ``e.preventDefault``
to ensure the href is not triggered.
###
app.directive 'cradminLegacySetfieldvalue', [
  ->
    return {
      scope: {
        value: "@cradminLegacySetfieldvalue"
        fieldid: "@cradminLegacySetfieldvalueFieldId"
        moveFocusOnClick: "@cradminLegacySetfieldvalueMoveFocusOnClick"
      }

      link: ($scope, $element) ->
        fieldElement = angular.element("##{$scope.fieldid}")
        if $scope.moveFocusOnClick?
          focusElement = angular.element("##{$scope.moveFocusOnClick}")
        if fieldElement.length == 0
          console?.error? "Could not find a field with the '#{$scope.fieldid}' ID."
        else
          $element.on 'click', (e) ->
            e.preventDefault()
            fieldElement.val $scope.value
            fieldElement.trigger 'change'
            if focusElement?
              focusElement.focus()
          return
    }
]
