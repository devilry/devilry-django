import React from 'react'
import PropTypes from 'prop-types'
import EmptyBooleanFilter from './EmptyBooleanFilter'

/**
 * Empty or boolean filter - users can select between "empty" or "true" or "false".
 * Works just like {@link EmptyBooleanFilter}, but the filter is wrapped
 * in a paragraph with a label after the
 *
 * See {@link TightLabeledEmptyBooleanFilter.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "TightLabeledEmptyBooleanFilter",
 *    "props": {
 *      "name": "include_disabled_users",
 *      "label": "Include disabled users?"
 *    }
 * }
 *
 * @example <caption>Spec - with initial value</caption>
 * {
 *    "component": "TightLabeledEmptyBooleanFilter",
 *    "initialValue": true,
 *    "props": {
 *      "name": "include_disabled_users",
 *      "label": "Include disabled users?"
 *    }
 * }
 *
 * @example <caption>Spec - with custom labels</caption>
 * {
 *    "component": "TightLabeledEmptyBooleanFilter",
 *    "initialValue": true,
 *    "props": {
 *      "name": "include_disabled_users",
 *      "label": "Include disabled users?",
 *      "emptyLabel": "Any",
 *      "trueLabel": "Please do",
 *      "falseLabel": "Please do not"
 *    }
 * }
 */
export default class TightLabeledEmptyBooleanFilter extends EmptyBooleanFilter {
  static get propTypes () {
    const propTypes = super.propTypes
    propTypes.label = PropTypes.string.isRequired
    propTypes.wrapperClassName = PropTypes.string
    propTypes.ariaLabel = PropTypes.string
    return propTypes
  }

  /**
   * Get default props. Extends the default props
   * from {@link EmptyBooleanFilter.defaultProps}.
   *
   * @return {Object}
   * @property {string} label The label shown after the select element.
   *    **Can be used in spec**.
   * @property {string} ariaLabel The aria label of the select element.
   *    Defaults to ``label``.
   *    **Can be used in spec**.
   * @property {bool} value Must be true, false or null.
   */
  static get defaultProps () {
    const defaultProps = super.defaultProps
    defaultProps.ariaLabel = null
    defaultProps.label = null
    defaultProps.className = 'select select--outlined select--size-xsmall select--width-xxsmall'
    defaultProps.wrapperClassName = 'paragraph paragraph--xtight'
    return defaultProps
  }

  get ariaLabel () {
    if (this.props.ariaLabel === null) {
      return this.props.label
    }
    return this.props.ariaLabel
  }

  renderAfterSelectLabelText () {
    return <span key={'labelText'}>{this.props.label}</span>
  }

  // renderLabelContent () {
  //   const content = super.renderLabelContent()
  //   content.push(this.renderAfterSelectLabelText())
  //   return content
  // }

  render () {
    return <p className={this.props.wrapperClassName}>
      {super.render()}
      {' '}
      {this.renderAfterSelectLabelText()}
    </p>
  }
}
