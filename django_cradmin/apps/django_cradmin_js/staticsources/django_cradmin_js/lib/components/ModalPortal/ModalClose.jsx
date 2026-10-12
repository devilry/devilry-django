import React from 'react'
import PropTypes from 'prop-types'
import * as gettext from 'ievv_jsbase/lib/gettext'

export default class ModalClose extends React.Component {
  static get propTypes () {
    return {
      closeModalCallback: PropTypes.func.isRequired,
      buttonTitle: PropTypes.string.isRequired,
    }
  }

  static get defaultProps () {
    return {
      closeModalCallback: null,
      buttonTitle: gettext.gettext('Close')
    }
  }

  get buttonProps () {
    return {
      type: 'button',
      title: this.props.buttonTitle,
      onClick: this.props.closeModalCallback
    }
  }

  render () {
    return <div className='modal__close'>
      <button {...this.buttonProps}>
        <span className='cricon cricon--close' aria-hidden='true' />
      </button>
    </div>
  }
}
