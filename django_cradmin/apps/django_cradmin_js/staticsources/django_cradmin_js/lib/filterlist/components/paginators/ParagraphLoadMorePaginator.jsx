import React from 'react'
import PropTypes from 'prop-types'
import LoadMorePaginator from './LoadMorePaginator'

/**
 * Just like {@link LoadMorePaginator}, except that the button is
 * wrapped with a paragraph.
 *
 * See {@link ParagraphLoadMorePaginator.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "ParagraphLoadMorePaginator"
 * }
 *
 * @example <caption>Spec - advanced</caption>
 * {
 *    "component": "ParagraphLoadMorePaginator",
 *    "props": {
 *       "paragraphClassName": "paragraph paragraph--tight",
 *       "label": "Load some more items!",
 *       "bemBlock": "custombutton",
 *       "bemVariants": ["large", "dark"],
 *       "location": "left"
 *    }
 * }
 */
export default class ParagraphLoadMorePaginator extends LoadMorePaginator {
  static get propTypes () {
    return Object.assign({}, super.propTypes, {
      paragraphClassName: PropTypes.string
    })
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
    return Object.assign({}, super.defaultProps, {
      paragraphClassName: null
    })
  }

  renderLoadMoreButton () {
    return <p className={this.props.paragraphClassName}>
      {super.renderLoadMoreButton()}
    </p>
  }
}
