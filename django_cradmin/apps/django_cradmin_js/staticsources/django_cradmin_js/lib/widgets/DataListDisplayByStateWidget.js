import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import DomUtilities from "../utilities/DomUtilities";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class DataListDisplayByStateWidget extends AbstractWidget {
  getDefaultConfig() {
    return {
      signalNameSpace: null,
      displayStyle: 'block',
      // Valid values:
      // - 'IsInitializingDataList'
      // - 'IsNotInitializingDataList'
      // - 'UnfilteredIsEmpty'
      // - 'UnfilteredIsNotEmpty'
      // - 'FilteredIsNotEmpty'
      // - 'FilteredIsEmpty'
      // - 'HasNextPage'
      // - 'HasSearchString'
      // - 'HasFocus'
      // - 'HasNoFocus'
      // - 'HasSelectedItems'
      // - 'HasNoSelectedItems'
      showStates: [],

      hideStates: []
    };
  }

  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    this._widgetInstanceId = widgetInstanceId;
    this._name = `django_cradmin.widgets.DataListDisplayByStateWidget.${widgetInstanceId}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.widgets.DataListDisplayByStateWidget');
    if(this.config.signalNameSpace == null) {
      throw new Error('The signalNameSpace config is required.');
    }
    this._onDataListInitializedSignal = this._onDataListInitializedSignal.bind(this);
    this._onIsEmpyDataListSignal = this._onIsEmpyDataListSignal.bind(this);
    this._onNotEmpyDataListSignal = this._onNotEmpyDataListSignal.bind(this);
    this._onDataChangeSignal = this._onDataChangeSignal.bind(this);
    this._onSearchValueChangeSignal = this._onSearchValueChangeSignal.bind(this);
    this._onFocusSignal = this._onFocusSignal.bind(this);
    this._onBlurSignal = this._onBlurSignal.bind(this);
    this._onLoadingStateChangeSignal = this._onLoadingStateChangeSignal.bind(this);
    this._onSelectionChangeSignal = this._onSelectionChangeSignal.bind(this);

    this._watchedStates = new Set(this.config.showStates);
    for(let hideState of this.config.hideStates) {
      this._watchedStates.add(hideState);
    }
    this.stateSet = new Set();
    if(this._watchInitializingDataList()) {
      this.stateSet.add('IsInitializingDataList');
    }
    this._refresh();
    this.initializeSignalHandlers();
  }

  _watchIsEmpty() {
    return this._watchedStates.has('UnfilteredIsEmpty');
  }

  _watchNotEmpty() {
    return this._watchedStates.has('UnfilteredIsNotEmpty');
  }

  _watchInitializingDataList() {
    return this._watchedStates.has('IsInitializingDataList') ||
      this._watchedStates.has('IsNotInitializingDataList');
  }

  _watchResultCount() {
    return this._watchedStates.has('FilteredIsNotEmpty') ||
         this._watchedStates.has('FilteredIsEmpty');
  }

  _watchNextPage() {
    return this._watchedStates.has('HasNextPage');
  }

  _watchSearchString() {
    return this._watchedStates.has('HasSearchString');
  }

  _watchFocus() {
    return this._watchedStates.has('HasFocus') ||
         this._watchedStates.has('HasNoFocus');
  }

  _watchLoadingStateChange() {
    return this._watchedStates.has('IsLoading');
  }

  _watchSelectionChangeCount() {
    return this._watchedStates.has('HasSelectedItems') ||
         this._watchedStates.has('HasNoSelectedItems');
  }

  _listenForDataListInitializedSignal() {
    return this._watchInitializingDataList();
  }

  _listenForIsEmpyDataListSignal() {
    return this._watchIsEmpty();
  }

  _listenForNotEmpyDataListSignal() {
    return this._watchNotEmpty();
  }

  _listenForDataChangeSignal() {
    return this._watchResultCount() || this._watchNextPage();
  }

  _listenForSearchValueChangeSignal() {
    return this._watchSearchString();
  }

  _listenForFocusSignal() {
    return this._watchFocus();
  }

  _listenForBlurSignal() {
    return this._watchFocus();
  }

  _listenForLoadingStateChangeSignal() {
    return this._watchLoadingStateChange();
  }

  _listenForSelectionChangeSignal() {
    return this._watchSelectionChangeCount();
  }

  initializeSignalHandlers() {
    if(this._listenForDataListInitializedSignal()) {
      new SignalHandlerSingleton().addReceiver(
        `${this.config.signalNameSpace}.DataListInitialized`,
        this._name,
        this._onDataListInitializedSignal
      );
    }
    if(this._listenForIsEmpyDataListSignal()) {
      new SignalHandlerSingleton().addReceiver(
        `${this.config.signalNameSpace}.IsEmpyDataList`,
        this._name,
        this._onIsEmpyDataListSignal
      );
    }
    if(this._listenForNotEmpyDataListSignal()) {
      new SignalHandlerSingleton().addReceiver(
        `${this.config.signalNameSpace}.NotEmpyDataList`,
        this._name,
        this._onNotEmpyDataListSignal
      );
    }
    if(this._listenForDataChangeSignal()) {
      new SignalHandlerSingleton().addReceiver(
        `${this.config.signalNameSpace}.DataChange`,
        this._name,
        this._onDataChangeSignal
      );
    }
    if(this._listenForSearchValueChangeSignal()) {
      new SignalHandlerSingleton().addReceiver(
        `${this.config.signalNameSpace}.SearchValueChange`,
        this._name,
        this._onSearchValueChangeSignal
      );
    }
    if(this._listenForFocusSignal()) {
      new SignalHandlerSingleton().addReceiver(
        `${this.config.signalNameSpace}.Focus`,
        this._name,
        this._onFocusSignal
      );
    }
    if(this._listenForBlurSignal()) {
      new SignalHandlerSingleton().addReceiver(
        `${this.config.signalNameSpace}.Blur`,
        this._name,
        this._onBlurSignal
      );
    }
    if(this._listenForLoadingStateChangeSignal()) {
      new SignalHandlerSingleton().addReceiver(
        `${this.config.signalNameSpace}.LoadingStateChange`,
        this._name,
        this._onLoadingStateChangeSignal
      );
    }
    if(this._listenForSelectionChangeSignal()) {
      new SignalHandlerSingleton().addReceiver(
        `${this.config.signalNameSpace}.SelectionChange`,
        this._name,
        this._onSelectionChangeSignal
      );
    }
  }

  destroy() {
    new SignalHandlerSingleton().removeAllSignalsFromReceiver(
      this._name);
  }

  _onDataListInitializedSignal(receivedSignalInfo) {
    if(this.stateSet.has('IsInitializingDataList')) {
      this.stateSet.delete('IsInitializingDataList');
      this.stateSet.add('IsNotInitializingDataList');
      this._refresh();
    }
  }

  _onIsEmpyDataListSignal(receivedSignalInfo) {
    if(!this.stateSet.has('UnfilteredIsEmpty')) {
      this.stateSet.add('UnfilteredIsEmpty');
      this.stateSet.delete('UnfilteredIsNotEmpty');
      this._refresh();
    }
  }

  _onNotEmpyDataListSignal(receivedSignalInfo) {
    if(!this.stateSet.has('UnfilteredIsNotEmpty')) {
      this.stateSet.add('UnfilteredIsNotEmpty');
      this.stateSet.delete('UnfilteredIsEmpty');
      this._refresh();
    }
  }

  _checkDataChanges(data) {
    let hasChanges = false;
    if(this._watchResultCount()) {
      if(data.count > 0) {
        if(!this.stateSet.has('FilteredIsNotEmpty')) {
          this.stateSet.add('FilteredIsNotEmpty');
          this.stateSet.delete('FilteredIsEmpty');
          hasChanges = true;
        }
      } else {
        if(!this.stateSet.has('FilteredIsEmpty')) {
          this.stateSet.add('FilteredIsEmpty');
          this.stateSet.delete('FilteredIsNotEmpty');
          hasChanges = true;
        }
      }
    }

    if(this._watchNextPage()) {
      if(data.next) {
        if(!this.stateSet.has('HasNextPage')) {
          this.stateSet.add('HasNextPage');
          hasChanges = true;
        }
      } else {
        if(this.stateSet.has('HasNextPage')) {
          this.stateSet.delete('HasNextPage');
          hasChanges = true;
        }
      }
    }

    return hasChanges;
  }

  _onDataChangeSignal(receivedSignalInfo) {
    const data = receivedSignalInfo.data;
    if(this._checkDataChanges(data)) {
      this._refresh();
    }
  }

  _checkSearchStringChanges(searchString) {
    let hasChanges = false;
    if(searchString.length > 0) {
      if(!this.stateSet.has('HasSearchString')) {
        this.stateSet.add('HasSearchString');
        hasChanges = true;
      }
    } else {
      if(this.stateSet.has('HasSearchString')) {
        this.stateSet.delete('HasSearchString');
        hasChanges = true;
      }
    }
    return hasChanges;
  }

  _onSearchValueChangeSignal(receivedSignalInfo) {
    const searchString = receivedSignalInfo.data;
    if(this._checkSearchStringChanges(searchString)) {
      this._refresh();
    }
  }

  _onFocusSignal(receivedSignalInfo) {
    if(!this.stateSet.has('HasFocus')) {
      this.stateSet.add('HasFocus');
      this.stateSet.delete('HasNoFocus');
      this._refresh();
    }
  }

  _onBlurSignal(receivedSignalInfo) {
    if(!this.stateSet.has('HasNoFocus')) {
      this.stateSet.add('HasNoFocus');
      this.stateSet.delete('HasFocus');
      this._refresh();
    }
  }

  _checkLoadingChanges(isLoading) {
    let hasChanges = false;
    if(isLoading) {
      if(!this.stateSet.has('IsLoading')) {
        this.stateSet.add('IsLoading');
        hasChanges = true;
      }
    } else {
      if(this.stateSet.has('IsLoading')) {
        this.stateSet.delete('IsLoading');
        hasChanges = true;
      }
    }
    return hasChanges;
  }

  _onLoadingStateChangeSignal(receivedSignalInfo) {
    const isLoading = receivedSignalInfo.data;
    if(this._checkLoadingChanges(isLoading)) {
      this._refresh();
    }
  }

  _checkSelectionChanges(selectedItemsMap) {
    let hasChanges = false;
    if(selectedItemsMap.size == 0) {
      if(!this.stateSet.has('HasNoSelectedItems')) {
        this.stateSet.add('HasNoSelectedItems');
        this.stateSet.delete('HasSelectedItems');
        hasChanges = true;
      }
    } else {
      if(!this.stateSet.has('HasSelectedItems')) {
        this.stateSet.add('HasSelectedItems');
        this.stateSet.delete('HasNoSelectedItems');
        hasChanges = true;
      }
    }
    return hasChanges;
  }

  _onSelectionChangeSignal(receivedSignalInfo) {
    const selectedItemsMap = receivedSignalInfo.data.selectedItemsMap;
    if(this._checkSelectionChanges(selectedItemsMap)) {
      this._refresh();
    }
  }

  _display(display) {
    if(display) {
      DomUtilities.show(this.element, this.config.displayStyle);
    } else {
      DomUtilities.hide(this.element);
    }
  }

  _refresh() {
    let display = false;
    for(let state of this.config.showStates) {
      if(this.stateSet.has(state)) {
        display = true;
        break;
      }
    }
    for(let state of this.config.hideStates) {
      if(this.stateSet.has(state)) {
        display = false;
        break;
      }
    }
    if(this.logger.isDebug) {
      this.logger.debug(
        `State changes detected by widgetInstanceId=${this._widgetInstanceId}. New stateSet`,
        this.stateSet, 'Display:', display);
    }
    this._display(display);
  }
}
