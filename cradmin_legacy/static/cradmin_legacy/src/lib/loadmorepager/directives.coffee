angular.module('cradminLegacy.loadmorepager.directives', [])


.directive('cradminLegacyLoadMorePager', [
  '$timeout', 'cradminLegacyBgReplaceElement', 'cradminLegacyLoadmorepagerCoordinator'
  ($timeout, cradminLegacyBgReplaceElement, cradminLegacyLoadmorepagerCoordinator) ->

    pagerWrapperCssSelector = '.cradmin-legacy-loadmorepager'

    return {
      restrict: 'A',
      scope: true

      controller: ($scope, $element) ->
        $scope.loadmorePagerIsLoading = false

        $scope.getNextPageNumber = ->
          return $scope.loadmorePagerOptions.nextPageNumber

        $scope.pagerLoad = (options) ->
          options = angular.extend({}, $scope.loadmorePagerOptions, options)
          $scope.loadmorePagerIsLoading = true
          $targetElement = angular.element(options.targetElementCssSelector)

          replaceMode = false
          nextPageUrl = URI()
          updatedQueryDictAttributes = {}
          if options.mode == "reloadPageOneOnLoad"
            replaceMode = true
          else if options.mode == "loadAllOnClick"
            replaceMode = true
            nextPageUrl.setSearch('disablePaging', "true")
          else
            nextPageUrl.setSearch(options.pageQueryStringAttribute, $scope.getNextPageNumber())

          cradminLegacyBgReplaceElement.load({
            parameters: {
              method: 'GET'
              url: nextPageUrl.toString()
            },
            remoteElementSelector: options.targetElementCssSelector
            targetElement: $targetElement
            $scope: $scope
            replace: replaceMode
            onHttpError: (response) ->
              console?.error? 'ERROR loading page', response
            onSuccess: ($remoteHtmlDocument) ->
#              console.log 'Success!', $remoteHtmlDocument
#              if $remoteHtmlDocument
              if options.mode == "reloadPageOneOnLoad"
                $targetElement.removeClass('cradmin-legacy-loadmorepager-target-reloading-page1')
              else
                $element.addClass('cradmin-legacy-loadmorepager-hidden')

              if options.onSuccess?
                options.onSuccess()

            onFinish: ->
              $scope.loadmorePagerIsLoading = false
          })

        return

      link: ($scope, $element, attributes) ->
        $scope.loadmorePagerOptions = {
          pageQueryStringAttribute: "page"
          mode: "loadMoreOnClick"
        }
        if attributes.cradminLegacyLoadMorePager? and attributes.cradminLegacyLoadMorePager != ''
          angular.extend($scope.loadmorePagerOptions, angular.fromJson(attributes.cradminLegacyLoadMorePager))

        if not $scope.loadmorePagerOptions.targetElementCssSelector?
          throw Error('Missing required option: targetElementCssSelector')

        domId = $element.attr('id')
        cradminLegacyLoadmorepagerCoordinator.registerPager(domId, $scope)
        $scope.$on "$destroy", ->
          cradminLegacyLoadmorepagerCoordinator.unregisterPager(domId, $scope)

        if $scope.loadmorePagerOptions.mode == "reloadPageOneOnLoad"
          # We assume the initial digest cycle does not take more than 500ms
          $timeout(->
            $scope.pagerLoad()
          500)

        return
    }
])
