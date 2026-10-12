import React from "react";
import ReactDOM from "react-dom";
import CradminMoveButton from "./CradminMoveButton";
import CradminHtmlList from "./CradminHtmlList";


export default class CradminHtmlListWithMovableItems extends CradminHtmlList {

  static get defaultProps() {
    let defaultProps = super.defaultProps;
    defaultProps = Object.assign({}, defaultProps, {
      moveApiCallDelayMilliseconds: 2000,
      itemWrapperClassName: 'blocklist__movable-item-wrapper',
      itemMoveBarClassName: 'blocklist__movesidebar',
      itemMoveBarClassNameFirst: 'blocklist__movesidebar blocklist__movesidebar--only-down',
      itemMoveBarClassNameLast: 'blocklist__movesidebar blocklist__movesidebar--only-up',
      moveUpButtonClassName: 'blocklist__movebutton',
      moveUpButtonIconClassName: 'cricon cricon--chevron-up cricon--color-light',
      moveDownButtonClassName: 'blocklist__movebutton',
      moveDownButtonIconClassName: 'cricon cricon--chevron-down cricon--color-light'
    });
    return defaultProps;
  }

  get componentName() {
    return 'CradminHtmlListWithMovableItems'
  }

  makeInitialState() {
    let initialState = super.makeInitialState();
    initialState = Object.assign({}, initialState,  {
      isMovingItemKey: null,
      isCallingMoveApi: false,
      hasSearchValue: false,
      dataListIsLoading: false
    });
    return initialState;
  }

  initializeSignalHandlers() {
    super.initializeSignalHandlers();
    this._onMoveItemUpSignal = this._onMoveItemUpSignal.bind(this);
    this._onMoveItemDownSignal = this._onMoveItemDownSignal.bind(this);
    this._onMoveItemCompleteSignal = this._onMoveItemCompleteSignal.bind(this);
    this._onSearchValueChangeEmptySignal = this._onSearchValueChangeEmptySignal.bind(this);
    this._onSearchValueChangeNotEmptySignal = this._onSearchValueChangeNotEmptySignal.bind(this);
    this._onLoadingStateChangeSignal = this._onLoadingStateChangeSignal.bind(this);
    this.signalHandler.addReceiver(
      `${this.props.signalNameSpace}.SortableHtmlList.MoveItemUp`,
      this._name,
      this._onMoveItemUpSignal
    );
    this.signalHandler.addReceiver(
      `${this.props.signalNameSpace}.SortableHtmlList.MoveItemDown`,
      this._name,
      this._onMoveItemDownSignal
    );
    this.signalHandler.addReceiver(
      `${this.props.signalNameSpace}.MoveItemComplete`,
      this._name,
      this._onMoveItemCompleteSignal
    );
    this.signalHandler.addReceiver(
      `${this.props.signalNameSpace}.SearchValueChangeEmpty`,
      this._name,
      this._onSearchValueChangeEmptySignal
    );
    this.signalHandler.addReceiver(
      `${this.props.signalNameSpace}.SearchValueChangeNotEmpty`,
      this._name,
      this._onSearchValueChangeNotEmptySignal
    );
    this.signalHandler.addReceiver(
      `${this.props.signalNameSpace}.LoadingStateChange`,
      this._name,
      this._onLoadingStateChangeSignal
    );
  }

  _onSearchValueChangeEmptySignal(receivedSignalInfo) {
    this.setState({
      hasSearchValue: false
    });
  }

  _onSearchValueChangeNotEmptySignal(receivedSignalInfo) {
    this.setState({
      hasSearchValue: true
    });
  }

  _onLoadingStateChangeSignal(receivedSignalInfo) {
    const isLoading = receivedSignalInfo.data;
    this.setState({
      dataListIsLoading: isLoading
    });
  }

  // _getDataListDebugArray() {
  //   let debugArray = [];
  //   for(let itemData of this.state.dataList) {
  //     // debugArray.push(`  - ${itemData[this.props.keyAttribute]}`);
  //     debugArray.push(itemData[this.props.keyAttribute])
  //   }
  //   // return '\n' + debugArray.join('\n');
  //   return debugArray.join(', ')
  // }

  _cancelMoveTimer() {
    if(this._blurTimeoutId != undefined) {
      window.clearTimeout(this._blurTimeoutId);
    }
  }

  _startMoveTimer(callback) {
    this._blurTimeoutId = window.setTimeout(
      callback,
      this.props.moveApiCallDelayMilliseconds);
  }

  _sendMoveSignal(moveBeforeItemKey) {
    this.setState({
      isCallingMoveApi: true
    });
    this.signalHandler.send(`${this.props.signalNameSpace}.MoveItem`, {
      movingItemKey: this.state.isMovingItemKey,
      moveBeforeItemKey: moveBeforeItemKey
    });
  }

