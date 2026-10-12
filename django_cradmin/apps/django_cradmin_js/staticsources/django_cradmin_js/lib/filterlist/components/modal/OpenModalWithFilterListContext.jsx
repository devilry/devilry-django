import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilter from '../filters/AbstractFilter'
import BemUtilities from '../../../utilities/BemUtilities'
import OpenModalButton from '../../../components/ModalPortal/OpenModalButton'

export default class OpenModalWithFilterListContext extends AbstractFilter {
  static get propTypes () {
    return {
      ...super.propTypes,
      buttonLabel: PropTypes.string.isRequired,
      htmlTag: PropTypes.string,
      buttonClassName: PropTypes.string,
      buttonBemVariants: PropTypes.arrayOf(PropTypes.string),
      modalContentsComponent: PropTypes.any.isRequired,
      modalContentsComponentProps: PropTypes.object.isRequired
    }
  }

  static get defaultProps () {
    return {
      ...super.defaultProps,
      htmlTag: null,
      buttonClassName: null,
      buttonBemVariants: [],
      modalContentsComponentProps: {}
    }
  }

  get buttonClassName () {
    if (this.props.buttonClassName !== null) {
      return this.props.buttonClassName
    }
    return BemUtilities.addVariants('button', this.props.buttonBemVariants)
  }

  // Do nothing here, as this is not really a 'filter', and we do not want this to filter the httpRequest in any way.
  static filterHttpRequest (request) {}

  render () {
    const props = {
      htmlTag: this.props.htmlTag,
      modalContentsComponent: this.props.modalContentsComponent,
      buttonClassName: this.buttonClassName,
      buttonContents: this.props.buttonLabel,
      modalContentsComponentProps: {
        childExposedApi: this.props.childExposedApi,
        ...this.props.modalContentsComponentProps
      }
    }
    return <OpenModalButton {...props} />
  }
}
