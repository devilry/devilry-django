angular.module('cradminLegacy.multiselect2.directives', [])


.directive('cradminLegacyMultiselect2Target', [
  'cradminLegacyMultiselect2Coordinator', '$window'
  (cradminLegacyMultiselect2Coordinator, $window) ->
    return {
      restrict: 'A'
      scope: true

      controller: ($scope, $element) ->
        domId = $element.attr('id')
        $scope.selectedItemsScope = null

        if not domId?
          throw Error('Elements using cradmin-legacy-multiselect2-target must have an id.')

        cradminLegacyMultiselect2Coordinator.registerTarget(domId, $scope)
        $scope.$on "$destroy", ->
          cradminLegacyMultiselect2Coordinator.unregisterTarget(domId)

        $scope.select = (selectScope) ->
          ###
          Called by cradminLegacyMultiselect2Select via
          cradminLegacyMultiselect2Coordinator when an item is selected.

          Calls ``cradminLegacyMultiselect2TargetSelectedItems.select()``.
          ###
          $scope.selectedItemsScope.select(selectScope)
          if not $scope.$$phase
            $scope.$apply()

        $scope.isSelected = (selectScope) ->
          ###
          Called by cradminLegacyMultiselect2Select via
          cradminLegacyMultiselect2Coordinator to check if the item is selected.
          ###
          $scope.selectedItemsScope.isSelected(selectScope)

        $scope.hasItems = ->
          return $scope.selectedItemsScope?.hasItems()

        @setSelectedItemsScope = (selectedItemsScope) ->
          $scope.selectedItemsScope = selectedItemsScope

        @getSelectedItemsScope = ->
          return $scope.selectedItemsScope

        return

      link: ($scope, $element, attributes) ->
        $scope.options = {
          updateFormActionToWindowLocation: false
        }
        if attributes.cradminLegacyMultiselect2Target != ''
          options = angular.fromJson(attributes.cradminLegacyMultiselect2Target)
          angular.merge($scope.options, options)
        $element.on 'submit', (e) ->
          if $scope.options.updateFormActionToWindowLocation
            $element.attr('action', $window.location.href)
        return
    }
])


.directive('cradminLegacyMultiselect2TargetSelectedItems', [
  '$compile', 'cradminLegacyMultiselect2Coordinator',
  ($compile, cradminLegacyMultiselect2Coordinator) ->

    selectedItemCssClass = 'cradmin-legacy-multiselect2-target-selected-item'

    return {
      restrict: 'A'
      require: '^cradminLegacyMultiselect2Target'
      scope: true

      controller: ($scope, $element) ->
        $scope.selectedItemsCount = 0
        $scope.selectedItemsData = {}

        $scope.select = (selectScope) ->
          previewHtml = selectScope.getPreviewHtml()
          selectButtonDomId = selectScope.getDomId()
          html = "<div id='#{selectButtonDomId}_selected_item'" +
            "cradmin-legacy-multiselect2-target-selected-item='#{selectButtonDomId}' " +
            "class='#{selectedItemCssClass}'>" +
            "#{previewHtml}</div>"
          linkingFunction = $compile(html)
          loadedElement = linkingFunction($scope)
          angular.element(loadedElement).appendTo($element)
          $scope.selectedItemsCount += 1
          $scope.selectedItemsData[selectButtonDomId] = selectScope.getCustomData()

        $scope.deselectSelectedItem = (selectedItemScope) ->
          $scope.selectedItemsCount -= 1
          delete $scope.selectedItemsData[selectedItemScope.selectButtonDomId]
          cradminLegacyMultiselect2Coordinator.onDeselect(
            selectedItemScope.selectButtonDomId)

        $scope.isSelected = (selectScope) ->
          selectButtonDomId = selectScope.getDomId()
          return $element.find("##{selectButtonDomId}_selected_item").length > 0

        $scope.hasItems = ->
          return $scope.selectedItemsCount > 0

        $scope.getItemsCustomDataList = ->
          customDataList = []
          for selectButtonDomId, customData of $scope.selectedItemsData
            customDataList.push(customData)
          return customDataList

        return

      link: ($scope, $element, attributes, targetCtrl) ->
        targetCtrl.setSelectedItemsScope($scope)
        return
    }
])


.directive('cradminLegacyMultiselect2TargetSelectedItem', [
  'cradminLegacyMultiselect2Coordinator',
  (cradminLegacyMultiselect2Coordinator) ->
    return {
      restrict: 'A'
      scope: true

      controller: ($scope, $element) ->
        $scope.deselect = ->
          $element.remove()
          $scope.deselectSelectedItem($scope)
          return

        return

      link: ($scope, $element, attributes) ->
        $scope.selectButtonDomId = attributes.cradminLegacyMultiselect2TargetSelectedItem
        return
    }
])


