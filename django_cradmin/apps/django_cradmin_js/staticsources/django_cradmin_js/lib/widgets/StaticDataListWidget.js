import AbstractDataListWidget from "./AbstractDataListWidget";


export default class StaticDataListWidget extends AbstractDataListWidget {

  getDefaultConfig() {
    const defaultConfig = super.getDefaultConfig();
    defaultConfig.searchAttributes = ['title', 'description'];
    defaultConfig.dataList = [];
    return defaultConfig;
  }

  get classPath() {
    return 'django_cradmin.widgets.StaticDataListWidget';
  }

  // constructor(element, widgetInstanceId) {
  //   super(element, widgetInstanceId);
  // }

  _isClientSideSearchMatch(searchString, itemData) {
    for(let attribute of this.config.searchAttributes) {
      if(itemData[attribute] != undefined && itemData[attribute] != null) {
        if(itemData[attribute].toLowerCase().indexOf(searchString) != -1) {
          return true;
        }
      }
    }
    return false;
  }

  requestItemData(key) {
    return new Promise((resolve, reject) => {
      for(let itemData of this.config.dataList) {
        if(this._getKeyFromItemData(itemData) == key) {
          resolve(itemData);
        }
      }
      reject(new Error(
        `dataList does not contain an ` +
        `object with ${this.config.keyAttribute} = "${key}"`
      ));
    });
  }

  requestDataList(options) {
    return new Promise((resolve, reject) => {
      const resultItemsArray = [];
      const searchString = options.searchString.toLowerCase();
      for (let itemData of this.config.dataList) {
        if (this._isClientSideSearchMatch(searchString, itemData)) {
          resultItemsArray.push(itemData);
        }
      }
      resolve({
        count: resultItemsArray.length,
        results: resultItemsArray
      });
    });
  }
}
