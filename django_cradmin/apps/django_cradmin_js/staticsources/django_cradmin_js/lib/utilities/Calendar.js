//NOTE: This file was originally converted from coffeescript to ES6 using decaffeinate. If you see something weird,
//      please rewrite it to something readable :)

/**
Get an array of the short names for all the weekdays
in the current locale, in the the correct order for the
current locale.
*/
let getWeekdaysShortForCurrentLocale = function() {
  let weekdays = [];
  let weekdaysWithSundayFirst = moment.weekdaysShort();
  let firstDayOfWeek = moment.localeData().firstDayOfWeek();
  for (let index = firstDayOfWeek; index <= firstDayOfWeek + 6; index++) {
    if (index > 6) {
      index = Math.abs(7 - index);
    }
    let weekday = weekdaysWithSundayFirst[index];
    weekdays.push(weekday);
  }
  return weekdays;
};

class Month {
  constructor(firstDayOfMonth) {
    this.firstDayOfMonth = firstDayOfMonth;
    this.lastDayOfMonth = this.firstDayOfMonth.clone().add({
      days: this.firstDayOfMonth.daysInMonth() - 1
    });
  }

  getDaysInMonth() {
    return this.firstDayOfMonth.daysInMonth();
  }
}


class CalendarDay {
  constructor(momentObject, isInCurrentMonth, isDisabled, nowMomentObject) {
    this.momentObject = momentObject;
    this.isInCurrentMonth = isInCurrentMonth;
    this.nowMomentObject = nowMomentObject;
    this._isDisabled = isDisabled;
  }

  getNumberInMonth() {
    return this.momentObject.format('D');
  }

  isToday() {
    return this.momentObject.isSame(this.nowMomentObject, 'day');
  }

  isDisabled() {
    return this._isDisabled;
  }
}

class CalendarWeek {
  constructor() {
    this.calendarDays = [];
  }

  addDay(calendarDay) {
    return this.calendarDays.push(calendarDay);
  }

  getDayCount() {
    return this.calendarDays.length;
  }

  prettyOneLineFormat() {
    let formattedDays = [];
    for (let calendarDay of this.calendarDays) {
      let formattedDay = calendarDay.momentObject.format('DD');
      if (calendarDay.isInCurrentMonth) {
        formattedDay = ` ${formattedDay} `;
      } else {
        formattedDay = `(${formattedDay})`;
      }
      formattedDays.push(formattedDay);
    }
    return formattedDays.join(' ');
  }
}


class CalendarMonth {
  constructor(calendarCoordinator, momentObject){
    this.calendarCoordinator = calendarCoordinator;
    this.changeMonth(momentObject);
  }

  changeMonth(momentObject) {
    let firstDayOfMonthMomentObject = momentObject.clone().set({
      date: 1,
      hour: 0,
      minute: 0,
      second: 0,
      millisecond: 0
    });
    this.month = new Month(firstDayOfMonthMomentObject);
    this.calendarWeeks = [new CalendarWeek()];
    this.currentWeekIndex = 0;
    this.daysPerWeek = 7;
    this.totalWeeks = 6;
    this.currentDayCount = 0;
    this.lastDay = null;
    return this._build();
  }

  _buildPrefixedDays() {
    if (this.month.firstDayOfMonth.weekday() > 0) {
      let momentObject;
      for (let index = 1; index <= this.month.firstDayOfMonth.weekday(); index++) {
        momentObject = this.month.firstDayOfMonth.clone().subtract({
          days: index
        });
        this._addMomentObject(momentObject, false);
      }
    }
  }

  _buildSuffixedDays() {
    let totalDayCount = this.totalWeeks * this.daysPerWeek;
    return (() => {
      let result = [];
      while (this.currentDayCount < totalDayCount) {
        let momentObject = this.lastDay.momentObject.clone().add({
          days: 1
        });
        result.push(this._addMomentObject(momentObject, false));
      }
      return result;
    })();
  }

  _buildDaysBelongingInMonth() {
    let momentObject;
    for (let dayIndex = 1; dayIndex <= this.month.getDaysInMonth(); dayIndex ++) {
      momentObject = this.month.firstDayOfMonth.clone().date(dayIndex);
      this._addMomentObject(momentObject, true);
    }
  }

  _build(momentFirstDayOfMonth) {
    this._buildPrefixedDays();
    this._buildDaysBelongingInMonth();
    return this._buildSuffixedDays();
  }

