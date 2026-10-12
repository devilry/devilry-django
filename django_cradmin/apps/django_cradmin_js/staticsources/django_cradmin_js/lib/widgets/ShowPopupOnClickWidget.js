import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";

export default class ShowPopupOnClickWidget extends AbstractWidget {
  getDefaultConfig() {
    return {
      signalNameSpace: null
    };
  }

  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    this._widgetInstanceId = widgetInstanceId;
    this._name = `django_cradmin.widgets.ShowPopupOnClickWidget.${widgetInstanceId}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.widgets.ShowPopupOnClickWidget');
    if(this.config.signalNameSpace == null) {
      throw new Error('The signalNameSpace config is required.');
    }
    this._onClick = this._onClick.bind(this);
    this.element.addEventListener('click', this._onClick);
  }

  destroy() {
    this.element.removeEventListener('click', this._onClick);
  }

  _onClick(event) {
    event.preventDefault();
    new SignalHandlerSingleton().send(
      `${this.config.signalNameSpace}.ShowPopup`);
  }
}
