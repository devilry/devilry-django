import React from 'react'
import * as constants from './constants'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import ErrorBoundary from '../ErrorBoundary'
import BemUtilities from '../../utilities/BemUtilities'

export default class Modal extends React.Component {
  static get propTypes () {
    return {
      modalLocationId: PropTypes.string.isRequired,
      modalContentsComponent: PropTypes.func.isRequired,
      modalContentsComponentProps: PropTypes.object,
      closeOnBackdropClick: PropTypes.bool.isRequired,
      closeModalCallback: PropTypes.func.isRequired,
      modalBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    }
  }

  static get defaultProps () {
    return {
      modalLocationId: constants.MODAL_PLACEHOLDER_ID,
      closeOnBackdropClick: false,
      modalContentsComponentProps: {},
      modalBemVariants: []
    }
  }

  constructor (props) {
    super(props)
    this._modalLocation = null
    this.element = document.createElement('div')
    this.backdropClick = this.backdropClick.bind(this)
  }

  get baseModalClassName () {
    return 'modal'
  }

  get modalClassName () {
    return BemUtilities.addVariants(this.baseModalClassName, this.props.modalBemVariants)
  }

  get modalLocation () {
    if (this._modalLocation === null) {
      this._modalLocation = document.getElementById(this.props.modalLocationId)
    }
    return this._modalLocation
  }

  componentDidMount () {
    if (!this.modalLocation) {
      return
    }
    this.modalLocation.appendChild(this.element)
  }

  componentWillUnmount () {
    if (!this.modalLocation) {
      return
    }
    this.modalLocation.removeChild(this.element)
  }

  backdropClick () {
    if (this.props.closeOnBackdropClick) {
      this.props.closeModalCallback()
    }
  }

  renderContents () {
    const Contents = this.props.modalContentsComponent
    return <div className={this.modalClassName}>
      <div className={'modal__backdrop'} onClick={this.backdropClick} />
      <div className={'modal__content'}>
        <ErrorBoundary name={'OpenModalButton'}>
          <Contents closeModalCallback={this.props.closeModalCallback} {...this.props.modalContentsComponentProps} />
        </ErrorBoundary>
      </div>
    </div>
  }

  render () {
    if (!this.modalLocation || !this.element) {
      console.error('Cannot open modal without valid portalLocation and valid element.')
      return null
    }
    return ReactDOM.createPortal(
      this.renderContents(),
      this.element
    )
  }
}
