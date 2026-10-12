angular.module('cradminLegacy.forms.usethisbutton', [])

.directive('cradminLegacyUseThis', [
  '$window'
  ($window) ->
    ###
    The cradmin-legacy-use-this directive is used to select elements for
    the ``cradmin-legacy-model-choice-field`` directive. You add this directive
    to a button or a-element within an iframe, and this directive will use
    ``window.postMessage`` to send the needed information to the
    ``cradmin-legacy-model-choice-field-wrapper``.

    You may also use this if you create your own custom iframe communication
    receiver directive where a "use this" button within an iframe is needed.

    Example
    =======
    ```
      <a class="btn btn-default" cradmin-legacy-use-this="Peter Pan" cradmin-legacy-fieldid="id_name">
        Use this
      </a>
    ```

    How it works
    ============
    When the user clicks an element with this directive, the click
    is captured, the default action is prevented, and we decode the
    given JSON encoded value and add ``postmessageid='cradmin-legacy-use-this'``
    to the object making it look something like this::

      ```
      {
        postmessageid: 'cradmin-legacy-use-this',
        value: '<the value provided via the cradmin-legacy attribute>',
        fieldid: '<the fieldid provided via the cradmin-legacy-fieldid attribute>',
        preview: '<the preview HTML>'
      }
      ```

    We assume there is a event listener listening for the ``message`` event on
    the message in the parent of the iframe where this was clicked, but no checks
    ensuring this is made.
    ###
    return {
      restrict: 'A'
      scope: {
        data: '@cradminLegacyUseThis'
      }

      link: (scope, element, attrs) ->
        element.on 'click', (e) ->
          e.preventDefault()
          data = angular.fromJson(scope.data)
          data.postmessageid = 'cradmin-legacy-use-this'
          $window.parent.postMessage(
            angular.toJson(data),
            window.parent.location.href)

        return
    }
])

.directive('cradminLegacyUseThisHidden', [
  '$window'
  ($window) ->
    ###
    Works just like the ``cradmin-legacy-use-this`` directive, except this
    is intended to be triggered on load.

    The intended use-case is to trigger the same action as clicking a
    ``cradmin-legacy-use-this``-button but on load, typically after creating/adding
    a new item that the user wants to be selected without any further manual input.
    ###
    return {
      restrict: 'A'
      scope: {
        data: '@cradminLegacyUseThisHidden'
      }

      link: (scope, element, attrs) ->
        data = angular.fromJson(scope.data)
        data.postmessageid = 'cradmin-legacy-use-this'
        $window.parent.postMessage(
          angular.toJson(data),
          window.parent.location.href)
        return
    }
])
