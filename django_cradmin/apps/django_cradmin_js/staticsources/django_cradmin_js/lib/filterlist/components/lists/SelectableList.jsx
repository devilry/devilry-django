import React from 'react'
import AbstractList from './AbstractList'
import BemUtilities from '../../../utilities/BemUtilities'
import PropTypes from 'prop-types'
// import { KEYBOARD_NAVIGATION_GROUP_KEY_UP_DOWN } from '../../filterListConstants'

export default class SelectableList extends AbstractList {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    })
  }

  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      bemVariants: ['compact']
    })
  }

  get bemBlock () {
    return 'selectable-list'
  }

  get className () {
    return BemUtilities.addVariants(this.bemBlock, this.props.bemVariants)
  }

  // static getKeyboardNavigationGroups (componentSpec) {
  //   return [KEYBOARD_NAVIGATION_GROUP_KEY_UP_DOWN]
  // }

  getItemComponentProps (listItemData) {
    const props = super.getItemComponentProps(listItemData)
    props.bemBlock = this.bemBlock
    return props
  }

  render () {
    return <div className={this.className}>
      {this.renderListItems()}
    </div>
  }
}