  _sendMoveStartedSignal() {
    this.signalHandler.send(`${this.props.signalNameSpace}.MoveItemStarted`);
  }

  _moveItem(from_index, to_index) {
    if(to_index < 0) {
      throw new Error('Can not move a result item to an index smaller than 0');
    } else if(to_index > this.state.dataList.length) {
      throw new Error(
        'Can not move a result item to an index that is larger ' +
        'than the result array size.');
    }
    let itemData = this.state.dataList[from_index];
    let itemKey = itemData[this.props.keyAttribute];
    if(this.state.isMovingItemKey != null && this.state.isMovingItemKey != itemKey) {
      throw new Error(
        `Can not move item with key=${itemKey}. We are already in the ` +
        `process of moving the item with key=${this.state.isMovingItemKey}.`);
    }
    if(this.state.isMovingItemKey == null) {
      this._sendMoveStartedSignal();
    }

    this._cancelMoveTimer();
    let moveLast = to_index == (this.state.dataList.length - 1);
    let moveBeforeItemKey = null;
    this.state.dataList.splice(from_index, 1);
    if(moveLast) {
      this.state.dataList.push(itemData);
    } else {
      this.state.dataList.splice(to_index, 0, itemData);
      moveBeforeItemKey = this.state.dataList[to_index + 1][this.props.keyAttribute];
    }
    this.state.isMovingItemKey = itemData[this.props.keyAttribute];

    this.forceUpdate();
    this._startMoveTimer(() => {
      this._sendMoveSignal(moveBeforeItemKey);
    });
  }

  _onMoveItemUpSignal(receivedSignalInfo) {
    this.logger.debug('Received:', receivedSignalInfo.toString());
    this._moveItem(receivedSignalInfo.data.itemIndex,
      receivedSignalInfo.data.itemIndex - 1);
  }

  _onMoveItemDownSignal(receivedSignalInfo) {
    this.logger.debug('Received:', receivedSignalInfo.toString());
    this._moveItem(receivedSignalInfo.data.itemIndex,
      receivedSignalInfo.data.itemIndex + 1);
  }

  _onMoveItemCompleteSignal(receivedSignalInfo) {
    this.logger.debug('Received:', receivedSignalInfo.toString());
    this.setState({
      isCallingMoveApi: false,
      isMovingItemKey: null
    });
  }

  canMoveItem(itemData) {
    return !this.state.isCallingMoveApi &&
        !this.state.dataListIsLoading &&
        !this.state.hasSearchValue &&
        (this.state.isMovingItemKey == null || this.state.isMovingItemKey == itemData[this.props.keyAttribute]);
  }

  renderMoveUpButton(itemIndex, itemData) {
    if(itemIndex > 0 && this.canMoveItem(itemData)) {
      return <CradminMoveButton className={this.props.moveUpButtonClassName}
                                signalNameSpace={this.props.signalNameSpace}
                                itemIndex={itemIndex}
                                moveDirection="Up"
                                iconClassName={this.props.moveUpButtonIconClassName}/>;
    }
    return '';
  }

  renderMoveDownButton(itemIndex, itemData) {
    if(itemIndex < (this.state.dataList.length - 1) && this.canMoveItem(itemData)) {
      return <CradminMoveButton className={this.props.moveDownButtonClassName}
                         signalNameSpace={this.props.signalNameSpace}
                         itemIndex={itemIndex}
                         moveDirection="Down"
                         iconClassName={this.props.moveDownButtonIconClassName}/>;
    }
    return '';
  }

  makeMoveBarClassName(itemIndex) {
    if(itemIndex == 0) {
      return this.props.itemMoveBarClassNameFirst;
    } else if(itemIndex == (this.state.dataList.length - 1)) {
      return this.props.itemMoveBarClassNameLast;
    } else {
      return this.props.itemMoveBarClassName;
    }
  }

  renderMoveBar(itemIndex, itemData) {
    return <div className={this.makeMoveBarClassName(itemIndex)}>
      {this.renderMoveUpButton(itemIndex, itemData)}
      {this.renderMoveDownButton(itemIndex, itemData)}
    </div>;
  }

  renderItemWrapper(itemKey, itemData, itemIndex, renderedItem) {
    return <div key={itemKey} className={this.props.itemWrapperClassName}>
      {renderedItem}
      {this.renderMoveBar(itemIndex, itemData)}
    </div>;
  }

  renderItem(itemKey, itemData, itemIndex) {
    let renderedItem = super.renderItem(itemKey, itemData, itemIndex);
    return this.renderItemWrapper(itemKey, itemData, itemIndex, renderedItem);
  }

}
