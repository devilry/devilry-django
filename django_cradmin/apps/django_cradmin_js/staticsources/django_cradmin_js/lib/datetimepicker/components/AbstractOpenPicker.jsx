import React from 'react'
import PropTypes from 'prop-types'
import * as gettext from 'ievv_jsbase/lib/gettext'
import BemUtilities from '../../utilities/BemUtilities'
import moment from 'moment/moment'

export default class AbstractOpenPicker extends React.Component {
  static get defaultProps () {
    return {
      momentObject: null,
      momentObjectFormat: null,
      openButtonEmptyLabel: gettext.pgettext('datetimepicker', 'Select'),
      includeNowButton: true,
      nowButtonLabel: null,
      onOpen: null,
      onChange: null,
      wrapperBemVariants: ['xs'],
      buttonBarBemVariants: ['nomargin'],
      modalDomId: null,
      ariaDescribedByDomId: null,
      domIdPrefix: null,
      isOpen: false
    }
  }

  static get propTypes () {
    return {
      momentObject: PropTypes.any,
      momentObjectFormat: PropTypes.string.isRequired,
      openButtonEmptyLabel: PropTypes.string.isRequired,
      includeNowButton: PropTypes.bool,
      nowButtonLabel: PropTypes.string.isRequired,
      onOpen: PropTypes.func.isRequired,
      onChange: PropTypes.func.isRequired,
      wrapperBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      modalDomId: PropTypes.string,
      ariaDescribedByDomId: PropTypes.string.isRequired,
      domIdPrefix: PropTypes.string.isRequired,
      isOpen: PropTypes.bool.isRequired
    }
  }

  constructor (props) {
    super(props)
    this.onNowButtonClick = this.onNowButtonClick.bind(this)
    this.openButtonRef = React.createRef()
  }

  onNowButtonClick () {
    this.props.onChange(moment())
    this.openButtonRef.focus()
  }

  get openButtonAriaDescribedByDomId () {
    return `${this.props.domIdPrefix}_openPicker_openButton`
  }

  get wrapperBemBlock () {
    return 'max-width'
  }

  get wrapperClassName () {
    return BemUtilities.addVariants(this.wrapperBemBlock, this.props.wrapperBemVariants)
  }

  get buttonBarBemBlock () {
    return 'buttonbar'
  }

  get buttonBarClassName () {
    return BemUtilities.addVariants(this.buttonBarBemBlock, this.props.buttonBarBemVariants)
  }

  makeButtonClassName (bemVariants = []) {
    return BemUtilities.buildBemElement(this.buttonBarBemBlock, 'button', bemVariants)
  }

  renderIcon (name, bemVariants = []) {
    const className = BemUtilities.addVariants('cricon', [name, ...bemVariants])
    return <span className={className} aria-hidden='true' />
  }

  get openButtonLabelText () {
    if (this.props.momentObject === null) {
      return this.props.openButtonEmptyLabel
    }
    return this.props.momentObject.format(this.props.momentObjectFormat)
  }

  renderOpenButtonLabel () {
    return this.openButtonLabelText
  }

  renderOpenButtonIcon () {
    return <span>{this.renderIcon('calendar')}{' '}</span>
  }

  get openButtonAriaLabel () {
    let expandedState = gettext.pgettext('datetimepicker openButton', 'collapsed')
    if (this.props.isOpen) {
      expandedState = gettext.pgettext('datetimepicker openButton', 'expanded')
    }
    const ariaExtra = gettext.gettext('Calendar picker toggle button')
    return `${this.openButtonLabelText}. ${ariaExtra} - ${expandedState}`
  }

  get openButtonProps () {
    return {
      key: 'openButton',
      ref: this.openButtonRef,
      type: 'button',
      className: this.makeButtonClassName(['input-outlined', 'grow-2', 'width-xsmall']),
      onClick: this.props.onOpen,
      'aria-label': this.openButtonAriaLabel,
      'aria-describedby': `${this.props.ariaDescribedByDomId} ${this.openButtonAriaDescribedByDomId}`
    }
  }

  renderOpenButton () {
    return <button {...this.openButtonProps}>
      {this.renderOpenButtonIcon()}
      {this.renderOpenButtonLabel()}
    </button>
  }

  get openButtonAriaDescribedByText () {
    if (this.props.isOpen) {
      return gettext.gettext('You are currently on an expanded calendar picker toggle button. Use the focus change key (tab) to go to the calendar picker. Click the button to collapse/hide the calendar picker.')
    } else {
      return gettext.gettext('You are currently on an collapsed calendar picker toggle button. Click the button to expand the calendar picker.')
    }
  }

  renderOpenButtonAriaDescribedBy () {
    return <span id={this.openButtonAriaDescribedByDomId} className='screenreader-only' key={'aria-describedby'}>
      {this.openButtonAriaDescribedByText}
    </span>
  }

  renderNowButtonLabel () {
    return this.props.nowButtonLabel
  }

  renderNowButton () {
    return <button
      key={'nowButton'}
      type={'button'}
      className={this.makeButtonClassName(['fill', 'no-grow'])}
      onClick={this.onNowButtonClick}
      aria-describedby={this.props.ariaDescribedByDomId}
    >
      {this.renderNowButtonLabel()}
    </button>
  }

  renderButtons () {
    let buttons = [
      this.renderOpenButton()
    ]
    if (this.props.includeNowButton) {
      buttons.push(this.renderNowButton())
    }
    return buttons
  }

  renderButtonBar () {
    return <div className={this.buttonBarClassName}>
      {this.renderButtons()}
    </div>
  }

  focus () {
    this.openButtonRef.current.focus()
  }

  render () {
    return [
      this.renderOpenButtonAriaDescribedBy(),
      <div className={this.wrapperClassName} key={'buttonBarWrapper'}>
        {this.renderButtonBar()}
      </div>
    ]
  }
}
