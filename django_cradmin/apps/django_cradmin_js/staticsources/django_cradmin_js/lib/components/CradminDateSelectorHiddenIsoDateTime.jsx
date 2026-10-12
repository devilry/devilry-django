import React from "react";
import ReactDOM from "react-dom";
import CradminDateSelectorHiddenIsoDate from "./CradminDateSelectorHiddenIsoDate";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminDateSelectorHiddenIsoDateTime extends CradminDateSelectorHiddenIsoDate {
  static get defaultProps() {
    let defaultProps = super.defaultProps;
    defaultProps.initialHour = 0;
    defaultProps.initialMinute = 0;
    return defaultProps;
  }

  makeInitialState() {
    let initialState = super.makeInitialState();
    initialState.hour = this.props.initialHour;
    initialState.minute = this.props.initialMinute;
    return initialState;
  }

  makeValueFromStateObject() {
    let date = new Date(Date.UTC(
      this.state.year, this.state.month, this.state.day,
      this.state.hour, this.state.minute));
    return date.toISOString().split('.')[0].replace('T', ' ');
  }

  initializeSignalHandlers() {
    super.initializeSignalHandlers();
    this._onHourValueChangeSignal = this._onHourValueChangeSignal.bind(this);
    this._onMinuteValueChangeSignal = this._onMinuteValueChangeSignal.bind(this);
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.HourValueChange`,
      this._name,
      this._onHourValueChangeSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.MinuteValueChange`,
      this._name,
      this._onMinuteValueChangeSignal
    );
  }

  _onHourValueChangeSignal(receivedSignalInfo) {
    this.setState({hour: receivedSignalInfo.data});
  }

  _onMinuteValueChangeSignal(receivedSignalInfo) {
    this.setState({minute: receivedSignalInfo.data});
  }
}
