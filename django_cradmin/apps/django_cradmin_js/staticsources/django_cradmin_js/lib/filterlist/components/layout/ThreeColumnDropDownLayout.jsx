import React from 'react'
import PropTypes from 'prop-types'
import ThreeColumnLayout from './ThreeColumnLayout'
import BemUtilities from '../../../utilities/BemUtilities'

export default class ThreeColumnDropDownLayout extends ThreeColumnLayout {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      dropdownContentBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    })
  }

  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      dropdownContentBemVariants: ['spaced']
    })
  }

  get dropdownBemBlock () {
    return 'dropdown'
  }

  get dropdownContentBemElement () {
    return `${this.dropdownBemBlock}__content`
  }

  get dropdownContentClassName () {
    return BemUtilities.addVariants(
      this.dropdownContentBemElement, this.props.dropdownContentBemVariants)
  }

  render () {
    return <div className={this.dropdownBemBlock}>
      <div className={this.dropdownContentClassName}>
        {super.render()}
      </div>
    </div>
  }
}
