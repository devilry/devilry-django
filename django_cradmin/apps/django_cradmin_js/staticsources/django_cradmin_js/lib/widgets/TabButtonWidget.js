import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";
import WidgetRegistrySingleton from "ievv_jsbase/lib/widget/WidgetRegistrySingleton";

export default class TabButtonWidget extends AbstractWidget {
  getDefaultConfig() {
    return {
      id: 'defaultTab',
      activeClass: "tabs__tab--active"
    }
  }

  constructor(element) {
    super(element);
    this._tabPanelDomId = this.element.getAttribute('href').substring(1);
    if(!this._tabPanelDomId) {
      throw new Error('A TabButtonWidget must have a href attribute');
    }
    if(!this._domId) {
      throw new Error('A TabButtonWidget must have an id attribute');
    }
    this._onClickTabButton = this._onClickTabButton.bind(this);
    this._onActivateTabSignal = this._onActivateTabSignal.bind(this);
    this._initializeSignalHandlers();
    this.element.addEventListener('click', this._onClickTabButton);
  }

  _initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `cradmin.ActivateTab.${this.config.id}`,
      `cradmin.TabButtonWidget.${this.config.id}.${this._tabPanelDomId}`,
      this._onActivateTabSignal
    );
  }

  destroy() {
    this.element.removeEventListener('click', this._onClickTabButton);
    new SignalHandlerSingleton().removeReceiver(
      `cradmin.ActivateTab.${this.config.id}`,
      `cradmin.TabButtonWidget.${this.config.id}.${this._tabPanelDomId}`
    );
  }

  _onClickTabButton(event) {
    event.preventDefault();
    this._sendActivateTabSignal();
  }

  _sendActivateTabSignal() {
    new SignalHandlerSingleton().send(
      `cradmin.ActivateTab.${this.config.id}`,
      {tabPanelDomId: this._tabPanelDomId}
    );
  }

  _hasActiveClass() {
    return this.element.classList.contains(this.config.activeClass);
  }

  _isAriaSelected() {
    return this.element.getAttribute('aria-selected') == 'true';
  }


  _activate() {
    if(!this._hasActiveClass()) {
      this.element.classList.add(this.config.activeClass);
    }
    if(!this._isAriaSelected()) {
      this.element.setAttribute('aria-selected', 'true');
    }
  }

  _deactivate() {
    if(this._hasActiveClass()) {
      this.element.classList.remove(this.config.activeClass);
    }
    if(this._isAriaSelected()) {
      this.element.setAttribute('aria-selected', 'false');
    }
  }

  _onActivateTabSignal(receivedSignalInfo) {
    const tabPanelDomId = receivedSignalInfo.data.tabPanelDomId;
    if(this._tabPanelDomId == tabPanelDomId) {
      this._activate();
    } else {
      this._deactivate();
    }
  }

  useAfterInitializeAllWidgets() {
    return true;
  }

  get _domId() {
    return this.element.getAttribute('id');
  }

  afterInitializeAllWidgets() {
    const widgetRegistry = new WidgetRegistrySingleton();
    const tabPanelElement = document.getElementById(this._tabPanelDomId);
    const tabPanelWidget = widgetRegistry.getWidgetInstanceFromElement(tabPanelElement);
    const isActive = this._hasActiveClass();
    tabPanelWidget.initializeFromTabButton(isActive, this._domId);
    if(isActive) {
      // this._sendActivateTabSignal();
      this._activate();
    }
  }
}
