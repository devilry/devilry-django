import React from 'react'
import AbstractDateOrDateTimeSelect from './AbstractDateOrDateTimeSelect'
import PropTypes from 'prop-types'
import * as gettext from 'ievv_jsbase/lib/gettext'
import BemUtilities from '../../utilities/BemUtilities'

export default class AbstractModalDateOrDateTimeSelect extends AbstractDateOrDateTimeSelect {
  static get defaultProps () {
    return Object.assign({}, super.defaultProps, {
      bemVariants: ['modal'],
      bodyBemVariants: ['modal'],
      useButtonBemBlock: 'button',
      useButtonBemVariants: ['block', 'primary'],
      noneSelectedButtonLabel: null,
      title: null,
      useButtonLabel: gettext.pgettext('datetimepicker', 'Use'),
      openButtonEmptyLabel: gettext.pgettext('datetimepicker', 'Select'),
      openPickerProps: {}
    })
  }

  static get propTypes () {
    return Object.assign({}, {
      noneSelectedButtonLabel: PropTypes.string,
      title: PropTypes.string.isRequired,
      useButtonLabel: PropTypes.string.isRequired,
      openButtonEmptyLabel: PropTypes.string.isRequired,
      openPickerProps: PropTypes.object.isRequired
    })
  }

  constructor (props) {
    super(props)
    this.onOpenButtonClick = this.onOpenButtonClick.bind(this)
    this.onCloseButtonClick = this.onCloseButtonClick.bind(this)
    this.onUseButtonClick = this.onUseButtonClick.bind(this)
    this.useButtonRef = React.createRef()
    this.openPickerComponentRef = React.createRef()
  }

  makeInitialState () {
    return Object.assign({}, super.makeInitialState(), {
      isOpen: false
    })
  }

  onCompleteMomentObjectSelected () {
    if (this.selectType === 'date') {
      this.triggerOnChange(this.state.draftMomentObject)
    }
  }

  postSetDraftMomentObject (isCompleteDate = false, isCompleteDateTime = false) {
    if (this.selectType === 'date') {
      if (isCompleteDate || isCompleteDateTime) {
        this.onCompleteMomentObjectSelected()
      }
    } else if (this.selectType === 'datetime') {
      if (isCompleteDateTime) {
        this.onCompleteMomentObjectSelected()
      }
    }
  }

  setDraftMomentObject (draftMomentObject, isCompleteDate = false, isCompleteDateTime = false) {
    this.setState({
      draftMomentObject: draftMomentObject
    }, () => {
      this.postSetDraftMomentObject(isCompleteDate, isCompleteDateTime)
    })
  }

  get ariaLabel () {
    return this.props.ariaLabel ? this.props.ariaLabel : this.props.title
  }

  get useButtonClassName () {
    return BemUtilities.addVariants(this.props.useButtonBemBlock, this.props.useButtonBemVariants)
  }

  get backdropClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'backdrop')
  }

  get titleClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'title')
  }

  get closeButtonClassName () {
    return BemUtilities.buildBemElement(this.props.bemBlock, 'close')
  }

  get closeButtonTitle () {
    return gettext.gettext('Close')
  }

  get closeButtonIconClassName () {
    return 'cricon cricon--close'
  }

  get modalDomId () {
    return `${this.domIdPrefix}_modal`
  }

  triggerOnChange (momentObject, onComplete = null) {
    super.triggerOnChange(momentObject, () => {
      this.setState({
        isOpen: false
      }, () => {
        this.openPickerComponentRef.current.focus()
        if (onComplete) {
          onComplete()
        }
      })
    })
  }

  onUseButtonClick () {
    this.triggerOnChange(this.state.draftMomentObject)
  }

  onOpenButtonClick () {
    this.setState({
      isOpen: !this.state.isOpen
    })
  }

  onCloseButtonClick () {
    this.setState({
      isOpen: false
    })
  }

  get openPickerComponentProps () {
    return {
      ...this.props.openPickerProps,
      key: 'openPicker',
      ref: this.openPickerComponentRef,
      momentObject: this.props.momentObject,
      isOpen: this.state.isOpen,
      domIdPrefix: this.domIdPrefix,
      onOpen: this.onOpenButtonClick,
      onChange: this.triggerOnChange,
      modalDomId: this.modalDomId,
      ariaDescribedByDomId: this.ariaDescribedByDomId
    }
  }

  get openPickerComponentClass () {
    throw new Error('The openPickerComponentClass getter must be implemented in subclasses')
  }

  renderOpenPicker () {
    const OpenPickerComponent = this.openPickerComponentClass
    return <OpenPickerComponent {...this.openPickerComponentProps} />
  }

  renderCloseButton () {
    return <div className={this.closeButtonClassName} key={'closeButton'}>
      <button
        type='button'
        title={this.closeButtonTitle}
        onClick={this.onCloseButtonClick}
        aria-describedby={this.ariaDescribedByDomId}
      >
        <span className={this.closeButtonIconClassName} aria-hidden='true' />
      </button>
    </div>
  }

  renderTitle () {
    if (this.props.title === null) {
      return null
    }
    return <div key={'title'} className={this.titleClassName} aria-hidden>
      {this.props.title}
    </div>
  }

  renderUseButtonLabel () {
    return this.props.useButtonLabel
  }

  get useButtonProps () {
    return {
      key: 'useButton',
      ref: this.useButtonRef,
      type: 'button',
      className: this.useButtonClassName,
      onClick: this.onUseButtonClick
    }
  }

  renderUseButton () {
    if (this.state.draftMomentObject === null || this.selectType !== 'datetime') {
      return null
    }
    return <button {...this.useButtonProps}>
      {this.renderUseButtonLabel()}
    </button>
  }

  renderBodyContent () {
    return [
      this.renderCloseButton(),
      this.renderTitle(),
      ...super.renderBodyContent(),
      this.renderUseButton()
    ]
  }

  renderBackdrop () {
    return <div key={'backdrop'} className={this.backdropClassName} onClick={this.onCloseButtonClick} />
  }

  renderContent () {
    return [
      this.renderBackdrop(),
      ...super.renderContent()
    ]
  }

  renderModal () {
    if (this.state.isOpen) {
      return <div className={this.className} aria-live={'assertive'} id={this.modalDomId} key={'modal'}>
        {this.renderContent()}
      </div>
    }
    return null
  }

  render () {
    return [
      this.renderAriaDescribedBy(),
      this.renderOpenPicker(),
      this.renderModal()
    ]
  }
}
