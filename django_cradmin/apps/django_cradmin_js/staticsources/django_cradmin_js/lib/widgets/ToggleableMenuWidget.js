import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";

export default class ToggleableMenuWidget extends AbstractWidget {
  getDefaultConfig() {
    return {
      id: 'mainmenu',
      activeCssClass: 'expandable-menu--expanded'
    }
  }

  constructor(element) {
    super(element);
    this.onToggleMenuSignal = this.onToggleMenuSignal.bind(this);
    this._initializeSignalHandlers();
  }

  _initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `cradmin.ToggleMenu.${this.config.id}`,
      `cradmin.ToggleableMenuWidget.${this.config.id}`,
      this.onToggleMenuSignal
    );
  }

  onToggleMenuSignal(receivedSignalInfo) {
    this.toggle();
  }

  toggle() {
    if(this.element.classList.contains(this.config.activeCssClass)) {
      this.element.classList.remove(this.config.activeCssClass);
    } else {
      this.element.classList.add(this.config.activeCssClass);
    }
  }

  destroy() {
    this.element.removeEventListener('click', this._onClick);
    new SignalHandlerSingleton().removeReceiver(
      `cradmin.ToggleMenu.${this.config.id}`,
      `cradmin.ToggleableMenuWidget.${this.config.id}`
    );
  }
}
