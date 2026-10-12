import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


/**
 * Geolocation debug widget.
 *
 * For debugging {@link GeoLocationWidget}.
 */
export default class GeoLocationDebugWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    if (this.config.signalNameSpace == null) {
      throw Error("signalNameSpace is required!");
    }
    this._name = `django_cradmin.widgets.GeoLocationDebugWidget.${this.config.signalNameSpace}`;
    this._onGeoLocationUpdate = this._onGeoLocationUpdate.bind(this);
    this._onGeoLocationPermissionDenied = this._onGeoLocationPermissionDenied.bind(this);
    this._onGeoLocationUnavailable = this._onGeoLocationUnavailable.bind(this);
    this._onGeoLocationTimeout = this._onGeoLocationTimeout.bind(this);
    this.initializeSignalHandlers();
  }

  initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `${this.config.signalNameSpace}.GeoLocationUpdate`,
      this._name,
      this._onGeoLocationUpdate
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.config.signalNameSpace}.GeoLocationPermissionDenied`,
      this._name,
      this._onGeoLocationPermissionDenied
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.config.signalNameSpace}.GeoLocationUnavailable`,
      this._name,
      this._onGeoLocationUnavailable
    );
    new SignalHandlerSingleton().addReceiver(
      `${this.config.signalNameSpace}.GeoLocationTimeout`,
      this._name,
      this._onGeoLocationTimeout
    );
  }

  _onGeoLocationUpdate(receivedSignalInfo) {
    const positionObject = receivedSignalInfo.data;
    this.element.innerHTML = `GeoLocation: ${positionObject.coords.latitude}, ${positionObject.coords.longitude}`;
  }

  _onGeoLocationPermissionDenied(receivedSignalInfo) {
    this.element.innerHTML = `GeoLocation error: permission denied`;
  }

  _onGeoLocationUnavailable(receivedSignalInfo) {
    this.element.innerHTML = `GeoLocation error: unavailable`;
  }

  _onGeoLocationTimeout(receivedSignalInfo) {
    this.element.innerHTML = `GeoLocation error: timeout`;
  }

  destroy() {
    new SignalHandlerSingleton()
      .removeAllSignalsFromReceiver(this._name);
  }

}
