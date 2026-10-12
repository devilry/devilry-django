import React from "react";
import DomUtilities from "../utilities/DomUtilities";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import SignalHandlerSingleton from "ievv_jsbase/lib/SignalHandlerSingleton";


export default class CradminMoveButton extends React.Component {
  static get defaultProps() {
    return {
      iconClassName: '',
      className: 'button',
      moveDirection: null,
      itemIndex: null,
      signalNameSpace: null,
      ariaLabel: ''
    }
  }

  constructor(props) {
    super(props);
    this._name = `django_cradmin.components.MoveButton.${this.props.signalNameSpace}`;
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.MoveButton');
    if(this.props.signalNameSpace == null) {
      throw new Error('The signalNameSpace prop is required.');
    }
    if(this.props.moveDirection == null) {
      throw new Error('The moveDirection prop is required.');
    }
    if(this.props.itemIndex == null) {
      throw new Error('The itemIndex prop is required.');
    }
    this.signalHandler = new SignalHandlerSingleton();
    this.onClick = this.onClick.bind(this);
  }

  onClick(event) {
    event.preventDefault();
    this.signalHandler.send(`${this.props.signalNameSpace}.SortableHtmlList.MoveItem${this.props.moveDirection}`, {
      itemIndex: this.props.itemIndex
    });
  }

  renderButtonContent() {
    return <span className={this.props.iconClassName} aria-hidden="true"/>;
  }

  render() {
    return <button type="button"
                   className={this.props.className}
                   onClick={this.onClick}
                   aria-label={this.props.ariaLabel}>
      {this.renderButtonContent()}
    </button>;
  }
}
