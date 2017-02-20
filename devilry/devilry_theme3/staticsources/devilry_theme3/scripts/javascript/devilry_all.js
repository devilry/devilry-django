import DownloadCompressedArchiveWidget from "./widgets/DownloadCompressedArchiveWidget";
import DownloadCompressedArchiveStartButtonWidget from "./widgets/DownloadCompressedArchiveStartButtonWidget";
import DownloadCompressedArchiveDownloadLinkWidget from "./widgets/DownloadCompressedArchiveDownloadLinkWidget";
import GradingConfigurationWidget from "./widgets/GradingConfigurationWidget";
import GradingConfigurationCustomTableWidget from "./widgets/GradingConfigurationCustomTableWidget";


export default class DevilryTheme3All {
  constructor() {
    new window.ievv_jsbase_core.LoggerSingleton().setDefaultLogLevel(
      window.ievv_jsbase_core.LOGLEVEL.DEBUG);
    const widgetRegistry = new window.ievv_jsbase_core.WidgetRegistrySingleton();
    widgetRegistry.registerWidgetClass('devilry-download-compressed-archive',
      DownloadCompressedArchiveWidget);
    widgetRegistry.registerWidgetClass('devilry-download-compressed-archive-startbutton',
      DownloadCompressedArchiveStartButtonWidget);
    widgetRegistry.registerWidgetClass('devilry-download-compressed-archive-downloadlink',
      DownloadCompressedArchiveDownloadLinkWidget);
    widgetRegistry.registerWidgetClass('devilry-grading-configuration',
      GradingConfigurationWidget);
    widgetRegistry.registerWidgetClass('devilry-grading-configuration-custom-table',
      GradingConfigurationCustomTableWidget);

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
