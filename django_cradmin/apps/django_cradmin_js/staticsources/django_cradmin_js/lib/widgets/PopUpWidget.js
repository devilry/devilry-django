import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import DomUtilities from "../utilities/DomUtilities";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class PopUpWidget extends AbstractWidget {
  getDefaultConfig() {
    return {
      signalNameSpace: null
    };
  }

  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    this._widgetInstanceId = widgetInstanceId;
    this._name = `django_cradmin.widgets.PopUpWidget.${widgetInstanceId}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.widgets.PopUpWidget');
    if(this.config.signalNameSpace == null) {
      throw new Error('The signalNameSpace config is required.');
    }
    this._onShowPopupSignal = this._onShowPopupSignal.bind(this);
    this._onHidePopupSignal = this._onHidePopupSignal.bind(this);
    this._signalHandler = new SignalHandlerSingleton();
    this.initializeSignalHandlers();
  }

  initializeSignalHandlers() {
    this._signalHandler.addReceiver(
      `${this.config.signalNameSpace}.ShowPopup`,
      this._name,
      this._onShowPopupSignal);
    this._signalHandler.addReceiver(
      `${this.config.signalNameSpace}.HidePopup`,
      this._name,
      this._onHidePopupSignal);
  }

  destroy() {
    this._signalHandler.removeAllSignalsFromReceiver(this._name);
  }

  _onShowPopupSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    DomUtilities.show(this.element);
    document.body.classList.add('fill-view-height');
  }

  _onHidePopupSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    DomUtilities.hide(this.element);
    document.body.classList.remove('fill-view-height');
  }
}
