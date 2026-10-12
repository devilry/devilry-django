import AbstractFilterList from './AbstractFilterList'

export default class PageNumberPaginationFilterList extends AbstractFilterList {
  makePaginationStateFromHttpResponse (httpResponse, paginationOptions) {
    let page = 1
    if (paginationOptions && paginationOptions.page) {
      page = paginationOptions.page
    }
    return {
      page: page,
      next: httpResponse.bodydata.next,
      previous: httpResponse.bodydata.previous,
      count: httpResponse.bodydata.count
    }
  }

  getFirstPagePaginationOptions (paginationState) {
    return null
  }

  getCurrentPaginationPage (paginationState) {
    if (paginationState && paginationState.page) {
      return paginationState.page
    }
    return 1
  }

  getNextPagePaginationOptions (paginationState) {
    if (paginationState) {
      if (!paginationState.next) {
        return null
      }
      return {
        page: this.getCurrentPaginationPage(paginationState) + 1
      }
    }
    return null
  }

  getPreviousPagePaginationOptions (paginationState) {
    if (paginationState) {
      if (paginationState.previous === null) {
        return null
      }
      return {
        page: this.getCurrentPaginationPage(paginationState) - 1
      }
    }
    return null
  }

  getSpecificPagePaginationOptions (pageNumber, paginationState) {
    return {
      page: pageNumber
    }
  }

  getPaginationPageCount (paginationState) {
    return null
  }

  getTotalListItemCount (paginationState) {
    return paginationState.count
  }
}
