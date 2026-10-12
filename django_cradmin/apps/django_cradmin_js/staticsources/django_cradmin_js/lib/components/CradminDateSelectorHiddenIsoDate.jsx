import React from "react";
import ReactDOM from "react-dom";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminDateSelectorHiddenIsoDate extends React.Component {
  static get defaultProps() {
    return {
      signalNameSpace: null,
      inputType: 'hidden',
      inputName: null,
      initialDay: null,
      initialMonth: null,
      initialYear: null,
    };
  }

  makeInitialState() {
    return {
      day: this.props.initialDay,
      month: this.props.initialMonth,
      year: this.props.initialYear,
    }
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.CradminDateSelectorHiddenIsoDate.${this.props.signalNameSpace}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminDateSelectorHiddenIsoDate');

    this.state = this.makeInitialState();
    this._onDayValueChangeSignal = this._onDayValueChangeSignal.bind(this);
    this._onMonthValueChangeSignal = this._onMonthValueChangeSignal.bind(this);
    this._onYearValueChangeSignal = this._onYearValueChangeSignal.bind(this);
    this.initializeSignalHandlers();
  }

  initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.DayValueChange`,
      this._name,
      this._onDayValueChangeSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.MonthValueChange`,
      this._name,
      this._onMonthValueChangeSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.YearValueChange`,
      this._name,
      this._onYearValueChangeSignal
    );
  }

  isInvalid() {
    return this.state.day == null
      || this.state.year == null
      || this.state.month == null;
  }

  makeValueFromStateObject() {
      let date = new Date(Date.UTC(this.state.year, this.state.month, this.state.day));
      return date.toISOString().split('T')[0];
  }

  _onDayValueChangeSignal(receivedSignalInfo) {
    this.setState({day: receivedSignalInfo.data});
  }

  _onMonthValueChangeSignal(receivedSignalInfo) {
    this.setState({month: receivedSignalInfo.data});
  }

  _onYearValueChangeSignal(receivedSignalInfo) {
    this.setState({year: receivedSignalInfo.data});
  }

  render() {
    let value = '';
    if(!this.isInvalid()) {
      value = this.makeValueFromStateObject();
    }
    return <input
      type={this.props.inputType}
      name={this.props.inputName}
      value={value}
      readOnly
    />;
  }
}