  _addMomentObject(momentObject, isInCurrentMonth) {
    let week = this.calendarWeeks[this.currentWeekIndex];
    if (week.getDayCount() >= this.daysPerWeek) {
      this.calendarWeeks.push(new CalendarWeek());
      this.currentWeekIndex += 1;
      week = this.calendarWeeks[this.currentWeekIndex];
    }

    let isDisabled = !this.calendarCoordinator.momentObjectIsAllowed(momentObject);
    let calendarDay = new CalendarDay(momentObject, isInCurrentMonth, isDisabled,
      this.calendarCoordinator.nowMomentObject);
    week.addDay(calendarDay);
    this.currentDayCount += 1;
    return this.lastDay = calendarDay;
  }

  prettyprint() {
    let rowFormatted;
    for (week in this.calendarWeeks) {
      rowFormatted = [];
      console.log(week.prettyOneLineFormat());
    }
  }
}


/**
Coordinates the common calendar data no matter what kind of
view we present.
*/
export class CalendarCoordinator {
  constructor({selectedMomentObject,
                 minimumDatetime,
                 maximumDatetime,
                 nowMomentObject}) {
    // We operate with two momentObjects:
    // - selectedMomentObject: This is the actual moment object
    //   that the user has selected. This can be null if the user
    //   has not selected a value yet.
    // - shownMomentObject: This reflects the value shown on the screen
    //   at any given moment (E.g.: It changes each time a user changes
    //   the day, month, hour, etc). This is never ``null``.
    this.selectedMomentObject = selectedMomentObject;
    this.minimumDatetime = minimumDatetime;
    this.maximumDatetime = maximumDatetime;
    this.nowMomentObject = nowMomentObject;
    if (this.selectedMomentObject != null) {
      this.shownMomentObject = this.selectedMomentObject.clone();
    } else {
      // We set this to start the date picker on the current date
      this.setToNow();

      // If the current time is not allowed, pick the first allowed value
      if (!this.momentObjectIsAllowed(this.shownMomentObject)) {
        this.shownMomentObject = this.minimumDatetime.clone();
      }
    }
  }

  selectShownValue() {
    return this.selectedMomentObject = this.shownMomentObject.clone();
  }

  clearSelectedMomentObject() {
    return this.selectedMomentObject = null;
  }

  momentObjectIsAllowed(momentObject, ignoreTime=true) {
    let isAllowed = true;
    if (this.minimumDatetime != null) {
      let { minimumDatetime } = this;
      if (ignoreTime) {
        minimumDatetime = minimumDatetime.clone().set({
          hour: 0,
          minute: 0,
          second: 0
        });
      }
      isAllowed = !momentObject.isBefore(minimumDatetime);
    }
    if (isAllowed && (this.maximumDatetime != null)) {
      let { maximumDatetime } = this;
      if (ignoreTime) {
        maximumDatetime = maximumDatetime.clone().set({
          hour: 23,
          minute: 59,
          second: 59
        });
      }
      isAllowed = !momentObject.isAfter(maximumDatetime);
    }
    return isAllowed;
  }

  todayIsValidValue() {
    return this.momentObjectIsAllowed(this.nowMomentObject);
  }

  nowIsValidValue() {
    return this.momentObjectIsAllowed(this.nowMomentObject, false);
  }

  shownDateIsToday() {
    return this.shownMomentObject.isSame(this.nowMomentObject, 'day');
  }

  shownDateIsTodayAndNowIsValid() {
    return this.shownDateIsToday() && this.nowIsValidValue();
  }

  setToNow() {
    return this.shownMomentObject = this.nowMomentObject.clone();
  }
}


/**
Coordinates the common calendar data for a month-view.
*/
export class MonthlyCalendarCoordinator {
  constructor({calendarCoordinator,
                 yearselectValues,
                 hourselectValues,
                 minuteselectValues,
                 yearFormat,
                 monthFormat,
                 dayOfMonthSelectFormat,
                 dayOfMonthTableCellFormat,
                 hourFormat,
                 minuteFormat}) {
    this.calendarCoordinator = calendarCoordinator;
    this.yearselectValues = yearselectValues;
    this.hourselectValues = hourselectValues;
    this.minuteselectValues = minuteselectValues;
    this.yearFormat = yearFormat;
    this.monthFormat = monthFormat;
    this.dayOfMonthSelectFormat = dayOfMonthSelectFormat;
    this.dayOfMonthTableCellFormat = dayOfMonthTableCellFormat;
    this.hourFormat = hourFormat;
    this.minuteFormat = minuteFormat;
    this.dayobjects = null;  // Updated in @_changeSelectedDate()
    this._initWeekdays();
    this._initMonthObjects();
    this._initYearObjects();
    this._initHourObjects();
    this._initMinuteObjects();
    this._changeSelectedDate();
  }


