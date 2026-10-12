import React from 'react'
import * as constants from './constants'
import PropTypes from 'prop-types'

export default class ModalLocation extends React.Component {
  static get propTypes () {
    return {
      id: PropTypes.string
    }
  }

  static get defaultProps () {
    return {
      id: constants.MODAL_PLACEHOLDER_ID
    }
  }

  render () {
    return <div id={this.props.id} />
  }
}
