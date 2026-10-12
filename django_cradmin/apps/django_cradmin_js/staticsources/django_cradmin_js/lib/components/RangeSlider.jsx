import React from 'react'
import PropTypes from 'prop-types'
import BemUtilities from '../utilities/BemUtilities'

export default class RangeSlider extends React.Component {
  static get defaultProps () {
    return {
      bemBlock: 'range-input',
      bemVariants: [],
      min: 0,
      max: null,
      value: 0,
      onChange: null
    }
  }

  static get propTypes () {
    return {
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      min: PropTypes.number.isRequired,
      max: PropTypes.number.isRequired,
      value: PropTypes.number.isRequired,
      onChange: PropTypes.func.isRequired
    }
  }

  get className () {
    return BemUtilities.addVariants(this.props.bemBlock, this.props.bemVariants)
  }

  handleChange (e) {
    const value = parseInt(e.target.value, 10)
    this.props.onChange(value)
  }

  render () {
    return <input
      type={'range'}
      className={this.className}
      min={this.props.min} max={this.props.max}
      value={this.props.value}
      onChange={this.handleChange.bind(this)}
    />
  }
}
