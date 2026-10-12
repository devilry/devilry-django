import React from 'react'
import { ChildExposedApiMock } from '../filterlists/testHelpers'
import { RENDER_LOCATION_DEFAULT } from '../../filterListConstants'

export function renderComponentGroup (componentGroupComponentClass, props = {}) {
  const fullProps = Object.assign({
    childExposedApi: new ChildExposedApiMock(),
    location: RENDER_LOCATION_DEFAULT,
    uniqueComponentKey: 'test',
    enabledComponentGroups: new Set()
  }, props)
  return React.createElement(componentGroupComponentClass, fullProps)
}
