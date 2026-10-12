import React from 'react'
import 'ievv_jsbase/lib/utils/i18nFallbacks'
import { COMPONENT_GROUP_EXPANDABLE } from '../../../filterListConstants'
import AbstractGenericIdListSearchInputMultiSelect from './AbstractGenericIdListSearchInputMultiSelect'
import SearchInputExpandCollapseButton from '../components/SearchInputExpandCollapseButton'

export default class AbstractGenericIdListDropDownSearchInputMultiSelect extends AbstractGenericIdListSearchInputMultiSelect {
  static shouldReceiveFocusEvents (componentSpec) {
    return true
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onClickExpandCollapseButton = this.onClickExpandCollapseButton.bind(this)
    this.onExpandandCollapseButtonFocus = this.onExpandandCollapseButtonFocus.bind(this)
  }

  onAnyComponentFocus (newFocusComponentInfo, prevFocusComponentInfo, didChangeFilterListFocus) {
    if (newFocusComponentInfo.uniqueComponentKey === this.props.uniqueComponentKey) {
      return
    }
    if (newFocusComponentInfo.componentGroups === null) {
      this.disableExpandableComponentGroup()
    } else if (newFocusComponentInfo.componentGroups.indexOf(this.expandableComponentGroup) === -1) {
      this.disableExpandableComponentGroup()
    }
  }

  onAnyComponentBlur (blurredComponentInfo, didChangeFilterListFocus) {
    if (didChangeFilterListFocus) {
      this.disableExpandableComponentGroup()
    }
  }

  get expandableComponentGroup () {
    return COMPONENT_GROUP_EXPANDABLE
  }

  isExpanded () {
    return this.props.childExposedApi.componentGroupIsEnabled(this.expandableComponentGroup)
  }

  toggleExpandableComponentGroup () {
    this.props.childExposedApi.toggleComponentGroup(this.expandableComponentGroup)
  }

  enableExpandableComponentGroup () {
    this.props.childExposedApi.enableComponentGroup(this.expandableComponentGroup)
  }

  disableExpandableComponentGroup () {
    this.props.childExposedApi.disableComponentGroup(this.expandableComponentGroup)
  }

  onClickExpandCollapseButton () {
    this.toggleExpandableComponentGroup()
  }

  onFocus (...args) {
    this.enableExpandableComponentGroup()
    super.onFocus()
  }

  onClickClearButton () {
    this.props.childExposedApi.deselectAllItems()
  }

  onExpandandCollapseButtonFocus () {
    // NOTE: We do not use this.onFocus() since that toggles the
    // collapsible component group. This leads to a race-condition
    // when just clicking on the expand button since it will first get focus,
    // which will expand the component group on, then be clicked, which will
    // toggle the group off.
    super.onFocus()
  }

  renderExpandCollapseButton () {
    return <SearchInputExpandCollapseButton
      key={'expand-collapse-button'}
      onClick={this.onClickExpandCollapseButton}
      onFocus={this.onExpandandCollapseButtonFocus}
      onBlur={this.onBlur}
      isExpanded={this.isExpanded()} />
  }

  renderButtons () {
    return [
      this.renderClearButton(),
      this.renderExpandCollapseButton()
    ]
  }
}
