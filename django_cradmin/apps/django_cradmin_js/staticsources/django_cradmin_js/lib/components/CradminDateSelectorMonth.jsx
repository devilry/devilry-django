import React from "react";
import ReactDOM from "react-dom";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";
import 'ievv_jsbase/lib/utils/i18nFallbacks'


export default class CradminDateSelectorMonth extends React.Component {
  static get defaultProps() {
    return {
      signalNameSpace: null,
      extraSelectAttributes: {},
      labelText: window.gettext('Month'),
      monthLabels: [
        window.pgettext('month shortname', 'Jan'),
        window.pgettext('month shortname', 'Feb'),
        window.pgettext('month shortname', 'Mar'),
        window.pgettext('month shortname', 'Apr'),
        window.pgettext('month shortname', 'May'),
        window.pgettext('month shortname', 'Jun'),
        window.pgettext('month shortname', 'Jul'),
        window.pgettext('month shortname', 'Aug'),
        window.pgettext('month shortname', 'Sep'),
        window.pgettext('month shortname', 'Oct'),
        window.pgettext('month shortname', 'Nov'),
        window.pgettext('month shortname', 'Des')
      ],
      useLabels: true,
      initialValue: new Date().getUTCMonth()
    }
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.CradminDateSelectorMonth.${this.props.signalNameSpace}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminDateSelectorMonth');

    this._handleMonthChange = this._handleMonthChange.bind(this);
    this._postInit = this._postInit.bind(this);
    this.state = {value: 0, disabled: true};
    if (!this.props.useLabels) {
      this.props.monthLabels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    }

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
    this.logger.debug(`month, afterinitializeall...`);
    this.setState({disabled: false});
    this._sendDateUpdateSignal(this.props.initialValue);
  }

  _sendDateUpdateSignal(newMonth) {
    this.setState({value: newMonth});

    if (newMonth <= 0) {
      newMonth = null;
    } else {
      newMonth--;
    }

    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.MonthValueChange`, newMonth, (info) => {
        if (this.logger.isDebug) {
          this.logger.debug(`Update month: \n\tNew month: ${newMonth}\n\t${info}`);
        }
      });
  }

  _handleMonthChange(event) {
    let newMonth = event.target.value;
    this._sendDateUpdateSignal(newMonth);
  }

  renderOptions() {
    if (this.state.disabled) {
      return [];
    }

    let monthOptions = [
      <option key={`${this._name}.monthOption.0`} value={0}>{this.props.labelText}</option>
    ];
    for (let monthNumber = 1; monthNumber <= this.props.monthLabels.length; monthNumber++) {
      monthOptions.push(
        <option key={`${this._name}.monthOption.${monthNumber}`} value={monthNumber}>{this.props.monthLabels[monthNumber-1]}</option>
      );
    }
    return monthOptions;
  }

  render() {
    return (
      <select value={this.state.value || 0}
              onChange={this._handleMonthChange}
              disabled={this.state.disabled}
              {...this.props.extraSelectAttributes}>
        {this.renderOptions()}
      </select>
    )
  }
}
