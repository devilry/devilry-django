import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class GeoLocationFilterWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    this._name = `django_cradmin.widgets.GeoLocationFilterWidget.${this.config.signalNameSpace}`;
    this._onGeoLocationUpdate = this._onGeoLocationUpdate.bind(this);
    this.initializeSignalHandlers();
  }

  getDefaultConfig() {
    return {
      signalNameSpace: null,
      latitudeFilterKey: "latitude",
      longitudeFilterKey: "longitude"
    }
  }

  initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `${this.config.signalNameSpace}.GeoLocationUpdate`,
      this._name,
      this._onGeoLocationUpdate
    );
  }

  _onGeoLocationUpdate(receivedSignalInfo) {
    const positionObject = receivedSignalInfo.data;

    const filtersMapPatch = new Map();
    filtersMapPatch.set(this.config.latitudeFilterKey, positionObject.coords.latitude);
    filtersMapPatch.set(this.config.longitudeFilterKey, positionObject.coords.longitude);
    new SignalHandlerSingleton().send(
      `${this.config.signalNameSpace}.PatchFilters`,
      filtersMapPatch);
  }

  destroy() {
    new SignalHandlerSingleton()
      .removeAllSignalsFromReceiver(this._name);
  }
}