.directive('cradminLegacyMultiselect2Select', [
  '$rootScope', 'cradminLegacyMultiselect2Coordinator',
  ($rootScope, cradminLegacyMultiselect2Coordinator) ->

    itemWrapperSelectedCssClass = 'cradmin-legacy-multiselect2-item-wrapper-selected'

    return {
      restrict: 'A',
      scope: {
        options: '=cradminLegacyMultiselect2Select'
      }

      controller: ($scope, $element) ->
        $scope.getPreviewHtml = ->
          $containerElement = $element.parents($scope.options.preview_container_css_selector)
          $previewElement = $containerElement.find($scope.options.preview_css_selector)
          return $previewElement.html()

        $scope.getDomId = ->
          return $element.attr('id')

        $scope.getListElementCssSelector = ->
          return $scope.options.listelement_css_selector

        $scope.onDeselect = ->
          ###
          Called by cradminLegacyMultiselect2Coordinator when the item is deselected.
          ###
          $scope.getItemWrapperElement().removeClass(itemWrapperSelectedCssClass)

        $scope.markAsSelected = ->
          $scope.getItemWrapperElement().addClass(itemWrapperSelectedCssClass)

        $scope.getItemWrapperElement = ->
          return $element.closest($scope.options.item_wrapper_css_selector)

        $scope.getTargetDomId = ->
          return $scope.options.target_dom_id

        $scope.getCustomData = ->
          if $scope.options.custom_data?
            return $scope.options.custom_data
          else
            return {}

        unregisterBgReplaceEventHandler = $scope.$on 'cradminLegacyBgReplaceElementEvent', (event, options) ->
          # We only care about this if the replaced element in one of our parent elements
          if $element.closest(options.remoteElementSelector).length > 0
            targetDomId = $scope.options.target_dom_id
            if cradminLegacyMultiselect2Coordinator.isSelected(targetDomId, $scope)
              $scope.markAsSelected()

        cradminLegacyMultiselect2Coordinator.registerSelectScope($scope)
        $scope.$on '$destroy', ->
          unregisterBgReplaceEventHandler()
          cradminLegacyMultiselect2Coordinator.unregisterSelectScope($scope)

        return

      link: ($scope, $element, attributes) ->
        select = ->
          cradminLegacyMultiselect2Coordinator.select($scope)

        if $scope.options.is_selected
          # We need to fall back on a watcher if the targetScope does not exist on load.
          # This happens if the target scope is after the select scope in the body.
          if cradminLegacyMultiselect2Coordinator.targetScopeExists($scope.getTargetDomId())
            select()
          else
            targetScopeExistsWatcherCancel = $scope.$watch(
              ->
                return cradminLegacyMultiselect2Coordinator.targetScopeExists($scope.getTargetDomId())
              , (newValue, oldValue) ->
                if newValue
                  select()
                  targetScopeExistsWatcherCancel()
            )

        $element.on 'click', (e) ->
          e.preventDefault()
          select()

        return
    }
])


.directive('cradminLegacyMultiselect2Selectall', [
  '$rootScope', 'cradminLegacyMultiselect2Coordinator',
  ($rootScope, cradminLegacyMultiselect2Coordinator) ->
    return {
      restrict: 'A',
#      scope: {
#        options: '=cradminLegacyMultiselect2Selectall'
#      }
      scope: true

      controller: ($scope, $element) ->
        return

      link: ($scope, $element, attributes) ->
        $scope.options = angular.fromJson(attributes.cradminLegacyMultiselect2Selectall)
        targetDomId = $scope.options.target_dom_id
        selectAll = ->
          cradminLegacyMultiselect2Coordinator.selectAll(targetDomId)

        $element.on 'click', (e) ->
          e.preventDefault()
          $scope.pagerLoad({
            onSuccess: ->
              selectAll()
          })

        return
    }
])



.directive('cradminLegacyMultiselect2UseThis', [
  '$window'
  ($window) ->
    ###
    The ``cradmin-legacy-multiselect2-use-this`` directive is used to select elements for
    the ``cradmin-legacy-model-choice-field`` directive. You add this directive
    to a button or a-element within an iframe, and this directive will use
    ``window.postMessage`` to send the needed information to the
    ``cradmin-legacy-model-choice-field-wrapper``.

    You may also use this if you create your own custom iframe communication
    receiver directive where a "use this" button within an iframe is needed.

    Example
    =======
    ```
      <button type="button"
              class="btn btn-default"
              cradmin-legacy-multiselect2-use-this='{"fieldid": "id_name"}'>
          Use this
      </button>
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
        value: '<JSON encoded data for the selected items>',
        preview: '<preview HTML for the selected items>'
        <all options provided to the directive>
      }
      ```

    We assume there is a event listener listening for the ``message`` event on
    the message in the parent of the iframe where this was clicked, but no checks
    ensuring this is made.
    ###
    return {
      restrict: 'A'
      require: '^cradminLegacyMultiselect2Target'
      scope: {
        data: '@cradminLegacyMultiselect2UseThis'
      }

      link: ($scope, $element, attributes, targetCtrl) ->
        getSelectedItemsData = ->
          allData = {
            values: []
            preview: ""
          }
          for itemData in targetCtrl.getSelectedItemsScope().getItemsCustomDataList()
            allData.values.push(itemData.value)
            allData.preview += itemData.preview
          return allData

        $element.on 'click', (e) ->
          e.preventDefault()
          data = angular.fromJson($scope.data)
          data.postmessageid = 'cradmin-legacy-use-this'
          selectedItemsData = getSelectedItemsData()
          data.value = angular.toJson(selectedItemsData.values)
          data.preview = selectedItemsData.preview
          $window.parent.postMessage(
            angular.toJson(data),
            window.parent.location.href)

        return
    }
])
