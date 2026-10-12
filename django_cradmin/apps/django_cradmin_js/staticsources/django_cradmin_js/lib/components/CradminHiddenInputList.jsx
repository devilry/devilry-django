import React from "react";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminHiddenInputList extends React.Component {

  static get defaultProps() {
    return {
      keyAttribute: 'id',
      signalNameSpace: null,
      inputName: null,
      inputType: "hidden"
    }
  }

  constructor(props) {
    super(props);
    this._name = 'django_cradmin.components.CradminHiddenInputList';
    this.logger = new LoggerSingleton().getLogger(
      this._name);
    if(this.props.signalNameSpace == null) {
      throw new Error('The signalNameSpace prop is required.');
    }
    if(this.props.inputName == null) {
      throw new Error('The inputName prop is required.');
    }
    this._onSelectionChangeSignal = this._onSelectionChangeSignal.bind(this);

    this.state = {
      selectedItemsMap: new Map()
    };

    this.initializeSignalHandlers();
  }

  initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.SelectionChange`,
      this._name,
      this._onSelectionChangeSignal
    );
  }

  componentWillUnmount() {
    new SignalHandlerSingleton().removeReceiver(
      `${this.props.signalNameSpace}.SelectionChange`,
      this._name
    );
  }

  _onSelectionChangeSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    this.setState({
      selectedItemsMap: receivedSignalInfo.data.selectedItemsMap
    });
  }

  render() {
    return <span>
      {this.renderItems()}
    </span>;
  }

  renderItem(value) {
    return <input key={value}
                  value={value}
                  type={this.props.inputType}
                  name={this.props.inputName}
                  readOnly={true} />;
  }

  renderItems() {
    const items = [];
    for(let value of this.state.selectedItemsMap.keys()) {
      items.push(this.renderItem(value));
    }
    return items;
  }
}
