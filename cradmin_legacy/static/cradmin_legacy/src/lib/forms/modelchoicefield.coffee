angular.module('cradminLegacy.forms.modelchoicefield', [])

.provider 'cradminLegacyModelChoiceFieldCoordinator', ->
  class ModelChoiceFieldOverlay
    constructor: (@cradminLegacyWindowDimensions) ->
      @modelChoiceFieldIframeWrapper = null
      @bodyContentWrapperElement = angular.element('#cradmin_legacy_bodycontentwrapper')
      @bodyElement = angular.element('body')
    registerModeChoiceFieldIframeWrapper: (modelChoiceFieldIframeWrapper) ->
      @modelChoiceFieldIframeWrapper = modelChoiceFieldIframeWrapper
    onChangeValueBegin: (fieldWrapperScope) ->
      @modelChoiceFieldIframeWrapper.onChangeValueBegin(fieldWrapperScope)
    addBodyContentWrapperClass: (cssclass) ->
      @bodyContentWrapperElement.addClass(cssclass)
    removeBodyContentWrapperClass: (cssclass) ->
      @bodyContentWrapperElement.removeClass(cssclass)
    disableBodyScrolling: ->
      @bodyElement.addClass('cradmin-legacy-noscroll')
    enableBodyScrolling: ->
      @bodyElement.removeClass('cradmin-legacy-noscroll')
      @cradminLegacyWindowDimensions.triggerWindowResizeEvent()


  @$get = (['cradminLegacyWindowDimensions', (cradminLegacyWindowDimensions) ->
    return new ModelChoiceFieldOverlay(cradminLegacyWindowDimensions)
  ])

  return @


.directive('cradminLegacyModelChoiceFieldIframeWrapper', [
  '$window', '$timeout', 'cradminLegacyModelChoiceFieldCoordinator', 'cradminLegacyWindowDimensions'
  ($window, $timeout, cradminLegacyModelChoiceFieldCoordinator, cradminLegacyWindowDimensions) ->
    return {
      restrict: 'A'
      scope: {}

      controller: ($scope) ->
        $scope.origin = "#{window.location.protocol}//#{window.location.host}"
        $scope.bodyElement = angular.element($window.document.body)
        cradminLegacyModelChoiceFieldCoordinator.registerModeChoiceFieldIframeWrapper(this)

        @setIframe = (iframeScope) ->
          $scope.iframeScope = iframeScope

        @_setField = (fieldScope) ->
          $scope.fieldScope = fieldScope

        @_setPreviewElement = (previewElementScope) ->
          $scope.previewElementScope = previewElementScope

        @setLoadSpinner = (loadSpinnerScope) ->
          $scope.loadSpinnerScope = loadSpinnerScope

        @setIframeWrapperInner = (iframeInnerScope) ->
          $scope.iframeInnerScope = iframeInnerScope

        @onChangeValueBegin = (fieldWrapperScope) ->
          @_setField(fieldWrapperScope.fieldScope)
          @_setPreviewElement(fieldWrapperScope.previewElementScope)
          $scope.iframeScope.beforeShowingIframe(fieldWrapperScope.iframeSrc)
          $scope.show()

        @onIframeLoadBegin = ->
          $scope.loadSpinnerScope.show()

        @onIframeLoaded = ->
          $scope.iframeInnerScope.show()
          $scope.loadSpinnerScope.hide()

        $scope.onChangeValue = (event) ->
          if event.origin != $scope.origin
            console.error "Message origin '#{event.origin}' does not match current origin '#{$scope.origin}'."
            return
          data = angular.fromJson(event.data)
          if $scope.fieldScope.fieldid != data.fieldid
            # console.log "The received message was not for this field " +
            #   "(#{$scope.fieldScope.fieldid}), it was for #{data.fieldid}"
            return
          $scope.fieldScope.setValue(data.value)
          $scope.previewElementScope.setPreviewHtml(data.preview)
          $scope.hide()
          $scope.iframeScope.afterFieldValueChange()

        $window.addEventListener('message', $scope.onChangeValue, false)

        $scope.onWindowResize = (newWindowDimensions) ->
          $scope.iframeScope.setIframeSize()

        $scope.show = ->
          $scope.iframeWrapperElement.addClass('cradmin-legacy-floating-fullsize-iframe-wrapper-show')
          cradminLegacyModelChoiceFieldCoordinator.disableBodyScrolling()
          cradminLegacyModelChoiceFieldCoordinator.addBodyContentWrapperClass(
            'cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper')
          cradminLegacyModelChoiceFieldCoordinator.addBodyContentWrapperClass(
            'cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper-push')
          cradminLegacyWindowDimensions.register $scope

        $scope.hide = ->
          $scope.iframeWrapperElement.removeClass('cradmin-legacy-floating-fullsize-iframe-wrapper-show')
          cradminLegacyModelChoiceFieldCoordinator.removeBodyContentWrapperClass(
            'cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper')
          cradminLegacyModelChoiceFieldCoordinator.removeBodyContentWrapperClass(
            'cradmin-legacy-floating-fullsize-iframe-bodycontentwrapper-push')
          cradminLegacyModelChoiceFieldCoordinator.enableBodyScrolling()
          $scope.iframeScope.onHide()
          cradminLegacyWindowDimensions.unregister $scope

        @closeIframe = ->
          $scope.hide()

        return

      link: (scope, element, attrs, wrapperCtrl) ->
        scope.iframeWrapperElement = element
        return
    }
])

