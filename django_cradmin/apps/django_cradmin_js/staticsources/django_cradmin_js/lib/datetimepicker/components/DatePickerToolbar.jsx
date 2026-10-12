import React from 'react'
import PropTypes from 'prop-types'
import BemUtilities from '../../utilities/BemUtilities'
import * as gettext from 'ievv_jsbase/lib/gettext'
import YearSelect from './YearSelect'
import MonthSelect from './MonthSelect'
import MomentRange from '../../utilities/MomentRange'

export default class DatePickerToolbar extends React.Component {
  static get defaultProps () {
    return {
      momentObject: null,
      momentRange: null,
      bemBlock: 'paginator',
      bemVariants: [],
      buttonBemVariants: [],
      leftButtonIcon: 'chevron-left',
      rightButtonIcon: 'chevron-right',
      buttonIconBemVariants: [],
      leftButtonTitle: gettext.gettext('Previous'),
      rightButtonTitle: gettext.gettext('Next'),
      onPrevMonth: null,
      onNextMonth: null,
      onMonthSelect: null,
      onYearSelect: null,
      ariaDescribedByDomId: null
    }
  }

  static get propTypes () {
    return {
      momentObject: PropTypes.any.isRequired,
      momentRange: PropTypes.instanceOf(MomentRange).isRequired,
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      buttonBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      leftButtonIcon: PropTypes.string.isRequired,
      rightButtonIcon: PropTypes.string.isRequired,
      buttonIconBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      leftButtonTitle: PropTypes.string.isRequired,
      rightButtonTitle: PropTypes.string.isRequired,
      onPrevMonth: PropTypes.func.isRequired,
      onNextMonth: PropTypes.func.isRequired,
      onMonthSelect: PropTypes.func.isRequired,
      onYearSelect: PropTypes.func.isRequired,
      ariaDescribedByDomId: PropTypes.string.isRequired
    }
  }

  get className () {
    return BemUtilities.addVariants(this.props.bemBlock, this.props.bemVariants)
  }

  get buttonClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'button', ['secondary'])
  }

  get leftButtonIconClassName () {
    return BemUtilities.addVariants('cricon', this.props.buttonIconBemVariants.concat([this.props.leftButtonIcon]))
  }

  get rightButtonIconClassName () {
    return BemUtilities.addVariants('cricon', this.props.buttonIconBemVariants.concat([this.props.rightButtonIcon]))
  }

  get currentDateClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'label')
  }

  get prevMonthMoment () {
    return this.props.momentObject.clone().subtract(1, 'month')
  }

  get nextMonthMoment () {
    return this.props.momentObject.clone().add(1, 'month')
  }

  renderPrevMonthButtonAriaLabel () {
    return gettext.interpolate(gettext.gettext('Select previous month (%(month)s)'), {
      month: this.prevMonthMoment.format('MMMM YYYY')
    }, true)
  }

  renderNextMonthButtonAriaLabel () {
    return gettext.interpolate(gettext.gettext('Select next month (%(month)s)'), {
      month: this.nextMonthMoment.format('MMMM YYYY')
    }, true)
  }

  isValidMonth (monthMomentObject) {
    return this.props.momentRange.contains(monthMomentObject)
  }

  renderPrevMonthButton () {
    return <button
      className={this.buttonClassName}
      title={this.props.leftButtonTitle}
      onClick={this.props.onPrevMonth}
      disabled={!this.isValidMonth(this.prevMonthMoment)}
      aria-label={this.renderPrevMonthButtonAriaLabel()}
      aria-describedby={this.props.ariaDescribedByDomId}
    >
      <span className={this.leftButtonIconClassName} aria-hidden='true' />
    </button>
  }

  renderNextMonthButton () {
    return <button
      className={this.buttonClassName}
      title={this.props.rightButtonTitle}
      onClick={this.props.onNextMonth}
      disabled={!this.isValidMonth(this.nextMonthMoment)}
      aria-label={this.renderNextMonthButtonAriaLabel()}
      aria-describedby={this.props.ariaDescribedByDomId}
    >
      <span className={this.rightButtonIconClassName} aria-hidden='true' />
    </button>
  }

  get yearSelectComponentClass () {
    return YearSelect
  }

  get yearSelectComponentProps () {
    return {
      momentObject: this.props.momentObject,
      momentRange: this.props.momentRange,
      onChange: this.props.onYearSelect,
      ariaDescribedByDomId: this.props.ariaDescribedByDomId
    }
  }

  renderYearSelect () {
    const YearSelectComponent = this.yearSelectComponentClass
    return <YearSelectComponent key={'yearSelect'} {...this.yearSelectComponentProps} />
  }

  get monthSelectComponentClass () {
    return MonthSelect
  }

  get monthSelectComponentProps () {
    return {
      momentObject: this.props.momentObject,
      momentRange: this.props.momentRange,
      onChange: this.props.onMonthSelect,
      ariaDescribedByDomId: this.props.ariaDescribedByDomId
    }
  }

  renderMonthSelect () {
    const MonthSelectComponent = this.monthSelectComponentClass
    return <MonthSelectComponent key={'monthSelect'} {...this.monthSelectComponentProps} />
  }

  renderCurrentDate () {
    return <span>
      {this.renderMonthSelect()}
      {' '}
      {this.renderYearSelect()}
    </span>
  }

  render () {
    return <div className={this.className}>
      {this.renderPrevMonthButton()}
      {this.renderCurrentDate()}
      {this.renderNextMonthButton()}
    </div>
  }
}
