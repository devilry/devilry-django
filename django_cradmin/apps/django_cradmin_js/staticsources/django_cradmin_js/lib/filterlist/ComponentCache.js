import AbstractFilter from './components/filters/AbstractFilter'
import AbstractPaginator from './components/paginators/AbstractPaginator'
import AbstractList from './components/lists/AbstractList'
import FilterListRegistrySingleton from './FilterListRegistrySingleton'
import PrettyFormat from 'ievv_jsbase/lib/utils/PrettyFormat'
import AbstractListItem from './components/items/AbstractListItem'
import AbstractLayout from './components/layout/AbstractLayout'
import { RENDER_LOCATION_DEFAULT } from './filterListConstants'
import AbstractSelectedItems from './components/selecteditems/AbstractSelectedItems'
import AbstractComponentGroup from './components/componentgroup/AbstractComponentGroup'

export class KeyboardNavigationGroupItem {
  constructor (componentSpec, index) {
    this.componentSpec = componentSpec
    this.index = index
  }
}

/**
 * Defines the component layout within a {@link LayoutComponentSpec}.
 */
export class ComponentLayout {
  constructor () {
    /**
     * Maps locations to arrays of components.
     *
     * The {@link AbstractLayout} component uses this
     * to determine how to render the items.
     *
     * The locations are not sorted, but the array of components
     * within each location key is sorted, and should be rendered
     * in the listed order.
     *
     * @type {Map}
     */
    this.layoutMap = new Map()
  }

  /**
   * Add a component to the layout.
   *
   * Used when parsing the `body` and `header` props
   * for {@link AbstractFilterList}.
   *
   * @param {{}} componentSpec
   */
  add (componentSpec) {
    if (!this.layoutMap.has(componentSpec.props.location)) {
      this.layoutMap.set(componentSpec.props.location, [])
    }
    this.layoutMap.get(componentSpec.props.location).push(componentSpec)
  }

  /**
   * Get the components at a given location.
   *
   * @param {string} location The location.
   * @returns {[]} Always returns a (possibly empty) array even if there are no
   *    items at the provided location.
   */
  getComponentsAtLocation (location) {
    return this.layoutMap.get(location) || []
  }
}

export class AbstractComponentSpec {
  constructor (componentClass, rawComponentSpec) {
    /**
     * An instance of {@link FilterListRegistrySingleton} for convenience.
     *
     * @type {FilterListRegistrySingleton}
     */
    this.filterListRegistry = new FilterListRegistrySingleton()
    this._componentClass = componentClass
    this._componentSpec = Object.assign({}, rawComponentSpec)
    this._keyboardNavigationGroupPointerMap = new Map()
  }

  _makeUniqueComponentKeyPrefix () {
    return this.componentClassName
  }

  _makeUniqueComponentKey (componentCache) {
    const suffix = componentCache.makeUniqueComponentKey(componentCache)
    return `${this._makeUniqueComponentKeyPrefix()}-${suffix}`
  }

  _makeDomIdPrefix (componentCache, uniqueComponentKey) {
    return `${componentCache.domIdPrefix}${uniqueComponentKey}`
  }

  _raiseMissingRequiredAttributeError (attribute) {
    throw new Error(
      `${this.componentClassName} Missing required attribute "${attribute}": ${this.prettyFormatRawComponentSpec()}`)
  }

  clean (componentCache) {
    if (!this._componentSpec.props) {
      this._componentSpec.props = {}
    }
    if (!this._componentSpec.props.componentGroups) {
      this._componentSpec.props.componentGroups = null
    }
    this._componentSpec.props.uniqueComponentKey = this._makeUniqueComponentKey(componentCache)
    this._componentSpec.props.domIdPrefix = this._makeDomIdPrefix(
      componentCache, this._componentSpec.props.uniqueComponentKey)
    if (!componentCache.typeMap.has(this.constructor.name)) {
      componentCache.typeMap.set(this.constructor.name, [])
    }
    componentCache.addComponentSpecToTypeMap(this)

    // const keyboardNavigationGroups = this._componentClass.getKeyboardNavigationGroups ? this._componentClass.getKeyboardNavigationGroups(this) : []
    // for (const keyboardNavigationGroup of keyboardNavigationGroups) {
    //   componentCache.addComponentSpecToKeyboardNavigationGroup(keyboardNavigationGroup, this)
    // }
  }

  prettyFormatRawComponentSpec () {
    return new PrettyFormat().toString()
  }

  get componentClass () {
    return this._componentClass
  }

  get componentClassName () {
    return this.componentClass.name
  }

  get props () {
    return this._componentSpec.props
  }
}

