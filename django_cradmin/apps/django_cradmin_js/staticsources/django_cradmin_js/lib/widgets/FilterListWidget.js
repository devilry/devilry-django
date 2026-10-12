import React from 'react'
import ReactDOM from 'react-dom'
import AbstractWidget from 'ievv_jsbase/lib/widget/AbstractWidget'
import FilterListRegistry from '../filterlist/FilterListRegistrySingleton'

export default class FilterListWidget extends AbstractWidget {
  getDefaultConfig () {
    return {
      component: 'PageNumberPaginationFilterList'
    }
  }

  constructor (element, widgetInstanceId) {
    super(element, widgetInstanceId)
    const registry = new FilterListRegistry()
    if (!this.config.component) {
      throw new Error('The "component" config is required')
    }
    const filterListComponentClass = registry.getFilterListComponent(this.config.component)
    if (!filterListComponentClass) {
      throw new Error(
        `No filterlist component registered for ` +
        `the "${this.config.component}" alias.`)
    }

    delete this.config.component
    const reactElement = React.createElement(filterListComponentClass, this.config)
    ReactDOM.render(
      reactElement,
      this.element
    )
  }

  destroy () {
    ReactDOM.unmountComponentAtNode(this.element)
  }
}
