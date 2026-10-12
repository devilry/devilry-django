import React from "react";
import DomUtilities from "../utilities/DomUtilities";
import {HotKeys} from "react-hotkeys";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminSelectedListItem extends React.Component {

  static get defaultProps() {
    return {
      className: 'selectable-list__item  selectable-list__item--selected',
      contentClassName: 'selectable-list__itemcontent',
      iconWrapperClassName: 'selectable-list__icon',
      iconClassName: 'cricon cricon--close cricon--color-light',
      titleTagName: 'strong',
      titleClassName: 'selectable-list__itemtitle',
      descriptionClassName: '',
      ariaTitlePrefix: 'Deselect',
      renderMode: 'TitleAndDescription',
      focusClosestSiblingOnDeSelect: true,
      previousItemData: null,
      nextItemData: null,
      uniqueListId: '',
      useHotKeys: false
    }
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.CradminSelectedListItem.${this.props.signalNameSpace}.${this.props.uniqueListId}.${this.props.itemKey}`;
    this.handleDeSelect = this.handleDeSelect.bind(this);
    this.handleFocus = this.handleFocus.bind(this);
    this.handleBlur = this.handleBlur.bind(this);
    this._onFocusOnSelectedItemSignal = this._onFocusOnSelectedItemSignal.bind(this);
    this.initializeSignalHandlers();
  }

  initializeSignalHandlers() {
    new SignalHandlerSingleton().addReceiver(
      `${this.props.signalNameSpace}.FocusOnSelectedItem.${this.props.itemKey}`,
      this._name,
      this._onFocusOnSelectedItemSignal
    );
  }

  componentWillUnmount() {
    new SignalHandlerSingleton()
      .removeAllSignalsFromReceiver(this._name);
  }

  _deselectItem() {
    new SignalHandlerSingleton().send(
      `${this.props.signalNameSpace}.DeSelectItem`,
      this.props.data
    );

    if(this.props.focusClosestSiblingOnDeSelect) {
      let closestSiblingData = this.props.previousItemData;
      if(closestSiblingData == null) {
        closestSiblingData = this.props.nextItemData;
      }
      if(closestSiblingData == null) {
        new SignalHandlerSingleton().send(
          `${this.props.signalNameSpace}.CouldNotFocusOnClosestSelectedItem`);
      } else {
        new SignalHandlerSingleton().send(
          `${this.props.signalNameSpace}.FocusOnDeSelectableItem`,
          closestSiblingData
        );
      }
    }
  }

  handleDeSelect(event) {
    event.preventDefault();
    this._deselectItem();
  }

  handleFocus() {
    if(this.props.setDataListFocus) {
      new SignalHandlerSingleton().send(
        `${this.props.signalNameSpace}.Focus`
      );
    }
  }

  handleBlur() {
    if(this.props.setDataListFocus) {
      new SignalHandlerSingleton().send(
        `${this.props.signalNameSpace}.Blur`
      );
    }
  }

  _onFocusOnSelectedItemSignal() {
    DomUtilities.forceFocus(this._domElement);
  }

  get ariaTitle() {
    if(this.props.data.ariaTitle) {
      return this.props.data.ariaTitle;
    } else {
      let ariaTitle = this.props.data.title;
      if(this.props.ariaTitlePrefix) {
        ariaTitle = `${this.props.ariaTitlePrefix} ${ariaTitle}`;
      }
      return ariaTitle;
    }
  }

  renderTitle() {
    return React.createElement(this.props.titleTagName, {
      className: this.props.titleClassName
    }, this.props.data.title);
  }

  renderDescription() {
    if(this.props.data.description && this.props.data.description != '') {
      return <p className={this.props.descriptionClassName}>{this.props.data.description}</p>;
    } else {
      return '';
    }
  }

  renderIcon() {
    return <i className={this.props.iconClassName} />;
  }

  renderIconWrapper() {
    return <div className={this.props.iconWrapperClassName}>
      {this.renderIcon()}
    </div>;
  }

  renderContentModeTitleAndDescription() {
    return <div className={this.props.contentClassName}>
      {this.renderTitle()}
      {this.renderDescription()}
    </div>;
  }

  renderContentModeTitleOnly() {
    return <div className={this.props.contentClassName}>
      {this.props.data.title}
    </div>;
  }

  renderContentModeHtml() {
    return <div className={this.props.contentClassName}
                dangerouslySetInnerHTML={{__html: this.props.data.html}}></div>;
  }

  renderContent() {
    if(this.props.renderMode == 'TitleAndDescription') {
      return this.renderContentModeTitleAndDescription();
    } else if(this.props.renderMode == 'TitleOnly') {
      return this.renderContentModeTitleOnly();
    } else if(this.props.renderMode == 'html') {
      return this.renderContentModeHtml();
    } else {
      throw new Error(`Invalid renderMode: ${this.props.renderMode}`);
    }
  }

  _focusPreviousItem() {
    if(this.props.previousItemData == null) {
      new SignalHandlerSingleton().send(
        `${this.props.signalNameSpace}.FocusBeforeFirstSelectableItem`);
    } else {
      new SignalHandlerSingleton().send(
        `${this.props.signalNameSpace}.FocusOnSelectableItem`,
        this.props.previousItemData
      );
    }
  }

  _focusNextItem() {
    if(this.props.nextItemData == null) {
      new SignalHandlerSingleton().send(
        `${this.props.signalNameSpace}.FocusAfterLastSelectableItem`);
    } else {
      new SignalHandlerSingleton().send(
        `${this.props.signalNameSpace}.FocusOnSelectableItem`,
        this.props.nextItemData
      );
    }
  }

  get hotKeysMap() {
    return {
      'deselect': ['delete', 'backspace']
    };
  }

  get hotKeysHandlers() {
    return {
      'deselect': (event) => {
        event.preventDefault();
        this._deselectItem();
      }
    }
  }

  renderWrapper() {
    return <a href="#" className={this.props.className}
              ref={(domElement) => { this._domElement = domElement; }}
              onClick={this.handleDeSelect}
              onFocus={this.handleFocus}
              onBlur={this.handleBlur}
              aria-label={this.ariaTitle}
              role="button">
      {this.renderContent()}
      {this.renderIconWrapper()}
    </a>
  }

  render() {
    if(this.props.useHotKeys) {
      return <HotKeys keyMap={this.hotKeysMap} handlers={this.hotKeysHandlers}>
        {this.renderWrapper()}
      </HotKeys>
    } else {
      return this.renderWrapper();
    }
  }
}
