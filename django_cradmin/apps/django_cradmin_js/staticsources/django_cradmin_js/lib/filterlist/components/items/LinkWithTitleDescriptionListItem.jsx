import React from 'react'
import TitleDescriptionListItem from './TitleDescriptionListItem'
import propTypes from 'prop-types'

export default class LinkWithTitleDescriptionListItem extends TitleDescriptionListItem {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      url: propTypes.string.isRequired
    })
  }

  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      url: '',
      bemVariants: ['link']
    })
  }

  render () {
    return <a className={this.className} href={this.props.url}>
      <h2 className={this.titleClassName}>{this.props.title}</h2>
      <p className={this.descriptionClassName}>
        {this.props.description}
      </p>
    </a>
  }
}
