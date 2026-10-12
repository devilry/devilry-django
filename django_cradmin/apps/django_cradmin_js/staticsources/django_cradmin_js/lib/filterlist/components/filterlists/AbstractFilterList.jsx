import React from 'react'
import PropTypes from 'prop-types'
import HttpDjangoJsonRequest from 'ievv_jsbase/lib/http/HttpDjangoJsonRequest'
import FilterListRegistrySingleton from '../../FilterListRegistrySingleton'
import { MULTISELECT, SINGLESELECT } from '../../filterListConstants'
import 'ievv_jsbase/lib/utils/i18nFallbacks'
import LoadingIndicator from '../../../components/LoadingIndicator'
import { ComponentCache } from '../../ComponentCache'
import ChildExposedApi from './ChildExposedApi'
import { UrlParser } from 'ievv_jsbase/lib/http/UrlParser'
import QueryString from 'ievv_jsbase/lib/http/QueryString'
import UniqueDomIdSingleton from 'ievv_jsbase/lib/dom/UniqueDomIdSingleton'

export default class AbstractFilterList extends React.Component {
  static get propTypes () {
    return {
      idAttribute: PropTypes.string.isRequired,
      className: PropTypes.string,
      selectMode: PropTypes.oneOf([SINGLESELECT, MULTISELECT, null]),
      autoLoadFirstPage: PropTypes.bool.isRequired,
      skipLoadingMissingSelectedItemDataFromApi: PropTypes.bool.isRequired,
      domIdPrefix: PropTypes.string,
      onFocus: PropTypes.func,
      onBlur: PropTypes.func,
      onSelectItem: PropTypes.func,
      onSelectItems: PropTypes.func,
      onDeselectItem: PropTypes.func,
      onDeselectItems: PropTypes.func,
      onSelectedItemsMoved: PropTypes.func,
      onDeselectAllItems: PropTypes.func,

      getItemsApiUrl: PropTypes.string.isRequired,
      updateSingleItemSortOrderApiUrl: PropTypes.string,

      components: PropTypes.arrayOf(PropTypes.object).isRequired,

      initiallySelectedItemIds: PropTypes.array.isRequired,
      // updateHttpMethod: (props, propName, componentName) => {
      //   if(!props[propName] || !/^(post|put)$/.test(props[propName])) {
      //     return new Error(
      //       `Invalid prop ${propName} supplied to ${componentName}. Must ` +
      //       `be "post" or "put".`
      //     )
      //   }
      // }
    }
  }

  /**
   * Get default props.
   *
   * TODO: Document all the props.
   *
   * @return {Object}
   * @property {string} idAttribute The ID attribute in the getItemsApiUrl API. Defaults to `id`.
   * @property {string} getItemsApiUrl The API to get the items from (with a GET request). Required.
   * @property {string} domIdPrefix The DOM id prefix that we use when we need to set IDs on DOM elements
   *    within the list. This is optional, but highly recommended to set. If this is not set,
   *    we generate a prefix from the `getItemsApiUrl` and a random integer.
   * @property {function} onGetListItemsFromApiRequestBegin
   *    Called each time we initialize an API request to get items. Called with
   *    three arguments: (<this - the filterlist object>, paginationOptions, clearOldItems).
   *    See {@link AbstractFilterList#loadItemsFromApi} for documentation of ``paginationOptions``
   *    and ``clearOldItems``.
   * @property {function} onGetListItemsFromApiRequestSuccess
   *    Called each time we successfully complete an API request to get items. Called with
   *    three arguments: (<this - the filterlist object>, paginationOptions, clearOldItems).
   *    See {@link AbstractFilterList#loadItemsFromApi} for documentation of ``paginationOptions``
   *    and ``clearOldItems``.
   * @property {function} onGetListItemsFromApiRequestError
   *    Called each time we successfully complete an API request to get items. Called with
   *    three arguments: (<this - the filterlist object>, error, paginationOptions, clearOldItems).
   *    See {@link AbstractFilterList#loadItemsFromApi} for documentation of ``paginationOptions``
   *    and ``clearOldItems``. ``error`` is the exception object.
   * @property {number} filterApiDelayMilliseconds Number of milliseconds we wait from the last filter change until
   *    we perform an API request. Defaults to ``500``.
   * @property {string} selectMode One of {@link SINGLESELECT}, {@link MULTISELECT} or null. Always set this
   *    to something other than null when using a configuration that enables selecting items.
   * @property {function} onSelectItems Callback function called each time a user adds to the selected items
   *    when `selectMode` is {@link MULTISELECT}. Called with two arguments `(addedSelectedListItemIds, filterList)`
   *    where `addedSelectedListItemIds` is the items that was just added to the selection, and
   *    `filterList` is a reference to this filterlist object.
   * @property {function} onDeselectItems Callback function called each time a user removes from the selected items
   *    when `selectMode` is {@link MULTISELECT}. Called with two arguments `(removedSelectedListItemIds, filterList)`
   *    where `removedSelectedListItemIds` is the items that was just removed from the selection, and
   *    `filterList` is a reference to this filterlist object.
   * @property {function} onSelectedItemsMoved Callback function called each time a user moves a selected item
   *    when `selectMode` is {@link MULTISELECT}. Called with one argument `(filterList)` where `filterList` is a
   *    reference to this filterlist object.
   * @property {function} onSelectItem Callback function called each time a user adds to the selected items
   *    when `selectMode` is {@link SINGLESELECT}. Called with two arguments `(selectedItemId, filterList)`
   *    where `selectedItemId` is the ID of the selected item, and `filterList` is a reference to this
   *    filterlist object.
   * @property {function} onDeselectItem Callback function called each time a user removes from the selected items
   *    when `selectMode` is {@link SINGLESELECT}. Called with two arguments `(deselectedItemId, filterList)`
   *    where `deselectedItemId` is the ID of the deselected item, and `filterList` is a reference to this
   *    filterlist object.
   */
  static get defaultProps () {
    return {
      idAttribute: 'id',
      className: null,
      selectMode: null,
      autoLoadFirstPage: true,
      skipLoadingMissingSelectedItemDataFromApi: false,
      onFocus: null,
      onBlur: null,
      onSelectItem: null,
      onSelectItems: null,
      onDeselectItem: null,
      onDeselectItems: null,
      onSelectedItemsMoved: null,
      onDeselectAllItems: null,
      onGetListItemsFromApiRequestBegin: null,
      onGetListItemsFromApiRequestError: null,
      onGetListItemsFromApiRequestSuccess: null,
      filterApiDelayMilliseconds: 500,
      bindFiltersToQuerystring: false,

      getItemsApiUrl: null,
      updateSingleItemSortOrderApiUrl: null,
      initiallySelectedItemIds: [],
      domIdPrefix: null,
      components: [{
        component: 'ThreeColumnLayout',
        layout: [{
          component: 'BlockList',
          itemSpec: {
            component: 'IdOnlyItem'
          }
        }, {
          component: 'LoadMorePaginator'
        }]
      }]
    }
  }

  constructor (props) {
    super(props)
    this.setupBoundMethods()
    this._apiRequestNumber = 0
    this.childExposedApi = this.makeChildExposedApi()
    this._filterApiUpdateTimeoutId = null
    this._saveMovingItemTimeout = null
    this._blurTimeoutId = null
    this.filterListRegistry = new FilterListRegistrySingleton()
    this.state = this.getInitialState()
    this.filterSpecCache = new Map()
    this.cachedHeaderSpec = null
    this.cachedBodySpec = null
    this.cachedItemSpec = null
    this.cachedListSpec = null
    this.cachedPaginatorSpec = null
    this._focusChangeListeners = new Set()
    this._selectionChangeListeners = new Set()
    this._currentFocusChildInfo = null
  }

