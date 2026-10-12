import React from 'react'
import PropTypes from 'prop-types'
import LoadMorePaginator from './LoadMorePaginator'
import BemUtilities from '../../../utilities/BemUtilities'

/**
 * Just like {@link LoadMorePaginator}, except that the button is
 * wrapped with a paragraph.
 *
 * See {@link BoxLoadMorePaginator.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "BoxLoadMorePaginator"
 * }
 *
 * @example <caption>Spec - advanced</caption>
 * {
 *    "component": "BoxLoadMorePaginator",
 *    "props": {
 *       "boxBemVariants": ['spacing--small'],
 *       "label": "Load some more items!",
 *       "bemBlock": "custombutton",
 *       "bemVariants": ["large", "dark"],
 *       "location": "left"
 *    }
 * }
 */
export default class BoxLoadMorePaginator extends LoadMorePaginator {
  static get propTypes () {
    return {
      ...super.propTypes,
      boxBemBlock: PropTypes.string.isRequired,
      boxBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    }
  }

  /**
   * Get default props. Extends the default props
   * from {@link LoadMorePaginator.defaultProps}.
   *
   * @return {Object}
   * @property {string} paragraphClassName The css class for the paragraph.
   *    Defaults to `null`.
   *    **Can be used in spec**.
   */
  static get defaultProps () {
    return {
      ...super.defaultProps,
      boxBemBlock: 'box',
      boxBemVariants: ['spacing--small']
    }
  }

  get boxClassName () {
    return BemUtilities.buildBemBlock(this.props.boxBemBlock, this.props.boxBemVariants)
  }

  renderLoadMoreButton () {
    return <div className={this.boxClassName}>
      {super.renderLoadMoreButton()}
    </div>
  }
}
