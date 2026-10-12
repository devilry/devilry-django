import React from 'react'
import PropTypes from 'prop-types'
import AbstractListItem from './AbstractListItem'
import BemUtilities from '../../../utilities/BemUtilities'

export default class SelectableTitleDescriptionListItem extends AbstractListItem {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      title: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      titleBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
      contentBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    })
  }

  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      bemBlock: 'selectable-list',
      bemVariants: [],
      titleBemVariants: [],
      contentBemVariants: []
    })
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onClick = this.onClick.bind(this)
  }

  onClick () {
    if (this.props.isSelected) {
      this.props.childExposedApi.deselectItem(this.props.listItemId)
    } else {
      this.props.childExposedApi.selectItem(this.props.listItemId)
    }
  }

  get className () {
    const bemVariants = [...this.props.bemVariants]
    if (this.props.isSelected) {
      bemVariants.push('selected')
    }
    return BemUtilities.buildBemElement(
      this.props.bemBlock, 'item', bemVariants)
  }

  get iconWrapperClassName () {
    return 'selectable-list__icon'
  }

  get iconClassName () {
    return 'cricon cricon--check cricon--color-light'
  }

  get contentClassName () {
    return BemUtilities.buildBemElement(
      this.props.bemBlock, 'itemcontent', this.props.contentBemVariants)
  }

  get titleClassName () {
    return BemUtilities.buildBemElement(
      this.props.bemBlock, 'itemtitle', this.props.titleBemVariants)
  }

  get descriptionClassName () {
    return ''
  }

  renderIcon () {
    if (this.props.isSelected) {
      return <i className={this.iconClassName}/>
    }
    return null
  }

  renderIconWrapper () {
    return <div className={this.iconWrapperClassName}>
      {this.renderIcon()}
    </div>
  }

  renderContent () {
    return <div className={this.contentClassName}>
      <h2 className={this.titleClassName}>{this.props.title}</h2>
      <p className={this.descriptionClassName}>
        {this.props.description}
      </p>
    </div>
  }

  render () {
    return <div
      className={this.className}
      tabIndex={0}
      aria-selected={this.props.isSelected}
      onFocus={this.onFocus}
      onBlur={this.onBlur}
      onClick={this.onClick}>
      {this.renderIconWrapper()}
      {this.renderContent()}
    </div>
  }
}
