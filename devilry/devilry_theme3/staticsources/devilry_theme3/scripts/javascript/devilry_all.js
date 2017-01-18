import DownloadCompressedArchiveWidget from "./widgets/DownloadCompressedArchiveWidget";


export default class DevilryTheme3All {
  constructor() {
    new window.ievv_jsbase_core.LoggerSingleton().setDefaultLogLevel(
      window.ievv_jsbase_core.LOGLEVEL.DEBUG);
    const widgetRegistry = new window.ievv_jsbase_core.WidgetRegistrySingleton();
    widgetRegistry.registerWidgetClass('devilry-download-compressed-archive',
      DownloadCompressedArchiveWidget);

    if (document.readyState != 'loading'){
      widgetRegistry.initializeAllWidgetsWithinElement(document.body);
    } else {
      document.addEventListener('DOMContentLoaded', () => {
        widgetRegistry.initializeAllWidgetsWithinElement(document.body);
      });
    }
  }
}

new DevilryTheme3All();