  /**
   * Make a {@link ChildExposedApi} object.
   *
   * See {@link ChildExposedApi} for more details.
   *
   * @returns {ChildExposedApi}
   */
  makeChildExposedApi () {
    return new ChildExposedApi(this)
  }

  componentDidMount () {
    this.setState({
      ...AbstractFilterList.refreshComponentCache(this.props, this.state), isMounted: true
    }, () => {
      this.loadMissingSelectedItemDataFromApi()
      this.loadInitialFilterValues()
      if (this.props.autoLoadFirstPage) {
        this.loadFirstPageFromApi()
      }
    })
  }

  static getDerivedStateFromProps (nextProps, prevState) {
    if (prevState.isMounted) {
      let nextState = AbstractFilterList.refreshComponentCache(nextProps, prevState)
      nextState = {...nextState, isMounted: true}
      if ('selectMode' in nextProps) {
        nextState = {...nextState, selectMode: nextProps.selectMode}
      }
      return nextState
    }
    return null

  }

  setupBoundMethods () {
    this.loadMissingSelectedItemDataFromApi = this.loadMissingSelectedItemDataFromApi.bind(this)
  }

  _makeInitiallySelectedListItemsMap () {
    const selectedListItemsMap = new Map()
    for (let itemId of this.props.initiallySelectedItemIds) {
      selectedListItemsMap.set(itemId, null)
    }
    return selectedListItemsMap
  }

  /**
   * Get the initial react state.
   *
   * Useful for subclasses.
   *
   * @returns {object} The initial state.
   */
  getInitialState () {
    return {
      listItemsDataArray: [],
      listItemsDataMap: new Map(),
      isLoadingNewItemsFromApi: false,
      isLoadingMoreItemsFromApi: false,
      componentCache: AbstractFilterList.makeEmptyComponentCache(),
      paginationState: {},
      hasFocus: false,
      selectedListItemsMap: this._makeInitiallySelectedListItemsMap(),
      loadSelectedItemsFromApiError: null,
      loadItemsFromApiError: null,
      enabledComponentGroups: new Set(),
      selectMode: this.props.selectMode,
      isMounted: false,
      isMovingListItemId: null,
      allListItemMovementIsLocked: false
    }
  }

  /**
   * Make an empty component cache.
   *
   * @returns {ComponentCache} An object of {@link ComponentCache} or a subclass.
   */
  static makeEmptyComponentCache (domIdPrefix = null) {
    if (!domIdPrefix) {
      domIdPrefix = `${new UniqueDomIdSingleton().generate()}-`
    }
    return new ComponentCache([], domIdPrefix)
  }

  /**
   * Make a {@link ComponentCache} object.
   *
   * @param rawComponentSpecs
   * @param domIdPrefix
   * @returns {ComponentCache}
   */
  static buildComponentCache (rawComponentSpecs, domIdPrefix) {
    const componentCache = AbstractFilterList.makeEmptyComponentCache(domIdPrefix)
    componentCache.addRawLayoutComponentSpecs(rawComponentSpecs)
    return componentCache
  }

  static refreshComponentCache (props, state) {
    const componentCache = AbstractFilterList.buildComponentCache(props.components, props.domIdPrefix)
    return Object.assign(
      AbstractFilterList.makeInitialFilterValues(componentCache.filterMap.values(), state),
      {componentCache}
    )
  }

  //
  //
  // Component groups
  //
  //

  /**
   * Disable a component group.
   *
   * See {@link AbstractFilterList#toggleComponentGroup} for more info
   * about component groups.
   *
   * @param {string} group The group to disable.
   */
  disableComponentGroup (group) {
    this.setState((prevState) => {
      const enabledComponentGroups = new Set(prevState.enabledComponentGroups)
      enabledComponentGroups.delete(group)
      return {
        enabledComponentGroups: enabledComponentGroups
      }
    })
  }

  /**
   * Enable a component group.
   *
   * See {@link AbstractFilterList#toggleComponentGroup} for more info
   * about component groups.
   *
   * @param {string} group The group to enable.
   */
  enableComponentGroup (group) {
    this.setState((prevState) => {
      const enabledComponentGroups = new Set(prevState.enabledComponentGroups)
      enabledComponentGroups.add(group)
      return {
        enabledComponentGroups: enabledComponentGroups
      }
    })
  }

  /**
   * Is a component group enabled?
   *
   * See {@link AbstractFilterList#toggleComponentGroup} for more info
   * about component groups.
   *
   * @param {string|null} group The group to check. If this is null, we always return `true`.
   * @return {bool} Is the component group enabled?
   */
  componentGroupIsEnabled (group) {
    if (group === null) {
      return true
    }
    return this.state.enabledComponentGroups.has(group)
  }

  /**
   * Is all the provided component groups enabled?
   *
   * @param {[string]|null} groups
   * @return {bool} Is all the component groups enabled?
   */
  componentGroupsIsEnabled (groups) {
    if (groups === null) {
      return true
    }
    for (let group of groups) {
      if (!this.componentGroupIsEnabled(group)) {
        return false
      }
    }
    return true
  }

  /**
   * Toggle a component group between disabled/enabled.
   *
   * A component group is just a string that any component
   * in `body` or `header` can set via their `componentGroup`
   * prop. You can then use this method, {@link AbstractFilterList#enableComponentGroup}
   * or {@link AbstractFilterList#disableComponentGroup} to enable/disable
   * rendering of a whole group of components. This is perfect
   * for things like dropdowns, toggle advanced filters, etc.
   *
   * We provide the {@link COMPONENT_GROUP_EXPANDABLE} and
   * {@link COMPONENT_GROUP_ADVANCED} constants, and you
   * should use these (or their values in case of purely configuring
   * through JSON input) unless you have needs not covered by them.
   *
   * @param {string} group The group to enable/disable.
   */
  toggleComponentGroup (group) {
    if (this.componentGroupIsEnabled(group)) {
      this.disableComponentGroup(group)
    } else {
      this.enableComponentGroup(group)
    }
  }

  //
  //
  // Focus/blur
  //
  //

  _stopBlurTimer () {
    if (this._blurTimeoutId) {
      window.clearTimeout(this._blurTimeoutId)
    }
  }

  onBlurTimerTimeout (childInfo) {
    const didChangeFilterListFocus = this.state.hasFocus !== false
    this.setState({
      hasFocus: false
    }, () => {
      this.callAllFocusChangeListeners('onAnyComponentBlur',
        childInfo, didChangeFilterListFocus)
      this._currentFocusChildInfo = null
      if (this.props.onBlur) {
        this.props.onBlur(this)
      }
    })
  }

  get blurTimerTimeout () {
    return 200
  }

  _startBlurTimer (childInfo) {
    this._blurTimeoutId = window.setTimeout(() => {
      this.onBlurTimerTimeout(childInfo)
    }, this.blurTimerTimeout)
  }

  onChildBlur (childInfo) {
    this.callAllFocusChangeListeners('onAnyComponentBlur',
      childInfo, false)
    this._startBlurTimer(childInfo)
  }

  onChildFocus (childInfo) {
    this._stopBlurTimer()
    const didChangeFilterListFocus = this.state.hasFocus !== true
    this.setState({
      hasFocus: true
    }, () => {
      const prevChildInfo = this._currentFocusChildInfo
      this.callAllFocusChangeListeners(
        'onAnyComponentFocus', childInfo, prevChildInfo, didChangeFilterListFocus)
      this._currentFocusChildInfo = childInfo
      if (this.props.onFocus) {
        this.props.onFocus(this)
      }
    })
  }

