import React from 'react'
import PropTypes from 'prop-types'
import BemUtilities from '../../utilities/BemUtilities'
import * as gettext from 'ievv_jsbase/lib/gettext'
import MomentRange from '../../utilities/MomentRange'

export default class YearSelect extends React.Component {
  static get defaultProps () {
    return {
      selectBemBlock: 'select',
      selectBemVariants: ['outlined', 'size-xsmall', 'width-xxsmall'],
      inputBemBlock: 'input',
      inputBemVariants: ['outlined', 'inline', 'size-xsmall', 'width-xxsmall'],
      ariaLabel: gettext.gettext('Year'),
      momentObject: null,
      momentRange: null,
      onChange: null,
      renderAsInputThreshold: 200,
      ariaDescribedByDomId: null
    }
  }

  static get propTypes () {
    return {
      momentObject: PropTypes.any.isRequired,
      momentRange: PropTypes.instanceOf(MomentRange).isRequired,
      selectBemBlock: PropTypes.string.isRequired,
      selectBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      ariaLabel: PropTypes.string.isRequired,
      onChange: PropTypes.func,
      ariaDescribedByDomId: PropTypes.string.isRequired
    }
  }

  get selectClassName () {
    return BemUtilities.addVariants(this.props.selectBemBlock, this.props.selectBemVariants)
  }

  get inputClassName () {
    return BemUtilities.addVariants(this.props.inputBemBlock, this.props.inputBemVariants)
  }

  get minYear () {
    return this.props.momentRange.start.year()
  }

  get maxYear () {
    return this.props.momentRange.end.year()
  }

  get selectedYear () {
    return this.props.momentObject.year()
  }

  renderYear (year) {
    return <option key={year} value={year} aria-label={year} aria-describedby={this.props.ariaDescribedByDomId}>
      {year}
    </option>
  }

  renderYears () {
    let year = this.minYear
    let renderedYears = []
    while (year <= this.maxYear) {
      renderedYears.push(this.renderYear(year))
      year += 1
    }
    return renderedYears
  }

  handleSelectChange (e) {
    const value = parseInt(e.target.value, 10)
    if (this.props.onChange) {
      this.props.onChange(value)
    }
  }

  handleInputChange (e) {
    const value = parseInt(e.target.value, 10)
    if (this.props.onChange) {
      this.props.onChange(value)
    }
  }

  shouldRenderAsSelect () {
    return (this.maxYear - this.minYear) <= this.props.renderAsInputThreshold
  }

  renderAsSelect () {
    return <label className={this.selectClassName}>
      <select
        aria-label={this.props.ariaLabel}
        value={this.selectedYear}
        onChange={this.handleSelectChange.bind(this)}
        aria-describedby={this.props.ariaDescribedByDomId}
      >
        {this.renderYears()}
      </select>
    </label>
  }

  renderAsInput () {
    return <input
      className={this.inputClassName}
      onChange={this.handleInputChange.bind(this)}
      value={this.selectedYear}
      aria-describedby={this.props.ariaDescribedByDomId}
    />
  }

  render () {
    if (this.shouldRenderAsSelect()) {
      return this.renderAsSelect()
    }
    return this.renderAsInput()
  }
}
