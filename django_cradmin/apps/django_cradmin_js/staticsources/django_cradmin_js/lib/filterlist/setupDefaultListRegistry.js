import FilterListRegistry from './FilterListRegistrySingleton'
import BlockList from './components/lists/BlockList'
import IdOnlyListItem from './components/items/IdOnlyListItem'
import CheckboxBooleanFilter from './components/filters/CheckboxBooleanFilter'
import TitleDescriptionListItem from './components/items/TitleDescriptionListItem'
import LoadMorePaginator from './components/paginators/LoadMorePaginator'
import SearchFilter from './components/filters/SearchFilter'
import DropDownSearchFilter from './components/filters/DropDownSearchFilter'
import SelectableTitleDescriptionListItem from './components/items/SelectableTitleDescriptionListItem'
import SelectableList from './components/lists/SelectableList'
import ThreeColumnLayout from './components/layout/ThreeColumnLayout'
import PageNumberPaginationFilterList from './components/filterlists/PageNumberPaginationFilterList'
import ThreeColumnDropDownLayout from './components/layout/ThreeColumnDropDownLayout'
import HiddenFieldRenderSelectedItems from './components/selecteditems/HiddenFieldRenderSelectedItems'
import SelectableListRenderSelectedItems from './components/selecteditems/SelectableListRenderSelectedItems'
import BlockListRenderSelectedItems from './components/selecteditems/BlockListRenderSelectedItems'
import ParagraphLoadMorePaginator from './components/paginators/ParagraphLoadMorePaginator'
import SubmitSelectedItems from './components/selecteditems/SubmitSelectedItems'
import LinkWithTitleDescriptionListItem from './components/items/LinkWithTitleDescriptionListItem'
import SelectComponentGroup from './components/componentgroup/SelectComponentGroup'
import DropDownSelectFilter from './components/filters/DropDownSelectFilter'
import TightLabeledEmptyBooleanFilter from './components/filters/TightLabeledEmptyBooleanFilter'
import EmptyBooleanFilter from './components/filters/EmptyBooleanFilter'
import BlockListRenderSortableSelectedItems from './components/selecteditems/BlockListRenderSortableSelectedItems'

export function setupDefaultListRegistryFilterListComponents (registry) {
  registry.registerFilterListComponent('PageNumberPaginationFilterList', PageNumberPaginationFilterList)
}

export function setupDefaultListRegistryLayoutComponents (registry) {
  registry.registerLayoutComponent('ThreeColumnLayout', ThreeColumnLayout)
  registry.registerLayoutComponent('ThreeColumnDropDownLayout', ThreeColumnDropDownLayout)
}

export function setupDefaultListRegistryListComponents (registry) {
  registry.registerListComponent('BlockList', BlockList)
  registry.registerListComponent('SelectableList', SelectableList)
}

export function setupDefaultListRegistryFilterComponents (registry) {
  registry.registerFilterComponent('CheckboxBooleanFilter', CheckboxBooleanFilter)
  registry.registerFilterComponent('DropDownSelectFilter', DropDownSelectFilter)
  registry.registerFilterComponent('SearchFilter', SearchFilter)
  registry.registerFilterComponent('DropDownSearchFilter', DropDownSearchFilter)
  registry.registerFilterComponent('EmptyBooleanFilter', EmptyBooleanFilter)
  registry.registerFilterComponent('TightLabeledEmptyBooleanFilter', TightLabeledEmptyBooleanFilter)
}

export function setupDefaultListRegistryItemComponents (registry) {
  registry.registerItemComponent('IdOnlyItem', IdOnlyListItem)
  registry.registerItemComponent('TitleDescriptionItem', TitleDescriptionListItem)
  registry.registerItemComponent('SelectableTitleDescriptionItem', SelectableTitleDescriptionListItem)
  registry.registerItemComponent('LinkWithTitleDescriptionListItem', LinkWithTitleDescriptionListItem)
}

export function setupDefaultListRegistryPaginatorComponents (registry) {
  registry.registerPaginatorComponent('LoadMorePaginator', LoadMorePaginator)
  registry.registerPaginatorComponent('ParagraphLoadMorePaginator', ParagraphLoadMorePaginator)
}

export function setupDefaultListRegistryComponentGroupComponents (registry) {
  registry.registerComponentGroupComponent('SelectComponentGroup', SelectComponentGroup)
}

export function setupDefaultListRegistrySelectedItemsComponents (registry) {
  registry.registerSelectedItemsComponent('HiddenFieldRenderSelectedItems', HiddenFieldRenderSelectedItems)
  registry.registerSelectedItemsComponent('SelectableListRenderSelectedItems', SelectableListRenderSelectedItems)
  registry.registerSelectedItemsComponent('BlockListRenderSelectedItems', BlockListRenderSelectedItems)
  registry.registerSelectedItemsComponent('BlockListRenderSortableSelectedItems', BlockListRenderSortableSelectedItems)
  registry.registerSelectedItemsComponent('SubmitSelectedItems', SubmitSelectedItems)
}

export default function setupDefaultListRegistry () {
  const registry = new FilterListRegistry()
  setupDefaultListRegistryFilterListComponents(registry)
  setupDefaultListRegistryLayoutComponents(registry)
  setupDefaultListRegistryListComponents(registry)
  setupDefaultListRegistryFilterComponents(registry)
  setupDefaultListRegistryItemComponents(registry)
  setupDefaultListRegistryPaginatorComponents(registry)
  setupDefaultListRegistrySelectedItemsComponents(registry)
  setupDefaultListRegistryComponentGroupComponents(registry)
}