  registerFocusChangeListener (componentObject) {
    this._focusChangeListeners.add(componentObject)
  }

  unregisterFocusChangeListener (componentObject) {
    this._focusChangeListeners.delete(componentObject)
  }

  callAllFocusChangeListeners (methodName, ...args) {
    for (let componentObject of this._focusChangeListeners) {
      componentObject[methodName](...args)
    }
  }

  //
  //
  // Selected items list mutation
  //
  //

  /**
   * Get the index of the selectedListItemId in the selectedItemsArray.
   * @param selectedListItemId
   * @param selectedItemsArray
   * @returns {number} the index of the selected item in the array.
   */
  getIndexOfItem (selectedListItemId, selectedItemsArray) {
    return selectedItemsArray.findIndex(itemId => itemId === selectedListItemId)
  }

  /**
   * Returns true if the selectedListeItemId is the first element in selectedListItemsMap.
   *
   * @param selectedListItemId
   * @returns {boolean}
   */
  selectedItemIsFirst (selectedListItemId) {
    const item = Array.from(this.state.selectedListItemsMap.values())[0]
    if (item === null) {
      return false
    }
    return item.id === selectedListItemId
  }

  /**
   * Returns true if the selectedListeItemId is the last element in selectedListItemsMap.
   *
   * @param selectedListItemId
   * @returns {boolean}
   */
  selectedItemIsLast (selectedListItemId) {
    const item = Array.from(this.state.selectedListItemsMap.values()).slice(-1)[0]
    if (item === null) {
      return false
    }
    return item.id === selectedListItemId
  }

  /**
   * Get an array of the selected item ids from selectedListItemsMap.
   * @returns {Array}
   */
  selectedItemIdsAsArray () {
    return Array.from(this.state.selectedListItemsMap.keys())
  }

  /**
   * Build a new map from a reordered array of selected item ids to replace current
   * selectedListItemsMap
   * @param reorderedArray
   * @returns {Map<Number, Object>}
   */
  getItemsMapFromReorderedArray (reorderedArray) {
    let selectedItemsMap = new Map()
    for (let itemId of reorderedArray) {
      selectedItemsMap.set(itemId, this.state.selectedListItemsMap.get(itemId))
    }
    return selectedItemsMap
  }

  /**
   * Moves an element with selectedItemId one step up in the selectedListItemsMap.
   * @param selectedItemId the selected item id to move up.
   */
  selectedItemMoveUp (selectedItemId) {
    if (this.selectedItemIsFirst(selectedItemId)) {
      return
    }
    let selectedItemsArray = this.selectedItemIdsAsArray()
    if (selectedItemsArray[0] === selectedItemId) {
      return
    }
    const index = this.getIndexOfItem(selectedItemId, selectedItemsArray)
    let newArray = [
      ...selectedItemsArray.slice(0, index - 1),
      selectedItemsArray[index],
      selectedItemsArray[index - 1],
      ...selectedItemsArray.slice(index + 1)
    ]
    this.setState({
      selectedListItemsMap: this.getItemsMapFromReorderedArray(newArray)
    }, () => {
      if (this.props.onSelectedItemsMoved) {
        this.props.onSelectedItemsMoved(this)
      }
    })
  }

  /**
   * Moves an element with selectedItemId one step down in the selectedListItemsMap.
   * @param selectedItemId the selected item id to move down.
   */
  selectedItemMoveDown (selectedItemId) {
    if (this.selectedItemIsLast(selectedItemId)) {
      return
    }
    let selectedItemsArray = this.selectedItemIdsAsArray()
    const index = this.getIndexOfItem(selectedItemId, selectedItemsArray)
    let newArray = [
      ...selectedItemsArray.slice(0, index),
      selectedItemsArray[index + 1],
      selectedItemsArray[index],
      ...selectedItemsArray.slice(index + 2)
    ]
    this.setState({
      selectedListItemsMap: this.getItemsMapFromReorderedArray(newArray)
    }, () => {
      if (this.props.onSelectedItemsMoved) {
        this.props.onSelectedItemsMoved(this)
      }
    })
  }


  //
  //
  // List mutations
  //
  //

  /**
   * Get the index of listItemId in the listItemsDataArray
   * @param listItemId The list item id
   * @returns {number} the index of item in list
   */
  getIndexOfId (listItemId) {
    return this.state.listItemsDataArray.findIndex(item => item.listItemId === listItemId)
  }

  /**
   * Returns true if the listItemId is the first element in listItemsDataArray
   * @param listItemId the list item id
   * @returns {boolean}
   */
  isFirst (listItemId) {
    return this.getIndexOfId(listItemId) === 0
  }

  /**
   * Returns true if the listItemId is the last element in listItemsDataArray
   * @param listItemId the list item id
   * @returns {boolean}
   */
  isLast (listItemId) {
    return this.getIndexOfId(listItemId) === this.state.listItemsDataArray.length - 1
  }

  /**
   * Get the element before the listItemId element
   * @param listItemId the list item id
   * @returns {null|number} returns null if list item id is the first element, otherwise the object before.
   */
  getBefore (listItemId) {
    if (this.isFirst(listItemId)) {
      return null
    }
    return this.state.listItemsDataArray[this.getIndexOfId(listItemId) - 1]
  }

  /**
   * Get the element after the listItemId element
   * @param listItemId the list item id
   * @returns {null|number} returns null if the list item id is the last element, otherwise the object after.
   */
  getAfter (listItemId) {
    if (this.isLast(listItemId)) {
      return null
    }
    return this.state.listItemsDataArray[this.getIndexOfId(listItemId) + 1]
  }

  /**
   * Moves an element with listItemId one step up in the listItemsDataArray
   * @param listItemId the list item id to move
   */
  moveUp (listItemId, callback = null) {
    const index = this.getIndexOfId(listItemId)
    if (index === 0) {
      return
    }
    this.setState({
      listItemsDataArray: [
        ...this.state.listItemsDataArray.slice(0, index - 1),
        this.state.listItemsDataArray[index],
        this.state.listItemsDataArray[index - 1],
        ...this.state.listItemsDataArray.slice(index + 1)]
    }, () => {
      if (callback !== null) {
        callback(listItemId)
      }
    })
  }

  /**
   * Moves an element with listItemId one step down in the listItemsDataArray
   * @param listItemId the list item id to move
   */
  moveDown (listItemId, callback = null) {
    const index = this.getIndexOfId(listItemId)
    if (index === this.state.listItemsDataArray.lastIndex - 1) {
      return
    }
    this.setState({
      listItemsDataArray: [
        ...this.state.listItemsDataArray.slice(0, index),
        this.state.listItemsDataArray[index + 1],
        this.state.listItemsDataArray[index],
        ...this.state.listItemsDataArray.slice(index + 2)
      ]
    }, () => {
      if (callback !== null) {
        callback(listItemId)
      }
    })
  }

