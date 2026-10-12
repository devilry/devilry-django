import WidgetRegistrySingleton from 'ievv_jsbase/lib/widget/WidgetRegistrySingleton'
import MenuToggleWidget from './MenuToggleWidget'
import ToggleableMenuWidget from './ToggleableMenuWidget'
import TabButtonWidget from './TabButtonWidget'
import TabPanelWidget from './TabPanelWidget'
import SearchInputWidget from './SearchInputWidget'
import SelectableListWidget from './SelectableListWidget'
import SelectedListWidget from './SelectedListWidget'
import HtmlListWidget from './HtmlListWidget'
import StaticDataListWidget from './StaticDataListWidget'
import ApiDataListWidget from './ApiDataListWidget'
import DataListDisplayByStateWidget from './DataListDisplayByStateWidget'
import LoadMoreButtonWidget from './LoadMoreButtonWidget'
import HiddenInputListWidget from './HiddenInputListWidget'
import SignalRouterWidget from './SignalRouterWidget'
import PopUpWidget from './PopUpWidget'
import ShowPopupOnClickWidget from './ShowPopupOnClickWidget'
import HidePopupOnClickWidget from './HidePopupOnClickWidget'
import FilterCheckboxFilter from './FilterCheckboxWidget'
import FilterRadioButtonWidget from './FilterRadioButtonWidget'
import FilterRadioButtonWithCustomChoiceWidget from './FilterRadioButtonWithCustomChoiceWidget'
import AutoSubmitFormAfterCountdownWidget from './AutoSubmitFormAfterCountdownWidget'
import PrintOnClickWidget from './PrintOnClickWidget'
import DateSelectorWidget from './DateSelectorWidget'
import HtmlListWithMovableItemsWidget from './HtmlListWithMovableItemsWidget'
import GeoLocationWidget from './GeoLocationWidget'
import GeoLocationFilterWidget from './GeoLocationFilterWidget'
import GeoLocationDebugWidget from './GeoLocationDebugWidget'
import RotatingPlaceholderWidget from './RotatingPlaceholderWidget'
import FilterListWidget from './FilterListWidget'
import DisableFormSubmitOnEnter from './DisableFormSubmitOnEnter'

/**
 * Register all the cradmin widgets in the ievv_jsbase WidgetRegistrySingleton.
 */
export default function registerAllCradminWidgets () {
  const widgetRegistry = new WidgetRegistrySingleton()
  // widgetRegistry.registerWidgetClass('cradmin-datetime-picker', DateTimePicker);
  widgetRegistry.registerWidgetClass('cradmin-menutoggle', MenuToggleWidget)
  widgetRegistry.registerWidgetClass('cradmin-toggleable-menu', ToggleableMenuWidget)
  widgetRegistry.registerWidgetClass('cradmin-tab-button', TabButtonWidget)
  widgetRegistry.registerWidgetClass('cradmin-tab-panel', TabPanelWidget)
  widgetRegistry.registerWidgetClass('cradmin-search-input', SearchInputWidget)
  widgetRegistry.registerWidgetClass('cradmin-static-data-list', StaticDataListWidget)
  widgetRegistry.registerWidgetClass('cradmin-api-data-list', ApiDataListWidget)
  widgetRegistry.registerWidgetClass('cradmin-data-list-display-by-state', DataListDisplayByStateWidget)
  widgetRegistry.registerWidgetClass('cradmin-selectable-list', SelectableListWidget)
  widgetRegistry.registerWidgetClass('cradmin-selected-list', SelectedListWidget)
  widgetRegistry.registerWidgetClass('cradmin-html-list', HtmlListWidget)
  widgetRegistry.registerWidgetClass('cradmin-html-list-with-movable-items', HtmlListWithMovableItemsWidget)
  widgetRegistry.registerWidgetClass('cradmin-load-more-button', LoadMoreButtonWidget)
  widgetRegistry.registerWidgetClass('cradmin-hidden-input-list', HiddenInputListWidget)
  widgetRegistry.registerWidgetClass('cradmin-signal-router', SignalRouterWidget)
  widgetRegistry.registerWidgetClass('cradmin-popup', PopUpWidget)
  widgetRegistry.registerWidgetClass('cradmin-show-popup', ShowPopupOnClickWidget)
  widgetRegistry.registerWidgetClass('cradmin-hide-popup', HidePopupOnClickWidget)
  widgetRegistry.registerWidgetClass('cradmin-filter-checkbox', FilterCheckboxFilter)
  widgetRegistry.registerWidgetClass('cradmin-filter-radio-button', FilterRadioButtonWidget)
  widgetRegistry.registerWidgetClass('cradmin-filter-radio-button-with-custom-choice', FilterRadioButtonWithCustomChoiceWidget)
  widgetRegistry.registerWidgetClass('cradmin-dateselector', DateSelectorWidget)
  widgetRegistry.registerWidgetClass('cradmin-auto-submit-form-after-countdown', AutoSubmitFormAfterCountdownWidget)
  widgetRegistry.registerWidgetClass('cradmin-print-on-click', PrintOnClickWidget)
  widgetRegistry.registerWidgetClass('cradmin-geolocation', GeoLocationWidget)
  widgetRegistry.registerWidgetClass('cradmin-geolocation-debug', GeoLocationDebugWidget)
  widgetRegistry.registerWidgetClass('cradmin-geolocation-filter', GeoLocationFilterWidget)
  widgetRegistry.registerWidgetClass('cradmin-rotating-placeholder', RotatingPlaceholderWidget)
  widgetRegistry.registerWidgetClass('cradmin-filterlist', FilterListWidget)
  widgetRegistry.registerWidgetClass('cradmin-disable-form-submit-on-enter', DisableFormSubmitOnEnter)
}
