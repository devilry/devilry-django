import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilter from './AbstractFilter'
import * as gettext from 'ievv_jsbase/lib/gettext'
import DropdownDateSelect from '../../../datetimepicker/components/DropdownDateSelect'
import moment from 'moment'

/**
 * Base class for date filters.
 */
export class AbstractDateFilter extends AbstractFilter {
  static get propTypes () {
    return {
      ...super.propTypes,
      dateFormat: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      wrapperClassName: PropTypes.string.isRequired,
      pickerProps: PropTypes.object.isRequired
    }
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractFilter.defaultProps}.
   *
   * @return {Object}
   * @property {string} dateFormat A momentjs date format. Used to convert the value from and to momentjs object.
   *    Defaults to "YYYY-MM-DD" (iso format).
   * @property {string} label Label for the field.
   * @property {string} wrapperClassName CSS class name for the wrapper element.
   */
  static get defaultProps () {
    return {
      ...super.defaultProps,
      dateFormat: 'YYYY-MM-DD',
      label: null,
      wrapperClassName: 'fieldwrapper',
      pickerProps: {}
    }
  }

  static filterHttpRequest (httpRequest, name, value) {
    if (value === null || value === '') {
      return
    }
    super.filterHttpRequest(httpRequest, name, value)
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onChange = this.onChange.bind(this)
  }

  onChange (momentObject) {
    let value = null
    if (momentObject !== null) {
      value = momentObject.format(this.props.dateFormat)
    }
    this.setFilterValue(value)
  }

  get momentValue () {
    if (this.props.value) {
      return moment(this.props.value, this.props.dateFormat)
    }
    return null
  }

  get dateSelectComponentClass () {
    throw new Error('dateSelectComponentClass getter must be overridden in subclasses')
  }

  get dateSelectComponentProps () {
    return {
      momentObject: this.momentValue,
      onChange: this.onChange,
      pickerProps: this.props.pickerProps
    }
  }

  renderDateSelect () {
    const Component = this.dateSelectComponentClass
    return <Component {...this.dateSelectComponentProps} />
  }

  renderLabelContent () {
    return this.props.label
  }

  renderLabel () {
    return <label className={'label'}>
      {this.renderLabelContent()}
    </label>
  }

  render () {
    return <div className={this.props.wrapperClassName}>
      {this.renderLabel()}
      {this.renderDateSelect()}
    </div>

  }
}


/**
 * Date filter.
 *
 * See {@link DropDownDateFilter.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "DropDownDateFilter",
 *    "props": {
 *      "name": "from_date",
 *      "label": "From date"
 *    }
 * }
 */
export class DropDownDateFilter extends AbstractDateFilter {
  static get propTypes () {
    return {
      ...super.propTypes,
      openPickerProps: PropTypes.object.isRequired
    }
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractDateFilter.defaultProps}.
   *
   * @return {Object}
   * @property {bool} value Must be true, false or null.
   */
  static get defaultProps () {
    return {
      ...super.defaultProps,
      openPickerProps: {}
    }
  }

  get dateSelectComponentClass () {
    return DropdownDateSelect
  }

  get dateSelectComponentProps () {
    return {
      ...super.dateSelectComponentProps,
      title: this.props.label,
      openPickerProps: this.props.openPickerProps
    }
  }
}
