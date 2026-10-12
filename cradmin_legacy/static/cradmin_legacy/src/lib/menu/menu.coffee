angular.module('cradminLegacy.menu', [])


.directive('cradminLegacyMenu', [
  ->
    ###* Menu that collapses automatically on small displays.

    Example
    =======

    ```html
    <nav cradmin-legacy-menu class="cradmin-legacy-menu">
      <div class="cradmin-legacy-menu-mobileheader">
        <a href="#" role="button"
            class="cradmin-legacy-menu-mobiletoggle"
            ng-click="cradminMenuTogglePressed()"
            ng-class="{'cradmin-legacy-menu-mobile-toggle-button-expanded': cradminMenuDisplay}"
            aria-pressed="{{ getAriaPressed() }}">
          Menu
        </a>
      </div>
      <div class="cradmin-legacy-menu-content"
          ng-class="{'cradmin-legacy-menu-content-display': cradminMenuDisplay}">
        <ul>
          <li><a href="#">Menu item 1</a></li>
          <li><a href="#">Menu item 2</a></li>
        </ul>
      </div>
    </nav>
    ```

    Design notes
    ============

    The example uses css classes provided by the default cradmin CSS, but
    you specify all classes yourself, so you can easily provide your own
    css classes and still use the directive.
    ###

    return {
      scope: true

      controller: ($scope, cradminLegacyPagePreview) ->
        $scope.cradminMenuDisplay = false
        $scope.cradminMenuTogglePressed = ->
          $scope.cradminMenuDisplay = !$scope.cradminMenuDisplay

        $scope.getAriaPressed = ->
          if $scope.cradminMenuDisplay
            return 'true'
          else
            return 'false'

        @close = ->
          $scope.cradminMenuDisplay = false
          $scope.$apply()

        return
    }
])


.directive('cradminLegacyMenuAutodetectOverflowY', [
  'cradminLegacyWindowDimensions'
  (cradminLegacyWindowDimensions) ->
    ###*
    ###
    return {
      require: '?cradminLegacyMenu'

      controller: ($scope) ->
        $scope.onWindowResize = (newWindowDimensions) ->
          $scope.setOrUnsetOverflowYClass()

        $scope.setOrUnsetOverflowYClass = ->
          menuDomElement = $scope.menuElement?[0]
          if menuDomElement?
            if menuDomElement.clientHeight < menuDomElement.scrollHeight
              $scope.menuElement.addClass($scope.overflowYClass)
            else
              $scope.menuElement.removeClass($scope.overflowYClass)

        disableInitialWatcher = $scope.$watch(
          ->
            if $scope.menuElement?[0]?
              return true
            else
              return false
          , (newValue) ->
            if newValue
              $scope.setOrUnsetOverflowYClass()
              disableInitialWatcher()
        )

        return

      link: ($scope, element, attrs) ->
        $scope.overflowYClass = attrs.cradminLegacyMenuAutodetectOverflowY
        $scope.menuElement = element

        cradminLegacyWindowDimensions.register $scope
        $scope.$on '$destroy', ->
          cradminLegacyWindowDimensions.unregister $scope
        return
    }
])

.directive('cradminLegacyMenuCloseOnClick', [
  ->
    ###* Directive that you can put on menu links to automatically close the
    menu on click.
    ###

    return {
      require: '^^cradminLegacyMenu'

      link: (scope, element, attrs, cradminLegacyMenuCtrl) ->
        element.on 'click', ->
          cradminLegacyMenuCtrl.close()
          return
        return
    }
])
