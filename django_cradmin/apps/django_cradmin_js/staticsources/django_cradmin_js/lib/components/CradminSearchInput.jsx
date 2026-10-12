import React from "react";
import {HotKeys} from 'react-hotkeys';
import DomUtilities from "../utilities/DomUtilities";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminSearchInput extends React.Component {
  static get defaultProps() {
    return {
      changeDelay: 250,
      placeholder: 'Search ...',
      className: 'input input--outlined',
      autofocus: false,
      signalNameSpace: null,
    }
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.CradminSearchInput.${this.props.signalNameSpace}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminSearchInput');
    if(this.props.signalNameSpace == null) {
      throw new Error('The signalNameSpace prop is required.');
    }
    this.handleChange = this.handleChange.bind(this);
    this.handleFocus = this.handleFocus.bind(this);
    this.handleBlur = this.handleBlur.bind(this);
    this._onDataListInitializedSignal = this._onDataListInitializedSignal.bind(this);
    this._onClearSearchFieldSignal = this._onClearSearchFieldSignal.bind(this);
    this._onFocusOnSearchFieldSignal = this._onFocusOnSearchFieldSignal.bind(this);
    this._onMoveItemStartedSignal = this._onMoveItemStartedSignal.bind(this);
    this._onMoveItemCompleteSignal = this._onMoveItemCompleteSignal.bind(this);
    this.state = {
      searchString: '',
      disabled: false
    };
    this.initializeSignalHandlers();
  }

  initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.DataListInitialized`,
      this._name,
      this._onDataListInitializedSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.ClearSearchField`,
      this._name,
      this._onClearSearchFieldSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.FocusOnSearchField`,
      this._name,
      this._onFocusOnSearchFieldSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.MoveItemStarted`,
      this._name,
      this._onMoveItemStartedSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.MoveItemComplete`,
      this._name,
      this._onMoveItemCompleteSignal
    );
  }

  componentWillUnmount() {
    new SignalHandlerSingleton()
      .removeAllSignalsFromReceiver(this._name);
  }

  _onMoveItemStartedSignal() {
    this.setState({
      disabled: true
    });
  }

  _onMoveItemCompleteSignal() {
    this.setState({
      disabled: false
    });
  }

  _onDataListInitializedSignal(receivedSignalInfo) {
    this.setState({searchString: receivedSignalInfo.data.searchString});
    if(this.props.autofocus) {
      this.handleFocus();
      DomUtilities.forceFocus(this._inputDomElement);
    }
  }

  _onClearSearchFieldSignal(receivedSignalInfo) {
    this.setState({
      searchString: ''
    });
    this._sendChangeSignal();
  }

  _onFocusOnSearchFieldSignal(receivedSignalInfo) {
    DomUtilities.forceFocus(this._inputDomElement);
  }

  handleChange(event) {
    this._cancelInputTimeout();
    const searchString = event.target.value;
    this.setState({searchString: searchString});
    this._timeoutId = window.setTimeout(
      () => {this._sendChangeSignal()},
      this.props.changeDelay);
    if(searchString.length > 0) {
      new SignalHandlerSingleton().send(
        `${this.props.signalNameSpace}.SearchValueChangeNotEmpty`,
        this.state.searchString);
    } else {
      new SignalHandlerSingleton().send(
        `${this.props.signalNameSpace}.SearchValueChangeEmpty`,
        this.state.searchString);
    }
  }

  _cancelInputTimeout() {
    if(this._timeoutId != undefined) {
      window.clearTimeout(this._timeoutId);
    }
  }

  _sendChangeSignal() {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.SearchValueChange`,
      this.state.searchString);
  }

  handleFocus() {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.Focus`);
  }

  handleBlur() {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.Blur`);
  }

  get hotKeysMap() {
    return {
      'downKey': ['down'],
      'enterKey': ['enter'],
      'escapeKey': ['escape']
    };
  }

  _onDownKey() {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.SearchDownKey`);
  }

  _onEnterKey() {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.SearchEnterKey`);
  }

  _onEscapeKey() {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.SearchEscapeKey`);
  }

  get hotKeysHandlers() {
    return {
      'downKey': (event) => {
        event.preventDefault();
        this._onDownKey();
      },
      'enterKey': (event) => {
        event.preventDefault();
        this._onEnterKey();
      },
      'escapeKey': (event) => {
        event.preventDefault();
        this._onEscapeKey();
      },
    }
  }

  renderInputField() {
    return <input type="search"
                  disabled={this.state.disabled}
                  ref={(input) => { this._inputDomElement = input; }}
                  placeholder={this.props.placeholder}
                  className={this.props.className}
                  value={this.state.searchString}
                  onChange={this.handleChange}
                  onFocus={this.handleFocus}
                  onBlur={this.handleBlur}/>;
  }

  render() {
    return <HotKeys keyMap={this.hotKeysMap} handlers={this.hotKeysHandlers}>
      {this.renderInputField()}
    </HotKeys>;
  }
}
