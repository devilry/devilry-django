angular.module('cradminLegacy.forms.clearabletextinput', [])

.directive('cradminLegacyClearableTextinput', [
  ->
    return {
      restrict: 'A',
      link: ($scope, $element, attributes) ->
        targetElementSelector = attributes.cradminLegacyClearableTextinput
        $target = angular.element(targetElementSelector)

        onTargetValueChange = ->
          if $target.val() == ''
            $element.removeClass('cradmin-legacy-clearable-textinput-button-visible')
          else
            $element.addClass('cradmin-legacy-clearable-textinput-button-visible')

        $element.on 'click', (e) ->
          e.preventDefault()
          $target.val('')
          $target.focus()
          $target.change()

        $target.on 'change', ->
          onTargetValueChange()

        $target.on 'keydown', (e) ->
          onTargetValueChange()

        onTargetValueChange()
    }
])
