import DownloadCompressedArchiveWidget from "./widgets/DownloadCompressedArchiveWidget";
import DownloadCompressedArchiveStartButtonWidget from "./widgets/DownloadCompressedArchiveStartButtonWidget";
import DownloadCompressedArchiveDownloadLinkWidget from "./widgets/DownloadCompressedArchiveDownloadLinkWidget";
import GradingConfigurationWidget from "./widgets/GradingConfigurationWidget";
import GradingConfigurationCustomTableWidget from "./widgets/GradingConfigurationCustomTableWidget";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import LOGLEVEL from "ievv_jsbase/lib/log/loglevel";
import WidgetRegistrySingleton from "ievv_jsbase/lib/widget/WidgetRegistrySingleton";


const logger = new LoggerSingleton();
logger.setDefaultLogLevel(LOGLEVEL.INFO);

const widgetRegistry = new WidgetRegistrySingleton();
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

function _onDomReady() {
  // Initialize all widgets in document.body
  widgetRegistry.initializeAllWidgetsWithinElement(document.body);
}

if (document.readyState != 'loading'){
  _onDomReady();
} else {
  document.addEventListener('DOMContentLoaded', () => {
    _onDomReady();
  });
}
