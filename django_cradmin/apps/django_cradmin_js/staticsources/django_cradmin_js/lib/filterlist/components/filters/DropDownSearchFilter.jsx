import React from 'react'
import AbstractSearchInputFilter from './AbstractSearchInputFilter'
import 'ievv_jsbase/lib/utils/i18nFallbacks'
import { COMPONENT_GROUP_EXPANDABLE } from '../../filterListConstants'
import SearchInputExpandCollapseButton from './components/SearchInputExpandCollapseButton'

/**
 * Dropdown search input filter.
 *
 * Works mostly like {@link SearchFilter} except that it expands/collapses
 * the {@link COMPONENT_GROUP_EXPANDABLE} component group when
 * it has focus and any search input (or when the expand button is clicked).
 *
 * See {@link SearchFilter.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "DropDownSearchFilter",
 *    "props": {
 *      "name": "search"
 *    }
 * }
 *
 * @example <caption>Spec - with initial value</caption>
 * {
 *    "component": "DropDownSearchFilter",
 *    "initialValue": "people",
 *    "props": {
 *      "name": "search"
 *    }
 * }
 *
 * @example <caption>Spec - with label and rotating placeholder</caption>
 * {
 *    "component": "DropDownSearchFilter",
 *    "props": {
 *      "name": "search",
 *      "label": "Search for some people",
 *      "placeholder": ["Thor", "Santa Claus", "Odin"]
 *    }
 * }
 *
 * @example <caption>Spec - full example with something to expand</caption>
 * {
 *   "getItemsApiUrl": "https://example.com/path/to/my/api",
 *   "header": {
 *     "component": "ThreeColumnLayout",
 *     "layout": [{
 *       "component": "DropDownSearchFilter",
 *       "props": {
 *         "name": "search"
 *       }
 *     }]
 *   },
 *   "body": {
 *     "component": "ThreeColumnDropDownLayout",
 *     "props": {
 *       "componentGroups": ["expandable"]
 *     },
 *     "layout": [{
 *       "component": "SelectableList",
 *       "itemSpec": {
 *         "component": "SelectableTitleDescriptionItem",
 *         "props": {
 *           "bemVariants": ["neutral-light", "bordered"]
 *         }
 *       }
 *     }, {
 *       "component": "LoadMorePaginator"
 *     }]
 *   }
 * }
 */
export default class DropDownSearchFilter extends AbstractSearchInputFilter {
  /**
   * Get default props. Same props as for
   * {@link AbstractSearchInputFilter.defaultProps}.
   *
   * @return {Object}
   */
  static get defaultProps () {
    return super.defaultProps
  }

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
