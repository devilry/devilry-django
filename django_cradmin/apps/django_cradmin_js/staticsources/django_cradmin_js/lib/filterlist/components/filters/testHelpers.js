import React from 'react'
import { ChildExposedApiMock } from '../filterlists/testHelpers'
import { RENDER_LOCATION_CENTER } from '../../filterListConstants'

export function renderFilter (filterComponentClass, props = {}) {
  const fullProps = Object.assign({
    childExposedApi: new ChildExposedApiMock(),
    location: RENDER_LOCATION_CENTER,
    uniqueComponentKey: 'test',
    name: 'test'
  }, props)
  return React.createElement(filterComponentClass, fullProps)
}
