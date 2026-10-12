import React from 'react'
import PropTypes from 'prop-types'
import LoggerSingleton from 'ievv_jsbase/lib/log/LoggerSingleton'
import Modal from './Modal'
import * as constants from './constants'

export default class OpenModalButton extends React.Component {
  static get propTypes () {
    return {
      htmlTag: PropTypes.string,
      buttonClassName: PropTypes.string,
      buttonContents: PropTypes.any,
      modalClosedCallback: PropTypes.func,
      modalOpenedCallback: PropTypes.func,
      closeOnBackdropClick: PropTypes.bool,
      modalContentsComponent: PropTypes.func.isRequired,
      modalContentsComponentProps: PropTypes.object,
      modalEventInterceptTypes: PropTypes.arrayOf(PropTypes.string).isRequired,
      isDisabled: PropTypes.bool,
      extraButtonAttributes: PropTypes.object,
      modalLocationId: PropTypes.string.isRequired,
      modalOpen: PropTypes.bool.isRequired,
      modalBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    }
  }

  static get defaultProps () {
    return {
      htmlTag: 'button',
      buttonClassName: 'button button--compact',
      buttonContents: 'Open modal',
      modalContentsComponent: null,
      modalClosedCallback: null,
      modalOpenedCallback: null,
      closeOnBackdropClick: false,
      modalContentsComponentProps: {},
      modalEventInterceptTypes: [],
      isDisabled: false,
      extraButtonAttributes: {},
      modalLocationId: constants.MODAL_PLACEHOLDER_ID,
      modalOpen: false,
      modalBemVariants: []
    }
  }

  constructor (props) {
    super(props)
    this.logger = new LoggerSingleton().getLogger(this.name)
    this.state = {
      showModal: this.props.modalOpen
    }

    this.openModal = this.openModal.bind(this)
    this.closeModal = this.closeModal.bind(this)
  }

  openModal (event = null) {
    if (event !== null && typeof event.stopPropagation === 'function') {
      event.stopPropagation()
    }
    if (event !== null && typeof event.preventDefault === 'function') {
      event.preventDefault()
    }
    if (this.props.isDisabled) {
      return
    }
    this.setState({
      showModal: true
    }, this.props.modalOpenedCallback)
  }

  closeModal () {
    this.setState({
      showModal: false
    }, () => {
      if (this.props.modalClosedCallback !== null) {
        this.props.modalClosedCallback()
      }
    })
  }

  renderOpenModalButton () {
    const TagName = this.props.htmlTag
    const props = {
      key: 'magic-portal-modal button',
      tabIndex: '0',
      className: this.props.buttonClassName,
      onClick: this.openModal,
      disabled: this.props.isDisabled,
      ...this.props.extraButtonAttributes
    }
    if (this.props.htmlTag === 'button') {
      props.type = 'button'
    } else {
      props.role = 'button'
    }
    return <TagName {...props}>
      {this.props.buttonContents}
    </TagName>
  }

  renderModal () {
    if (!this.state.showModal) {
      return null
    }
    const props = {
      modalLocationId: this.props.modalLocationId,
      modalBemVariants: this.props.modalBemVariants,
      modalContentsComponent: this.props.modalContentsComponent,
      modalContentsComponentProps: this.props.modalContentsComponentProps,
      closeOnBackdropClick: this.props.closeOnBackdropClick,
      closeModalCallback: this.closeModal
    }
    return <Modal key={'magic-portal modal'} {...props} />
  }

  render () {
    return [
      this.renderModal(),
      this.renderOpenModalButton()
    ]
  }
}
