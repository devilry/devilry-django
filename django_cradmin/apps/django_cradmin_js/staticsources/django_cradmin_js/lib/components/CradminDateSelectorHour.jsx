import React from "react";
import ReactDOM from "react-dom";
import CradminDateSelectorInput from "./CradminDateSelectorInput";


export default class CradminDateSelectorHour extends CradminDateSelectorInput {
  get signalName() {
    return 'HourValueChange';
  }

  get maxValue() {
    return 23;
  }
}
