import React from 'react'
import PropTypes from 'prop-types'
import 'ievv_jsbase/lib/utils/i18nFallbacks'
import BemUtilities from '../utilities/BemUtilities'

/**
 * Renders a loading indicator.
 *
 * Uses the `loading-indicator` bem block from the cradmin styles by default.
 *
 * @example
 * <LoadingIndicator/>
 *
 * @example <caption>With message - screenreader only</caption>
 * <LoadingIndicator message="Loading the awesome ..."/>
 *
 * @example <caption>With message - visible to anyone</caption>
 * <LoadingIndicator message="Loading the awesome ..." visibleMessage={true} />
 *
 * @example <caption>Light variant</caption>
 * <LoadingIndicator message="Loading the awesome ..." bemVariants={["light"]} />
 */
export default class LoadingIndicator extends React.Component {
  static get propTypes () {
    return {
      message: PropTypes.string.isRequired,
      bemBlock: PropTypes.string.isRequired,
      visibleMessage: PropTypes.bool.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string)
    }
  }

  static get defaultProps () {
    return {
      message: window.gettext('Loading ...'),
      bemBlock: 'loading-indicator',
      visibleMessage: false,
      bemVariants: []
    }
  }

  get indicatorClassName () {
    return BemUtilities.addVariants(`${this.props.bemBlock}__indicator`, this.props.bemVariants)
  }

  get messageScreenReaderOnlyClassName () {
    return `${this.props.bemBlock}__text`
  }

  get messageVisibleClassName () {
    return BemUtilities.addVariants(`${this.props.bemBlock}__label`, this.props.bemVariants)
  }

  renderScreenReaderOnlyMessage () {
    return <span className={this.messageScreenReaderOnlyClassName}>
      {this.props.message}
    </span>
  }

  renderVisibleMessage () {
    return <span className={this.messageVisibleClassName}>
      {this.props.message}
    </span>
  }

  renderMessage () {
    if (this.props.visibleMessage) {
      return this.renderVisibleMessage()
    }
    return this.renderScreenReaderOnlyMessage()
  }

  render () {
    return <span className={this.props.bemBlock}>
      <span className={this.indicatorClassName} />
      <span className={this.indicatorClassName} />
      <span className={this.indicatorClassName} />
      {this.renderMessage()}
    </span>
  }
}