  /**
   *
   * @example <caption>Typical example within some child component of the filterlist</caption>
   *
   * handleMoveUp () {
   *   // this.props.listItemId would work for list item renderables, but you may get it from somewhere else
   *   this.childExposedApi.setIsMovingListItemId(this.props.listItemId, (listItemId) => {
   *     this.childExposedApi.moveUp(listItemId, () => {
   *       this.childExposedApi.setSaveMovingItemTimeout((listItemId) => {
   *         this.saveMovedItem(listItemId)
   *       })
   *     })
   *   })
   * }
   *
   * saveMovedItem (listItemId) {
   *   this.childExposedApi.lockAllListItemMovement(() => {
   *     new HttpRequest()
   *        .post(...)
   *        .then(() => {
   *           this.childExposedApi.clearIsMovingListItemId()
   *        })
   *        .catch(() => {
   *           // Show some error, and perhaps call clearisMovingListItemId()
   *        })
   *   })
   * }
   *
   * @param listItemId
   * @param callback
   */
  setIsMovingListItemId (listItemId, callback = null) {
    this.setState({
      isMovingListItemId: listItemId
    }, () => {
      if (callback !== null) {
        callback(listItemId)
      }
    })
  }

  /**
   * Get the ID of the list-item currently being moved.
   *
   * @returns {*}
   */
  get isMovingListItemId () {
    return this.state.isMovingListItemId
  }

  /**
   * Should item-movement be completely disabled?
   *
   * @returns {bool}
   */
  get allListItemMovementIsLocked () {
    return this.state.allListItemMovementIsLocked
  }

  /**
   * Sets the `allListItemMovementIsLocked` in state, and the
   * callback should handle the POST-request to an API.
   *
   * For example usage, see the example for `setIsMovingListItemId`.
   *
   * @param callback
   */
  lockAllListItemMovement (callback = null) {
    this.setState({
      allListItemMovementIsLocked: true
    }, () => {
      if (callback !== null) {
        callback()
      }
    })
  }

  /**
   * Sets `isMovingListItemId` to ``null`` and `allListItemMovementIsLocked` to
   * ``false`` in state.
   *
   * @see setIsMovingListItemId
   */
  clearIsMovingListItemId () {
    this.setState({
      isMovingListItemId: null,
      allListItemMovementIsLocked: false
    })
  }

  /**
   * A timeout applied everytime an item is moved, that resets when moving an item
   * before the previous timeout.
   *
   * For example usage, see the example for `setIsMovingListItemId`.
   *
   * @param callback
   * @param timeoutMilliseconds
   */
  setSaveMovingItemTimeout (callback, timeoutMilliseconds = 500) {
    if (this._saveMovingItemTimeout) {
      window.clearTimeout(this._saveMovingItemTimeout)
    }
    this._saveMovingItemTimeout = window.setTimeout(callback, timeoutMilliseconds)
  }

  //
  //
  // Single and multiselect
  //
  //

  /**
   * Change selectMode to given selectMode
   *
   * NOTE: this is not error-handled, so users should take care to only use selectModes that make sense for the
   * current use-case.
   *
   * @param selectMode the selectMode to change to.
   */
  setSelectMode (selectMode) {
    this.setState({
      selectMode: selectMode
    })
  }

  /**
   * Is `props.selectMode === 'single'`?
   *
   * WARNING: The default value for `props.selectMode` is `null`,
   * which means that this method returns `false` by default.
   * This means that you normally want to use {@link AbstractFilterList#isMultiSelectMode}
   * instead of this method unless you work with 3 states of selectMode
   * (no select (null), singleselect and multiselect)
   *
   * @returns {boolean}
   */
  isSingleSelectMode () {
    return this.state.selectMode === SINGLESELECT
  }

  /**
   * Is `props.selectMode === 'multi'`?
   *
   * @returns {boolean}
   */
  isMultiSelectMode () {
    return this.state.selectMode === MULTISELECT
  }

  /**
   * Is the provided `listItemId` selected?
   *
   * @param listItemId The ID of a list item.
   * @returns {boolean}
   */
  itemIsSelected (listItemId) {
    return this.state.selectedListItemsMap.has(listItemId)
  }

  /**
   * Get an array with the IDs of the selected items.
   *
   * You will typically use this in combination with
   * the `onSelectItems`, `onDeselectItems` and `onSelectedItemsMoved` to store the
   * selected items in some parent component. Both `onSelectItems`
   * and `onDeselectItems` gets a reference to this filterlist class
   * as their second argument. `onSelectedItemsMoved` gets a reference to this filterlist as
   * its only argument.
   *
   * @example <caption>A typical callback function for the onSelectItems / onDeselectItems props</caption>
   * onSelectItemsHandler (addedSelectedListItemIds, filterList) {
   *   const allSelectedItemIds = filterList.getSelectedListItemIds()
   * }
   *
   * @example <caption>A typical callback function for the onSelectedItemsMoved prop</caption>
   * onSelectedItemsMovedHandler (filterList) {
   *   const allSelectedItemIds = filterList.getSelectedListItemIds()
   * }
   */
  getSelectedListItemIds () {
    return Array.from(this.state.selectedListItemsMap.keys())
  }

  /**
   * Select an item.
   *
   * @param listItemId The ID of a list item.
   */
  selectItem (listItemId) {
    this.selectItems([listItemId])
  }

  registerSelectionChangeListener (componentObject) {
    this._selectionChangeListeners.add(componentObject)
  }

  unregisterSelectionChangeListener (componentObject) {
    this._selectionChangeListeners.delete(componentObject)
  }

  callAllSelectionChangeListeners (methodName, ...args) {
    for (let componentObject of this._selectionChangeListeners) {
      componentObject[methodName](...args)
    }
  }

  onSelectedItems (listItemIds) {
    this.callAllSelectionChangeListeners('onSelectItems', listItemIds)
  }

  onDeselectItems (listItemIds) {
    this.callAllSelectionChangeListeners('onDeselectItems', listItemIds)
  }

  /**
   * Select multiple items.
   *
   * @param {[]} listItemIds Array of list item IDs. The array can not have more
   *    than 1 item unless {@link AbstractFilterList#isMultiSelectMode} is `true`.
   */
  selectItems (listItemIds) {
    if (listItemIds.length > 1 && !this.isMultiSelectMode()) {
      throw new Error('Can not select multiple items unless selectMode is "multi".')
    }
    if (!this.isMultiSelectMode()) {
      this.deselectAllItems()
    }
    this.setState((prevState, props) => {
      const selectedListItemsMap = prevState.selectedListItemsMap
      for (let listItemId of listItemIds) {
        let listItemData = null
        if (prevState.listItemsDataMap.has(listItemId)) {
          listItemData = prevState.listItemsDataMap.get(listItemId)
        }
        selectedListItemsMap.set(listItemId, listItemData)
      }
      return {
        selectedListItemsMap: selectedListItemsMap
      }
    }, () => {
      this.loadMissingSelectedItemDataFromApi()
      this.onSelectedItems(listItemIds)
      if (this.props.onSelectItems) {
        this.props.onSelectItems(listItemIds, this)
      }
      if (!this.isMultiSelectMode()) {
        if (this.props.onSelectItem && listItemIds.length > 0) {
          this.props.onSelectItem(listItemIds[0], this)
        }
      }
    })
  }

  /**
   * Deselect an item.
   *
   * @param listItemId The ID of a list item.
   */
  deselectItem (listItemId) {
    this.deselectItems([listItemId])
  }

  /**
   * Deselect multiple items.
   *
   * @param {[]} listItemIds Array of list item IDs.
   */
  deselectItems (listItemIds) {
    this.setState((prevState) => {
      const selectedListItemsMap = prevState.selectedListItemsMap
      for (let listItemId of listItemIds) {
        selectedListItemsMap.delete(listItemId)
      }
      return {
        selectedListItemsMap: selectedListItemsMap
      }
    }, () => {
      this.onDeselectItems()
      if (this.props.onDeselectItems) {
        this.props.onDeselectItems(listItemIds, this)
      }
      if (!this.isMultiSelectMode()) {
        if (this.props.onDeselectItem && listItemIds.length > 0) {
          this.props.onDeselectItem(listItemIds[0], this)
        }
      }
      if (this.props.onDeselectAllItems && this.state.selectedListItemsMap.size === 0) {
        this.props.onDeselectAllItems(this)
      }
    })
  }

