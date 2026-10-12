import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";

/**
 * Geolocation widget.
 */
export default class GeoLocationWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId);
    this.locationSuccess = this.locationSuccess.bind(this);
    this.locationError = this.locationError.bind(this);
    if (this.config.signalNameSpace == null) {
      throw Error("signalNameSpace is required!");
    }
    if(navigator && navigator.geolocation) {
      this.getLocation();
    } else {
      this.handleBrowserWithoutGeolocationSupport();
    }
  }

  getDefaultConfig() {
    return {
      enableHighAccuracy: true,
      watchLocation: true,
      signalNameSpace: null,
    }
  }

  locationSuccess(position){
    new SignalHandlerSingleton().send(
      `${this.config.signalNameSpace}.GeoLocationUpdate`,
      position);
  }

  locationError(error) {
    if (error.code == 1) { // 1 = PERMISSION_DENIED
      new SignalHandlerSingleton().send(
        `${this.config.signalNameSpace}.GeoLocationPermissionDenied`);
    } else if(error.code == 2) { // 2 = POSITION_UNAVAILABLE
      new SignalHandlerSingleton().send(
        `${this.config.signalNameSpace}.GeoLocationUnavailable`);
    } else if(error.code == 3) { // 3 = TIMEOUT
      new SignalHandlerSingleton().send(
        `${this.config.signalNameSpace}.GeoLocationTimeout`);
    }
    new SignalHandlerSingleton().send(
      `${this.config.signalNameSpace}.GeoLocationError`, error);
  }

  getLocation() {
    const options = {
      enableHighAccuracy: this.config.enableHighAccuracy
    };
    if (this.config.watchLocation) {
      this.watchPositionId = navigator.geolocation.watchPosition(this.locationSuccess, this.locationError, options);
    } else {
      navigator.geolocation.getCurrentPosition(this.locationSuccess, this.locationError, options);
    }
  }

  handleBrowserWithoutGeolocationSupport() {
    new SignalHandlerSingleton().send(
      `${this.config.signalNameSpace}.GeoLocationNotSupported`);
  }

  destroy() {
    if (this.watchPositionId != undefined) {
      navigator.geolocation.clearWatch(this.watchPositionId);
    }
  }
}
