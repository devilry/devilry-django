import React from 'react'
import PropTypes from 'prop-types'
import 'ievv_jsbase/lib/utils/i18nFallbacks'

export default class AriaDescribedByTarget extends React.Component {
  static get propTypes () {
    return {
      message: PropTypes.string.isRequired,
      domId: PropTypes.string.isRequired
    }
  }

  static get defaultProps () {
    return {
      message: null,
      domId: null
    }
  }

  render () {
    return <span id={this.props.domId} style={{display: 'none'}}>
      {this.props.message}
    </span>
  }
}