  _sortConfigObjectsByValue(configObjects) {
    let compareFunction = function(a, b) {
      if (a.value < b.value) {
        return -1;
      }
      if (a.value > b.value) {
        return 1;
      }
      return 0;
    };
    return configObjects.sort(compareFunction);
  }

  _initWeekdays() {
    return this.shortWeekdays = getWeekdaysShortForCurrentLocale();
  }

  _initYearObjects() {
    let selectedYearValue = this.calendarCoordinator.shownMomentObject.year();
    let hasSelectedYearValue = false;

    let formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
      month: 0,
      date: 0,
      hour: 0,
      minute: 0,
      second: 0
    });

    this._yearsMap = {};
    this.yearselectConfig = [];
    for (let year of this.yearselectValues) {
      var label = formatMomentObject.set({
        year
      }).format(this.yearFormat);
      var yearConfig = {
        value: year,
        label
      };
      this.yearselectConfig.push(yearConfig);
      this._yearsMap[year] = yearConfig;
      if (year === selectedYearValue) {
        hasSelectedYearValue = true;
      }
    }

    if (!hasSelectedYearValue) {
      // Since we do not include all years in the yearList, we need
      // to handle the case when the given datetimes year is not in the
      // list. We handle this by adding it to the end of the list.
      var label = formatMomentObject.set({
        year: selectedYearValue
      }).format(this.yearFormat);
      var yearConfig = {
        value: selectedYearValue,
        label
      };
      this.yearselectConfig.push(yearConfig);
      this._yearsMap[yearConfig.value] = yearConfig;

      // Sort the config to put the newly added config in
      // its natural place.
      return this._sortConfigObjectsByValue(this.yearselectConfig);
    }
  }

  _initMonthObjects() {
    let label;
    let monthObject;
    this.monthselectConfig = [];
    this._monthsMap = {};

    let formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
      month: 0,
      date: 0,
      hour: 0,
      minute: 0,
      second: 0
    });
    for (let monthnumber = 0; monthnumber < 12; monthnumber++) {
      label = formatMomentObject.set({
        month: monthnumber
      }).format(this.monthFormat);
      monthObject = {
        value: monthnumber,
        label
      };
      this.monthselectConfig.push(monthObject);
      this._monthsMap[monthnumber] = monthObject;
    }
  }

  _initHourObjects() {
    let selectedHourValue = this.calendarCoordinator.shownMomentObject.hour();
    let hasSelectedHourValue = false;
    let formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
      minute: 0,
      second: 0
    });
    this._hoursMap = {};
    this.hourselectConfig = [];
    for (let hour of this.hourselectValues) {
      var label = formatMomentObject.set({
        hour
      }).format(this.hourFormat);
      var hourConfig = {
        value: hour,
        label
      };
      this.hourselectConfig.push(hourConfig);
      this._hoursMap[hourConfig.value] = hourConfig;
      if (hourConfig.value === selectedHourValue) {
        hasSelectedHourValue = true;
      }
    }

    if (!hasSelectedHourValue) {
      // Since we do not include all hours in the hourList, we need
      // to handle the case when the given datetimes hour is not in the
      // list. We handle this by adding it to the end of the list.
      var label = formatMomentObject.set({
        hour: selectedHourValue
      }).format(this.hourFormat);
      var hourConfig = {
        value: selectedHourValue,
        label
      };
      this.hourselectConfig.push(hourConfig);
      this._hoursMap[hourConfig.value] = hourConfig;
      return this._sortConfigObjectsByValue(this.hourselectConfig);
    }
  }

  _initMinuteObjects() {
    let selectedMinuteValue = this.calendarCoordinator.shownMomentObject.minute();
    let hasSelectedMinuteValue = false;
    let formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
      second: 0
    });
    this._minutesMap = {};
    this.minuteselectConfig = [];
    for (let minute of this.minuteselectValues) {
      var label = formatMomentObject.set({
        minute
      }).format(this.minuteFormat);
      var minuteConfig = {
        value: minute,
        label
      };
      this.minuteselectConfig.push(minuteConfig);
      this._minutesMap[minuteConfig.value] = minuteConfig;
      if (minuteConfig.value === selectedMinuteValue) {
        hasSelectedMinuteValue = true;
      }
    }

    if (!hasSelectedMinuteValue) {
      // Since we do not include all minutes in the minuteList, we need
      // to handle the case when the given datetimes minute is not in the
      // list. We handle this by adding it to the end of the list.
      var label = formatMomentObject.set({
        minute: selectedMinuteValue
      }).format(this.minuteFormat);
      var minuteConfig = {
        value: selectedMinuteValue,
        label
      };
      this.minuteselectConfig.push(minuteConfig);
      this._minutesMap[minuteConfig.value] = minuteConfig;
      return this._sortConfigObjectsByValue(this.minuteselectConfig);
    }
  }

  _setCurrentYear() {
    let currentYearNumber = this.calendarMonth.month.firstDayOfMonth.year();
    this.currentYearObject = this._yearsMap[currentYearNumber];
    if (this.currentYearObject == null) {
      console.warn(`The given year, ${currentYearNumber} is not one of the available choices`);
    }
  }

  _setCurrentMonth() {
    let currentMonthNumber = this.calendarMonth.month.firstDayOfMonth.month();
    this.currentMonthObject = this._monthsMap[currentMonthNumber];
    if (this.currentMonthObject == null) {
      console.warn(`The given month number, ${currentMonthNumber} is not one of the available choices`);
    }
  }

  _setCurrentHour() {
    let currentHourNumber = this.calendarCoordinator.shownMomentObject.hour();
    this.currentHourObject = this._hoursMap[currentHourNumber];
    if (this.currentHourObject == null) {
      console.warn(`The given hour, ${currentHourNumber} is not one of the available choices`);
    }
  }

  _setCurrentMinute() {
    let currentMinuteNumber = this.calendarCoordinator.shownMomentObject.minute();
    this.currentMinuteObject = this._minutesMap[currentMinuteNumber];
    if (this.currentMinuteObject == null) {
      console.warn(`The given minute, ${currentMinuteNumber} is not one of the available choices`);
    }
  }

  _updateDayObjects() {
    let label;
    let dayNumberObject;
    let formatMomentObject = this.calendarCoordinator.shownMomentObject.clone().set({
      hour: 0,
      minute: 0,
      second: 0
    });
    this.dayobjects = [];
    for (let daynumber = 1; index <= this.calendarMonth.month.getDaysInMonth(); index++) {
      label = formatMomentObject.set({
        date: daynumber
      }).format(this.dayOfMonthSelectFormat);

      dayNumberObject = {
        value: daynumber,
        label: label
      };
      this.dayobjects.push(dayNumberObject);
    }
  }

  /*
  Change month to the month containing the given momentObject,
  and select the date.

  As long as you change ``@calendarCoordinator.shownMomentObject``, this
  will update everything to mirror the change (selected day, month, year, ...).
  */
  _changeSelectedDate() {
    this.calendarMonth = new CalendarMonth(this.calendarCoordinator, this.calendarCoordinator.shownMomentObject);
    this._setCurrentYear();
    this._setCurrentMonth();
    this._setCurrentHour();
    this._setCurrentMinute();
    this._updateDayObjects();
    return this.currentDayObject = this.dayobjects[this.calendarCoordinator.shownMomentObject.date()-1];
  }

  handleDayChange(momentObject) {
    this.calendarCoordinator.shownMomentObject = momentObject.clone().set({
      hour: this.currentHourObject.value,
      minute: this.currentMinuteObject.value
    });
    return this._changeSelectedDate();
  }

  handleCurrentDayObjectChange() {
    let momentObject = moment({
      year: this.currentYearObject.value,
      month: this.currentMonthObject.value,
      day: this.currentDayObject.value
    });
    return this.handleDayChange(momentObject);
  }

  handleCalendarDayChange(calendarDay) {
    return this.handleDayChange(calendarDay.momentObject);
  }

  handleCurrentMonthChange() {
    this.calendarCoordinator.shownMomentObject.set({
      month: this.currentMonthObject.value
    });
    return this._changeSelectedDate();
  }

  handleCurrentYearChange() {
    this.calendarCoordinator.shownMomentObject.set({
      year: this.currentYearObject.value
    });
    return this._changeSelectedDate();
  }

  handleCurrentHourChange() {
    this.calendarCoordinator.shownMomentObject.set({
      hour: this.currentHourObject.value
    });
    return this._changeSelectedDate();
  }

  handleCurrentMinuteChange() {
    this.calendarCoordinator.shownMomentObject.set({
      minute: this.currentMinuteObject.value
    });
    return this._changeSelectedDate();
  }

  handleFocusOnCalendarDay(calendarDay) {
    return this.lastFocusedMomentObject = calendarDay.momentObject;
  }

  getLastFocusedMomentObject() {
    if (this.lastFocusedMomentObject != null) {
      return this.lastFocusedMomentObject;
    } else {
      return this.calendarCoordinator.shownMomentObject;
    }
  }

  getDayOfMonthLabelForTableCell(calendarDay) {
    return calendarDay.momentObject.format(this.dayOfMonthTableCellFormat);
  }

  setToToday() {
    return this.handleDayChange(this.calendarCoordinator.nowMomentObject.clone());
  }
}
