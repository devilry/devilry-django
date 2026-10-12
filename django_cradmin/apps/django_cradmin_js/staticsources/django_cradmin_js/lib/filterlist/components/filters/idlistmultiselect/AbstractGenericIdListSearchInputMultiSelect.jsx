import React from 'react'
import PropTypes from 'prop-types'
import AbstractSearchInputFilter from '../AbstractSearchInputFilter'
import * as reduxApiUtilities from 'ievv_jsbase/lib/utils/reduxApiUtilities'
import LoadingIndicator from '../../../../components/LoadingIndicator'

export default class AbstractGeneridIdListSearchInputMultiSelect extends AbstractSearchInputFilter {
  static get propTypes () {
    return {
      ...super.propTypes,
      idListItemMap: PropTypes.object,
      getIdListItemAction: PropTypes.func
    }
  }

  static get defaultProps () {
    return {
      ...super.defaultProps,
      idListItemMap: new Map(),
      getIdListItemAction: () => {
        console.warn('getIdListItemAction not given in props!')
        return null
      }
    }
  }

  getInitialState () {
    return {
      ...super.getInitialState(),
      hasAllReduxData: false
    }
  }

  get idListItemNotFoundFallback () {
    return new Map()
  }

  getLabelForId (id) {
    console.warn('Should be overridden in subclass')
    return id
  }

  deselectItemById (id) {
    this.props.childExposedApi.deselectItems([id])
  }

  renderSelected (id) {
    return <span key={`selected-${id}`} className={'searchinput__selected'}>
      <span className={'searchinput__selected_preview searchinput__selected_preview--with-deselect'}>
        {this.getLabelForId(parseInt(id))}
      </span>
      <button
        type={'button'}
        className={'searchinput__deselect'}
        onClick={() => { this.deselectItemById(id) }}>
        <i className={'searchinput__deselect_icon cricon cricon--close cricon--color-light'} />
      </button>
    </span>
  }

  renderSelectedValues () {
    if (!this.state.hasAllReduxData) {
      return <LoadingIndicator />
    }
    return this.props.childExposedApi.selectedItemIdsAsArray().map(id => this.renderSelected(id))
  }

  renderBodyContent () {
    return <React.Fragment>
      {this.renderSelectedValues()}
      {super.renderBodyContent()}
    </React.Fragment>
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
      for (const id of nextProps.childExposedApi.selectedItemIdsAsArray()) {
        const idListItem = reduxApiUtilities.getObjectFromReduxMapOrNullIfLoading(
          nextProps.idListItemMap,
          parseInt(id),
          nextProps.getIdListItemAction,
          nextProps.dispatch
        )
        if (idListItem === null) {
          hasAllReduxData = false
        }
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
