describe 'cradminLegacyImagePreviewImg', ->
  $compile = null
  $rootScope = null
  beforeEach(module('cradminLegacy.imagepreview'))

  # Store references to $rootScope and $compile
  # so they are available to all tests in this describe block
  beforeEach inject((_$compile_, _$rootScope_) ->
    # The injector unwraps the underscores (_) from around the parameter names when matching
    $compile = _$compile_
    $rootScope = _$rootScope_
  )

  it 'should hide IMG if no src', ->
    scope = {}
    html = """
    <div cradmin-legacy-image-preview>
      <img cradmin-legacy-image-preview-img>
      <input type="file" name="myfile" cradmin-legacy-image-preview-filefield>
    </div>
    """
    element = $compile(html)($rootScope)
    $rootScope.$digest()
    expect(element.find('img').hasClass('ng-hide')).toBe(true)

  it 'should show IMG if src', ->
    scope = {}
    html = """
    <div cradmin-legacy-image-preview>
      <img cradmin-legacy-image-preview-img src="https://upload.wikimedia.org/wikipedia/commons/b/ba/Crystal_Clear_app_tux.png?download">
      <input type="file" name="myfile" cradmin-legacy-image-preview-filefield>
    </div>
    """
    element = $compile(html)($rootScope)
    $rootScope.$digest()
    expect(element.find('img').hasClass('ng-hide')).toBe(false)
