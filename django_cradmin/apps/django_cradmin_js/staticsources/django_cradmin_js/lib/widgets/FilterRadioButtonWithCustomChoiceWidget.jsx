import React from "react";
import ReactDOM from "react-dom";
import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import CradminFilterRadioButtonWithCustomChoice from "../components/CradminFilterRadioButtonWithCustomChoice";


export default class FilterRadioButtonWithCustomChoiceWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    ReactDOM.render(
      <CradminFilterRadioButtonWithCustomChoice {...this.config} />,
      this.element
    );
  }

  destroy() {
    ReactDOM.unmountComponentAtNode(this.element);
  }
}
