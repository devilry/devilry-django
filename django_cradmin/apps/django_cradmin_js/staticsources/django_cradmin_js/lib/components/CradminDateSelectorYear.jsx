import React from "react";
import ReactDOM from "react-dom";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";
import 'ievv_jsbase/lib/utils/i18nFallbacks'


export default class CradminDateSelectorYear extends React.Component {
  static get defaultProps() {
    let currentYear = new Date().getUTCFullYear();
    return {
      signalNameSpace: null,
      extraSelectAttributes: {},
      labelText: window.gettext('Year'),
      minYear: currentYear - 10,
      maxYear: currentYear + 50,
      initialValue: null
    };
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.CradminDateSelectorYear.${this.props.signalNameSpace}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminDateSelectorYear');

    this._handleYearChange = this._handleYearChange.bind(this);
    this._postInit = this._postInit.bind(this);
    this.state = {value: 0, disabled: true};

    this._initializeSignalHandlers();
  }

  _initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.initializeValues`,
      this._name,
      this._postInit
    );
  }

  _postInit() {
    if (!this.state.disabled) {
      return;
    }
    this.setState({disabled: false});
    this._sendDateUpdateSignal(this.props.initialValue)
  }

  _sendDateUpdateSignal(newYear) {
    this.setState({value: newYear});

    if (newYear == 0) {
      newYear = null;
    }

    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.YearValueChange`, newYear, (info) => {
        if (this.logger.isDebug) {
          this.logger.debug(`Update year: \n\tNew year: ${newYear}\n\t${info}`);
        }
      });
  }

  _handleYearChange(event) {
    let newYear = event.target.value;
    this._sendDateUpdateSignal(newYear);
  }

  renderOptions() {
    if (this.state.disabled) {
      return [];
    }
    let yearOptions = [
      <option key={`${this._name}.yearOption.0`} value={0}>{this.props.labelText}</option>
    ];
    for (let year = this.props.minYear; year <= this.props.maxYear; year++) {
      yearOptions.push(
        <option key={`${this._name}.yearOption.${year}`} value={year}>{year}</option>
      );
    }

    return yearOptions
  }

  render() {
    return (
      <select value={this.state.value || 0}
              onChange={this._handleYearChange}
              disabled={this.state.disabled}
              {...this.props.extraSelectAttributes}>
        {this.renderOptions()}
      </select>
    )
  }
}
