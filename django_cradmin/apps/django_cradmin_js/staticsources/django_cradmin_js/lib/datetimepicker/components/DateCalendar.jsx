import React from 'react'
import moment from 'moment'
import range from 'lodash/range'
import chunk from 'lodash/chunk'
import PropTypes from 'prop-types'
import BemUtilities from '../../utilities/BemUtilities'
import * as gettext from 'ievv_jsbase/lib/gettext'

export default class DateCalendar extends React.Component {
  static get defaultProps () {
    return {
      momentObject: null,
      initialFocusMomentObject: moment(),
      bemBlock: 'calendar-month',
      bemVariants: [],
      onDaySelect: null,
      ariaDescribedByDomId: null
    }
  }

  static get propTypes () {
    return {
      momentObject: PropTypes.any,
      initialFocusMomentObject: PropTypes.any.isRequired,
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      onDaySelect: PropTypes.func.isRequired,
      ariaDescribedByDomId: PropTypes.string.isRequired
    }
  }

  getMoment () {
    let momentObject = null
    if (this.props.momentObject === null) {
      momentObject = this.props.initialFocusMomentObject.clone()
    } else {
      momentObject = this.props.momentObject.clone()
    }
    return momentObject
  }

  get className () {
    return BemUtilities.addVariants(this.props.bemBlock, this.props.bemVariants)
  }

  get headerClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'header')
  }

  get headerRowClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'header-row')
  }

  get headerDayClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'header-day')
  }

  get bodyClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'body')
  }

  get weekClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'week')
  }

  isValidDay (dayMomentObject) {
    return this.props.momentRange.contains(dayMomentObject)
  }

  makeDayButtonClassName (dayMomentObject) {
    const bemVariants = []
    if (!dayMomentObject.isSame(this.getMoment(), 'month')) {
      bemVariants.push('muted')
    } else if (this.props.momentObject !== null && this.props.momentObject.isSame(dayMomentObject, 'day')) {
      bemVariants.push('selected')
    } else {
      const now = moment()
      if (dayMomentObject.isSame(now, 'day')) {
        bemVariants.push('today')
      }
    }

    return BemUtilities.buildBemElement(this.props.bemBlock, 'daybutton', bemVariants)
  }

  makeDayClassName (dayMomentObject) {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'day')
  }

  renderDayButtonAriaLabel (dayMomentObject) {
    return gettext.interpolate(gettext.gettext('Select %(date)s'), {
      date: dayMomentObject.format('LL')
    }, true)
  }

  renderDayButtonLabel (dayMomentObject) {
    return dayMomentObject.format('D')
  }

  renderDayButton (dayMomentObject) {
    return <button
      tabIndex={0}
      className={this.makeDayButtonClassName(dayMomentObject)}
      aria-label={this.renderDayButtonAriaLabel(dayMomentObject)}
      aria-describedby={this.props.ariaDescribedByDomId}
      disabled={!this.isValidDay(dayMomentObject)}
      onClick={(e) => {
        e.preventDefault()
        this.props.onDaySelect(dayMomentObject)
      }}
    >
      {this.renderDayButtonLabel(dayMomentObject)}
    </button>
  }

  renderDay (dayMomentObject) {
    return <div key={dayMomentObject.format()} className={this.makeDayClassName(dayMomentObject)}>
      {this.renderDayButton(dayMomentObject)}
    </div>
  }

  renderDaysInWeek (daysInWeek, year, month, week) {
    return daysInWeek.map(day => {
      let realMonth = month
      let realYear = year
      if (week === 0 && day > 7) {
        realMonth -= 1
      } else if (week >= 4 && day <= 14) {
        realMonth += 1
      }

      if (realMonth > 11) {
        realYear += 1
        realMonth = 0
      }
      if (realMonth < 0) {
        realYear -= 1
        realMonth = 11
      }

      const dayMomentObject = moment({
        year: realYear,
        month: realMonth,
        day: day
      })
      if (dayMomentObject.format() === 'Invalid date') {
        console.log('CRAP', year, realMonth, day)
      }
      return this.renderDay(dayMomentObject)
    })
  }

  renderWeek (daysInWeek, year, month, week) {
    return <div key={week} className={this.weekClassName}>
      {this.renderDaysInWeek(daysInWeek, year, month, week)}
    </div>
  }

  renderWeeks () {
    const momentObject = this.getMoment()
    const firstDayOfWeek = momentObject.localeData().firstDayOfWeek()
    const endOfPreviousMonth = momentObject.clone().subtract(1, 'month').endOf('month').date()
    const startDayOfCurrentMonth = momentObject.clone().date(1).day()
    const endOfCurrentMonth = momentObject.clone().endOf('month').date()
    const year = momentObject.year()
    const month = momentObject.month()

    let days = [].concat(
      range(
        (endOfPreviousMonth - startDayOfCurrentMonth + firstDayOfWeek + 1),
        (endOfPreviousMonth + 1)
      ),
      range(
        1,
        (endOfCurrentMonth + 1)
      ),
      range(
        1,
        (42 - endOfCurrentMonth - startDayOfCurrentMonth + firstDayOfWeek + 1)
      )
    )
    return chunk(days, 7).map((daysInWeek, week) => {
      return this.renderWeek(daysInWeek, year, month, week)
    })
  }

  renderBody () {
    return <div className={this.bodyClassName}>
      {this.renderWeeks()}
    </div>
  }

  renderHeaderRowContent () {
    const momentObject = this.getMoment()
    const firstDayOfWeek = momentObject.localeData().firstDayOfWeek()
    let weekdays = momentObject.localeData().weekdaysShort()
    weekdays = weekdays.slice(firstDayOfWeek).concat(weekdays.slice(0, firstDayOfWeek))

    return weekdays.map((weekday, index) => {
      return <div key={index} className={this.headerDayClassName}>{weekday}</div>
    })
  }

  renderHeaderRow () {
    return <div className={this.headerRowClassName}>
      {this.renderHeaderRowContent()}
    </div>
  }

  renderHeader () {
    return <div className={this.headerClassName}>
      {this.renderHeaderRow()}
    </div>
  }

  render () {
    return <div className={this.className}>
      {this.renderHeader()}
      {this.renderBody()}
    </div>
  }
}