.directive('cradminLegacyModelChoiceFieldIframeWrapperInner', [
  '$window'
  ($window) ->
    return {
      require: '^^cradminLegacyModelChoiceFieldIframeWrapper'
      restrict: 'A'
      scope: {}

      controller: ($scope) ->
        $scope.scrollToTop = ->
          $scope.element.scrollTop(0)
        $scope.show = ->
          $scope.element.removeClass('ng-hide')
        $scope.hide = ->
          $scope.element.addClass('ng-hide')
        return

      link: (scope, element, attrs, wrapperCtrl) ->
        scope.element = element
        wrapperCtrl.setIframeWrapperInner(scope)
        return
    }
])

.directive 'cradminLegacyModelChoiceFieldIframeClosebutton', ->
  return {
    require: '^cradminLegacyModelChoiceFieldIframeWrapper'
    restrict: 'A'
    scope: {}

    link: (scope, element, attrs, iframeWrapperCtrl) ->
      element.on 'click', (e) ->
        e.preventDefault()
        iframeWrapperCtrl.closeIframe()
      return
  }

.directive 'cradminLegacyModelChoiceFieldLoadSpinner', ->
  return {
    require: '^^cradminLegacyModelChoiceFieldIframeWrapper'
    restrict: 'A'
    scope: {}

    controller: ($scope) ->
      $scope.hide = ->
        $scope.element.addClass('ng-hide')
      $scope.show = ->
        $scope.element.removeClass('ng-hide')

    link: (scope, element, attrs, wrapperCtrl) ->
      scope.element = element
      wrapperCtrl.setLoadSpinner(scope)
      return
  }

