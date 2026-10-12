import React from 'react'
import { ChildExposedApiMock } from '../filterlists/testHelpers'
import { RENDER_LOCATION_CENTER } from '../../filterListConstants'

export function renderPaginator (paginatorComponentClass, props = {}) {
  const fullProps = Object.assign({
    childExposedApi: new ChildExposedApiMock(),
    location: RENDER_LOCATION_CENTER,
    listItemsDataArray: [],
    uniqueComponentKey: 'test'
  }, props)
  return React.createElement(paginatorComponentClass, fullProps)
}
