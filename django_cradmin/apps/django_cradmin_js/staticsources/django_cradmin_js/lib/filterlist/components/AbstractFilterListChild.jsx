import React from 'react'
import PropTypes from 'prop-types'

/**
 * Base class for all child components of {@link AbstractFilterList}.
 *
 * See {@link AbstractFilterListChild.defaultProps} for documentation for
 * props and their defaults.
 */
export default class AbstractFilterListChild extends React.Component {
  static get propTypes () {
    return {
      childExposedApi: PropTypes.object.isRequired,
      willReceiveFocusEvents: PropTypes.bool.isRequired,
      willReceiveSelectionEvents: PropTypes.bool.isRequired,
      componentGroups: PropTypes.arrayOf(PropTypes.string),
      uniqueComponentKey: PropTypes.string.isRequired,
      domIdPrefix: PropTypes.string.isRequired,
      isMovingListItemId: PropTypes.any,
      allListItemMovementIsLocked: PropTypes.bool.isRequired,
      selectMode: PropTypes.string
    }
  }

  /**
   * Get default props.
   *
   * @return {Object}
   * @property {ChildExposedApi} childExposedApi Object with public methods from
   *    {@link AbstractFilterList}.
   *    _Provided automatically by the parent component_.
   * @property {string} uniqueComponentKey A unique key for this component
   *    instance.
   *    _Provided automatically by the parent component_.
   * @property {[string]|null} componentGroups The groups this component belongs to.
   *    See {@link AbstractFilterList#toggleComponentGroup}.
   *    **Can be used in spec**.
   * @property {string} domIdPrefix DOM id prefix.
   *    _Provided automatically_.
   */
  static get defaultProps () {
    return {
      childExposedApi: null,
      componentGroups: null,
      willReceiveFocusEvents: false,
      willReceiveSelectionEvents: false,
      domIdPrefix: null,
      isMovingListItemId: null,
      allListItemMovementIsLocked: false,
      selectMode: null
    }
  }

  /**
   * Does the component listen to focus changes?
   *
   * If this returns ``true``, the component will receive
   * onFocus and onBlur events.
   *
   * @param {AbstractComponentSpec} componentSpec The component spec.
   * @returns {boolean}
   */
  static shouldReceiveFocusEvents (componentSpec) {
    return false
  }

  // /**
  //  * The focus groups this item belongs to.
  //  *
  //  * @param {AbstractComponentSpec} componentSpec The component spec.
  //  * @returns {[]} Array of focus groups.
  //  */
  // static getKeyboardNavigationGroups (componentSpec) {
  //   return []
  // }

  constructor (props) {
    super(props)
    this.setupBoundMethods()
    this.state = {}
  }

  get domIdPrefix () {
    return this.props.domIdPrefix
  }

  makeDomId (domIdSuffix = null) {
    if (domIdSuffix) {
      return `${this.domIdPrefix}-${domIdSuffix}`
    }
    return this.domIdPrefix
  }

  /**
   * Make sure you call super.componentWillUnmount() if you override this.
   */
  componentWillUnmount () {
    if (this.props.willReceiveFocusEvents) {
      this.props.childExposedApi.unregisterFocusChangeListener(this)
    }
    if (this.props.willReceiveSelectionEvents) {
      this.props.childExposedApi.unregisterSelectionChangeListener(this)
    }
  }

  /**
   * Make sure you call super.componentWillUnmount() if you override this.
   */
  componentDidMount () {
    if (this.props.willReceiveFocusEvents) {
      this.props.childExposedApi.registerFocusChangeListener(this)
    }
    if (this.props.willReceiveSelectionEvents) {
      this.props.childExposedApi.registerSelectionChangeListener(this)
    }
  }

  /**
   * Setup bound methods.
   *
   * Binds {@link AbstractFilter#onFocus} and {@link AbstractFilter#onBlur}
   * to ``this` by default, but you can override this
   * method to bind more methods. In that case, ensure
   * you call `super.setupBoundMethods()`!
   */
  setupBoundMethods () {
    this.onFocus = this.onFocus.bind(this)
    this.onBlur = this.onBlur.bind(this)
    this.onAnyComponentFocus = this.onAnyComponentFocus.bind(this)
    this.onAnyComponentBlur = this.onAnyComponentBlur.bind(this)
  }

  /**
   * See {@link AbstractFilterListChild#onBlur} and {@link AbstractFilterListChild#onFocus}.
   *
   * @return {{}} An object with information about this component relevant
   *    for blur/focus management.
   */
  getBlurFocusCallbackInfo () {
    return {
      uniqueComponentKey: this.props.uniqueComponentKey,
      componentGroups: this.props.componentGroups
    }
  }

  /**
   * Should be called when the component looses focus.
   *
   * By default this calls AbstractFilterList#onChildBlur with the
   * information from AbstractFilterListChild#getBlurFocusCallbackInfo.
   */
  onBlur () {
    this.props.childExposedApi.onChildBlur(this.getBlurFocusCallbackInfo())
  }

  /**
   * Should be called when the component gains focus.
   *
   * By default this calls AbstractFilterList#onChildFocus with the
   * information from AbstractFilterListChild#getBlurFocusCallbackInfo.
   */
  onFocus () {
    this.props.childExposedApi.onChildFocus(this.getBlurFocusCallbackInfo())
  }

  onAnyComponentFocus (newFocusComponentInfo, prevFocusComponentInfo, didChangeFilterListFocus) {
  }

  onAnyComponentBlur (blurredComponentInfo, didChangeFilterListFocus) {
  }

  onSelectItems (listItemIds) {
  }

  onDeselectItems (listItemIds) {
  }

  getComponentGroupsForChildComponent (componentSpec) {
    if (this.props.componentGroups === null) {
      return componentSpec.props.componentGroups
    }
    if (componentSpec.props.componentGroups === null) {
      return this.props.componentGroups
    }
    return this.props.componentGroups.concat(componentSpec.props.componentGroups)
  }

  /**
   * Make props for child components that is also a subclass
   * of AbstractFilterListChild.
   *
   * @param {AbstractComponentSpec} componentSpec The spec for the child component.
   * @param {{}} extraProps Extra props. These will not override any props
   *    set by default.
   * @returns {{}} Object with child component props.
   */
  makeChildComponentProps (componentSpec, extraProps) {
    return Object.assign({}, extraProps, {
      childExposedApi: this.props.childExposedApi,
      componentGroups: this.getComponentGroupsForChildComponent(componentSpec),
      selectMode: this.props.selectMode,
      isMovingListItemId: this.props.isMovingListItemId,
      allListItemMovementIsLocked: this.props.allListItemMovementIsLocked
    })
  }
}
