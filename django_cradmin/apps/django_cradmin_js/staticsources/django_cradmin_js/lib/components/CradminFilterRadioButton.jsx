import React from "react";
import ReactDOM from "react-dom";
import typeDetect from 'ievv_jsbase/lib/utils/typeDetect';
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminFilterRadioButton extends React.Component {
  static get defaultProps() {
    return {
      wrapperClassName: "",
      labelClassName: "radio radio--block",
      indicatorClassName: "radio__control-indicator",
      inputName: null,
      initialValue: null,
      optionsList: []
    };
  }

  constructor(props) {
    super(props);
    this._validateProps();
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminFilterRadioButton');
    this._name = `django_cradmin.components.CradminFilterRadioButton.${this.props.signalNameSpace}`;

    this.originalValues = {};
    for (let option of this.props.optionsList) {
      this.originalValues[`${option.value}`] = option.value;
    }

    this._onDataListInitializedSignal = this._onDataListInitializedSignal.bind(this);
    this._onChange = this._onChange.bind(this);
    this._onFiltersChangeSignal = this._onFiltersChangeSignal.bind(this);
    this._onFocus = this._onFocus.bind(this);
    this._onBlur = this._onBlur.bind(this);

    this.state = {
      selectedValue: this.getInitialValue()
    };

    this.initializeSignalHandlers();
  }

  _validateProps() {
    if (typeDetect(this.props.optionsList) != "array" || this.props.optionsList.length == 0) {
      throw Error(`this.props.optionsObject must be a list containing at least one {value: "value", label: "label"} object`);
    }
    if (typeDetect(this.props.inputName) != "string" || this.props.inputName == '') {
      throw Error(`props.optionsList.inputName must be a valid string`);
    }
    if(this.props.signalNameSpace == null) {
      throw new Error('The signalNameSpace prop is required.');
    }
    if(this.props.filterKey == null) {
      throw new Error('The filterKey prop is required.');
    }
  }

  getInitialValue() {
    if (this.props.initialValue != null) {
      return this.props.initialValue;
    }
    return this.props.optionsList[0].value;
  }

  initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.DataListInitialized`,
      this._name,
      this._onDataListInitializedSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.FiltersChange`,
      this._name,
      this._onFiltersChangeSignal
    );
  }

  _getNewValueFromFiltersMap(filtersMap){
    let newValue = filtersMap.get(this.props.filterKey);
    if(newValue == undefined) {
      newValue = this.getInitialValue();
    }
    return newValue;
  }

  _setValueFromFiltersMap(filtersMap) {
    let newValue = this._getNewValueFromFiltersMap(filtersMap);
    this.setState({
      selectedValue: newValue
    });
  }

  _onDataListInitializedSignal(receivedSignalInfo) {
    const state = receivedSignalInfo.data;
    this._setValueFromFiltersMap(state.filtersMap);
  }

  componentWillUnmount() {
    new SignalHandlerSingleton()
      .removeAllSignalsFromReceiver(this._name);
  }

  _sendChangeSignal() {
    const filtersMapPatch = new Map();
    filtersMapPatch.set(this.props.filterKey, this.changeToValue);
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.PatchFilters`,
      filtersMapPatch);
  }

  _onChange(event) {
    event.preventDefault();
    this.changeToValue = this.originalValues[event.target.value];
    this._sendChangeSignal();
  }

  _onFocus(event) {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.Focus`);
  }

  _onBlur(event) {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.Blur`);
  }

  _onFiltersChangeSignal(receivedSignalInfo) {
    this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    const filtersMap = receivedSignalInfo.data;
    this._setValueFromFiltersMap(filtersMap);
  }

  getRenderOptionIndicator() {
    if (this.props.indicatorClassName == null || this.props.indicatorClassName == "") {
      return "";
    }
    return <span className={this.props.indicatorClassName} />;
  }

  getRenderOptions() {
    let renderedOptions = [];
    for (let option of this.props.optionsList) {
      let renderedOption = <label key={option.value} className={this.props.labelClassName}>
        <input type="radio"
               name={this.props.inputName}
               value={option.value}
               onChange={this._onChange}
               checked={this.state.selectedValue == option.value}
               onFocus={this._onFocus}
               onBlur={this._onBlur}
        />
        {this.getRenderOptionIndicator()}
        {option.label}
      </label>;

      renderedOptions.push(renderedOption);
    }
    return renderedOptions;
  }

  render() {
    return <div className={this.props.wrapperClassName}>
      {this.getRenderOptions()}
    </div>
  }
}
