import React from "react";
import ReactDOM from "react-dom";
import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import CradminLoadMoreButton from "../components/CradminLoadMoreButton";


export default class LoadMoreButtonWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    ReactDOM.render(
      <CradminLoadMoreButton {...this.config} />,
      this.element
    );
  }

  destroy() {
    ReactDOM.unmountComponentAtNode(this.element);
  }
}
