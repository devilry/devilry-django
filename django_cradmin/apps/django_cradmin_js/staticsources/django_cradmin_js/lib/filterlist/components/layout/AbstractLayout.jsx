import React from 'react'
import PropTypes from 'prop-types'
import 'ievv_jsbase/lib/utils/i18nFallbacks'
import AbstractFilterListChild from '../AbstractFilterListChild'
import LoadingIndicator from '../../../components/LoadingIndicator'
import AbstractFilter from '../filters/AbstractFilter'
import AbstractList from '../lists/AbstractList'
import AbstractPaginator from '../paginators/AbstractPaginator'
import AbstractSelectedItems from '../selecteditems/AbstractSelectedItems'
import AbstractComponentGroup from '../componentgroup/AbstractComponentGroup'

export default class AbstractLayout extends AbstractFilterListChild {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      layout: PropTypes.object.isRequired,
      listItemsDataArray: PropTypes.array.isRequired,
      listItemsDataMap: PropTypes.instanceOf(Map).isRequired,
      selectedListItemsMap: PropTypes.instanceOf(Map).isRequired,
      enabledComponentGroups: PropTypes.instanceOf(Set).isRequired,
      isLoadingNewItemsFromApi: PropTypes.bool.isRequired,
      isLoadingMoreItemsFromApi: PropTypes.bool.isRequired
    })
  }

  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      layout: null,
      listItemsDataArray: null,
      listItemsDataMap: null,
      selectedListItemsMap: null,
      enabledComponentGroups: null,
      isLoadingNewItemsFromApi: false,
      isLoadingMoreItemsFromApi: false
    })
  }

  //
  //
  // Rendering
  //
  //

  renderLoadingIndicator () {
    return <LoadingIndicator key={`loadingIndicator`} />
  }

  /**
   * Used by {@link AbstractLayout#shouldRenderComponent} when
   * the provided componentSpec.componentClass is a subclass
   * of {@link AbstractFilter}.
   *
   * By default this returns `true`.
   *
   * @param componentSpec
   * @returns {boolean}
   */
  shouldRenderFilterComponent (componentSpec) {
    return true
  }

  /**
   * Used by {@link AbstractLayout#shouldRenderComponent} when
   * the provided componentSpec.componentClass is a subclass
   * of {@link AbstractList}.
   *
   * By default this returns `true`.
   *
   * @param componentSpec The component we want to determine if should be rendered.
   * @returns {boolean} `true` to render the component, and `false` to not render
   *    the component.
   */
  shouldRenderListComponent (componentSpec) {
    return true
  }

  /**
   * Used by {@link AbstractLayout#shouldRenderComponent} when
   * the provided componentSpec.componentClass is a subclass
   * of {@link AbstractPaginator}.
   *
   * By default this returns `true` unless we are loading a new list
   * of items from the API (which typically happens when a filter is changed).
   *
   * @param componentSpec The component we want to determine if should be rendered.
   * @returns {boolean} `true` to render the component, and `false` to not render
   *    the component.
   */
  shouldRenderPaginatorComponent (componentSpec) {
    return !this.props.isLoadingNewItemsFromApi && !this.props.isLoadingMoreItemsFromApi
  }

  /**
   * Used by {@link AbstractLayout#shouldRenderComponent} when
   * the provided componentSpec.componentClass is a subclass
   * of {@link AbstractSelectedItems}.
   *
   * By default this returns `true`.
   *
   * @param componentSpec The component we want to determine if should be rendered.
   * @returns {boolean} `true` to render the component, and `false` to not render
   *    the component.
   */
  shouldRenderSelectedItemsComponent (componentSpec) {
    return true
  }

  /**
   * Used by {@link AbstractLayout#shouldRenderComponent} when
   * the provided componentSpec.componentClass is a subclass
   * of {@link AbstractComponentGroup}.
   *
   * By default this returns `true`.
   *
   * @param componentSpec The component we want to determine if should be rendered.
   * @returns {boolean} `true` to render the component, and `false` to not render
   *    the component.
   */
  shouldRenderComponentGroupComponent (componentSpec) {
    return true
  }

  /**
   * Determine if a component should be rendered.
   *
   * Perfect place to hook in things like "show advanced" filters etc.
   * in subclasses, but you will normally want to override one of
   * {@link AbstractLayout#shouldRenderFilterComponent},
   * {@link AbstractLayout#shouldRenderListComponent} or
   * {@link AbstractLayout#shouldRenderPaginatorComponent} instead
   * of this method.
   *
   * @param componentSpec The component we want to determine if should be rendered.
   * @param componentProps The props for the component we want to determine if should be rendered.
   * @returns {boolean} `true` to render the component, and `false` to not render
   *    the component.
   */
  shouldRenderComponent (componentSpec, componentProps) {
    if (!this.props.childExposedApi.componentGroupsIsEnabled(componentProps.componentGroups)) {
      return false
    }
    if (componentSpec.componentClass.prototype instanceof AbstractFilter) {
      return this.shouldRenderFilterComponent(componentSpec)
    } else if (componentSpec.componentClass.prototype instanceof AbstractList) {
      return this.shouldRenderListComponent(componentSpec)
    } else if (componentSpec.componentClass.prototype instanceof AbstractPaginator) {
      return this.shouldRenderPaginatorComponent(componentSpec)
    } else if (componentSpec.componentClass.prototype instanceof AbstractSelectedItems) {
      return this.shouldRenderSelectedItemsComponent(componentSpec)
    } else if (componentSpec.componentClass.prototype instanceof AbstractComponentGroup) {
      return this.shouldRenderComponentGroupComponent(componentSpec)
    } else {
      throw new Error(
        `Could not determine if we should render component. ` +
        `Unsupported component type: ${componentSpec.componentClassName}`)
    }
  }

  getFilterComponentProps (componentSpec) {
    const props = {
      value: this.props.childExposedApi.getFilterValue(componentSpec.props.name),
      enabledComponentGroups: this.props.enabledComponentGroups,
      selectedListItemsMap: this.props.selectedListItemsMap
    }
    if (componentSpec.componentClass.shouldReceiveSelectedItems(componentSpec)) {
      props.selectedListItemsMap = this.props.selectedListItemsMap
    }
    return props
  }

  getListComponentProps (componentSpec) {
    return {
      listItemsDataArray: this.props.listItemsDataArray,
      selectedListItemsMap: this.props.selectedListItemsMap
    }
  }

  getPaginatorComponentProps (componentSpec) {
    return {
      listItemsDataArray: this.props.listItemsDataArray
    }
  }

  getSelectedItemsComponentProps (componentSpec) {
    return {
      selectedListItemsMap: this.props.selectedListItemsMap
    }
  }

  getComponentGroupComponentProps (componentSpec) {
    return {
      enabledComponentGroups: this.props.enabledComponentGroups,
    }
  }

  getComponentTypeSpecificExtraProps (componentSpec) {
    if (componentSpec.componentClass.prototype instanceof AbstractFilter) {
      return this.getFilterComponentProps(componentSpec)
    } else if (componentSpec.componentClass.prototype instanceof AbstractList) {
      return this.getListComponentProps(componentSpec)
    } else if (componentSpec.componentClass.prototype instanceof AbstractPaginator) {
      return this.getPaginatorComponentProps(componentSpec)
    } else if (componentSpec.componentClass.prototype instanceof AbstractSelectedItems) {
      return this.getSelectedItemsComponentProps(componentSpec)
    } else if (componentSpec.componentClass.prototype instanceof AbstractComponentGroup) {
      return this.getComponentGroupComponentProps(componentSpec)
    } else {
      throw new Error(
        `Could not determine type-specific extra props. ` +
        `Unsupported component type: ${componentSpec.componentClassName}`)
    }
  }

  getFocusableComponentProps (componentSpec) {
    if (componentSpec.componentClass.shouldReceiveFocusEvents(componentSpec)) {
      return {
        willReceiveFocusEvents: true
      }
    }
    return {
      willReceiveFocusEvents: false
    }
  }

  getComponentProps (componentSpec) {
    const props = Object.assign({}, componentSpec.props, {
      key: componentSpec.props.uniqueComponentKey
    }, this.getComponentTypeSpecificExtraProps(componentSpec), this.getFocusableComponentProps(componentSpec))
    return this.makeChildComponentProps(componentSpec, props)
  }

  renderComponent (componentSpec, componentProps) {
    return React.createElement(componentSpec.componentClass, componentProps)
  }

  renderComponentsAtLocation (location, fallback = null) {
    const renderedComponents = []
    for (let componentSpec of this.props.layout.getComponentsAtLocation(location)) {
      const componentProps = this.getComponentProps(componentSpec)
      if (this.shouldRenderComponent(componentSpec, componentProps)) {
        renderedComponents.push(this.renderComponent(componentSpec, componentProps))
      }
    }
    if (renderedComponents.length === 0) {
      return fallback
    }
    return renderedComponents
  }
}
