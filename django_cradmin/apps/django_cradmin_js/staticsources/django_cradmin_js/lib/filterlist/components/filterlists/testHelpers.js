export class ChildExposedApiMock {
  constructor () {
    this.loadMoreItemsFromApi = jest.fn()
    this.loadNextPageFromApi = jest.fn()
    this.loadPreviousPageFromApi = jest.fn()
    this.loadSpecificPageFromApi = jest.fn()

    this.selectItem = jest.fn()
    this.selectItems = jest.fn()
    this.deselectItem = jest.fn()
    this.deselectItems = jest.fn()
    this.deselectAllItems = jest.fn()
    this.itemIsSelected = jest.fn()
    this.getIdFromListItemData = jest.fn()

    this.setFilterValue = jest.fn()
    this.getFilterValue = jest.fn()

    this.setSelectMode = jest.fn()
    this.isSingleSelectMode = jest.fn()
    this.isMultiSelectMode = jest.fn()

    this.hasPreviousPaginationPage = jest.fn()
    this.hasNextPaginationPage = jest.fn()
    this.getPaginationPageCount = jest.fn()
    this.getTotalListItemCount = jest.fn()

    this.onChildFocus = jest.fn()
    this.onChildBlur = jest.fn()

    this.disableComponentGroup = jest.fn()
    this.enableComponentGroup = jest.fn()
    this.toggleComponentGroup = jest.fn()
    this.componentGroupIsEnabled = jest.fn()
    this.componentGroupsIsEnabled = jest.fn()
    this.registerFocusChangeListener = jest.fn()
    this.unregisterFocusChangeListener = jest.fn()

    this.makeListItemsHttpRequest = jest.fn()

    this.moveDown = jest.fn()
    this.moveUp = jest.fn()
    this.isLast = jest.fn()
    this.isFirst = jest.fn()
    this.getAfter = jest.fn()
    this.getBefore = jest.fn()
  }

  get listComponentSpecs () {
    return []
  }
}

