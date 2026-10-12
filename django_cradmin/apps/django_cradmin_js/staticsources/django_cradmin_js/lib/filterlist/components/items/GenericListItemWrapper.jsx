import React from 'react'
import PropTypes from 'prop-types'
import AbstractListItem from './AbstractListItem'

export default class GenericListItemWrapper extends AbstractListItem {
  static get propTypes () {
    return {
      ...super.propTypes,
      componentType: PropTypes.func.isRequired,
      componentProps: PropTypes.object,
      listItemIdName: PropTypes.string.isRequired
    }
  }

  static get defaultProps () {
    return {
      ...super.defaultProps,
      componentType: null,
      componentProps: {},
      listItemIdName: null
    }
  }

  render () {
    const {componentProps, listItemIdName, listItemId, componentType, ...otherProps} = this.props
    const Type = componentType
    const props = {
      [listItemIdName]: listItemId,
      listItemId,
      ...componentProps,
      ...otherProps
    }
    return <Type {...props} />
  }
}
