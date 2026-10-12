import 'ievv_jsbase/lib/polyfill/all'
import LoggerSingleton from 'ievv_jsbase/lib/log/LoggerSingleton'
import LOGLEVEL from 'ievv_jsbase/lib/log/loglevel'
import WidgetRegistrySingleton from 'ievv_jsbase/lib/widget/WidgetRegistrySingleton'
import 'ievv_jsbase/lib/utils/i18nFallbacks'

import registerAllCradminWidgets from './widgets/registerAllCradminWidgets'
import setupDefaultListRegistry from './filterlist/setupDefaultListRegistry'
import registerAllDatetimePickerWidgets from './datetimepicker/widgets/registerAllDatetimePickerWidgets'
import registerAllHtml5DatetimePickerWidgets from './html5datetimepicker/widgets/registerAllHtml5DatetimePickerWidgets'

function _onDomReady () {
  new LoggerSingleton().setDefaultLogLevel(LOGLEVEL.INFO)
  registerAllCradminWidgets()
  registerAllDatetimePickerWidgets()
  registerAllHtml5DatetimePickerWidgets()
  setupDefaultListRegistry()

  const widgetRegistry = new WidgetRegistrySingleton()
  widgetRegistry.initializeAllWidgetsWithinElement(document.body)
  widgetRegistry.initializeAllWidgetsWithinElement(document.body)
}

if (document.readyState !== 'loading') {
  _onDomReady()
} else {
  document.addEventListener('DOMContentLoaded', () => {
    _onDomReady()
  })
}
