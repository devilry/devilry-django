angular.module('cradminLegacy.backgroundreplace_element.providers', [])


.provider 'cradminLegacyBgReplaceElement', ->
  ###
  Makes a request to a an URL, and replaces or extends a DOM element
  on the current page with the same DOM element within
  the requested URL.

  Can be used for many things, such as:

  - Infinite scroll (append content from ``?page=<pagenumber>``).
  - Live filtering (replace the filtered list when a filter changes).
  ###
  class BgReplace
    constructor: ($http, $compile, $rootScope) ->
      @http = $http
      @compile = $compile
      @rootScope = $rootScope

    loadUrlAndExtractRemoteElementHtml: (options, onSuccess) ->
      url = options.parameters.url
      parsedUrl = URI(url)
      parsedUrl.setSearch("cradmin-bgreplaced", 'true')
      options.parameters.url = parsedUrl.toString()

      @http(options.parameters).then((response) ->
        html = response.data
        $remoteHtmlDocument = angular.element(html)
        remoteElement = $remoteHtmlDocument.find(options.remoteElementSelector)
        remoteElementInnerHtml = remoteElement.html()
        onSuccess(remoteElementInnerHtml, $remoteHtmlDocument)
      , (response) ->
        if options.onFinish?
          options.onFinish()
        if options.onHttpError?
          options.onHttpError(response)
        else
          console?.error? "Failed to load", options.parameters
      )

    __removeElement: ($element) ->
      for childDomElement in $element.children()
        $childElement = angular.element(childDomElement)
        @__removeElement($childElement)
      isolatedScope = $element.isolateScope()
      if isolatedScope?
        isolatedScope.$destroy()
      $element.remove()

    __removeAllChildren: ($element) ->
      # We can not just use $element.empty() because that does not call
      # $destroy() on the isolated scopes, so we remove the elements with
      # a recursive method and removes the deepest children first while
      # calling $destroy() on all the isolated scopes we find.
      for childDomElement in $element.children()
        $childElement = angular.element(childDomElement)
        @__removeElement($childElement)

    updateTargetElement: (options, remoteElementInnerHtml, $remoteHtmlDocument) =>
      if options.replace
        @__removeAllChildren(options.targetElement)
      $compile = @compile
      linkingFunction = $compile(remoteElementInnerHtml)
      loadedElement = linkingFunction(options.$scope)

      options.targetElement.append(loadedElement)
      if options.onFinish?
        options.onFinish()
      if options.onSuccess
        options.onSuccess($remoteHtmlDocument)

      # Broadcast an event on the $rootScope, to allow code that need
      # to do something when changes to the DOM occur. The event handlers
      # get ``options`` as input, and they will typically be interested in
      # checking if the DOM elements they control are children of ``options.targetElement``,
      # and they may want to consider ``options.replace``.
      @rootScope.$broadcast 'cradminLegacyBgReplaceElementEvent', options

    load: (options) ->
      me = @
      @loadUrlAndExtractRemoteElementHtml options, (remoteElementInnerHtml, $remoteHtmlDocument) ->
        me.updateTargetElement(options, remoteElementInnerHtml, $remoteHtmlDocument)

  @$get = (['$http', '$compile', '$rootScope', ($http, $compile, $rootScope) ->
    return new BgReplace($http, $compile, $rootScope)
  ])

  return @
