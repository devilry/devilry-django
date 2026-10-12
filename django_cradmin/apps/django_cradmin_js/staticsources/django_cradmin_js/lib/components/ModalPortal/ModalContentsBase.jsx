import React from 'react'
import PropTypes from 'prop-types'
import * as gettext from 'ievv_jsbase/lib/gettext'
import ModalClose from './ModalClose'
import ErrorBoundary from '../ErrorBoundary'

export default class ModalContentsBase extends React.Component {
  static get propTypes () {
    return {
      closeModalCallback: PropTypes.func.isRequired,
      headerClassName: PropTypes.string.isRequired,
      includeCloseButton: PropTypes.bool.isRequired,
      closeButtonTitle: PropTypes.string.isRequired
    }
  }

  static get defaultProps () {
    return {
      closeModalCallback: null,
      headerClassName: 'h3',
      includeCloseButton: true,
      closeButtonTitle: gettext.gettext('Close')
    }
  }

  get closeButtonProps () {
    return {
      key: 'close button',
      closeModalCallback: this.props.closeModalCallback,
      buttonTitle: this.props.closeButtonTitle
    }
  }

  renderCloseButton () {
    return <ModalClose {...this.closeButtonProps} />
  }

  get includeCloseButton () {
    return this.props.includeCloseButton
  }

  renderCloseButtonIfEnabled () {
    if (this.includeCloseButton) {
      return this.renderCloseButton()
    }
    return null
  }

  renderBody () {
    console.error('renderBody should be overridden by subclasses!')
    return null
  }

  renderTitleText () {
    console.error('renderTitleText should be overridden by subclasses!')
    return null
  }

  renderTitleContent () {
    return <h2 className={this.props.headerClassName}>
      {this.renderTitleText()}
    </h2>
  }

  renderTitle () {
    return <div className={'modal__title'} key={'title'}>
      {this.renderTitleContent()}
    </div>
  }

  render () {
    return <React.Fragment>
      {this.renderCloseButtonIfEnabled()}
      {this.renderTitle()}
      <ErrorBoundary key={'body error boundary'} name={'modal content'}>
        {this.renderBody()}
      </ErrorBoundary>
    </React.Fragment>
  }
}
