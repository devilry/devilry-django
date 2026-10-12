import React from 'react'
import PropTypes from 'prop-types'
import BemUtilities from '../../utilities/BemUtilities'

export default class TimeDisplay extends React.Component {
  static get defaultProps () {
    return {
      momentObject: null,
      showSeconds: false,
      bemBlock: 'timedisplay',
      bemVariants: []
    }
  }

  static get propTypes () {
    return {
      momentObject: PropTypes.any.isRequired,
      showSeconds: PropTypes.bool.isRequired,
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    }
  }

  get className () {
    return BemUtilities.addVariants(this.props.bemBlock, this.props.bemVariants)
  }

  get separatorClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'separator')
  }

  get numberClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'number')
  }

  renderSeparator (key) {
    return <span key={key} className={this.separatorClassName}>:</span>
  }

  renderNumber (key, number) {
    return <span key={key} className={this.numberClassName}>{number}</span>
  }

  renderHours () {
    return this.renderNumber('hours', this.props.momentObject.format('HH'))
  }

  renderMinutes () {
    return this.renderNumber('minutes', this.props.momentObject.format('mm'))
  }

  renderSeconds () {
    return this.renderNumber('seconds', this.props.momentObject.format('ss'))
  }

  renderNumbers () {
    const renderedNumbers = [
      this.renderHours(),
      this.renderSeparator('separator1'),
      this.renderMinutes()
    ]
    if (this.props.showSeconds) {
      renderedNumbers.push(this.renderSeparator('separator2'))
      renderedNumbers.push(this.renderSeconds())
    }
    return renderedNumbers
  }

  render () {
    return <span className={this.className}>
      {this.renderNumbers()}
    </span>
  }
}
