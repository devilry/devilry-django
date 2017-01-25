import AbstractWidget from "ievv_jsbase/widget/AbstractWidget";

export default class DownloadCompressedArchiveDownloadLinkWidget extends AbstractWidget {
  constructor(element) {
    super(element);
    this._onFinishedSignal = this._onFinishedSignal.bind(this);
    this.signalHandler = new window.ievv_jsbase_core.SignalHandlerSingleton();
    this.signalHandler.addReceiver(
      `${this.config.signalNameSpace}.Finished`,
      `${this.config.signalNameSpace}.DownloadLinkReceiver`,
      this._onFinishedSignal);
  }

  _onFinishedSignal(receivedSignalInfo) {
    console.log('FINISHED', receivedSignalInfo.data);
    this.element.setAttribute('href', receivedSignalInfo.data.download_link);
  }

  destroy() {
    this.signalHandler.removeAllSignalsFromReceiver(
      `${this.config.signalNameSpace}.DownloadLinkReceiver`);
  }
}