  /**
   * Deselect all selected items.
   */
  deselectAllItems () {
    const listItemIds = Array.from(this.state.selectedListItemsMap.keys())
    this.deselectItems(listItemIds)
  }

  getSelectedItemIdsWithMissingItemData () {
    const selectedItemIdsWithMissingItemData = []
    for (let [listItemId, listItemData] of this.state.selectedListItemsMap) {
      if (listItemData === null) {
        selectedItemIdsWithMissingItemData.push(listItemId)
      }
    }
    return selectedItemIdsWithMissingItemData
  }

  // filterLoadSelectedItemDataFromApiRequest (httpRequest, listItemIds) {
  //   httpRequest.urlParser.queryString.setIterable(
  //     this.props.getItemsApiIdsQueryStringArgument,
  //     listItemIds)
  // }

  setLoadMissingSelectedItemDataFromApiErrorMessage (errorObject) {
    this.setState({
      loadSelectedItemsFromApiError: window.gettext('Failed to load selected list items from the server.')
    })
  }

  clearLoadMissingSelectedItemDataFromApiErrorMessage () {
    if (this.state.loadSelectedItemsFromApiError !== null) {
      this.setState({
        loadSelectedItemsFromApiError: null
      })
    }
  }

  handleLoadMissingSelectedItemDataFromApiError (errorObject) {
    console.error('Error:', errorObject.toString())
    this.setLoadMissingSelectedItemDataFromApiErrorMessage(errorObject)
  }

  handleRetrieveListItemDataError (listItemResponse) {
    console.warn('Failed to retrieve list item data:', listItemResponse)
  }

  loadMissingSelectedItemDataFromApi () {
    if (this.props.skipLoadingMissingSelectedItemDataFromApi) {
      return
    }
    const itemIdsWithMissingData = this.getSelectedItemIdsWithMissingItemData()
    if (itemIdsWithMissingData.length === 0) {
      return
    }
    if (this.state.isLoadingSelectedItemDataFromApi) {
      // Do not allow this to run in parallel
      setTimeout(this.loadMissingSelectedItemDataFromApi, 20)
      return
    }
    this.clearLoadMissingSelectedItemDataFromApiErrorMessage()
    this.setState({
      isLoadingSelectedItemDataFromApi: true
    }, () => {
      this.loadMultipleItemDataFromApi(
        itemIdsWithMissingData)
        .then((selectedItemDataArray) => {
          this.setState((prevState) => {
            const selectedListItemsMap = prevState.selectedListItemsMap
            for (let listItemResponse of selectedItemDataArray) {
              const listItemId = listItemResponse.listItemId
              if (listItemResponse.status === 200) {
                selectedListItemsMap.set(listItemId, listItemResponse.data)
              } else {
                selectedListItemsMap.delete(listItemId)
                this.handleRetrieveListItemDataError(listItemResponse)
              }
            }
            return {
              selectedListItemsMap: selectedListItemsMap,
              isLoadingSelectedItemDataFromApi: false
            }
          })
        })
        .catch((error) => {
          this.handleLoadMissingSelectedItemDataFromApiError(error)
        })
    })
  }

  get selectedItemIds () {
    return Array.from(this.state.selectedListItemsMap.keys())
  }

  //
  //
  // Filters
  //
  //

  /**
   * Get the delay after changing a filter value until
   * we make the API request. This avoids extra API requests
   * when users change many filter values fast (I.E.: search, or
   * clicking many checkboxes fast).
   *
   * If a new filter value is set before this delay is
   * exceeded, the delay is reset and a new delay is started.
   *
   * @returns {number} Number of milliseconds to wait before
   *    making the API request on filter value change.
   *    Defaults to `this.props.filterApiDelayMilliseconds`.
   */
  get filterApiDelayMilliseconds () {
    return this.props.filterApiDelayMilliseconds
  }

  _stopFilterApiUpdateTimer () {
    if (this._filterApiUpdateTimeoutId) {
      window.clearTimeout(this._filterApiUpdateTimeoutId)
    }
  }

  _startFilterApiUpdateTimer () {
    this._filterApiUpdateTimeoutId = window.setTimeout(() => {
      this.loadFromApiOnFilterChange()
    }, this.filterApiDelayMilliseconds)
  }

  static _getStateVariableNameForFilter (filterName) {
    return `filterstate_${filterName}`
  }

  static _makeFilterValue(filterName, value) {
    if (value === undefined) {
      value = null
    }
    return {
      [AbstractFilterList._getStateVariableNameForFilter(filterName)]: value
    }
  }

  _setFilterValueInState (filterName, value, onComplete = () => {}) {
    this.setState(AbstractFilterList._makeFilterValue(filterName, value), () => {
      if (this.props.bindFiltersToQuerystring) {
        this.syncFilterValuesToQueryString(filterName, value)
      }
      this.onFilterValueSetInState(filterName, value)
      onComplete()
    })
  }

  onFilterValueSetInState (filterName, value) {}

  loadFilterValuesFromQueryString () {
    const queryString = new QueryString(window.location.search)
    let newState = {}
    let stateUpdateNeeded = false
    for (let filterName of queryString.keys()) {
      const filterSpec = this.state.componentCache.filterMap.get(filterName)
      if (filterSpec) {
        const value = filterSpec.componentClass.getValueFromQueryString(queryString, filterName)
        newState[AbstractFilterList._getStateVariableNameForFilter(filterName)] = value
        stateUpdateNeeded = true
      }
    }
    if (stateUpdateNeeded) {
      this.setState(newState)
    }
  }

  loadInitialFilterValues () {
    if (this.props.bindFiltersToQuerystring) {
      this.loadFilterValuesFromQueryString()
    }
  }

  setFilterValueInQueryString (queryString, filterName) {
    const filterSpec = this.state.componentCache.filterMap.get(filterName)
    const value = this.getFilterValue(filterName)
    if (!filterSpec.allowNullInQuerystring && (value === null || value === undefined || value === '')) {
      queryString.remove(filterName)
    } else {
      filterSpec.componentClass.setInQueryString(queryString, filterName, value, filterSpec.allowNullInQuerystring)
    }
  }

  syncFilterValuesToQueryString (changedFilterName = null, changedFilterValue = null) {
    const urlParser = new UrlParser(window.location.href)
    if (changedFilterName !== null) {
      this.setFilterValueInQueryString(urlParser.queryString, changedFilterName)
    } else {
      for (let filterName of this.state.componentCache.filterMap.keys()) {
        this.setFilterValueInQueryString(urlParser.queryString, filterName)
      }
    }
    const newUrl = urlParser.buildUrl()
    window.history.replaceState({path: newUrl}, '', newUrl)
  }

  /**
   * Set the value of a filter.
   * @param filterName The name of the filter.
   * @param value The new filter value.
   * @param {bool} noDelay Perform the API request immediately if
   *    this is `true` (see {@link AbstractFilterList#filterApiDelayMilliseconds}).
   *    Defaults to `false`.
   */
  setFilterValue (filterName, value, noDelay = false) {
    this._stopFilterApiUpdateTimer()
    this._setFilterValueInState(filterName, value, () => {
      if (noDelay) {
        this.loadFromApiOnFilterChange()
      } else {
        this._startFilterApiUpdateTimer()
      }
    })
  }

