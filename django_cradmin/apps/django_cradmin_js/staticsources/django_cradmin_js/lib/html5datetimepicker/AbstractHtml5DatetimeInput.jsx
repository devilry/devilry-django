import React from 'react'
import PropTypes from 'prop-types'
import BemUtilities from '../utilities/BemUtilities'
import * as is from 'is_js'
import UniqueDomIdSingleton from 'ievv_jsbase/lib/dom/UniqueDomIdSingleton'
import * as gettext from 'ievv_jsbase/lib/gettext'

export default class AbstractHtml5DatetimeInput extends React.Component {
  static get defaultProps () {
    return {
      value: null,
      bemBlock: 'searchinput',
      bemVariants: ['outlined'],
      buttonIconBemVariants: ['close'],
      errorBemVariants: ['error'],
      messageBemBlock: 'message',
      messageErrorBemVariants: ['error'],
      messageInfoBemVariants: ['info'],
      onChange: null,
      ariaLabel: null,
      ariaLabelledBy: null,
      ariaDescribedBy: null,
      clearButtonTitle: gettext.pgettext('cradmin html5 datetime selector', 'Clear'),
      min: null,
      max: null,
      readOnly: false,
      required: false,
      extraClassNames: '',
      inputName: null
    }
  }

  static get propTypes () {
    return {
      value: PropTypes.string,
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      buttonIconBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      clearButtonTitle: PropTypes.string.isRequired,
      errorBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      messageBemBlock: PropTypes.string.isRequired,
      messageErrorBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      messageInfoBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      onChange: PropTypes.func,
      ariaLabel: PropTypes.string,
      ariaLabelledBy: PropTypes.string,
      ariaDescribedBy: PropTypes.string,
      min: PropTypes.string,
      max: PropTypes.string,
      readOnly: PropTypes.bool.isRequired,
      required: PropTypes.bool.isRequired,
      extraClassNames: PropTypes.string,
      inputName: PropTypes.string
    }
  }

  constructor (props) {
    super(props)
    this.messageDomId = new UniqueDomIdSingleton().generate()
    this.state = this.makeInitialState()
    this.setupBoundFunctions()
  }

  makeInitialState () {
    return {
      value: this.makeValidInputFieldValue(this.props.value || ''),
      isBlurred: false
    }
  }

  setupBoundFunctions () {
    this.onChange = this.onChange.bind(this)
    this.onBlur = this.onBlur.bind(this)
    this.onFocus = this.onFocus.bind(this)
    this.handleClearClick = this.handleClearClick.bind(this)
  }

  parseInputValue (stringValue) {
    throw new Error('parseInputValue must be implemented in subclass')
  }

  handleChange (stringValue) {
    throw new Error('handleChange must be implemented in subclass')
  }

  handleClearClick () {
    this.handleChange('')
  }

  onChange (e) {
    this.handleChange(e.target.value)
  }

  onBlur (e) {
    throw new Error('onBlur must be implemented in subclass')
  }

  get inputFormat () {
    throw new Error('inputFormat must be implemented in subclass')
  }

  onFocus () {
    this.setState({
      isBlurred: false
    })
  }

  get wrapperClassName () {
    let bemVariants = this.props.bemVariants
    if (!this.hasValidInput()) {
      bemVariants = this.props.errorBemVariants
    }
    return `${BemUtilities.buildBemBlock(this.props.bemBlock, bemVariants)} ${this.props.extraClassNames}`
  }

  get bodyClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'body')
  }

  get inputClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'input')
  }

  get buttonClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'button')
  }

  get buttonIconClassName () {
    const buttonIconClass = BemUtilities.buildBemElement(this.props.bemBlock, 'buttonicon')
    const crIconClass = BemUtilities.buildBemBlock('cricon', this.props.buttonIconBemVariants)
    return `${buttonIconClass} ${crIconClass}`
  }

  get messageClassName () {
    let bemVariants = this.props.messageInfoBemVariants
    if (this.state.isBlurred) {
      bemVariants = this.props.messageErrorBemVariants
    }
    return BemUtilities.buildBemBlock(this.props.messageBemBlock, bemVariants)
  }

  getInputType () {
    throw new Error('getInputType must be implemented in subclass')
  }

  get inputType () {
    if (this.browserFullySupportsDateInput()) {
      return this.getInputType()
    }
    return 'text'
  }

  get humanReadableInputFormat () {
    throw new Error('humanReadableInputFormat must be implemented in subclass')
  }

  browserFullySupportsDateInput () {
    // NOTE: This can be simplified, but is not for readability
    // return false
    if (is.chrome() || is.firefox() || is.opera() || is.edge()) {
      return true
    }
    if (is.safari() && !is.desktop()) {
      return true
    }
    return false
  }

  get placeholder () {
    if (this.browserFullySupportsDateInput()) {
      return null
    }

    return this.humanReadableInputFormat
  }

  makeValidInputFieldValue () {
    throw new Error('makeValidInputFieldValue must be implemented in subclass')
  }

  get inputProps () {
    let ariaDescribedByArray = []
    let props = {
      type: this.inputType,
      placeholder: this.placeholder,
      min: this.props.min,
      max: this.props.max,
      value: this.state.value,
      readOnly: this.props.readOnly,
      required: this.props.required,
      'aria-label': this.props.ariaLabel,
      'aria-labelledby': this.props.ariaLabelledBy,
      onChange: this.onChange,
      onBlur: this.onBlur,
      onFocus: this.onFocus,
      className: this.inputClassName,
      name: this.props.inputName
    }

    if (!this.hasValidInput()) {
      ariaDescribedByArray.push(this.messageDomId)
      if (this.state.isBlurred) {
        props['aria-invalid'] = true
      }
    }
    if (this.props.ariaDescribedBy) {
      ariaDescribedByArray.push(this.props.ariaDescribedBy)
    }
    if (ariaDescribedByArray.length > 0) {
      props['aria-describedby'] = ariaDescribedByArray.join(' ')
    }

    return props
  }

  renderInput () {
    throw new Error('renderInput must be implemented in subclass')
  }

  hasValidInput () {
    const currentValue = this.state.value
    if (!currentValue) {
      return true
    }
    const parseResult = this.parseInputValue(currentValue)
    return parseResult.isValid
  }

  renderInvalidInputText () {
    throw new Error('renderInvalidInputText must be implemented in subclass')
  }

  renderInvalidInputMessage () {
    return <p className={this.messageClassName} id={this.messageDomId}>
      {this.renderInvalidInputText()}
    </p>
  }

  renderErrors () {
    if (this.hasValidInput()) {
      return null
    }
    return this.renderInvalidInputMessage()
  }

  renderWrappedInput () {
    return <div className={this.wrapperClassName}>
      <span className={this.bodyClassName}>
        {this.renderInput()}
      </span>
      <button type={'button'} className={this.buttonClassName} title={this.props.clearButtonTitle} onClick={this.handleClearClick}>
        <span className={this.buttonIconClassName} aria-hidden />
      </button>
    </div>
  }

  render () {
    return <React.Fragment>
      {this.renderWrappedInput()}
      {this.renderErrors()}
    </React.Fragment>
  }
}