.directive('cradminLegacyModelChoiceFieldIframe', [
  '$interval'
  ($interval) ->
    return {
      require: '^cradminLegacyModelChoiceFieldIframeWrapper'
      restrict: 'A'
      scope: {}

      controller: ($scope) ->
        scrollHeightInterval = null
        currentScrollHeight = 0

        getIframeWindow = ->
          return $scope.element.contents()

        getIframeDocument = ->
          return getIframeWindow()[0]

        getIframeScrollHeight = ->
          iframeDocument = getIframeDocument()
          if iframeDocument?.body?
            return iframeDocument.body.scrollHeight
          else
            return 0

        resizeIfScrollHeightChanges = ->
          newScrollHeight = getIframeScrollHeight()
          if newScrollHeight != currentScrollHeight
            currentScrollHeight = newScrollHeight
            $scope.setIframeSize()

        startScrollHeightInterval = ->
          if not scrollHeightInterval?
            scrollHeightInterval = $interval(resizeIfScrollHeightChanges, 500)

        stopScrollHeightInterval = ->
          if scrollHeightInterval?
            $interval.cancel(scrollHeightInterval)
            scrollHeightInterval = null

        $scope.onHide = ->
          stopScrollHeightInterval()

        $scope.afterFieldValueChange = ->
          # NOTE: We may want to add an option that clears the view
          #       after selecting a value.
          # $scope.element.attr('src', '')
          stopScrollHeightInterval()

        $scope.beforeShowingIframe = (iframeSrc) ->
          currentSrc = $scope.element.attr('src')
          if not currentSrc? or currentSrc == '' or currentSrc != iframeSrc
            $scope.loadedSrc = currentSrc
            $scope.wrapperCtrl.onIframeLoadBegin()
            $scope.resetIframeSize()
            $scope.element.attr('src', iframeSrc)
          startScrollHeightInterval()

        $scope.setIframeSize = ->
#          iframeDocument = getIframeDocument()
#          if iframeDocument?.body?
#            iframeBodyHeight = iframeDocument.body.offsetHeight
#            $scope.element.height(iframeBodyHeight)

        $scope.resetIframeSize = ->
#          $scope.element.height('40px')

        return

      link: (scope, element, attrs, wrapperCtrl) ->
        scope.element = element
        scope.wrapperCtrl = wrapperCtrl
        wrapperCtrl.setIframe(scope)
        scope.element.on 'load', ->
          wrapperCtrl.onIframeLoaded()
          scope.setIframeSize()
        return
    }
])


.directive('cradminLegacyModelChoiceFieldWrapper', [
  'cradminLegacyModelChoiceFieldCoordinator'
  (cradminLegacyModelChoiceFieldCoordinator) ->
    return {
      restrict: 'A'
      scope: {
        iframeSrc: '@cradminLegacyModelChoiceFieldWrapper'
      }

      controller: ($scope) ->
        @setField = (fieldScope) ->
          $scope.fieldScope = fieldScope

        @setPreviewElement = (previewElementScope) ->
          $scope.previewElementScope = previewElementScope

        @onChangeValueBegin = ->
          cradminLegacyModelChoiceFieldCoordinator.onChangeValueBegin($scope)

        return
    }
])


.directive('cradminLegacyModelChoiceFieldInput', [
  'cradminLegacyModelChoiceFieldCoordinator',
  (cradminLegacyModelChoiceFieldCoordinator) ->
    return {
      require: '^^cradminLegacyModelChoiceFieldWrapper'
      restrict: 'A'
      scope: {}

      controller: ($scope) ->
        $scope.setValue = (value) ->
          $scope.inputElement.val(value)
        return

      link: (scope, element, attrs, wrapperCtrl) ->
        scope.inputElement = element
        scope.fieldid = attrs['id']
        wrapperCtrl.setField(scope)
        return
    }
])

.directive('cradminLegacyModelChoiceFieldPreview', [
  'cradminLegacyModelChoiceFieldCoordinator',
  (cradminLegacyModelChoiceFieldCoordinator) ->
    return {
      require: '^^cradminLegacyModelChoiceFieldWrapper'
      restrict: 'A'
      scope: {}

      controller: ($scope) ->
        $scope.setPreviewHtml = (previewHtml) ->
          $scope.previewElement.html(previewHtml)
        return

      link: (scope, element, attrs, wrapperCtrl) ->
        scope.previewElement = element
        wrapperCtrl.setPreviewElement(scope)
        return
    }
])

.directive('cradminLegacyModelChoiceFieldChangebeginButton', [
  'cradminLegacyModelChoiceFieldCoordinator',
  (cradminLegacyModelChoiceFieldCoordinator) ->
    return {
      require: '^^cradminLegacyModelChoiceFieldWrapper'
      restrict: 'A'
      scope: {}

      link: (scope, element, attrs, wrapperCtrl) ->
        element.on 'click', (e) ->
          e.preventDefault()
          wrapperCtrl.onChangeValueBegin()
        return
    }
])