  static makeInitialFilterValues (filterSpecs, state) {
    let filter = {}
    for (let filterSpec of filterSpecs) {
      const filterKey = AbstractFilterList._getStateVariableNameForFilter(filterSpec.props.name)
      if (state[filterKey] === undefined) {
        filter = {...filter, ...AbstractFilterList._makeFilterValue(filterSpec.props.name, filterSpec.initialValue) }
      }
    }
    return filter
  }


  /**
   * Get the current value of a filter.
   *
   * @param filterName The name of the filter.
   * @returns Value of the filter.
   */
  getFilterValue (filterName) {
    return this.state[AbstractFilterList._getStateVariableNameForFilter(filterName)]
  }

  //
  //
  // List items
  //
  //

  /**
   * Get the ID of a list item from the item data.
   *
   * @param {{}} listItemData The list item data.
   * @returns {*} The ID of the list item.
   */
  getIdFromListItemData (listItemData) {
    if (this.props.idAttribute) {
      return listItemData[this.props.idAttribute]
    }
    throw new Error(
      'You have to specify the "idAttribute" prop, ' +
      'or override the getIdFromListItemData() method.')
  }

  //
  //
  // HTTP requests
  //
  //

  /**
   * Filter a list items HTTP request.
   *
   * Calls {@link AbstractFilter#filterHttpRequest}
   * on all filters.
   *
   * @param httpRequest The HTTP request.
   *    An object of the class returned by {@link AbstractFilter#getHttpRequestClass}
   */
  filterListItemsHttpRequest (httpRequest) {
    for (let filterSpec of this.state.componentCache.filterMap.values()) {
      const value = this.getFilterValue(filterSpec.props.name)
      filterSpec.componentClass.filterHttpRequest(
        httpRequest, filterSpec.props.name, value)
    }
  }

  /**
   * Get the HttpRequest class to use for the HTTP requests.
   *
   * Must return a subclass of HttpRequest from the ievv_jsbase library.
   *
   * Defaults to HttpDjangoJsonRequest.
   */
  getHttpRequestClass () {
    return HttpDjangoJsonRequest
  }

  /**
   * Add pagination options to a HTTP request.
   *
   * @param httpRequest A HTTP request object. Will always be an
   *    object of the class returned by {@link getHttpRequestClass}
   * @param {{}} paginationOptions The default implementation sets
   *    the provided options as querystring arguments.
   */
  paginateListItemsHttpRequest (httpRequest, paginationOptions) {
    if (paginationOptions) {
      httpRequest.urlParser.queryString.setValuesFromObject(paginationOptions)
    }
  }

  /**
   * Make list items HTTP request.
   *
   * @param {{}} paginationOptions Paginator options.
   * @param {bool} filter Should we filter the HTTP request using
   *    {@link AbstractFilter#filterListItemsHttpRequest}?
   *    Defaults to `true`.
   * @param {bool} paginate should we add paginationOptions using
   *    {@link AbstractFilterList#paginateListItemsHttpRequest}? Default: true
   * @returns {*} HTTP request object. An instance of the
   *    class returned by {@link AbstractFilter#getHttpRequestClass}.
   */
  makeListItemsHttpRequest (paginationOptions, filter = true, paginate = true) {
    const HttpRequestClass = this.getHttpRequestClass()
    const httpRequest = new HttpRequestClass(this.props.getItemsApiUrl)
    if (filter) {
      this.filterListItemsHttpRequest(httpRequest)
    }
    if (!paginate) {
      return httpRequest
    }
    this.paginateListItemsHttpRequest(httpRequest, paginationOptions)
    return httpRequest
  }

  getSingleItemApiUrl (listItemId) {
    return UrlParser.pathJoin(this.props.getItemsApiUrl, `${listItemId}`)
  }

  makeGetSingleItemHttpRequest (listItemId) {
    const HttpRequestClass = this.getHttpRequestClass()
    return new HttpRequestClass(this.getSingleItemApiUrl(listItemId))
  }

  /**
   * Get a human readable and user friendly load
   * items from API request error message.
   *
   * @param {Error} errorObject
   */
  getLoadItemsFromApiErrorMessage (errorObject) {
    return window.gettext('Failed to load list items from the server.')
  }

  /**
   * Update state with data about an error from a
   * load items from API http request.
   *
   * You normally want to override
   * {@link AbstractFilter#getLoadItemsFromApiErrorMessage}
   * instead of this method unless you are changing the error handling
   * completely.
   *
   * If you override this, you will need to also
   * override {@link AbstractFilter#clearLoadItemsFromApiErrorMessage}.
   *
   * @param {Error} errorObject
   */
  setLoadItemsFromApiErrorMessage (errorObject) {
    this.setState({
      loadItemsFromApiError: this.getLoadItemsFromApiErrorMessage(errorObject)
    })
  }

  /**
   * Clear the error messages set by
   * {@link AbstractFilter#setLoadItemsFromApiErrorMessage}.
   */
  clearLoadItemsFromApiErrorMessage () {
    if (this.state.loadItemsFromApiError !== null) {
      this.setState({
        loadItemsFromApiError: null
      })
    }
  }

  /**
   * Handle a failed load items from API http request.
   *
   * You normally want to override
   * {@link AbstractFilter#getLoadItemsFromApiErrorMessage}
   * instead of this method unless you are changing the error handling
   * completely.
   *
   * @param {Error} errorObject
   */
  handleGetListItemsFromApiRequestError (errorObject) {
    console.error('Error:', errorObject.toString())
    this.setLoadItemsFromApiErrorMessage(errorObject)
  }

  /**
   * Make pagination state from a HTTP response.
   *
   * The return value from this is stored in ``state.paginationState``,
   * and it is typically used in many of the methods for getting
   * pagination options ({@link getNextPagePaginationOptions},
   * {@link getPreviousPagePaginationOptions}, ...).
   *
   * @param httpResponse The HTTP response. Will always be a
   *    subclass of HttpResponse from the ievv_jsbase library.
   * @param paginationOptions The pagination options that was sent to
   *    the HTTP request.
   * @returns {object} Pagination state object defining the current pagination
   *    state.
   */
  makePaginationStateFromHttpResponse (httpResponse, paginationOptions) {
    return {}
  }

  /**
   * Get pagination options for the first paginated page.
   *
   * The returned options are used with
   * {@link AbstractFilterList#paginateListItemsHttpRequest}
   * when requesting the first page from the API.
   *
   * @param {int} paginationState The current pagination state.
   *    See {@link AbstractFilterList#makePaginationStateFromHttpResponse}
   * @returns {object|null} Pagination options. If this returns `null`,
   *     it means that no pagination options are needed to fetch the
   *     first page.
   */
  getFirstPagePaginationOptions (paginationState) {
    return null
  }

  /**
   * Get the current pagination page number.
   *
   * @param {int} paginationState The current pagination state.
   *    See {@link AbstractFilterList#makePaginationStateFromHttpResponse}
   * @returns {number}
   */
  getCurrentPaginationPage (paginationState) {
    return 1
  }

  /**
   * Get pagination options for the next page relative to the
   * currently active page.
   *
   * @param {int} paginationState The current pagination state.
   *    See {@link AbstractFilterList#makePaginationStateFromHttpResponse}
   * @returns {object|null} Pagination options. If this returns
   *    null, it means that there are no "next" page.
   */
  getNextPagePaginationOptions (paginationState) {
    return null
  }

