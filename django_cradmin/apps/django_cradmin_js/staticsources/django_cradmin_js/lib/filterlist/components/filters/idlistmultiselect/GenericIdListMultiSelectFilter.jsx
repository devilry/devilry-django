import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilter from '../AbstractFilter'
import AbstractGenericIdListMultiSelectItem from './AbstractGenericIdListMultiSelectItem'
import PageNumberPaginationFilterList from '../../filterlists/PageNumberPaginationFilterList'
import ThreeColumnLayout from '../../layout/ThreeColumnLayout'
import LoadMorePaginator from '../../paginators/LoadMorePaginator'
import DropDownSearchFilter from '../DropDownSearchFilter'
import * as gettext from 'ievv_jsbase/lib/gettext'
import SelectableList from '../../lists/SelectableList'
import GenericFilterListItemWrapper from './GenericFilterListItemWrapper'
import GenericSearchFilterWrapper from './GenericSearchFilterWrapper'
import { MULTISELECT } from '../../../filterListConstants'
import typeDetect from 'ievv_jsbase/lib/utils/typeDetect'
import ThreeColumnDropDownLayout from '../../layout/ThreeColumnDropDownLayout'

export default class GenericIdListMultiSelectFilter extends AbstractFilter {
  static get propTypes () {
    return {
      ...super.propTypes,
      idListApiUrl: PropTypes.string.isRequired,
      listItemIdName: PropTypes.string.isRequired,
      itemComponentType: PropTypes.any.isRequired,
      itemComponentPropOverrides: PropTypes.object,
      searchFilterComponentType: PropTypes.any,
      SearchFilterComponentPropOverrides: PropTypes.object,
      searchFilterLabel: PropTypes.string.isRequired,
      searchFilterName: PropTypes.string.isRequired,
      searchFilterPlaceholders: PropTypes.arrayOf(PropTypes.string.isRequired),
      dropDownBemVariants: PropTypes.arrayOf(PropTypes.string)
    }
  }

  static get defaultProps () {
    return {
      ...super.defaultProps,
      idListApiUrl: null,
      listItemIdName: 'id',
      itemComponentType: null,
      itemComponentPropOverrides: {},
      searchFilterLabel: gettext.pgettext('cradmin GenericIdListMultiSelect searchFilterLabel', 'Search'),
      searchFilterName: 'search',
      searchFilterPlaceholders: [gettext.gettext('Search ...')],
      searchFilterComponentType: DropDownSearchFilter,
      dropDownBemVariants: ['spaced-sm']
    }
  }

  get filterListSearchFieldConfig () {
    return {
      component: GenericSearchFilterWrapper,
      props: {
        name: 'search',
        componentType: this.props.searchFilterComponentType,
        label: this.props.searchFilterLabel,
        labelIsScreenreaderOnly: true,
        placeholder: this.props.searchFilterPlaceholders,
        ...this.props.SearchFilterComponentPropOverrides
      }
    }
  }

  get filterListStaticFilters () {
    return []
  }

  get filterListExtraFilters () {
    return []
  }

  get filterListFilterConfig () {
    return [
      ...this.filterListStaticFilters,
      ...this.filterListExtraFilters,
      this.filterListSearchFieldConfig
    ]
  }

  get itemComponentType () {
    if (!this.props.itemComponentType) {
      console.error(
        'No itemComponentType given in props. ' +
        'Falling back to AbstractGenericIdListMultiSelectItem. ' +
        'You should make a subclass of that component and pass it as "itemComponentType" in props!')
      return AbstractGenericIdListMultiSelectItem
    }
    return this.props.itemComponentType
  }

  get filterListItemListConfig () {
    return {
      component: SelectableList,
      itemSpec: {
        component: GenericFilterListItemWrapper,
        props: {
          listItemIdName: this.props.listItemIdName,
          componentType: this.itemComponentType,
          componentProps: this.props.itemComponentProps
        }
      }
    }
  }

  constructor (props) {
    super(props)
    this.filterListRef = React.createRef()
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.handleSelectItems = this.handleSelectItems.bind(this)
    this.handleDeselectItems = this.handleDeselectItems.bind(this)
  }

  handleSelectItems (data) {
    this.setFilterValue(this.filterListRef.selectedItemIdsAsArray())
    this.filterListRef.setFilterValue('search', '')
  }

  handleDeselectItems (data) {
    this.setFilterValue(this.filterListRef.selectedItemIdsAsArray())
  }

  get initiallySelectedItemIds () {
    if (!this.props.value) {
      return []
    }
    if (typeDetect(this.props.value) === 'array') {
      return this.props.value
    }
    const value = parseInt(this.props.value, 10)
    if (isNaN(value)) {
      return []
    }
    return [value]
  }

  get filterListConfig () {
    return {
      getItemsApiUrl: this.props.idListApiUrl,
      onSelectItems: this.handleSelectItems,
      onDeselectItems: this.handleDeselectItems,
      selectMode: MULTISELECT,
      initiallySelectedItemIds: this.initiallySelectedItemIds,
      components: [{
        component: ThreeColumnLayout,
        layout: this.filterListFilterConfig
      }, {
        component: ThreeColumnDropDownLayout,
        props: {
          componentGroups: ['expandable'],
          dropdownContentBemVariants: this.props.dropDownBemVariants
        },
        layout: [
          this.filterListItemListConfig,
          {
            component: LoadMorePaginator,
            props: {
              location: 'bottom'
            }
          }]
      }]
    }
  }

  render () {
    return <PageNumberPaginationFilterList {...this.filterListConfig} ref={ref => { this.filterListRef = ref }} />
  }
}
