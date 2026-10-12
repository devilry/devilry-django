import React from "react";
import CradminSelectableListItem from "./CradminSelectableListItem";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminSelectableList extends React.Component {

  static get defaultProps() {
    return {
      className: 'selectable-list',
      keyAttribute: 'id',
      renderSelected: true,
      signalNameSpace: null,
      itemComponentProps: {},
      loadMoreTreshold: 3
    }
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.CradminSelectableList.${this.props.signalNameSpace}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminSelectableList');
    if(this.props.signalNameSpace == null) {
      throw new Error('The signalNameSpace prop is required.');
    }
    this._onDataChangeSignal = this._onDataChangeSignal.bind(this);
    this._onSelectionChangeSignal = this._onSelectionChangeSignal.bind(this);
    this._onFocusOnSelectableItemSignal = this._onFocusOnSelectableItemSignal.bind(this);
    this._onFocusOnFirstSelectableItemSignal = this._onFocusOnFirstSelectableItemSignal.bind(this);
    this._onFocusOnLastSelectableItemSignal = this._onFocusOnLastSelectableItemSignal.bind(this);

    this._focusOnItemData = null;
    this.state = {
      dataList: [],
      renderableDataList: [],
      hasMorePages: false,
      selectedItemsMap: new Map()
    };

    this.initializeSignalHandlers();
  }

  initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.DataChange`,
      this._name,
      this._onDataChangeSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.SelectionChange`,
      this._name,
      this._onSelectionChangeSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.FocusOnSelectableItem`,
      this._name,
      this._onFocusOnSelectableItemSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.FocusOnFirstSelectableItem`,
      this._name,
      this._onFocusOnFirstSelectableItemSignal
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.FocusOnLastSelectableItem`,
      this._name,
      this._onFocusOnLastSelectableItemSignal
    );
  }

  componentWillUnmount() {
    new SignalHandlerSingleton()
      .removeAllSignalsFromReceiver(this._name);
  }

  render() {
    return <div className={this.props.className}>
      {this.renderItems()}
    </div>;
  }

  _loadMoreIfNeeded() {
    if(this.state.hasMorePages && this.state.renderableDataList.length < this.props.loadMoreTreshold) {
      this.logger.debug('Automatically sending the LoadMore signal because we are below the loadMoreTreshold');
      new SignalHandlerSingleton().send(
        `${this.props.signalNameSpace}.LoadMore`);
    }
  }

  _makeRenderableDataList(dataList) {
    let renderableDataList = dataList;
    if(!this.props.renderSelected) {
      renderableDataList = [];
      for(let itemData of dataList) {
        let itemKey = itemData[this.props.keyAttribute];
        let isSelected = this.state.selectedItemsMap.has(itemKey);
        if(!isSelected) {
          renderableDataList.push(itemData);
        }
      }
    }
    return renderableDataList;
  }

  _onDataChangeSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    const dataList = receivedSignalInfo.data.results;
    this.setState({
      dataList: dataList,
      renderableDataList: this._makeRenderableDataList(dataList),
      hasMorePages: receivedSignalInfo.data.next != null
    });
    this._loadMoreIfNeeded();
  }

  _onSelectionChangeSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    this.setState({
      selectedItemsMap: receivedSignalInfo.data.selectedItemsMap,
      renderableDataList: this._makeRenderableDataList(this.state.dataList),
    });
    this._loadMoreIfNeeded();
  }

  _onFocusOnSelectableItemSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    this._focusOnItemData = receivedSignalInfo.data;
    this.forceUpdate();
  }

  _onFocusOnFirstSelectableItemSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    if(this.state.renderableDataList.length > 0) {
      this._focusOnItemData = this.state.renderableDataList[0];
      this.forceUpdate();
    }
  }

  _onFocusOnLastSelectableItemSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    if(this.state.renderableDataList.length > 0) {
      this._focusOnItemData = this.state.renderableDataList[this.state.renderableDataList.length - 1];
      this.forceUpdate();
    }
  }

  renderItem(itemKey, props) {
    return <CradminSelectableListItem key={itemKey} {...props} />;
  }

  renderItems() {
    const items = [];
    let previousItemData = null;
    for(let index=0; index < this.state.renderableDataList.length; index++) {
      let itemData = this.state.renderableDataList[index];
      let itemKey = itemData[this.props.keyAttribute];
      let isSelected = this.state.selectedItemsMap.has(itemKey);

      let nextItemData = null;
      let isLast = index == (this.state.renderableDataList.length - 1);
      if(!isLast) {
        nextItemData = this.state.renderableDataList[index + 1];
      }

      let props = Object.assign({
        focusClosestSiblingOnSelect: !this.props.renderSelected
      }, this.props.itemComponentProps, {
        data: itemData,
        itemKey: itemKey,
        isSelected: isSelected,
        signalNameSpace: this.props.signalNameSpace,
        previousItemData: previousItemData,
        nextItemData: nextItemData
      });
      items.push(this.renderItem(itemKey, props));
      previousItemData = itemData;
    }
    return items;
  }

  _sendFocusOnItemSignal(itemData) {
    const itemKey = itemData[this.props.keyAttribute];
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.FocusOnSelectableItem.${itemKey}`);
  }

  componentDidUpdate() {
    if(this._focusOnItemData != null) {
      this._sendFocusOnItemSignal(this._focusOnItemData);
      this._focusOnItemData = null;
    }
  }
}
