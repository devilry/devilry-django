import HttpDjangoJsonRequest from 'ievv_jsbase/lib/http/HttpDjangoJsonRequest';
import typeDetect from 'ievv_jsbase/lib/utils/typeDetect';
import AbstractDataListWidget from "./AbstractDataListWidget";


export default class ApiDataListWidget extends AbstractDataListWidget {

  // getDefaultConfig() {
  //   const defaultConfig = super.getDefaultConfig();
  //   return defaultConfig;
  // }

  get classPath() {
    return 'django_cradmin.widgets.ApiDataListWidget';
  }

  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    if(!this.config.apiUrl) {
      throw new Error('apiUrl is a required config.');
    }
  }

  requestItemData(key) {
    return new Promise((resolve, reject) => {
      let url = this.config.apiUrl;
      if(!this.config.apiUrl.endsWith('/')) {
        url = `${url}/`;
      }
      url = `${url}${key}`;
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

  addFiltersToQueryString(filtersMap, queryString) {
    for(let [filterKey, filterValue] of filtersMap) {
      let filterValueType = typeDetect(filterValue);
      if(filterValueType == 'string') {
        queryString.set(filterKey, filterValue);
      } else if(filterValueType == 'number') {
        queryString.set(filterKey, filterValue.toString());
      } else if(filterValueType == 'array' || filterValueType == 'set') {
        let values = [];
        for(let value of filterValue) {
          values.push(`${value}`);
        }
        queryString.setIterable(filterKey, values);
      } else if(filterValueType == 'boolean') {
        if(filterValue) {
          queryString.set(filterKey, 'true');
        } else {
          queryString.set(filterKey, 'false');
        }
      } else if(filterValueType == 'null' || filterValueType == 'undefined') {
        // Do nothing
      } else {
        throw new Error(
          `Invalid filter value type for filterKey "${filterKey}". ` +
          `Type ${filterValueType} is not supported.`);
      }
    }
  }

  requestDataList(options) {
    return new Promise((resolve, reject) => {
      let url = this.config.apiUrl;
      if(options.next) {
        url = this.state.data.next;
      } else if(options.previous) {
        url = this.state.data.previous;
      }
      const request = new HttpDjangoJsonRequest(url);
      request.urlParser.queryString.set('search', options.searchString);
      this.addFiltersToQueryString(options.filtersMap, request.urlParser.queryString);
      if(this.logger.isDebug) {
        this.logger.debug('Requesting data list from API:', request.urlParser.buildUrl());
      }
      request.get()
        .then((response) => {
          resolve(response.bodydata);
        })
        .catch((error) => {
          reject(error);
        });
    });
  }

  moveItem(movingItemKey, moveBeforeItemKey) {
    if(!this.config.moveApiUrl) {
      throw new Error('Move support requires the moveApiUrl config.');
    }
    return new Promise((resolve, reject) => {
      let url = this.config.moveApiUrl;
      const request = new HttpDjangoJsonRequest(url);
      const requestData = {
        moving_object_id: movingItemKey,
        move_before_object_id: moveBeforeItemKey
      };
      if(this.logger.isDebug) {
        this.logger.debug(
          `Requesting move with a HTTP POST request to ${url} with the following request data:`,
          requestData);
      }
      request.post(requestData)
        .then((response) => {
          resolve(response.bodydata);
        })
        .catch((error) => {
          reject(error);
        });
    });
  }
}
