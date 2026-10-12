angular.module('cradminLegacy.loadmorepager.services', [])


.factory 'cradminLegacyLoadmorepagerCoordinator', ->
  ###
  Coordinates between cradminLegacyLoadMorePager directives.
  ###
  class Coordinator
    constructor: ->
      @targets = {}

    registerPager: (targetDomId, pagerScope) ->
      if not @targets[targetDomId]?
        @targets[targetDomId] = {}
      @targets[targetDomId][pagerScope.getNextPageNumber()] = pagerScope

    unregisterPager: (targetDomId, pagerScope) ->
      del @targets[targetDomId][pagerScope.getNextPageNumber()]

    __getPagerScope: (targetDomId, nextPageNumber) ->
      target = @targets[targetDomId]
      if not target?
        throw Error("No target with ID '#{targetDomId}' registered with cradminLegacyLoadmorepagerCoordinator.")
      pagerScope = target[nextPageNumber]
      if not pagerScope?
        throw Error("No pagerScope for targetDomId='#{targetDomId}' and nextPageNumber=#{nextPageNumber} " +
          "registered with cradminLegacyLoadmorepagerCoordinator.")
      return pagerScope

  return new Coordinator()
