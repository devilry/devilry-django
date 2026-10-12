import React from 'react'
import AbstractList from './AbstractList'
import BemUtilities from '../../../utilities/BemUtilities'
import PropTypes from 'prop-types'

export default class BlockList extends AbstractList {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    })
  }

  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      bemBlock: 'blocklist',
      bemVariants: ['tight']
    })
  }

  get className () {
    return BemUtilities.addVariants(this.props.bemBlock, this.props.bemVariants)
  }

  getItemComponentProps (listItemData) {
    const props = super.getItemComponentProps(listItemData)
    props.bemBlock = this.props.bemBlock
    return props
  }

  render () {
    return <div className={this.className}>
      {this.renderListItems()}
    </div>
  }
}
