import React from "react";
import ReactDOM from "react-dom";
import NumberFormat from "../utilities/NumberFormat";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminDateSelectorHiddenIsoTime extends React.Component {
  static get defaultProps() {
    return {
      signalNameSpace: null,
      inputType: 'hidden',
      inputName: null,
      initialHour: 0,
      initialMinute: 0
    };
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.CradminDateSelectorHiddenIsoTime.${this.props.signalNameSpace}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminDateSelectorHiddenIsoTime');

    this.state = {
      hour: this.props.initialHour,
      minute: this.props.initialMinute
    };
    this.state.value = this._formatStateAsFieldValue();
    this._onHourValueChangeSignal = this._onHourValueChangeSignal.bind(this);
    this._onMinuteValueChangeSignal = this._onMinuteValueChangeSignal.bind(this);
    this.initializeSignalHandlers();
  }

  initializeSignalHandlers() {
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

  _formatTimeNumber(number) {
    number = parseInt(number, 10);
    if(isNaN(number)) {
      number = 0;
    }
    return NumberFormat.zeroPaddedString(number);
  }

  _formatStateAsFieldValue() {
    return `${this._formatTimeNumber(this.state.hour)}:${this._formatTimeNumber(this.state.minute)}`;
  }

  render() {
    let value = this._formatStateAsFieldValue();
    return <input
      type={this.props.inputType}
      name={this.props.inputName}
      value={value}
      readOnly
    />;
  }
}
