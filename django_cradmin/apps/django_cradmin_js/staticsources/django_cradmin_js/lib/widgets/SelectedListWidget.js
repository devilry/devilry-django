import React from "react";
import ReactDOM from "react-dom";
import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import CradminSelectedList from "../components/CradminSelectedList";


export default class SelectedListWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    ReactDOM.render(
      <CradminSelectedList uniqueId={widgetInstanceId} {...this.config} />,
      this.element
    );
  }

  destroy() {
    ReactDOM.unmountComponentAtNode(this.element);
  }
}
