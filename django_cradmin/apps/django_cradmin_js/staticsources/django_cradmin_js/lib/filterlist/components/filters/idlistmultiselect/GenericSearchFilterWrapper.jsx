import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilter from '../AbstractFilter'

/**
 * This is a hack to make FilterList accept redux Connected Component, should discuss this with Espen
 */
export default class GenericSearchFilterWrapper extends AbstractFilter {
  static get propTypes () {
    return {
      ...super.propTypes,
      componentType: PropTypes.func.isRequired
    }
  }

  render () {
    const Type = this.props.componentType
    const {componentType, ...props} = this.props
    return <Type {...props} />
  }
}
