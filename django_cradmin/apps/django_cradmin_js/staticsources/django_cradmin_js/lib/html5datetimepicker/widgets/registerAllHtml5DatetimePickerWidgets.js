import WidgetRegistrySingleton from 'ievv_jsbase/lib/widget/WidgetRegistrySingleton'
import Html5DateInputWidget from './Html5DateInputWidget'
import Html5TimeInputWidget from './Html5TimeInputWidget'

/**
 * Register all the cradmin widgets for datetimepicker in the ievv_jsbase WidgetRegistrySingleton.
 */
export default function registerAllDatetimePickerWidgets () {
  const widgetRegistry = new WidgetRegistrySingleton()
  widgetRegistry.registerWidgetClass('cradmin-html5-datepicker', Html5DateInputWidget)
  widgetRegistry.registerWidgetClass('cradmin-html5-timepicker', Html5TimeInputWidget)
}
