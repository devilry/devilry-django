import React from 'react'
import PropTypes from 'prop-types'
import * as reduxApiUtilities from 'ievv_jsbase/lib/utils/reduxApiUtilities'
import CenteredLoadingIndicator from '../../../../components/CenteredLoadingIndicator'
import BemUtilities from '../../../../utilities/BemUtilities'
/**
 * Generic IdListMultiselectItem. You need to subclass this when using {@link GenericIdListMultiSelectFilter} and
 * override renderContents.
 *
 * You will also need to use redux' `connect` and make a function like {@link abstractIdListItemMapStateToProps} to map
 * `idListItemMap` and `getIdListItemAction`.
 *
 * If your redux-structure is not compatible with the one build by {@link reduxApiUtilities}, or you are not using redux
 * at all, you will also need to override {@link getDerivedStateFromProps}.
 */
export default class AbstractGenericIdListMultiSelectItem extends React.Component {
  static get propTypes () {
    return {
      id: PropTypes.number.isRequired,
      idListItemMap: PropTypes.object.isRequired,
      getIdListItemAction: PropTypes.func.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string.isRequired)
    }
  }

  static get defaultProps () {
    return {
      idListItemMap: new Map(),
      selectedValues: [],
      getIdListItemAction: () => {
        console.warn('getIdListItemAction not given in props!')
        return null
      },
      bemVariants: ['outlined']
    }
  }

  constructor (props) {
    super(props)

    this.state = this.makeInitialState()
    this.setupBoundFunctions()
  }

  /**
   * make and return the initial React-state. Defaults to `{hasAllReduxData: false}`
   */
  makeInitialState () {
    return {
      hasAllReduxData: false
    }
  }

  /**
   * only here to be overridden. A place to setup bound functions
   */
  setupBoundFunctions () {
    this.handleOnClick = this.handleOnClick.bind(this)
  }

  handleOnClick () {
    if (this.isSelected) {
      this.props.childExposedApi.deselectItems([this.props.id])
    } else {
      this.props.childExposedApi.selectItems([this.props.id])
    }
  }

  /**
   * Override this to use something other than `null` as a fallback if `this.props.id` is not found in
   * `this.props.idListItemMap`.
   * @return {null}
   */
  get idListItemNotFoundFallback () {
    return null
  }

  /**
   * Util to get idListItem.
   *
   * @return {*} lookup for `[this.props.id, 'data']` in `this.props.idListItemMap`, or
   *    `this.idListItemNotFoundFallback` if not found.
   */
  get idListItem () {
    return this.props.idListItemMap.getIn([this.props.id, 'data'], this.idListItemNotFoundFallback)
  }

  /**
   * Is the component selected
   *
   * @return {boolean} true if item is selected, false otherwise
   */
  get isSelected () {
    return this.props.childExposedApi.selectedItemIdsAsArray().includes(this.props.id)
  }

  get elementVariants () {
    return this.props.bemVariants
  }

  get elementClassName () {
    let variants = this.elementVariants
    if (this.isSelected) {
      variants = [...variants, 'selected']
    }
    return BemUtilities.buildBemElement('selectable-list', 'item', variants)
  }

  getLabel () {
    console.warn('getLabel: Should be overridden by subclass of AbstractIdGenericListMultiselectItem')
    return null
  }

  renderContent () {
    return this.getLabel()
  }

  renderContents () {
    return <button className={this.elementClassName}
      onClick={this.handleOnClick}>
      <div className={'selectable-list__icon'}>
        {this.isSelected ? <i className={'cricon cricon--check cricon--color-light'} /> : null}
      </div>
      <span className={'selectable-list__itemcontent'}>
        {this.renderContent()}
      </span>
    </button>
  }

  renderLoadingIndicator () {
    return <CenteredLoadingIndicator />
  }

  render () {
    if (!this.state.hasAllReduxData) {
      return this.renderLoadingIndicator()
    }
    return this.renderContents()
  }

  static getDerivedStateFromProps (nextProps, prevState) {
    let nextState = null
    let hasAllReduxData = true

    function setValueInNextState (valueObject) {
      nextState = {
        ...(nextState === null ? {} : nextState),
        ...valueObject
      }
    }

    function ensureIdListItemInStore () {
      const idListItem = reduxApiUtilities.getObjectFromReduxMapOrNullIfLoading(
        nextProps.idListItemMap,
        nextProps.id,
        nextProps.getIdListItemAction,
        nextProps.dispatch
      )
      if (idListItem === null) {
        hasAllReduxData = false
      }
    }

    ensureIdListItemInStore()

    if (hasAllReduxData !== prevState.hasAllReduxData) {
      setValueInNextState({ hasAllReduxData })
    }

    return nextState
  }
}

/**
 * example mapStateToProps in order to use {@link AbstractGenericIdListMultiSelectItem}.
 *
 * @param state redux-state
 * @return {{getIdListItemAction: null, idListItemMap: never, idListItemId: *}}
 */
export function abstractIdListItemMapStateToProps (state) {
  return {
    idListItemMap: new Map(),
    getIdListItemAction: null
  }
}
