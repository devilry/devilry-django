import React from "react";
import ReactDOM from "react-dom";
import CradminDateSelectorYear from "./CradminDateSelectorYear";
import CradminDateSelectorMonth from "./CradminDateSelectorMonth";
import CradminDateSelectorDay from "./CradminDateSelectorDay";
import CradminDateSelectorHour from "./CradminDateSelectorHour";
import CradminDateSelectorMinute from "./CradminDateSelectorMinute";
import CradminDateSelectorHiddenIsoDate from "./CradminDateSelectorHiddenIsoDate";
import CradminDateSelectorHiddenIsoDateTime from "./CradminDateSelectorHiddenIsoDateTime";
import CradminDateSelectorHiddenIsoTime from "./CradminDateSelectorHiddenIsoTime";

export default class CradminDateSelector extends React.Component {
  static get defaultProps() {
    return {
      signalNameSpace: null,
      includeDate: true,
      includeTime: false,
      monthBeforeDay: false,
      resultFieldProps: {},
      dayFieldProps: {},
      monthFieldProps: {},
      yearFieldProps: {},
      hourFieldProps: {},
      minuteFieldProps: {},

      initialDay: null,
      initialMonth: null,
      initialYear: new Date().getUTCFullYear(),
      initialMinute: 0,
      initialHour: 0
    };
  }

  renderResultField() {
    if(this.props.includeDate && this.props.includeTime) {
      return <CradminDateSelectorHiddenIsoDateTime
        signalNameSpace={this.props.signalNameSpace}
        initialDay={this.props.initialDay}
        initialMonth={this.props.initialMonth}
        initialYear={this.props.initialYear}
        initialHour={this.props.initialHour}
        initialMinute={this.props.initialMinute}
        {...this.props.resultFieldProps}
      />;
    } else if(this.props.includeDate) {
      return <CradminDateSelectorHiddenIsoDate
        signalNameSpace={this.props.signalNameSpace}
        initialDay={this.props.initialDay}
        initialMonth={this.props.initialMonth}
        initialYear={this.props.initialYear}
        {...this.props.resultFieldProps}
      />;
    } else {
      return <CradminDateSelectorHiddenIsoTime
        signalNameSpace={this.props.signalNameSpace}
        initialHour={this.props.initialHour}
        initialMinute={this.props.initialMinute}
        {...this.props.resultFieldProps}
      />;
    }
  }

  renderDayComponent() {
    return <label key="day" className="dateinput__select">
      <CradminDateSelectorDay
        signalNameSpace={this.props.signalNameSpace}
        initialValue={this.props.initialDay}
        {...this.props.dayFieldProps} />
    </label>;
  }

  renderMonthComponent() {
    return <label key="month" className="dateinput__select">
      <CradminDateSelectorMonth
        signalNameSpace={this.props.signalNameSpace}
        initialValue={this.props.initialMonth}
        {...this.props.monthFieldProps} />
    </label>;
  }

  renderYearComponent() {
    return <label key="year" className="dateinput__select">
      <CradminDateSelectorYear
        signalNameSpace={this.props.signalNameSpace}
        initialValue={this.props.initialYear}
        {...this.props.yearFieldProps} />
    </label>;
  }

  renderDateComponents() {
    let dateComponents = [];
    if(this.props.monthBeforeDay) {
      dateComponents = [
        this.renderMonthComponent(),
        this.renderDayComponent(),
      ];
    } else {
      dateComponents = [
        this.renderDayComponent(),
        this.renderMonthComponent(),
      ];
    }
    dateComponents.push(this.renderYearComponent());
    return dateComponents;
  }

  renderDateGroup() {
    return <div key="date" className="dateinput__group">
      {this.renderDateComponents()}
    </div>;
  }

  renderHourComponent() {
    return <CradminDateSelectorHour
      key="hour"
      signalNameSpace={this.props.signalNameSpace}
      initialValue={this.props.initialHour}
      {...this.props.hourFieldProps} />;
  }

  renderHourMinuteSeparatorComponent() {
    return <span key="hourminuteseparator"
                 className="dateinput__separator">:</span>;
  }

  renderMinuteComponent() {
    return <CradminDateSelectorMinute
      key="minute"
      signalNameSpace={this.props.signalNameSpace}
      initialValue={this.props.initialMinute}
      {...this.props.minuteFieldProps} />;
  }

  renderTimeComponents() {
    return [
      this.renderHourComponent(),
      this.renderHourMinuteSeparatorComponent(),
      this.renderMinuteComponent()
    ];
  }

  renderTimeGroup() {
    return <label key="time" className="dateinput__group">
      {this.renderTimeComponents()}
    </label>;
  }

  renderGroups() {
    let groups = [];
    if(this.props.includeDate) {
      groups.push(this.renderDateGroup());
    }
    if(this.props.includeTime) {
      groups.push(this.renderTimeGroup());
    }
    return groups;
  }

  render() {
    return <div className="dateinput">
      {this.renderGroups()}
      {this.renderResultField()}
    </div>;
  }
}