  /**
   * Get pagination options for the previous page relative to the
   * currently active page.
   *
   * @param {int} paginationState The current pagination state.
   *    See {@link AbstractFilterList#makePaginationStateFromHttpResponse}
   * @returns {object|null} Pagination options. If this returns
   *    null, it means that there are no "previous" page.
   */
  getPreviousPagePaginationOptions (paginationState) {
    return null
  }

  /**
   * Get pagination options for a specific page number.
   *
   * @param {int} pageNumber The page number.
   * @param {int} paginationState The current pagination state.
   *    See {@link AbstractFilterList#makePaginationStateFromHttpResponse}
   *
   * @returns {object} Pagination options
   */
  getSpecificPagePaginationOptions (pageNumber, paginationState) {
    throw new Error('getSpecificPagePaginationOptions() is not implemented')
  }

  /**
   * Get the total number of available paginatable pages.
   *
   * If this returns ``null``, it means that the information
   * is not available, and paginators depending on this information
   * can not be used.
   *
   * @returns {int|null}
   */
  getPaginationPageCount (paginationState) {
    return null
  }

  /**
   * Get the total number of available list items with the current filters
   * activated.
   *
   * If this returns ``null``, it means that the information
   * is not available, and paginators depending on this information
   * can not be used.
   *
   * @returns {int|null}
   */
  getTotalListItemCount (paginationState) {
    return null
  }

  /**
   * Do we have a previous paginatable page?
   *
   * @returns {boolean}
   */
  hasPreviousPaginationPage (paginationState) {
    return this.getPreviousPagePaginationOptions(paginationState) !== null
  }

  /**
   * Do we have a next paginatable page?
   *
   * @returns {boolean}
   */
  hasNextPaginationPage (paginationState) {
    return this.getNextPagePaginationOptions(paginationState) !== null
  }

  /**
   * Get an array of list items raw data objects from an API response.
   *
   * @param httpResponse The HTTP response. Will always be a
   *    subclass of HttpResponse from the ievv_jsbase library.
   */
  getItemsArrayFromHttpResponse (httpResponse) {
    return httpResponse.bodydata.results
  }

  /**
   * Make new items state from API response.
   *
   * Parses the HTTP response, and returns an object
   * with new state variables for the list items.
   *
   * @param {{}} prevState The current state.
   * @param {{}} props The current props.
   * @param httpResponse The HTTP response. Will always be a
   *    subclass of HttpResponse from the ievv_jsbase library.
   * @param clearOldItems If this is ``true``, we replace the
   *    items displayed in the list with the items from the response.
   *    If it is ``false``, we append the new items to the items
   *    displayed in the list.
   * @returns {{}} New state variables for the list items.
   */
  makeNewItemsStateFromApiResponse (prevState, props, httpResponse, clearOldItems) {
    const newItemsArray = this.getItemsArrayFromHttpResponse(httpResponse)
    let listItemsDataArray
    let listItemsDataMap
    if (clearOldItems) {
      listItemsDataMap = new Map()
      listItemsDataArray = newItemsArray
    } else {
      prevState.listItemsDataArray.push(...newItemsArray)
      listItemsDataArray = prevState.listItemsDataArray
      listItemsDataMap = prevState.listItemsDataMap
    }
    for (let listItemData of newItemsArray) {
      const listItemId = this.getIdFromListItemData(listItemData)
      listItemsDataMap.set(listItemId, listItemData)
    }
    return {
      listItemsDataArray: listItemsDataArray,
      listItemsDataMap: listItemsDataMap
    }
  }

  /**
   * Make react state variables from a successful load items from API HTTP response.
   *
   * You should normally not need to override this method.
   * It should normally be enough to override
   * {@link makeNewItemsStateFromApiResponse}
   * and {@link makePaginationStateFromHttpResponse}
   *
   * @param {{}} prevState The current state.
   * @param {{}} props The current props.
   * @param httpResponse The HTTP response. Will always be a
   *    subclass of HttpResponse from the ievv_jsbase library.
   * @param paginationOptions Pagination options normally created
   *    with {@link getNextPagePaginationOptions},
   *    {@link getNextPagePaginationOptions}, {@link getPreviousPagePaginationOptions}
   *    or {@link getSpecificPagePaginationOptions}.
   * @param clearOldItems See {@link makeNewItemsStateFromApiResponse}.
   * @returns {object}
   */
  makeStateFromLoadItemsApiSuccessResponse (prevState, props, httpResponse, paginationOptions, clearOldItems) {
    const newItemsState = this.makeNewItemsStateFromApiResponse(
        prevState, props, httpResponse, clearOldItems)
    return {
      isLoadingNewItemsFromApi: false,
      isLoadingMoreItemsFromApi: false,
      listItemsDataArray: newItemsState.listItemsDataArray,
      listItemsDataMap: newItemsState.listItemsDataMap,
      paginationState: this.makePaginationStateFromHttpResponse(httpResponse, paginationOptions)
    }
  }

  /**
   * Update state from load items API success response.
   *
   * Called by all the `load*FromApi` methods.
   *
   * @param httpResponse The HTTP response object.
   * @param {{}} paginationOptions The pagination options used by the HTTP request.
   * @param {bool} clearOldItems Should we clear old list items and replace
   *    them with the items in the response. If this is `false`, we should
   *    append the new items.
   */
  updateStateFromLoadItemsApiSuccessResponse (httpResponse, paginationOptions, clearOldItems) {
    this.setState((prevState, props) => {
      return this.makeStateFromLoadItemsApiSuccessResponse(
        prevState, props, httpResponse, paginationOptions, clearOldItems)
    })
  }

  _makeApiRequestNumber () {
    this._apiRequestNumber ++
    return this._apiRequestNumber
  }

  /**
   * Load items from API.
   *
   * Low level method. You normally call one of
   *
   * - {@link loadMoreItemsFromApi}
   * - {@link loadNextPageFromApi}
   * - {@link loadPreviousPageFromApi}
   * - {@link loadSpecificPageFromApi}
   *
   * instead of calling this method directly.
   *
   * @param {{}} paginationOptions Paginator options.
   * @param {bool} clearOldItems
   * @returns {Promise}
   */
  loadItemsFromApi (paginationOptions, clearOldItems) {
    const apiRequestNumber = this._makeApiRequestNumber()
    this._isLoadingItemsFromApiRequestNumber = apiRequestNumber

    if (this.props.onGetListItemsFromApiRequestBegin) {
      this.props.onGetListItemsFromApiRequestBegin(this, paginationOptions, clearOldItems)
    }
    return new Promise((resolve, reject) => {
      this.clearLoadItemsFromApiErrorMessage()
      const newState = {}
      if (clearOldItems) {
        newState.isLoadingNewItemsFromApi = true
      } else {
        newState.isLoadingMoreItemsFromApi = true
      }
      this.setState(newState, () => {
        this.makeListItemsHttpRequest(paginationOptions).get()
          .then((httpResponse) => {
            if (apiRequestNumber === this._isLoadingItemsFromApiRequestNumber) {
              this._isLoadingItemsFromApiRequestNumber = null
              resolve(httpResponse)
              if (this.props.onGetListItemsFromApiRequestSuccess) {
                this.props.onGetListItemsFromApiRequestSuccess(this, httpResponse, paginationOptions, clearOldItems)
              }
            } else {
              reject({isCancelled: true})
              if (this.props.onGetListItemsFromApiRequestError) {
                this.props.onGetListItemsFromApiRequestError(this, {isCancelled: true}, paginationOptions, clearOldItems)
              }
            }
          })
          .catch((error) => {
            this._isLoadingItemsFromApiRequestNumber = null
            reject(error)
            if (this.props.onGetListItemsFromApiRequestError) {
              this.props.onGetListItemsFromApiRequestError(this, error, paginationOptions, clearOldItems)
            }
          })
      })
    })
  }

