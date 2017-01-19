import AbstractWidget from "ievv_jsbase/widget/AbstractWidget";

export default class DownloadCompressedArchiveStartButtonWidget extends AbstractWidget {
  constructor(element) {
    super(element);
    this._onClick = this._onClick.bind(this);
    this.signalHandler = new window.ievv_jsbase_core.SignalHandlerSingleton();
    this.element.addEventListener('click', this._onClick);
  }

  _onClick(event) {
    event.preventDefault();
    this.signalHandler.send(`${this.config.signalNameSpace}.Start`);
  }

  destroy() {
    this.element.removeEventListener('click', this._onClick);
  }
}
