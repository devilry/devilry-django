import React from "react";
import CradminSelectedListItem from "./CradminSelectedListItem";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminSelectedList extends React.Component {

  static get defaultProps() {
    return {
      className: 'selectable-list selectable-list--inline selectable-list--nomargin',
      keyAttribute: 'id',
      signalNameSpace: null,
      uniqueId: '',
      itemComponentProps: {}
    }
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.CradminSelectedList.${this.props.signalNameSpace}.${this.props.uniqueId}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminSelectedList');
    if(this.props.signalNameSpace == null) {
      throw new Error('The signalNameSpace prop is required.');
    }
    this._onSelectionChangeSignal = this._onSelectionChangeSignal.bind(this);
    this._onFocusOnDeSelectableItemSignal = this._onFocusOnDeSelectableItemSignal.bind(this);
    this._onFocusOnFirstSelectedItemSignal = this._onFocusOnFirstSelectedItemSignal.bind(this);
    this._onFocusOnLastSelectedItemSignal = this._onFocusOnLastSelectedItemSignal.bind(this);

    this._focusOnItemData = null;
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
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.FocusOnDeSelectableItem`,
      this._name,
      this._onFocusOnDeSelectableItemSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.FocusOnFirstSelectedItem`,
      this._name,
      this._onFocusOnFirstSelectedItemSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.FocusOnLastSelectedItem`,
      this._name,
      this._onFocusOnLastSelectedItemSignal
    );
  }

  componentWillUnmount() {
    new SignalHandlerSingleton()
      .removeAllSignalsFromReceiver(this._name);
  }


  _onSelectionChangeSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    this.setState({
      selectedItemsMap: receivedSignalInfo.data.selectedItemsMap
    });
  }

  _onFocusOnDeSelectableItemSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    this._focusOnItemData = receivedSignalInfo.data;
  }

  _onFocusOnFirstSelectedItemSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    if(this.state.selectedItemsMap.size > 0) {
      const selectedItemsArray = Array.from(this.state.selectedItemsMap.values());
      this._focusOnItemData = selectedItemsArray[0];
    }
  }

  _onFocusOnLastSelectedItemSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    if(this.state.selectedItemsMap.size > 0) {
      const selectedItemsArray = Array.from(this.state.selectedItemsMap.values());
      this._focusOnItemData = selectedItemsArray[selectedItemsArray.length - 1];
    }
  }

  renderItem(itemKey, props) {
    return <CradminSelectedListItem key={itemKey} {...props} />;
  }

  renderItems() {
    const items = [];
    let itemKeys = Array.from(this.state.selectedItemsMap.keys());
    let previousItemData = null;
    for(let index=0; index < itemKeys.length; index++) {
      let itemKey = itemKeys[index];
      let itemData = this.state.selectedItemsMap.get(itemKey);

      let nextItemData = null;
      let isLast = index == (itemKeys.length - 1);
      if(!isLast) {
        nextItemData = this.state.selectedItemsMap.get(itemKeys[index + 1]);
      }

      let props = Object.assign({}, this.props.itemComponentProps, {
        data: itemData,
        itemKey: itemKey,
        signalNameSpace: this.props.signalNameSpace,
        previousItemData: previousItemData,
        nextItemData: nextItemData,
        uniqueListId: this.props.uniqueId
      });
      items.push(this.renderItem(itemKey, props));
      previousItemData = itemData;
    }
    return items;
  }

  render() {
    return <div className={this.props.className}>
      {this.renderItems()}
    </div>;
  }

  _sendFocusOnItemSignal(itemData) {
    const itemKey = itemData[this.props.keyAttribute];
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.FocusOnSelectedItem.${itemKey}`);
  }

  componentDidUpdate() {
    if(this._focusOnItemData != null) {
      this._sendFocusOnItemSignal(this._focusOnItemData);
      this._focusOnItemData = null;
    }
  }
}
