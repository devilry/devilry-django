angular.module('cradminLegacy.imagepreview', [])

.directive 'cradminLegacyImagePreview', ->
  ###
  A directive that shows a preview when an image field changes
  value.

  Components:
    - A wrapper (typically a DIV) using this directive (``cradmin-legacy-image-preview``)
    - An IMG element using the ``cradmin-legacy-image-preview-img`` directive. This is
      needed even if we have no initial image.
    - A file input field using the ``cradmin-legacy-image-preview-filefield`` directive.

  Example:

    <div cradmin-legacy-image-preview>
      <img cradmin-legacy-image-preview-img>
      <input type="file" name="myfile" cradmin-legacy-image-preview-filefield>
    </div>
  ###
  controller = ($scope) ->
    @setImg = (imgscope) ->
      $scope.cradminImagePreviewImage = imgscope
    @previewFile = (file) ->
      $scope.cradminImagePreviewImage.previewFile(file)
    return
  return {
    restrict: 'A'
    controller: controller
  }

.directive 'cradminLegacyImagePreviewImg', ->
  onFilePreviewLoaded = ($scope, srcData) ->
    $scope.element.attr('height', '')  # Unset height to avoid stretching
    $scope.element[0].src = srcData
    $scope.element.removeClass('ng-hide')

  controller = ($scope) ->
    $scope.previewFile = (file) ->
      reader = new FileReader()
      reader.onload = (evt) ->
        onFilePreviewLoaded($scope, evt.target.result)
      reader.readAsDataURL(file)
    return

  link = ($scope, element, attrs, previewCtrl) ->
    $scope.element = element
    previewCtrl.setImg($scope)
    if not element.attr('src')? or element.attr('src') == ''
      element.addClass('ng-hide')
    return

  return {
    require: '^cradminLegacyImagePreview'
    restrict: 'A'
    scope: {}
    controller: controller
    link: link
  }

.directive 'cradminLegacyImagePreviewFilefield', ->
  link = ($scope, element, attrs, previewCtrl) ->
    $scope.previewCtrl = previewCtrl
    $scope.element = element
    $scope.wrapperelement = element.parent()
    element.bind 'change', (evt) ->
      if evt.target.files?
        file = evt.target.files[0]
        $scope.previewCtrl.previewFile(file)
    element.bind 'mouseover', ->
      $scope.wrapperelement.addClass('cradmin-legacy-filewidget-field-and-overlay-wrapper-hover')
    element.bind 'mouseleave', ->
      $scope.wrapperelement.removeClass('cradmin-legacy-filewidget-field-and-overlay-wrapper-hover')
    return

  return {
    require: '^cradminLegacyImagePreview'
    restrict: 'A'
    scope: {}
    link: link
  }
