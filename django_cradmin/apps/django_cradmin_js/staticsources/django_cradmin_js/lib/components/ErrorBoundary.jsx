import React from 'react'
import PropTypes from 'prop-types'
import * as gettext from 'ievv_jsbase/lib/gettext'

/**
 * A default react errorboundary. This one is mostly made to test how it works, but does give a sane (and translatable)
 * error message.
 */
export default class ErrorBoundary extends React.Component {
  static get propTypes () {
    return {
      name: PropTypes.string.isRequired,
      children: PropTypes.any.isRequired
    }
  }

  constructor (props) {
    super(props)
    this.state = {hasError: false}
  }

  componentDidCatch () {
    this.setState({hasError: true})
  }

  render () {
    if (this.state.hasError) {
      return <p className={'message message--error'} >
        {gettext.gettext('Something went wrong, please reload the page and try again later')}
      </p>
    }
    return this.props.children
  }
}
