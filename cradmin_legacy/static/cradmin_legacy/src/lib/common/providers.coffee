angular.module('cradminLegacy.providers', [])


.provider 'cradminLegacyWindowDimensions', ->
  ###* Provider that makes it easy to listen for window resize.

  How it works
  ============
  You register a ``scope`` with the provider. Each time the window
  is resized, the provider will call ``scope.onWindowResize()``.
  The provider uses a ``300ms`` timeout before it triggers a
  resize, so your ``onWindowResize`` method will not be flooded
  with every pixel change.

  Example
  =======

  ```coffeescript
  mymodule.directive('myDirective', [
    'cradminLegacyWindowDimensions'
    (cradminLegacyWindowDimensions) ->
      return {
        controller: ($scope) ->
          $scope.onWindowResize = (newWindowDimensions) ->
            console.log 'Window was resized to', newWindowDimensions
          return

        link: ($scope, element, attrs) ->
          cradminLegacyWindowDimensions.register $scope
          $scope.$on '$destroy', ->
            cradminLegacyWindowDimensions.unregister $scope
          return
      }
  ])
  ```
  ###
  class WindowDimensionsProvider
    constructor: ($window, @timeout) ->
      @mainWindow = angular.element($window)
      @deviceMinWidths = {
        tablet: 768  # Bootstrap @screen-sm-min
        mediumDesktop: 992  # Bootstrap @screen-md-min
        largeDesktop: 1200  # Boostrap @screen-lg-min
      }
      @windowDimensions = @_getWindowDimensions()
      @applyResizeTimer = null
      @applyResizeTimerTimeoutMs = 300
      @listeningScopes = []

    _triggerResizeEventsForScope: (scope) ->
      scope.onWindowResize(@windowDimensions)

    register: (scope) ->
      scopeIndex = @listeningScopes.indexOf(scope)
      if scopeIndex != -1
        console.error(
          'Trying to register a scope that is already registered with ' +
          'cradminLegacyWindowDimensions. Scope:', scope)
        return
      if @listeningScopes.length < 1
        @mainWindow.bind 'resize', @_onWindowResize
      @listeningScopes.push(scope)

    unregister: (scope) ->
      scopeIndex = @listeningScopes.indexOf(scope)
      if scopeIndex == -1
        console.error(
          'Trying to unregister a scope that is not registered with ' +
          'cradminLegacyWindowDimensions. Scope:', scope)
      @listeningScopes.splice(scopeIndex, 1)
      if @listeningScopes.length < 1
        @mainWindow.unbind 'resize', @_onWindowResize

    _getWindowDimensions: ->
      return {
        height: @mainWindow.height()
        width: @mainWindow.width()
      }

    getDeviceFromWindowDimensions: (windowDimensions) ->
      if windowDimensions < @deviceMinWidths.tablet
        return 'phone'
      else if windowDimensions < @deviceMinWidths.mediumDesktop
        return 'tablet'
      else if windowDimensions < @deviceMinWidths.largeDesktop
        return 'medium-desktop'
      else
        return 'large-desktop'

    _updateWindowDimensions: (newWindowDimensions) ->
      @windowDimensions = newWindowDimensions
      @_onWindowDimensionsChange()

    _setWindowDimensions: ->
      newWindowDimensions = @_getWindowDimensions()
      if not angular.equals(newWindowDimensions, @windowDimensions)
        @_updateWindowDimensions(newWindowDimensions)

    _onWindowDimensionsChange: ->
      for scope in @listeningScopes
        @_triggerResizeEventsForScope(scope)

    triggerWindowResizeEvent: ->
      @_onWindowDimensionsChange()

    _onWindowResize: =>
      @timeout.cancel(@applyResizeTimer)

      # Use timeout to avoid triggering change for each pixel changed
      @applyResizeTimer = @timeout =>
        @_setWindowDimensions()
      , @applyResizeTimerTimeoutMs

  @$get = (['$window', '$timeout', ($window, $timeout) ->
    return new WindowDimensionsProvider($window, $timeout)
  ])

  return @


.provider 'cradminLegacyWindowScrollTop', ->
  ###* Provider that makes it easy to listen for scrolling on the main window.

  How it works
  ============
  You register a ``scope`` with the provider. Each time the window
  is scrolled, the provider will call ``scope.onWindowScrollTop()``.
  The provider uses a ``100ms`` timeout before it triggers a
  resize, so your ``onWindowScrollTop`` method will not be flooded
  with every pixel change.

  Example
  =======

  ```coffeescript
  mymodule.directive('myDirective', [
    'cradminLegacyWindowScrollTop'
    (cradminLegacyWindowScrollTop) ->
      return {
        controller: ($scope) ->
          $scope.onWindowScrollTop = (newTopPosition) ->
            console.log 'Window was scrolled to', newTopPosition
          return

        link: ($scope, element, attrs) ->
          cradminLegacyWindowScrollTop.register $scope
          $scope.$on '$destroy', ->
            cradminLegacyWindowScrollTop.unregister $scope
          return
      }
  ])
  ```
  ###
  class WindowScrollProvider
    constructor: ($window, @timeout) ->
      @mainWindow = angular.element($window)
      @scrollTopPosition = @_getScrollTopPosition()
      @applyScrollTimer = null
      @applyScrollTimerTimeoutMs = 50
      @listeningScopes = []
      @isScrolling = false

    register: (scope) ->
      scopeIndex = @listeningScopes.indexOf(scope)
      if scopeIndex != -1
        console.error(
          'Trying to register a scope that is already registered with ' +
          'cradminLegacyWindowScrollTop. Scope:', scope)
        return
      if @listeningScopes.length < 1
        @mainWindow.bind 'scroll', @_onScroll
      @listeningScopes.push(scope)
      scope.onWindowScrollTop(@scrollTopPosition, true)

    unregister: (scope) ->
      scopeIndex = @listeningScopes.indexOf(scope)
      if scopeIndex == -1
        console.error(
          'Trying to unregister a scope that is not registered with ' +
          'cradminLegacyWindowScrollTop. Scope:', scope)
      @listeningScopes.splice(scopeIndex, 1)
      if @listeningScopes.length < 1
        @mainWindow.unbind 'scroll', @_onScroll

    _getScrollTopPosition: ->
      return @mainWindow.scrollTop()

    _setScrollTopPosition: ->
      scrollTopPosition = @_getScrollTopPosition()
      @scrollTopPosition = scrollTopPosition
      @_onScrollTopChange()

    _onScrollTopChange: ->
      for scope in @listeningScopes
        scope.onWindowScrollTop(@scrollTopPosition)

    _notifyScrollStarted: ->
      scrollTopPosition = @_getScrollTopPosition()
      if scrollTopPosition != @scrollTopPosition
        for scope in @listeningScopes
          if scope.onWindowScrollTopStart?
            scope.onWindowScrollTopStart()

    _onScroll: =>
      @timeout.cancel(@applyScrollTimer)
      if not @isScrolling
        @_notifyScrollStarted()
      @isScrolling = true

      # Use timeout to avoid triggering change for each pixel changed
      @applyScrollTimer = @timeout =>
        @_setScrollTopPosition()
        @isScrolling = false
      , @applyScrollTimerTimeoutMs

  @$get = (['$window', '$timeout', ($window, $timeout) ->
    return new WindowScrollProvider($window, $timeout)
  ])

  return @
