import React from "react";
import ReactDOM from "react-dom";
import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import HttpDjangoJsonRequest from 'ievv_jsbase/lib/http/HttpDjangoJsonRequest';
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class AbstractSelectWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.widgets.AbstractSelectWidget');
    this.onSelectResultSignal = this.onSelectResultSignal.bind(this);
    this.onSearchRequestedSignal = this.onSearchRequestedSignal.bind(this);

    this._uniquePrefix = `django_cradmin.Select.${this.widgetInstanceId}`;
    this._searchRequestedSignalName = `${this._uniquePrefix}.SearchRequested`;
    this._searchCompletedSignalName = `${this._uniquePrefix}.SearchCompleted`;
    this._selectResultSignalName = `${this._uniquePrefix}.SelectResult`;

    this.initialValue = this._getInitialValue();
    this.selectedValue = this.initialValue;
    this.logger.debug(`initialValue: "${this.initialValue}"`);
    this._initializeSignalHandlers();
    if(this.initialValue != null) {
      this._loadPreviewForInitialValue();
    } else {
      this._updateUiForEmptyValue();
    }
  }

  getDefaultConfig() {
    return {
      valueAttribute: 'id',
      fetchEmptySearchOnLoad: false,
      toggleElementsOnValueChange: {
        loading: [],
        hasValue: [],
        noValue: []
      },
      updateInnerHtmlWithResult: {},
      clientsideSearch: {},
      searchApi: {
        url: null,
        staticData: {}
      },
      componentProps: {
        search: {},
        resultList: {},
        result: {}
      }
    }
  }

  _getInitialValue() {
    let initialValue = null;
    if(this.config.valueTargetInputId) {
      initialValue = document.getElementById(this.config.valueTargetInputId).value;
    } else if (this.config.initialValue) {
      initialValue = this.config.initialValue;
    }
    if(initialValue == undefined || initialValue == '') {
      initialValue = null;
    }
    return initialValue;
  }

  _initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      this._searchRequestedSignalName,
      'django_cradmin.widgets.AbstractSelectWidget',
      this.onSearchRequestedSignal
    );
    new SignalHandlerSingleton().addReceiver(
      this._selectResultSignalName,
      'django_cradmin.widgets.AbstractSelectWidget',
      this.onSelectResultSignal
    );
  }

  destroy() {
    this.element.removeEventListener('click', this._onClick);
    new SignalHandlerSingleton().removeReceiver(
      this._searchRequestedSignalName,
      'django_cradmin.widgets.AbstractSelectWidget'
    );
    new SignalHandlerSingleton().removeReceiver(
      this._selectResultSignalName,
      'django_cradmin.widgets.AbstractSelectWidget'
    );
    if(this._reactWrapperElement) {
      ReactDOM.unmountComponentAtNode(this._reactWrapperElement);
      this._reactWrapperElement.remove();
    }
  }

  _setValueTargetValue(value) {
    if(this.config.valueTargetInputId) {
      document.getElementById(this.config.valueTargetInputId).value = value;
    }
  }

  _hideElementById(domId) {
    const element = document.getElementById(domId);
    if(element) {
      element.setAttribute('style', 'display: none');
    }
  }

  _showElementById(domId) {
    const element = document.getElementById(domId);
    if(element) {
      element.setAttribute('style', 'display: block');
    }
  }

  _hideElementsById(domIdArray) {
    for(let domId of domIdArray) {
      this._hideElementById(domId);
    }
  }

  _showElementsById(domIdArray) {
    for(let domId of domIdArray) {
      this._showElementById(domId);
    }
  }

  _updatePreviews(resultObject) {
    for(let attribute of Object.keys(this.config.updateInnerHtmlWithResult)) {
      let domIds = this.config.updateInnerHtmlWithResult[attribute];
      let value = resultObject[attribute];
      if(value != undefined && value != null) {
        for(let domId of domIds) {
          const element = document.getElementById(domId);
          if(element) {
            element.innerHTML = value;
          }
        }
      }
    }
  }

  _getValueFromResultObject(resultObject) {
    return resultObject[this.config.valueAttribute];
  }

  _setLoading() {
    this._hideElementsById(this.config.toggleElementsOnValueChange.hasValue);
    this._hideElementsById(this.config.toggleElementsOnValueChange.noValue);
    this._showElementsById(this.config.toggleElementsOnValueChange.loading);
  }

  _updateUiForEmptyValue() {
    this.selectedValue = null;
    this._hideElementsById(this.config.toggleElementsOnValueChange.hasValue);
    this._hideElementsById(this.config.toggleElementsOnValueChange.loading);
    this._showElementsById(this.config.toggleElementsOnValueChange.noValue);
    this._setValueTargetValue('');
  }

  _updateUiFromResultObject(resultObject) {
    let value = this._getValueFromResultObject(resultObject);
    this.selectedValue = value;
    this._hideElementsById(this.config.toggleElementsOnValueChange.noValue);
    this._hideElementsById(this.config.toggleElementsOnValueChange.loading);
    this._showElementsById(this.config.toggleElementsOnValueChange.hasValue);
    this._setValueTargetValue(value);
    this._updatePreviews(resultObject);
  }

  onSelectResultSignal(receivedSignalInfo) {
    this.logger.debug(receivedSignalInfo.toString());
    let resultObject = receivedSignalInfo.data;
    if(resultObject == null) {
      this._updateUiForEmptyValue();
    } else {
      this._updateUiFromResultObject(resultObject);
    }
  }

  _useServerSideSearch() {
    return this.config.searchApi.url != undefined && this.config.searchApi.url != null;
  }

  onSearchRequestedSignal(receivedSignalInfo) {
    this.logger.debug(receivedSignalInfo.toString());
    const searchString = receivedSignalInfo.data;
    this.requestSearchResults(searchString)
      .then((results) => {
        this.sendSearchCompletedSignal(results);
      })
      .catch((error) => {
        throw error;
      });
  }

  sendSearchCompletedSignal(results) {
    this.logger.debug('Search complete. Result:', results);
    new SignalHandlerSingleton().send(
      this._searchCompletedSignalName,
      results
    );
  }

  _isClientSideSearchMatch(searchString, resultObject) {
    for(let attribute of this.config.clientsideSearch.searchAttributes) {
      if(resultObject[attribute] != undefined && resultObject[attribute] != null) {
        if(resultObject[attribute].toLowerCase().indexOf(searchString) != -1) {
          return true;
        }
      }
    }
    return false;
  }

  _requestClientSideSearchResults(searchString) {
    return new Promise((resolve, reject) => {
      const resultObjectArray = [];
      searchString = searchString.toLowerCase();
      for (let resultObject of this.config.clientsideSearch.data) {
        if (this._isClientSideSearchMatch(searchString, resultObject)) {
          resultObjectArray.push(resultObject);
        }
      }
      resolve({
        count: resultObjectArray.size,
        results: resultObjectArray
      });
    });
  }

  _requestServerSideSearchResults(searchString) {
    return new Promise((resolve, reject) => {
      const request = new HttpDjangoJsonRequest(this.config.searchApi.url);
      for (let attribute of Object.keys(this.config.searchApi.staticData)) {
        request.urlParser.queryString.set(
          attribute, this.config.searchApi.staticData[attribute]);
      }
      request.urlParser.queryString.set('search', searchString);
      request.get()
        .then((response) => {
          resolve(response.bodydata);
        })
        .catch((error) => {
          reject(error);
        });
    });
  }

  requestSearchResults(searchString='') {
    if(this._useServerSideSearch()) {
      return this._requestServerSideSearchResults(searchString);
    } else {
      return this._requestClientSideSearchResults(searchString);
    }
  }

  _requestSingleResultServerSide(value) {
    return new Promise((resolve, reject) => {
      let url = this.config.searchApi.url;
      if(!this.config.searchApi.url.endsWith('/')) {
        url = `${url}/`;
      }
      url = `${url}${value}`;
      const request = new HttpDjangoJsonRequest(url);
      request.get()
        .then((response) => {
          resolve(response.bodydata);
        })
        .catch((error) => {
          reject(error);
        });
    });
  }

  _requestSingleResultClientSide(value) {
    return new Promise((resolve, reject) => {
      for(let resultObject of this.config.clientsideSearch.data) {
        if(this._getValueFromResultObject(resultObject) == value) {
          resolve(resultObject);
        }
      }
      reject(new Error(
        `config.clientsideSearch.data does not contain an ` +
        `object with ${this.config.valueAttribute} = "${value}"`
      ));
    });
  }

  _requestSingleResult(value) {
    if(this._useServerSideSearch()) {
      return this._requestSingleResultServerSide(value);
    } else {
      return this._requestSingleResultClientSide(value);
    }
  }

  _loadPreviewForInitialValue() {
    this._setLoading();
    this._requestSingleResult(this.initialValue)
      .then((resultObject) => {
        this.logger.debug(`Loaded data for initialValue ("${this.initialValue}"):`, resultObject);
        this._updateUiFromResultObject(resultObject);
      })
      .catch((error) => {
        this.logger.error(
          `Failed to load data for initialValue: "${this.initialValue}". ` +
          `Error details: ${error.toString()}`);
      });
  }

  addReactWrapperElementToDocument(reactWrapperElement) {
    this.element.parentNode.insertBefore(reactWrapperElement, this.element.nextSibling);
  }

  initializeReactComponent() {
    this._reactWrapperElement = document.createElement('div');
    this.addReactWrapperElementToDocument(this._reactWrapperElement);
    const reactElement = this.makeReactElement();
    ReactDOM.render(
      reactElement,
      this._reactWrapperElement
    );
    if(this.config.fetchEmptySearchOnLoad) {
    this.requestSearchResults()
      .then((results) => {
        this.sendSearchCompletedSignal(results);
      })
      .catch((error) => {
        throw error;
      });
    }
  }

  makeReactComponentProps() {
    return {
      closeCallback: this._onClose,
      selectResultSignalName: this._selectResultSignalName,
      searchCompletedSignalName: this._searchCompletedSignalName,
      searchRequestedSignalName: this._searchRequestedSignalName,
      valueAttribute: this.config.valueAttribute,
      searchComponentProps: this.config.componentProps.search,
      resultListComponentProps: this.config.componentProps.resultList,
      resultComponentProps: this.config.componentProps.result,
      selectedValue: this.selectedValue
    }
  }

  makeReactElement() {
    throw new Error('You must override makeReactElement()');
  }
}