export class LayoutComponentSpec extends AbstractComponentSpec {
  clean (componentCache) {
    super.clean(componentCache)
    if (!this._componentSpec.layout) {
      this._raiseMissingRequiredAttributeError('layout')
    }
    if (!this._componentSpec.defaultLocation) {
      this._componentSpec.defaultLocation = RENDER_LOCATION_DEFAULT
    }
    this._componentSpec.props.layout = new ComponentLayout()
    for (let rawChildComponentSpec of this._componentSpec.layout) {
      const childComponentSpec = componentCache.makeComponentSpec(rawChildComponentSpec)
      if (!(childComponentSpec instanceof AbstractLayoutChildComponentSpec)) {
        throw new Error(`Invalid child component of a layout: ${childComponentSpec.componentClassName}`)
      }
      childComponentSpec.clean(componentCache, this._componentSpec.defaultLocation)
      this._componentSpec.props.layout.add(childComponentSpec)
    }
  }
}

export class ListItemComponentSpec extends AbstractComponentSpec {
}

export class AbstractLayoutChildComponentSpec extends AbstractComponentSpec {
  clean (componentCache, defaultLocation) {
    super.clean(componentCache)
    if (!this._componentSpec.props.location) {
      this._componentSpec.props.location = defaultLocation
    }
  }
}

export class ListComponentSpec extends AbstractLayoutChildComponentSpec {
  clean (componentCache, defaultLocation) {
    super.clean(componentCache, defaultLocation)
    if (!this._componentSpec.itemSpec) {
      this._raiseMissingRequiredAttributeError('itemSpec')
    }
    const itemComponentSpec = componentCache.makeComponentSpec(this._componentSpec.itemSpec)
    itemComponentSpec.clean(componentCache)
    if (!(itemComponentSpec instanceof ListItemComponentSpec)) {
      throw new Error(`Invalid child component of a list: ${itemComponentSpec.componentClassName}`)
    }
    this._componentSpec.props.itemSpec = itemComponentSpec
  }
}

export class FilterComponentSpec extends AbstractLayoutChildComponentSpec {
  _makeUniqueComponentKeyPrefix () {
    return `${this.componentClassName}-${this.props.name}`
  }

  clean (componentCache, defaultLocation) {
    super.clean(componentCache, defaultLocation)
    if (!this._componentSpec.props.name) {
      this._raiseMissingRequiredAttributeError('props.name')
    }
    if (componentCache.filterMap.has(this.filterName)) {
      throw new Error(`Multiple filters with the same name: ${this.filterName}`)
    }
    if (this._componentSpec.initialValue === undefined) {
      this._componentSpec.initialValue = null
    }
    componentCache.filterMap.set(this.filterName, this)
  }

  get filterName () {
    return this.props.name
  }

  get initialValue () {
    return this._componentSpec.initialValue
  }

  get allowNullInQuerystring () {
    return this._componentSpec.allowNullInQuerystring || false
  }
}

export class PaginatorComponentSpec extends AbstractLayoutChildComponentSpec {
}

export class SelectedItemsComponentSpec extends AbstractLayoutChildComponentSpec {
}

export class ComponentGroupComponentSpec extends AbstractLayoutChildComponentSpec {
}

/**
 * Parser for the `body` and `header` props for {@link AbstractFilterList}.
 *
 * Validates the provided objects, looks up `component` attributes
 * and sets their actual class in a new `componentClass` attribute,
 * and much more.
 *
 * You can extend this class, and override
 * {@link AbstractFilterList#makeEmptyComponentCache} to
 * use a subclass of this class to parse the AbstractFilterList
 * `components` prop.
 */
export class ComponentCache {
  constructor (rawLayoutComponentSpecs = [], domIdPrefix = '') {
    this.domIdPrefix = domIdPrefix

    /**
     * An instance of {@link FilterListRegistrySingleton} for convenience.
     *
     * @type {FilterListRegistrySingleton}
     */
    this.filterListRegistry = new FilterListRegistrySingleton()

    /**
     * Map from filter name to parsed filter spec.
     *
     * @type {Map}
     */
    this.filterMap = new Map()

    /**
     * Internal counter of the number of layout components.
     *
     * Used by {@link ComponentCache#makeUniqueComponentKey}.
     *
     * @type {number}
     */
    this.componentCount = 0

    /**
     * The layout component specs.
     *
     * @type {[LayoutComponentSpec]}
     */
    this.layoutComponentSpecs = []

    /**
     * Map of spec type string to list of component specs within the type.
     *
     * @type {Map}
     */
    this.typeMap = new Map()

    this.keyboardNavigationGroupMap = new Map()

    this.addRawLayoutComponentSpecs(rawLayoutComponentSpecs)
  }

