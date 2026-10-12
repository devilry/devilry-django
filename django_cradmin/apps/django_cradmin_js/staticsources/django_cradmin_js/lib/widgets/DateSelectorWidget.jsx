import React from "react";
import ReactDOM from "react-dom";
import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import CradminDateSelector from "../components/CradminDateSelector";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class DateSelectorWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    ReactDOM.render(
      <CradminDateSelector {...this.config} />,
      this.element
    );
  }

  destroy() {
    ReactDOM.unmountComponentAtNode(this.element);
  }

  useAfterInitializeAllWidgets() {
    return true;
  }

  afterInitializeAllWidgets() {
    new SignalHandlerSingleton().send(
      `${this.config.signalNameSpace}.initializeValues`);
  }
}
