import React from 'react'
import PropTypes from 'prop-types'
import AbstractListItem from './AbstractListItem'
import BemUtilities from '../../../utilities/BemUtilities'

export default class TitleDescriptionListItem extends AbstractListItem {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      title: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      titleBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    })
  }

  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      bemBlock: 'blocklist',
      bemVariants: [],
      titleBemVariants: []
    })
  }

  get className () {
    return BemUtilities.buildBemElement(
      this.props.bemBlock, 'item', this.props.bemVariants)
  }

  get titleClassName () {
    return BemUtilities.buildBemElement(
      this.props.bemBlock, 'itemtitle', this.props.titleBemVariants)
  }

  get descriptionClassName () {
    return ''
  }

  render () {
    return <div className={this.className}>
      <h2 className={this.titleClassName}>{this.props.title}</h2>
      <p className={this.descriptionClassName}>
        {this.props.description}
      </p>
    </div>
  }
}