  /**
   * Get the javascript class for a `component` string.
   *
   * Looks up the component in {@link FilterListRegistrySingleton}.
   *
   * @param {string} componentString A string alias for a component class.
   * @returns {*}
   */
  getClassForComponentString (componentString) {
    let componentClass = null
    if (componentString.endsWith('Filter')) {
      componentClass = this.filterListRegistry.getFilterComponent(componentString)
    } else if (componentString.endsWith('List')) {
      componentClass = this.filterListRegistry.getListComponent(componentString)
    } else if (componentString.endsWith('Paginator')) {
      componentClass = this.filterListRegistry.getPaginatorComponent(componentString)
    } else if (componentString.endsWith('SelectedItems')) {
      componentClass = this.filterListRegistry.getSelectedItemsComponent(componentString)
    } else if (componentString.endsWith('Layout')) {
      componentClass = this.filterListRegistry.getLayoutComponent(componentString)
    } else if (componentString.endsWith('Item')) {
      componentClass = this.filterListRegistry.getItemComponent(componentString)
    } else if (componentString.endsWith('ComponentGroup')) {
      componentClass = this.filterListRegistry.getComponentGroupComponent(componentString)
    } else {
      throw new Error(
        `Invalid component: "${componentString}". ` +
        `Must end with "Filter", "List", "ComponentGroup" or "Paginator".`)
    }
    if (!componentClass) {
      throw new Error(
        `No component class for "${componentString}" in the registry.`)
    }
    return componentClass
  }

  getComponentClass (componentSpec) {
    if (typeof componentSpec.component === 'string') {
      return this.getClassForComponentString(componentSpec.component)
    } else {
      return componentSpec.component
    }
  }

  /**
   * Make a unique key for a component.
   *
   * @returns {string}
   */
  makeUniqueComponentKey () {
    const key = this.componentCount
    this.componentCount++
    return `${key}`
  }

  getComponentSpecClass (componentClass) {
    if (componentClass.prototype instanceof AbstractFilter) {
      return FilterComponentSpec
    } else if (componentClass.prototype instanceof AbstractList) {
      return ListComponentSpec
    } else if (componentClass.prototype instanceof AbstractPaginator) {
      return PaginatorComponentSpec
    } else if (componentClass.prototype instanceof AbstractSelectedItems) {
      return SelectedItemsComponentSpec
    } else if (componentClass.prototype instanceof AbstractListItem) {
      return ListItemComponentSpec
    } else if (componentClass.prototype instanceof AbstractLayout) {
      return LayoutComponentSpec
    } else if (componentClass.prototype instanceof AbstractComponentGroup) {
      return ComponentGroupComponentSpec
    } else {
      throw new Error(
        `Invalid component: "${componentClass.name}". ` +
        `Must be a subclass of AbstractFilter, AbstractList, AbstractComponentGroup ` +
        `or AbstractPaginator.`)
    }
  }

  makeComponentSpec (rawComponentSpec) {
    const componentClass = this.getComponentClass(rawComponentSpec)
    const ComponentSpecClass = this.getComponentSpecClass(componentClass)
    return new ComponentSpecClass(componentClass, rawComponentSpec)
  }

  /**
   * Make a {@link LayoutComponentSpec}.
   *
   * @param {{}} rawLayoutComponentSpec The raw area spec.
   * @returns {LayoutComponentSpec}
   */
  makeLayoutComponent (rawLayoutComponentSpec) {
    const componentSpec = this.makeComponentSpec(rawLayoutComponentSpec)
    componentSpec.clean(this)
    return componentSpec
  }

  addRawLayoutComponentSpec (rawLayoutComponentSpec) {
    this.layoutComponentSpecs.push(this.makeLayoutComponent(rawLayoutComponentSpec))
  }

  addRawLayoutComponentSpecs (rawLayoutComponentSpecs) {
    for (let rawLayoutComponentSpec of rawLayoutComponentSpecs) {
      this.addRawLayoutComponentSpec(rawLayoutComponentSpec)
    }
  }

  addComponentSpecToTypeMap (componentSpec) {
    this.typeMap.get(componentSpec.constructor.name).push(componentSpec)
  }

  // addComponentSpecToKeyboardNavigationGroup (keyboardNavigationGroup, componentSpec) {
  //   if (!this.keyboardNavigationGroupMap.has(keyboardNavigationGroup)) {
  //     this.keyboardNavigationGroupMap.set(keyboardNavigationGroup, [])
  //   }
  //   const keyboardNavigationGroupItemsArray = this.keyboardNavigationGroupMap.get(keyboardNavigationGroup)
  //   const nextIndex = keyboardNavigationGroupItemsArray.length
  //   keyboardNavigationGroupItemsArray.push(new KeyboardNavigationGroupItem(componentSpec, nextIndex))
  // }
}
