angular.module('cradminLegacy.modal', [])

.directive('cradminLegacyModalWrapper', [
  ->
    ###* Shows a modal window on click.

    Example
    =======

    ```html
    <div cradmin-legacy-modal-wrapper>
      <button ng-click="showModal($event)" type="button">
        Show modal window
      </button>
      <div cradmin-legacy-modal class="cradmin-legacy-modal"
              ng-class="{'cradmin-legacy-modal-visible': modalVisible}">
          <div class="cradmin-legacy-modal-backdrop" ng-click="hideModal()"></div>
          <div class="cradmin-legacy-modal-content">
              <p>Something here</p>
              <button ng-click="hideModal()" type="button">
                Hide modal window
              </button>
          </div>
      </div>
    </div>
    ```
    ###
    return {
      scope: true

      controller: ($scope) ->
        $scope.modalVisible = false
        bodyElement = angular.element('body')

        $scope.showModal = (e) ->
          if e?
            e.preventDefault()
          $scope.modalVisible = true
          bodyElement.addClass('cradmin-legacy-noscroll')
          return

        $scope.hideModal = ->
          $scope.modalVisible = false
          bodyElement.removeClass('cradmin-legacy-noscroll')
          return

        return
    }
])

.directive('cradminLegacyModal', [
  ->
    return {
      require: '^^cradminLegacyModalWrapper'

      link: ($scope, element) ->
        body = angular.element('body')
        element.appendTo(body)
    }
])
