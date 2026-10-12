import React from "react";
import ReactDOM from "react-dom";
import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import CradminSearchInput from "../components/CradminSearchInput";


export default class SearchInputWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    ReactDOM.render(
      <CradminSearchInput {...this.config} />,
      this.element
    );
  }

  destroy() {
    ReactDOM.unmountComponentAtNode(this.element);
  }
}
