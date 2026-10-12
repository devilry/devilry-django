import React from "react";
import ReactDOM from "react-dom";
import CradminDateSelectorInput from "./CradminDateSelectorInput";


export default class CradminDateSelectorMinute extends CradminDateSelectorInput {
  get signalName() {
    return 'MinuteValueChange';
  }

  get maxValue() {
    return 59;
  }
}
