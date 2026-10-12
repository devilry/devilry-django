angular.module('cradminLegacy.scrollfixed', [])


.directive('cradminLegacyScrollTopFixed', [
  'cradminLegacyWindowScrollTop'
  (cradminLegacyWindowScrollTop) ->
    ###* Keep an item aligned relative to a given top pixel position on the screen when scrolling.

    Example
    =======

    ```html
    <div cradmin-legacy-scroll-top-fixed>
      Some content here.
    </div>
    ```

    Make sure you style your element with absolute position. Example:

    ```
    position: absolute;
    top: 0;
    left: 0;
    ```

    Uses the initial top position as the offset. This means that you can style an element
    with something like this:

    ```
    position: absolute;
    top: 40px;
    right: 90px;
    ```

    And have it stay 40px from the top of the viewarea.

    Handling mobile devices
    =======================
    You may not want to scroll content on small displays. You
    should solve this with CSS media queries - simply do not
    use ``position: absolute;`` for the screen sizes you do
    not want to scroll.
    ###

    isUsingDefaultScroll = true
    swapClasses = false

    swapCssClasses = ($scope, $element, newWindowTopPosition) ->
      settings = $scope.cradminLegacyScrollTopFixedSettings
      if newWindowTopPosition >= $scope.cradminLegacyScrollTopFixedInitialTopOffset
        if isUsingDefaultScroll
          $element.removeClass settings.cssClasses.defaultClass
          $element.addClass settings.cssClasses.scrollClass
          isUsingDefaultScroll = false
      else if newWindowTopPosition < $scope.cradminLegacyScrollTopFixedInitialTopOffset
        if not isUsingDefaultScroll
          $element.addClass settings.cssClasses.defaultClass
          $element.removeClass settings.cssClasses.scrollClass
          isUsingDefaultScroll = true

    return {
      controller: ($scope, $element, $attrs) ->
        $scope.cradminLegacyScrollTopFixedSettings = $scope.$eval($attrs.cradminLegacyScrollTopFixed)
        if $scope.cradminLegacyScrollTopFixedSettings.cssClasses?
          if $scope.cradminLegacyScrollTopFixedSettings.cssClasses.defaultClass and
              $scope.cradminLegacyScrollTopFixedSettings.cssClasses.scrollClass
            swapClasses = true

        $scope.onWindowScrollTopStart = ->
          if $scope.cradminLegacyScrollTopFixedSettings.cssClasses?.scrollingClass?
            $element.addClass($scope.cradminLegacyScrollTopFixedSettings.cssClasses.scrollingClass)

        $scope.onWindowScrollTop = (newWindowTopPosition, initialScrollTrigger) ->
          if swapClasses
            swapCssClasses $scope, $element, newWindowTopPosition

          offset = $scope.cradminLegacyScrollTopFixedInitialTopOffset

          if $scope.cradminLegacyScrollTopFixedSettings.pinToTopOnScroll
            if newWindowTopPosition > offset
              offset = 0
            else
              offset = offset - newWindowTopPosition

          newTopPosition = newWindowTopPosition + offset
          $scope.cradminLegacyScrollTopFixedElement.css('top', "#{newTopPosition}px")
          if $scope.cradminLegacyScrollTopFixedSettings.cssClasses?.scrollingClass?
            $element.removeClass($scope.cradminLegacyScrollTopFixedSettings.cssClasses.scrollingClass)
        return

      link: ($scope, element, attrs) ->
        $scope.cradminLegacyScrollTopFixedElement = element
#        $scope.cradminLegacyScrollTopFixedSettings = $scope.$eval(attrs.cradminLegacyScrollTopFixed)
        $scope.cradminLegacyScrollTopFixedInitialTopOffset = parseInt(element.css('top'), 10) || 0

        cradminLegacyWindowScrollTop.register $scope
        $scope.$on '$destroy', ->
          cradminLegacyWindowScrollTop.unregister $scope
        return
    }
])
