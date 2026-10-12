import React from "react";
import ReactDOM from "react-dom";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminHtmlList extends React.Component {

  static get defaultProps() {
    return {
      signalNameSpace: null,
      keyAttribute: 'id',
      htmlAttribute: 'html',
      loadMoreTreshold: 3,
      className: 'blocklist',
      itemClassName: 'blocklist__item blocklist__item--movable',
      itemTagName: 'div',
      itemUrlAttribute: 'url',  // Only used if itemTagName is "a"
    }
  }

  get componentName() {
    return 'CradminHtmlList'
  }

  makeInitialState() {
    return {
      dataList: [],
      hasMorePages: false
    }
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.${this.componentName}.${this.props.signalNameSpace}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.${this.componentName}');
    if(this.props.signalNameSpace == null) {
      throw new Error('The signalNameSpace prop is required.');
    }
    this.signalHandler = new SignalHandlerSingleton();
    this.state = this.makeInitialState();
    this.initializeSignalHandlers();
  }

  initializeSignalHandlers() {
    this._onDataChangeSignal = this._onDataChangeSignal.bind(this);
    this.signalHandler.addReceiver(
      `${this.props.signalNameSpace}.DataChange`,
      this._name,
      this._onDataChangeSignal
    );
  }

  componentWillUnmount() {
    this.signalHandler.removeAllSignalsFromReceiver(this._name);
  }

  _loadMoreIfNeeded() {
    if(this.state.hasMorePages && this.state.dataList.length < this.props.loadMoreTreshold) {
      this.logger.debug('Automatically sending the LoadMore signal because we are below the loadMoreTreshold');
      this.signalHandler.send(
        `${this.props.signalNameSpace}.LoadMore`);
    }
  }

  _onDataChangeSignal(receivedSignalInfo) {
    if(this.logger.isDebug) {
      this.logger.debug(receivedSignalInfo.toString(), receivedSignalInfo.data);
    }
    const dataList = receivedSignalInfo.data.results;
    this.setState({
      dataList: dataList,
      hasMorePages: receivedSignalInfo.data.next != null
    });
    this._loadMoreIfNeeded();
  }

  getItemUrl(itemData) {
    return itemData[this.props.itemUrlAttribute];
  }

  renderItem(itemKey, itemData, itemIndex) {
    let itemProps = {
      dangerouslySetInnerHTML: {__html: itemData[this.props.htmlAttribute]},
      className: this.props.itemClassName,
      key: itemKey
    };
    if(this.props.itemTagName == 'a') {
      itemProps['href'] = this.getItemUrl(itemData);
    }
    return React.createElement(this.props.itemTagName, itemProps);
  }

  // renderItemWrapper(itemKey, itemData, itemIndex) {
  //   return <div key={itemKey} className={this.props.itemWrapperClassName}>
  //     {this.renderItem(itemData)}
  //     {this.renderMoveBar(itemIndex, itemData)}
  //   </div>;
  // }

  renderItems() {
    const items = [];
    let itemIndex = 0;
    for(let itemData of this.state.dataList) {
      let itemKey = itemData[this.props.keyAttribute];
      items.push(this.renderItem(itemKey, itemData, itemIndex));
      itemIndex ++;
    }
    return items;
  }

  render() {
    return <div className={this.props.className}>
      {this.renderItems()}
    </div>;
  }
}
