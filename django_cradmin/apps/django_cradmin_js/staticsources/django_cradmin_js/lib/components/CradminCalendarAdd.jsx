import React from "react";
import ReactDOM from "react-dom";
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";
import ObjectManager from "ievv_jsbase/lib/utils/ObjectManager";
import CradminDateSelector from "./CradminDateSelector";


/**
 * Renders a UI for adding entries to a calendar.
 */
export default class CradminCalendarAdd extends React.Component {

  static get defaultProps() {
    return {
      signalNameSpace: null,
      className: 'calendar-add',
      dateSelectorProps: {}
    }
  }

  constructor(props) {
    super(props);
    if(this.props.signalNameSpace == null) {
      throw new Error('The signalNameSpace prop is required.');
    }
    this.logger = new LoggerSingleton().getLogger(
      'django_cradmin.components.CradminCalendarAdd');
    this._fromDateSelectorProps = ObjectManager.mergeAndClone(this.props.dateSelectorProps, {
      signalNameSpace: `${this.props.signalNameSpace}.FromDateTime`
    });
    this._toDateSelectorProps = ObjectManager.mergeAndClone(this.props.dateSelectorProps, {
      signalNameSpace: `${this.props.signalNameSpace}.ToDateTime`
    });
  }

  renderDateSelectors() {
    return <div>
      <CradminDateSelector {...this._fromDateSelectorProps}/>
      &mdash;
      <CradminDateSelector {...this._toDateSelectorProps}/>
    </div>;
  }

  render() {
    return <div className={this.props.className}>
      {this.renderDateSelectors()}
    </div>;
  }
}
