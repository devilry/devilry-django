import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilterListChild from '../AbstractFilterListChild'

export default class AbstractListItem extends AbstractFilterListChild {
  static get propTypes () {
    return {
      listItemId: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number
      ]).isRequired,
      isSelected: PropTypes.bool
    }
  }

  static get defaultProps () {
    return {
      listItemId: null,
      isSelected: false
    }
  }

  get domIdPrefix () {
    return `${this.props.domIdPrefix}${this.props.listItemId}`
  }
}
