import React from 'react'
import { ChildExposedApiMock } from '../filterlists/testHelpers'
import { RENDER_LOCATION_DEFAULT } from '../../filterListConstants'

export function renderSelectedItems (selectedItemsComponentClass, props = {}) {
  const fullProps = Object.assign({
    childExposedApi: new ChildExposedApiMock(),
    location: RENDER_LOCATION_DEFAULT,
    listItemsDataArray: [],
    uniqueComponentKey: 'test',
    selectedListItemsMap: new Map()
  }, props)
  return React.createElement(selectedItemsComponentClass, fullProps)
}
