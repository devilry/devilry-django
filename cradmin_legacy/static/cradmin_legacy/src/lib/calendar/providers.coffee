app = angular.module 'cradminLegacy.calendar.providers', []


app.provider 'cradminLegacyCalendarApi', ->

  ###*
  Get an array of the short names for all the weekdays
  in the current locale, in the the correct order for the
  current locale.
  ###
  getWeekdaysShortForCurrentLocale = ->
    weekdays = []
    weekdaysWithSundayFirst = moment.weekdaysShort()
    firstDayOfWeek = moment.localeData().firstDayOfWeek()
    for index in [firstDayOfWeek..firstDayOfWeek+6]
      if index > 6
        index = Math.abs(7 - index)
      weekday = weekdaysWithSundayFirst[index]
      weekdays.push(weekday)
    return weekdays

  class Month
    constructor: (@firstDayOfMonth) ->
      @lastDayOfMonth = @firstDayOfMonth.clone().add({
        days: @firstDayOfMonth.daysInMonth() - 1
      })

    getDaysInMonth: ->
      return @firstDayOfMonth.daysInMonth()


  class CalendarDay
    constructor: (@momentObject, @isInCurrentMonth, isDisabled, @nowMomentObject) ->
      @_isDisabled = isDisabled

    getNumberInMonth: ->
      return @momentObject.format('D')

    isToday: ->
      return @momentObject.isSame(@nowMomentObject, 'day')

    isDisabled: ->
      return @_isDisabled

  class CalendarWeek
    constructor: ->
      @calendarDays = []

    addDay: (calendarDay) ->
      @calendarDays.push(calendarDay)

    getDayCount: ->
      return @calendarDays.length

    prettyOneLineFormat: ->
      formattedDays = []
      for calendarDay in @calendarDays
        formattedDay = calendarDay.momentObject.format('DD')
        if calendarDay.isInCurrentMonth
          formattedDay = " #{formattedDay} "
        else
          formattedDay = "(#{formattedDay})"
        formattedDays.push(formattedDay)
      return formattedDays.join(' ')


  class CalendarMonth
    constructor: (@calendarCoordinator, momentObject)->
      @changeMonth(momentObject)

    changeMonth: (momentObject) ->
      firstDayOfMonthMomentObject = momentObject.clone().set({
        date: 1
        hour: 0
        minute: 0
        second: 0
        millisecond: 0
      })
      @month = new Month(firstDayOfMonthMomentObject)
      @calendarWeeks = [new CalendarWeek()]
      @currentWeekIndex = 0
      @daysPerWeek = 7
      @totalWeeks = 6
      @currentDayCount = 0
      @lastDay = null
      @__build()

    __buildPrefixedDays: ->
      if @month.firstDayOfMonth.weekday() > 0
        for index in [@month.firstDayOfMonth.weekday()..1]
          momentObject = @month.firstDayOfMonth.clone().subtract({
            days: index
          })
          @__addMomentObject(momentObject, false)

    __buildSuffixedDays: ->
      totalDayCount = @totalWeeks * @daysPerWeek
      while @currentDayCount < totalDayCount
        momentObject = @lastDay.momentObject.clone().add({
          days: 1
        })
        @__addMomentObject(momentObject, false)

    __buildDaysBelongingInMonth: ->
      for dayIndex in [1..@month.getDaysInMonth()]
        momentObject = @month.firstDayOfMonth.clone().date(dayIndex)
        @__addMomentObject(momentObject, true)

    __build: (momentFirstDayOfMonth) ->
      @__buildPrefixedDays()
      @__buildDaysBelongingInMonth()
      @__buildSuffixedDays()

    __addMomentObject: (momentObject, isInCurrentMonth) ->
      week = @calendarWeeks[@currentWeekIndex]
      if week.getDayCount() >= @daysPerWeek
        @calendarWeeks.push(new CalendarWeek())
        @currentWeekIndex += 1
        week = @calendarWeeks[@currentWeekIndex]

      isDisabled = not @calendarCoordinator.momentObjectIsAllowed(momentObject)
      calendarDay = new CalendarDay(momentObject, isInCurrentMonth, isDisabled,
        @calendarCoordinator.nowMomentObject)
      week.addDay(calendarDay)
      @currentDayCount += 1
      @lastDay = calendarDay

    prettyprint: ->
      for week in @calendarWeeks
        rowFormatted = []
        console?.log? week.prettyOneLineFormat()


  ###
  Coordinates the common calendar data no matter what kind of
  view we present.
  ###
  class CalendarCoordinator
    constructor: ({@selectedMomentObject,
                   @minimumDatetime,
                   @maximumDatetime,
                   @defaultNowTime,
                   @nowMomentObject}) ->
      # We operate with two momentObjects:
      # - selectedMomentObject: This is the actual moment object
      #   that the user has selected. This can be null if the user
      #   has not selected a value yet.
      # - shownMomentObject: This reflects the value shown on the screen
      #   at any given moment (E.g.: It changes each time a user changes
      #   the day, month, hour, etc). This is never ``null``.
      if @selectedMomentObject?
        @shownMomentObject = @selectedMomentObject.clone()
      else
        # We set this to start the date picker on the current date
        @setToNow()
        @setInitialTimeForDate()

        # If the current time is not allowed, pick the first allowed value
        if not @momentObjectIsAllowed(@shownMomentObject)
          @shownMomentObject = @minimumDatetime.clone()

    selectShownValue: ->
      @selectedMomentObject = @shownMomentObject.clone()

    clearSelectedMomentObject: ->
      @selectedMomentObject = null

    momentObjectIsAllowed: (momentObject, ignoreTime=true) ->
      isAllowed = true
      if @minimumDatetime?
        minimumDatetime = @minimumDatetime
        if ignoreTime
          minimumDatetime = minimumDatetime.clone().set({
            hour: 0
            minute: 0
            second: 0
          })
        isAllowed = not momentObject.isBefore(minimumDatetime)
      if isAllowed and @maximumDatetime?
        maximumDatetime = @maximumDatetime
        if ignoreTime
          maximumDatetime = maximumDatetime.clone().set({
            hour: 23
            minute: 59
            second: 59
          })
        isAllowed = not momentObject.isAfter(maximumDatetime)
      return isAllowed

    todayIsValidValue: ->
      return @momentObjectIsAllowed(@nowMomentObject)

    nowIsValidValue: ->
      return @momentObjectIsAllowed(@nowMomentObject, false)

    shownDateIsToday: ->
      return @shownMomentObject.isSame(@nowMomentObject, 'day')

    shownDateIsTodayAndNowIsValid: ->
      return @shownDateIsToday() && @nowIsValidValue()

    setToNow: ->
      @shownMomentObject = @nowMomentObject.clone()
    
    setInitialTimeForDate: ->
      if @defaultNowTime
        hour = @nowMomentObject.hour
        minute = @nowMomentObject.minute
        if @defaultNowTime.hour != undefined && @defaultNowTime.hour != null
          hour = @defaultNowTime.hour
        if @defaultNowTime.minute != undefined && @defaultNowTime.minute != null
          minute = @defaultNowTime.minute
        @shownMomentObject = @nowMomentObject.clone().set({
          hour: if @defaultNowTime.hour then @defaultNowTime.hour else hour,
          minute: if @defaultNowTime.minute? then @defaultNowTime.minute else minute,
          second: 0
        })


  ###*
  Coordinates the common calendar data for a month-view.
  ###
  class MonthlyCalendarCoordinator
    constructor: ({@calendarCoordinator,
                   @yearselectValues,
                   @hourselectValues,
                   @minuteselectValues,
                   @yearFormat,
                   @monthFormat,
                   @dayOfMonthSelectFormat,
                   @dayOfMonthTableCellFormat,
                   @hourFormat,
                   @minuteFormat}) ->
      @dayobjects = null  # Updated in @__changeSelectedDate()
      @__initWeekdays()
      @__initMonthObjects()
      @__initYearObjects()
      @__initHourObjects()
      @__initMinuteObjects()
      @__changeSelectedDate()


    __sortConfigObjectsByValue: (configObjects) ->
      compareFunction = (a, b) ->
        if a.value < b.value
          return -1
        if a.value > b.value
          return 1
        return 0
      configObjects.sort(compareFunction)

    __initWeekdays: ->
      @shortWeekdays = getWeekdaysShortForCurrentLocale()

    __initYearObjects: ->
      selectedYearValue = @calendarCoordinator.shownMomentObject.year()
      hasSelectedYearValue = false

      formatMomentObject = @calendarCoordinator.shownMomentObject.clone().set({
        month: 0
        date: 0
        hour: 0
        minute: 0
        second: 0
      })

      @__yearsMap = {}
      @yearselectConfig = []
      for year in @yearselectValues
        label = formatMomentObject.set({
          year: year
        }).format(@yearFormat)
        yearConfig = {
          value: year
          label: label
        }
        @yearselectConfig.push(yearConfig)
        @__yearsMap[year] = yearConfig
        if year == selectedYearValue
          hasSelectedYearValue = true

      if not hasSelectedYearValue
        # Since we do not include all years in the yearList, we need
        # to handle the case when the given datetimes year is not in the
        # list. We handle this by adding it to the end of the list.
        label = formatMomentObject.set({
          year: selectedYearValue
        }).format(@yearFormat)
        yearConfig = {
          value: selectedYearValue,
          label: label
        }
        @yearselectConfig.push(yearConfig)
        @__yearsMap[yearConfig.value] = yearConfig

        # Sort the config to put the newly added config in
        # its natural place.
        @__sortConfigObjectsByValue(@yearselectConfig)

    __initMonthObjects: ->
      @monthselectConfig = []
      @__monthsMap = {}

      formatMomentObject = @calendarCoordinator.shownMomentObject.clone().set({
        month: 0
        date: 0
        hour: 0
        minute: 0
        second: 0
      })
      for monthnumber in [0..11]
        label = formatMomentObject.set({
          month: monthnumber
        }).format(@monthFormat)
        monthObject = {
          value: monthnumber
          label: label
        }
        @monthselectConfig.push(monthObject)
        @__monthsMap[monthnumber] = monthObject

    __initHourObjects: ->
      selectedHourValue = @calendarCoordinator.shownMomentObject.hour()
      hasSelectedHourValue = false
      formatMomentObject = @calendarCoordinator.shownMomentObject.clone().set({
        minute: 0
        second: 0
      })
      @__hoursMap = {}
      @hourselectConfig = []
      for hour in @hourselectValues
        label = formatMomentObject.set({
          hour: hour
        }).format(@hourFormat)
        hourConfig = {
          value: hour
          label: label
        }
        @hourselectConfig.push(hourConfig)
        @__hoursMap[hourConfig.value] = hourConfig
        if hourConfig.value == selectedHourValue
          hasSelectedHourValue = true

      if not hasSelectedHourValue
        # Since we do not include all hours in the hourList, we need
        # to handle the case when the given datetimes hour is not in the
        # list. We handle this by adding it to the end of the list.
        label = formatMomentObject.set({
          hour: selectedHourValue
        }).format(@hourFormat)
        hourConfig = {
          value: selectedHourValue,
          label: label
        }
        @hourselectConfig.push(hourConfig)
        @__hoursMap[hourConfig.value] = hourConfig
        @__sortConfigObjectsByValue(@hourselectConfig)

    __initMinuteObjects: ->
      selectedMinuteValue = @calendarCoordinator.shownMomentObject.minute()
      hasSelectedMinuteValue = false
      formatMomentObject = @calendarCoordinator.shownMomentObject.clone().set({
        second: 0
      })
      @__minutesMap = {}
      @minuteselectConfig = []
      for minute in @minuteselectValues
        label = formatMomentObject.set({
          minute: minute
        }).format(@minuteFormat)
        minuteConfig = {
          value: minute
          label: label
        }
        @minuteselectConfig.push(minuteConfig)
        @__minutesMap[minuteConfig.value] = minuteConfig
        if minuteConfig.value == selectedMinuteValue
          hasSelectedMinuteValue = true

      if not hasSelectedMinuteValue
        # Since we do not include all minutes in the minuteList, we need
        # to handle the case when the given datetimes minute is not in the
        # list. We handle this by adding it to the end of the list.
        label = formatMomentObject.set({
          minute: selectedMinuteValue
        }).format(@minuteFormat)
        minuteConfig = {
          value: selectedMinuteValue,
          label: label
        }
        @minuteselectConfig.push(minuteConfig)
        @__minutesMap[minuteConfig.value] = minuteConfig
        @__sortConfigObjectsByValue(@minuteselectConfig)

    __setCurrentYear: ->
      currentYearNumber = @calendarMonth.month.firstDayOfMonth.year()
      @currentYearObject = @__yearsMap[currentYearNumber]
      if not @currentYearObject?
        console?.warn? "The given year, #{currentYearNumber} is not one of the available choices"

    __setCurrentMonth: ->
      currentMonthNumber = @calendarMonth.month.firstDayOfMonth.month()
      @currentMonthObject = @__monthsMap[currentMonthNumber]
      if not @currentMonthObject?
        console?.warn? "The given month number, #{currentMonthNumber} is not one of the available choices"

    __setCurrentHour: ->
      currentHourNumber = @calendarCoordinator.shownMomentObject.hour()
      @currentHourObject = @__hoursMap[currentHourNumber]
      if not @currentHourObject?
        console?.warn? "The given hour, #{currentHourNumber} is not one of the available choices"

    __setCurrentMinute: ->
      currentMinuteNumber = @calendarCoordinator.shownMomentObject.minute()
      @currentMinuteObject = @__minutesMap[currentMinuteNumber]
      if not @currentMinuteObject?
        console?.warn? "The given minute, #{currentMinuteNumber} is not one of the available choices"

    __updateDayObjects: ->
      formatMomentObject = @calendarCoordinator.shownMomentObject.clone().set({
        hour: 0
        minute: 0
        second: 0
      })
      @dayobjects = []
      for daynumber in [1..@calendarMonth.month.getDaysInMonth()]
        label = formatMomentObject.set({
          date: daynumber
        }).format(@dayOfMonthSelectFormat)
        dayNumberObject = {
          value: daynumber
          label: label
        }
        @dayobjects.push(dayNumberObject)

    ###
    Change month to the month containing the given momentObject,
    and select the date.

    As long as you change ``@calendarCoordinator.shownMomentObject``, this
    will update everything to mirror the change (selected day, month, year, ...).
    ###
    __changeSelectedDate: ->
      @calendarMonth = new CalendarMonth(@calendarCoordinator, @calendarCoordinator.shownMomentObject)
      @__setCurrentYear()
      @__setCurrentMonth()
      @__setCurrentHour()
      @__setCurrentMinute()
      @__updateDayObjects()
      @currentDayObject = @dayobjects[@calendarCoordinator.shownMomentObject.date()-1]

    handleDayChange: (momentObject) ->
      @calendarCoordinator.shownMomentObject = momentObject.clone().set({
        hour: @currentHourObject.value
        minute: @currentMinuteObject.value
      })
      @__changeSelectedDate()

    handleCurrentDayObjectChange: ->
      momentObject = moment({
        year: @currentYearObject.value
        month: @currentMonthObject.value
        day: @currentDayObject.value
      })
      @handleDayChange(momentObject)

    handleCalendarDayChange: (calendarDay) ->
      @handleDayChange(calendarDay.momentObject)

    handleCurrentMonthChange: ->
      @calendarCoordinator.shownMomentObject.set({
        month: @currentMonthObject.value
      })
      @__changeSelectedDate()

    handleCurrentYearChange: ->
      @calendarCoordinator.shownMomentObject.set({
        year: @currentYearObject.value
      })
      @__changeSelectedDate()

    handleCurrentHourChange: ->
      @calendarCoordinator.shownMomentObject.set({
        hour: @currentHourObject.value
      })
      @__changeSelectedDate()

    handleCurrentMinuteChange: ->
      @calendarCoordinator.shownMomentObject.set({
        minute: @currentMinuteObject.value
      })
      @__changeSelectedDate()

    handleFocusOnCalendarDay: (calendarDay) ->
      @lastFocusedMomentObject = calendarDay.momentObject

    getLastFocusedMomentObject: ->
      if @lastFocusedMomentObject?
        return @lastFocusedMomentObject
      else
        return @calendarCoordinator.shownMomentObject

    getDayOfMonthLabelForTableCell: (calendarDay) ->
      return calendarDay.momentObject.format(@dayOfMonthTableCellFormat)

    setToToday: ->
      @handleDayChange(@calendarCoordinator.nowMomentObject.clone())


  @$get = ->
    return {
      MonthlyCalendarCoordinator: MonthlyCalendarCoordinator
      CalendarCoordinator: CalendarCoordinator
    }

  return @