  /**
   * Load first page from the API.
   *
   * Loaded items replaces all items currently in the list.
   */
  loadFirstPageFromApi () {
    const paginationOptions = this.getFirstPagePaginationOptions()
    this.loadItemsFromApi(paginationOptions, true)
      .then((httpResponse) => {
        this.updateStateFromLoadItemsApiSuccessResponse(
          httpResponse, paginationOptions, true)
      })
      .catch((error) => {
        if (!error.isCancelled) {
          this.handleGetListItemsFromApiRequestError(error)
        }
      })
  }

  /**
   * Called when filter values changes to load new items from the API.
   *
   * By default, this is just an alias for
   * {@link AbstractFilterList#loadFirstPageFromApi}.
   */
  loadFromApiOnFilterChange () {
    this.loadFirstPageFromApi()
  }

  /**
   * Load more items from the API.
   *
   * Intended for _Load more_ buttons, and infinite scroll
   * implementations.
   *
   * Loaded items are appended at the end of the list.
   */
  loadMoreItemsFromApi () {
    const paginationOptions = this.getNextPagePaginationOptions(this.state.paginationState)
    this.loadItemsFromApi(paginationOptions, false)
      .then((httpResponse) => {
        this.updateStateFromLoadItemsApiSuccessResponse(
          httpResponse, paginationOptions, false)
      })
      .catch((error) => {
        if (!error.isCancelled) {
          this.handleGetListItemsFromApiRequestError(error)
        }
      })
  }

  /**
   * Load the next paginated "page" of items from the API.
   *
   * Intended to be used along with {@link loadPreviousPageFromApi} by
   * paginators with _Next_ and _Previous_ page buttons.
   *
   * Loaded items replace the current items in the list.
   */
  loadNextPageFromApi () {
    const paginationOptions = this.getNextPagePaginationOptions(this.state.paginationState)
    this.loadItemsFromApi(paginationOptions, true)
      .then((httpResponse) => {
        this.updateStateFromLoadItemsApiSuccessResponse(
          httpResponse, paginationOptions, true)
      })
      .catch((error) => {
        if (!error.isCancelled) {
          this.handleGetListItemsFromApiRequestError(error)
        }
      })
  }

  /**
   * Load the previous paginated "page" of items from the API.
   *
   * Intended to be used along with {@link loadNextPageFromApi} by
   * paginators with _Next_ and _Previous_ page buttons.
   *
   * Loaded items replace the current items in the list.
   */
  loadPreviousPageFromApi () {
    const paginationOptions = this.getPreviousPagePaginationOptions(this.state.paginationState)
    this.loadItemsFromApi(paginationOptions, true)
      .then((httpResponse) => {
        this.updateStateFromLoadItemsApiSuccessResponse(
          httpResponse, paginationOptions, true)
      })
      .catch((error) => {
        if (!error.isCancelled) {
          this.handleGetListItemsFromApiRequestError(error)
        }
      })
  }

  /**
   * Load a specific paginated "page" of items from the API.
   *
   * Intended to be used by paginators that use {@link getPaginationPageCount}
   * to render links to specific paginated pages.
   *
   * Loaded items replace the current items in the list.
   */
  loadSpecificPageFromApi (pageNumber) {
    const paginationOptions = this.getSpecificPagePaginationOptions(
      pageNumber, this.state.paginationState)
    this.loadItemsFromApi(paginationOptions, true)
      .then((httpResponse) => {
        this.updateStateFromLoadItemsApiSuccessResponse(
          httpResponse, paginationOptions, true)
      })
      .catch((error) => {
        if (!error.isCancelled) {
          this.handleGetListItemsFromApiRequestError(error)
        }
      })
  }

  //
  //
  // Rendering
  //
  //

  /**
   * Get props for a layout component.
   *
   * Used by {@link AbstractFilterList#renderLayoutComponent}.
   *
   * @param {LayoutComponentSpec} layoutComponentSpec The layout component spec
   * @returns {{}} Props for the layout component.
   */
  getLayoutComponentProps (layoutComponentSpec) {
    return Object.assign({}, layoutComponentSpec.props, {
      key: layoutComponentSpec.props.uniqueComponentKey,
      childExposedApi: this.childExposedApi,
      listItemsDataArray: this.state.listItemsDataArray,
      listItemsDataMap: this.state.listItemsDataMap,
      selectedListItemsMap: this.state.selectedListItemsMap,
      enabledComponentGroups: this.state.enabledComponentGroups,
      isLoadingNewItemsFromApi: this.state.isLoadingNewItemsFromApi,
      isLoadingMoreItemsFromApi: this.state.isLoadingMoreItemsFromApi,
      selectMode: this.state.selectMode,
      movingListItem: this.state.movingListItem,
      allListItemMovementIsLocked: this.state.allListItemMovementIsLocked
    })
  }

  /**
   * Should we render the provided layout component?
   *
   * Uses {@link AbstractFilterList#componentGroupsIsEnabled} to determine
   * if the component should be rendered.
   *
   * @param {LayoutComponentSpec} layoutComponentSpec A layout component spec.
   * @returns {bool}
   */
  shouldRenderLayoutComponentSpec (layoutComponentSpec) {
    return this.componentGroupsIsEnabled(layoutComponentSpec.props.componentGroups)
  }

  /**
   * Render a layout component.
   *
   * @param {LayoutComponentSpec} layoutComponentSpec A layout component spec.
   * @returns {null|React.Element}
   */
  renderLayoutComponent (layoutComponentSpec) {
    if (!this.shouldRenderLayoutComponentSpec(layoutComponentSpec)) {
      return null
    }
    return React.createElement(
      layoutComponentSpec.componentClass,
      this.getLayoutComponentProps(layoutComponentSpec))
  }

  renderComponents () {
    const renderedComponents = []
    for (let layoutComponentSpec of this.state.componentCache.layoutComponentSpecs) {
      renderedComponents.push(this.renderLayoutComponent(layoutComponentSpec))
    }
    return renderedComponents
  }

  loadSingleItemDataFromApi (listItemId) {
    return new Promise((resolve, reject) => {
      this.makeGetSingleItemHttpRequest(listItemId)
        .get()
        .then((httpResponse) => {
          resolve({
            status: httpResponse.status,
            data: httpResponse.bodydata,
            listItemId: listItemId
          })
        })
        .catch((error) => {
          if (error.response.isClientError()) {
            resolve({
              status: error.response.status,
              error: error,
              listItemId: listItemId
            })
          } else {
            reject(error)
          }
        })
    })
  }

  loadMultipleItemDataFromApi (listItemIds) {
    return new Promise((resolve, reject) => {
      const allPromises = []
      for (let listItemId of listItemIds) {
        allPromises.push(this.loadSingleItemDataFromApi(listItemId))
      }
      Promise.all(allPromises)
        .then((listItemDataArray) => {
          resolve(listItemDataArray)
        })
        .catch((error) => {
          reject(error)
        })
    })
  }

  render () {
    if (this.state.isLoadingSelectedItemDataFromApi) {
      return <LoadingIndicator />
    } else {
      return <div className={this.props.className}>
        {this.renderComponents()}
      </div>
    }
  }
}
