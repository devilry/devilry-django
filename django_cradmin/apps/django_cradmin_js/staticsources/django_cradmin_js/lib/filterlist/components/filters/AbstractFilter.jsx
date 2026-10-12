import React from 'react'
import PropTypes from 'prop-types'
import AbstractLayoutComponentChild from '../AbstractLayoutComponentChild'

/**
 * Base class for filter components.
 *
 * See {@link AbstractFilter.defaultProps} for documentation for
 * props and their defaults.
 */
export default class AbstractFilter extends AbstractLayoutComponentChild {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      name: PropTypes.string.isRequired,
      isStatic: PropTypes.bool,
      value: PropTypes.any,
      selectedListItemsMap: PropTypes.instanceOf(Map).isRequired
    })
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractLayoutComponentChild.defaultProps}.
   *
   * @return {Object}
   * @property {string} name The name of the filter.
   *    This is required, and defaults to `null`.
   *    **Must be be provided in spec**.
   * @property {bool} isStatic If this is `true`, the filter is not rendered,
   *    but API requests is always filtered by the value specified for the
   *    filter in the `initialValue` attribute of the spec for the filter.
   *    Defaults to `false`.
   *    **Can be used in spec**.
   * @property {*} value The current value of the filter.
   *    _Provided automatically by the parent component_.
   * @property {Map} selectedListItemsMap Map of selected items
   *    (maps ID to item data).
   *    _Provided automatically by the parent component_.
   */
  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      name: null,
      isStatic: false,
      value: null,
      selectedListItemsMap: null
    })
  }

  /**
   * Filter the provided HTTP request.
   *
   * Defaults to setting `<name>=<value>` is the querystring.
   * Non-trivial filters will need to override this.
   *
   * @param httpRequest The HTTP request.
   *    An object of the class returned by {@link AbstractFilter#getHttpRequestClass}
   * @param name The name of the filter. Will be the same as
   *    `props.name`.
   * @param value The current value of the filter.
   */
  static filterHttpRequest (httpRequest, name, value) {
    httpRequest.urlParser.queryString.setSmart(name, value)
  }

  static setInQueryString (queryString, name, value, allowNullInQuerystring = false) {
    if (!allowNullInQuerystring && value === null) {
      return
    }
    queryString.setSmart(name, value)
  }

  static getValueFromQueryString (queryString, name) {
    return queryString.getSmart(name, null)
  }

  /**
   * Should the filter receive selected items?
   *
   * If this returns ``true``, the component will receive
   * ``selectedListItemsMap`` as a prop. This also means
   * that the filter will re-render when selected items
   * change.
   *
   * ``selectedListItemsMap`` is a Map of selected items
   * that maps ID to item data.
   *
   * @param {FilterComponentSpec} componentSpec The component spec.
   * @returns {boolean}
   */
  static shouldReceiveSelectedItems (componentSpec) {
    return false
  }

  constructor (props) {
    super(props)
    this.state = this.getInitialState()
  }

  /**
   * Get the initial state for the filter.
   *
   * Ment to be overridden in subclasses to provide a uniform
   * way of setting initial state for filters that require state.
   *
   * @returns {{}}
   */
  getInitialState () {
    return {}
  }

  /**
   * Setup bound methods.
   *
   * Calls {@link AbstractFilterListChild#setupBoundMethods}, and
   * binds {@link AbstractFilter#setFilterValue}
   * to ``this` by default, but you can override this
   * method to bind more methods. In that case, ensure
   * you call `super.setupBoundMethods()`!
   */
  setupBoundMethods () {
    super.setupBoundMethods()
    this.setFilterValue = this.setFilterValue.bind(this)
  }

  /**
   * Set the value of the filter.
   *
   * If you set complex objects as value (array, object, map, set, ...),
   * you will need to override {@link AbstractFilter#filterHttpRequest}.
   *
   * @param value The value to set.
   */
  setFilterValue (value) {
    this.props.childExposedApi.setFilterValue(this.props.name, value)
  }

  get ariaProps () {
    let controlsDomIds = []
    for (const componentSpec of this.props.childExposedApi.listComponentSpecs) {
      controlsDomIds.push(componentSpec.props.domIdPrefix)
    }
    return {
      'aria-controls': controlsDomIds.join(' ')
    }
  }
}
