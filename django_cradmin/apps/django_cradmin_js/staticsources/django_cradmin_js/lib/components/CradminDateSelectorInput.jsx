import React from "react";
import NumberFormat from "../utilities/NumberFormat";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminDateSelectorInput extends React.Component {
  static get defaultProps() {
    return {
      signalNameSpace: null,
      inputClassName: 'dateinput__input',
      inputType: 'number',
      placeholder: '00',
      extraInputAttributes: {},
      initialValue: 0,
    };
  }

  _formatValue(value) {
    if(isNaN(value)) {
      return '00';
    } else {
      return NumberFormat.zeroPaddedString(value);
    }
  }

  get signalName() {
    throw new Error("Must be implemented in subclasses");
  }

  get minValue() {
    return 0;
  }

  get maxValue() {
    throw new Error("Must be implemented in subclasses");
  }

  constructor(props) {
    super(props);
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminDateSelectorInput');

    this.state = {
      value: this._formatValue(this.props.initialValue)
    };
    this._handleValueChange = this._handleValueChange.bind(this);
    this._handleClick = this._handleClick.bind(this);
  }

  _sendDateUpdateSignal(newValue) {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.${this.signalName}`, newValue);
  }

  _handleValueChange(event) {
    let stringValue = event.target.value.trim();
    let numericValue = parseInt(stringValue, 10);
    if(isNaN(numericValue)) {
      numericValue = 0;
    }
    if (numericValue > this.maxValue) {
      numericValue = this.maxValue;
    } else if (numericValue < this.minValue) {
      numericValue = this.minValue;
    }
    this.setState({value: this._formatValue(numericValue)});
    this._sendDateUpdateSignal(numericValue);
  }

  _handleClick(event) {
    this._inputElement.select();
  }

  render() {
    return <input value={this.state.value || ""}
                  ref={(input) => { this._inputElement = input; }}
                  type={this.props.inputType}
                  min={this.minValue}
                  max={this.maxValue}
                  step="1"
                  onChange={this._handleValueChange}
                  className={this.props.inputClassName}
                  placeholder={this.props.placeholder}
                  onClick={this._handleClick}
                  {...this.props.extraInputAttributes}/>;
  }
}
