import React from "react";
import ReactDOM from "react-dom";
import CradminFilterRadioButton from "./CradminFilterRadioButton";


export default class CradminFilterRadioButtonWithCustomChoice extends CradminFilterRadioButton {
  static get defaultProps() {
    const superProps = super.defaultProps;
    const props = {
      customInputChangeDelay: 250,
      customInputExtraProps: {},
      customInputType: "text",
      customInputPlaceHolder: "",
      customInputLabelClassName: "label",
      customInputClassName: "input input--inline-xxsmall",
      customInputLabel: null,
      customInputSuffix: "",
      customInputPrefix: ""
    };
    return Object.assign({}, superProps, props);
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.CradminFilterRadioButtonWithCustomChoice.${this.props.signalNameSpace}`;
    this._onCustomInputChange = this._onCustomInputChange.bind(this);
  }

  _validateProps() {
    super._validateProps();
    if (this.props.customInputLabel == null) {
      throw Error("customInputLabel is a required property!");
    }
  }

  _onCustomInputChange(event) {
    this._cancelInputTimeout();
    this.setState({selectedValue: event.target.value});
    this.changeToValue = event.target.value;

    this._customInputTimeoutId = window.setTimeout(() => {this._sendChangeSignal()}, this.props.customInputTimeoutDelay);
  }

  _cancelInputTimeout() {
    if (this._customInputTimeoutId != undefined) {
      window.clearTimeout(this._customInputTimeoutId);
    }
  }

  render() {
    return <div className={this.props.wrapperClassName}>
      {this.getRenderOptions()}
      <label className={this.props.customInputLabelClassName}>
        {this.props.customInputLabel}
        <input type={this.props.customInputType}
               className={this.props.customInputClassName}
               placeholder={this.props.customInputPlaceHolder}
               onChange={this._onCustomInputChange}
               onBlur={this._onBlur}
               onFocus={this._onFocus}
               value={this.state.selectedValue}
        />
      </label>
    </div>
  }
}
