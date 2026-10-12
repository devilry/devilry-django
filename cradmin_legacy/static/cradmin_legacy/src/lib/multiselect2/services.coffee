angular.module('cradminLegacy.multiselect2.services', [])


.factory 'cradminLegacyMultiselect2Coordinator', ->
  ###
  Coordinates between cradminLegacyMultiselect2Select
  and cradminLegacyMultiselect2Target.
  ###
  class Coordinator
    constructor: ->
      @targets = {}
      @selectScopes = {}

    registerTarget: (targetDomId, targetScope) ->
      @targets[targetDomId] = targetScope

    unregisterTarget: (targetDomId, targetScope) ->
      delete @targets[targetDomId]

    __getTargetScope: (targetDomId) ->
      targetScope = @targets[targetDomId]
      if not targetScope?
        throw Error("No target with ID '#{targetDomId}' registered with cradminLegacyMultiselect2Coordinator.")
      return targetScope

    targetScopeExists: (targetDomId) ->
      return @targets[targetDomId]?

    select: (selectScope) ->
      targetScope = @__getTargetScope(selectScope.getTargetDomId())
      if not targetScope.isSelected(selectScope)
        targetScope.select(selectScope)
        selectScope.markAsSelected()

    onDeselect: (selectButtonDomId) ->
      $selectElement = angular.element('#' + selectButtonDomId)
      if $selectElement?
        selectScope = $selectElement.isolateScope()
        if selectScope?
          selectScope.onDeselect()
      # If we can not find the selectedElement or the scope, that just means
      # that the item has been removed from the body due to filtering, paging,
      # searching etc.

    isSelected: (targetDomId, selectScope) ->
      targetScope = @__getTargetScope(targetDomId)
      return targetScope.isSelected(selectScope)

    registerSelectScope: (selectScope) ->
      if @selectScopes[selectScope.getTargetDomId()]?.map[selectScope.getDomId()]?
        console.log "selectScope with id=#{selectScope.getDomId()} is already " +
            "registered for target #{selectScope.getTargetDomId()}"
#        throw Error("selectScope with id=#{selectScope.getDomId()} is already " +
#            "registered for target #{selectScope.getTargetDomId()}")
      else
        if not @selectScopes[selectScope.getTargetDomId()]?
          @selectScopes[selectScope.getTargetDomId()] = {
            map: {}  # Maps selectScope.getDomId() to index in the list (below)
            list: []  # List of selectScopes in the order they where added
          }
        listIndex = @selectScopes[selectScope.getTargetDomId()].list.push(selectScope)
        @selectScopes[selectScope.getTargetDomId()].map[selectScope.getDomId()] = listIndex

    unregisterSelectScope: (selectScope) ->
      if @selectScopes[selectScope.getTargetDomId()]?.map[selectScope.getDomId()]?
        listIndex = @selectScopes[selectScope.getTargetDomId()][selectScope.getDomId()]
        @selectScopes[selectScope.getTargetDomId()].list.splice(listIndex, 1)
        delete @selectScopes[selectScope.getTargetDomId()].map[selectScope.getDomId()]
      else
        throw Error("selectScope with id=#{selectScope.getDomId()} is not " +
            "registered for target #{selectScope.getTargetDomId()}")

    selectAll: (targetDomId) ->
      for selectScope in @selectScopes[targetDomId].list
        @select(selectScope)

  return new Coordinator()
