import React from 'react'
import {
  RENDER_LOCATION_BOTTOM, RENDER_LOCATION_CENTER, RENDER_LOCATION_DEFAULT,
  RENDER_LOCATION_LEFT,
  RENDER_LOCATION_RIGHT,
  RENDER_LOCATION_TOP
} from '../../filterListConstants'
import AbstractLayout from './AbstractLayout'
import BemUtilities from '../../../utilities/BemUtilities'
import PropTypes from 'prop-types'

export default class ThreeColumnLayout extends AbstractLayout {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      leftColumnBemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    })
  }

  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      leftColumnBemVariants: ['large'],
      centerColumnBemVariants: [],
      rightColumnBemVariants: ['small'],
      topBarBemVariants: [],
      bottomBarBemVariants: []
    })
  }

  //
  //
  // Css classes
  //
  //
  get bemBlock () {
    return 'columnlayout'
  }

  get className () {
    return this.bemBlock
  }

  get leftColumnClassName () {
    return BemUtilities.buildBemElement(this.bemBlock, 'column', this.props.leftColumnBemVariants)
  }

  get centerColumnClassName () {
    return BemUtilities.buildBemElement(this.bemBlock, 'column', this.props.centerColumnBemVariants)
  }

  get rightColumnClassName () {
    return BemUtilities.buildBemElement(this.bemBlock, 'column', this.props.rightColumnBemVariants)
  }

  get barBemBlock () {
    return 'box'
  }

  get topBarClassName () {
    return BemUtilities.addVariants(this.barBemBlock, this.props.topBarBemVariants)
  }

  get bottomBarClassName () {
    return BemUtilities.addVariants(this.barBemBlock, this.props.bottomBarBemVariants)
  }

  //
  //
  // Rendering
  //
  //

  renderLeftColumnContent () {
    return this.renderComponentsAtLocation(RENDER_LOCATION_LEFT)
  }

  renderLeftColumn () {
    const content = this.renderLeftColumnContent()
    if (content) {
      return <div className={this.leftColumnClassName} key={'leftColumn'}>
        {content}
      </div>
    }
    return null
  }

  renderTopBarContent () {
    return this.renderComponentsAtLocation(RENDER_LOCATION_TOP)
  }

  renderTopBar () {
    const content = this.renderTopBarContent()
    if (content && content.length > 0) {
      return <div className={this.topBarClassName} key={'topBar'}>
        {content}
      </div>
    }
    return null
  }

  renderBottomBarContent () {
    return this.renderComponentsAtLocation(RENDER_LOCATION_BOTTOM) || []
  }

  renderBottomBar () {
    const content = this.renderBottomBarContent()
    if (content && content.length > 0) {
      return <div className={this.bottomBarClassName} key={'bottomBar'}>
        {content}
      </div>
    }
    return null
  }

  renderRightColumnContent () {
    return this.renderComponentsAtLocation(RENDER_LOCATION_RIGHT)
  }

  renderRightColumn () {
    const content = this.renderRightColumnContent()
    if (content && content.length > 0) {
      return <div className={this.rightColumnClassName} key={'rightColumn'}>
        {content}
      </div>
    }
    return null
  }

  renderCenterColumnContent () {
    const centerColumnContent = [
      this.renderTopBar()
    ]
    centerColumnContent.push(...this.renderComponentsAtLocation(RENDER_LOCATION_CENTER, []))
    centerColumnContent.push(...this.renderComponentsAtLocation(RENDER_LOCATION_DEFAULT, []))
    if (this.props.isLoadingNewItemsFromApi || this.props.isLoadingMoreItemsFromApi) {
      centerColumnContent.push(this.renderLoadingIndicator())
    }
    centerColumnContent.push(this.renderBottomBar())
    return centerColumnContent
  }

  renderCenterColumn () {
    const content = this.renderCenterColumnContent()
    if (content && content.length > 0) {
      return <div className={this.centerColumnClassName} key={'centerColumn'}>
        {content}
      </div>
    }
    return null
  }

  renderContent () {
    return [
      this.renderLeftColumn(),
      this.renderCenterColumn(),
      this.renderRightColumn()
    ]
  }

  render () {
    return <div className={this.className} id={this.makeDomId()} aria-live={'polite'} aria-atomic={'true'}>
      {this.renderContent()}
    </div>
  }
}
