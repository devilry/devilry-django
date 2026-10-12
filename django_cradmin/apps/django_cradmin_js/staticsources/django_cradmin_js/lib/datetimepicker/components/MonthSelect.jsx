import React from 'react'
import PropTypes from 'prop-types'
import BemUtilities from '../../utilities/BemUtilities'
import * as gettext from 'ievv_jsbase/lib/gettext'
import MomentRange from '../../utilities/MomentRange'

export default class MonthSelect extends React.Component {
  static get defaultProps () {
    return {
      bemBlock: 'select',
      bemVariants: ['outlined', 'size-xsmall', 'width-xxsmall'],
      ariaLabel: gettext.gettext('Month'),
      momentObject: null,
      momentRange: null,
      onChange: null,
      ariaDescribedByDomId: null
    }
  }

  static get propTypes () {
    return {
      momentObject: PropTypes.any.isRequired,
      momentRange: PropTypes.instanceOf(MomentRange).isRequired,
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      ariaLabel: PropTypes.string.isRequired,
      onChange: PropTypes.func,
      ariaDescribedByDomId: PropTypes.string.isRequired
    }
  }

  get className () {
    return BemUtilities.addVariants(this.props.bemBlock, this.props.bemVariants)
  }

  get selectedMonth () {
    return this.props.momentObject.month()
  }

  isValidMonth (monthMomentObject) {
    return this.props.momentRange.contains(monthMomentObject)
  }

  renderMonthAriaLabel (monthMomentObject) {
    return monthMomentObject.format('MMMM YYYY')
  }

  renderMonthLabel (monthMomentObject) {
    return monthMomentObject.format('MMM')
  }

  renderMonth (monthMomentObject) {
    return <option
      key={monthMomentObject.format()}
      value={monthMomentObject.month()}
      disabled={!this.isValidMonth(monthMomentObject)}
      aria-label={this.renderMonthAriaLabel(monthMomentObject)}
    >
      {this.renderMonthLabel(monthMomentObject)}
    </option>
  }

  makeMomentForMonthNumber (monthNumber) {
    return this.props.momentObject.clone().month(monthNumber)
  }

  renderMonths () {
    const renderedMonths = []
    let monthNumber = 0
    while (monthNumber < 12) {
      const monthMomentObject = this.makeMomentForMonthNumber(monthNumber)
      renderedMonths.push(this.renderMonth(monthMomentObject))
      monthNumber++
    }
    return renderedMonths
  }

  handleChange (e) {
    const value = parseInt(e.target.value, 10)
    if (this.props.onChange) {
      this.props.onChange(value)
    }
  }

  render () {
    return <label className={this.className}>
      <select
        aria-label={this.props.ariaLabel}
        value={this.selectedMonth}
        onChange={this.handleChange.bind(this)}
        aria-describedby={this.props.ariaDescribedByDomId}
      >
        {this.renderMonths()}
      </select>
    </label>
  }
}
