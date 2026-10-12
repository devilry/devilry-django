app = angular.module 'cradminLegacy.forms.datetimewidget', ['cfp.hotkeys']

#app.config (hotkeysProvider) ->
#  hotkeysProvider.includeCheatSheet = false

app.directive 'cradminLegacyDatetimeSelector', [
  '$timeout', '$compile', '$rootScope', 'hotkeys', 'cradminLegacyCalendarApi', 'cradminLegacyWindowDimensions'
  ($timeout, $compile, $rootScope, hotkeys, cradminLegacyCalendarApi, cradminLegacyWindowDimensions) ->

    return {
      scope: {
        config: "=cradminLegacyDatetimeSelector"
      }
      templateUrl: 'forms/dateselector.tpl.html'

      controller: ($scope, $element) ->
        $scope.page = null

        ###
        Handles keyboard navigation.
        ###
        $scope.__keyboardNavigation = (event, direction) ->
          if direction == 'pageup' or direction == 'pagedown'
            event.preventDefault()
          if $element.find('.cradmin-legacy-datetime-selector-table').is(':visible')
            activeElement = angular.element(document.activeElement)
            if activeElement.hasClass('cradmin-legacy-datetime-selector-daybuttoncell-button')
              event.preventDefault()

              if direction == 'right'
                nextSibling = activeElement.parent().next()
                if nextSibling.length > 0
                  newFocusTd = nextSibling
              if direction == 'left'
                previousSibling = activeElement.parent().prev()
                if previousSibling.length > 0
                  newFocusTd = previousSibling
              if direction == 'up'
                previousTr = activeElement.parent().parent().prev()
                if previousTr.length > 0
                  newFocusTd = angular.element(previousTr.children().get(activeElement.parent().index()))
              if direction == 'down'
                nextTr = activeElement.parent().parent().next()
                if nextTr.length > 0
                  newFocusTd = angular.element(nextTr.children().get(activeElement.parent().index()))
              if newFocusTd? and newFocusTd.length > 0
                newFocusTd.find('button').focus()


              if direction == 'home'
                activeElement.parent().parent().parent().find('button:enabled').first().focus()
              if direction == 'end'
                activeElement.parent().parent().parent().find('button:enabled').last().focus()

              if direction == 'pageup'
                $element.find('.cradmin-legacy-datetime-selector-monthselect').focus()

            else if direction == 'pagedown'
              if activeElement.parent().hasClass('cradmin-legacy-datetime-selector-dateselectors')
                lastFocusedElement = $element.find('.cradmin-legacy-datetime-selector-daybuttoncell-lastfocused button')
                if lastFocusedElement.is(':visible')
                  lastFocusedElement.focus()
                else
                  angular.element(
                    $element.find('.cradmin-legacy-datetime-selector-daybuttoncell-in-current-month button').first()
                  ).focus()

        ###
        Called when enter is pressed in any of the select fields.

        If we have a visible use-button, we do the same as if the user
        pressed that. If we are on page1, on desktop (no use-button),
        we move the focus into the first day of the current month
        in the day select table, or to the selected day if that is visible.
        ###
        $scope.__onSelectEnterPressed = ->
          if $scope.page == 1
            useButton = $element.find('.cradmin-legacy-datetime-selector-dateview ' +
              '.cradmin-legacy-datetime-selector-use-button')
            if useButton.is(":visible")
              $scope.onClickUseTime()
            else
              tableElement = $element.find('.cradmin-legacy-datetime-selector-table')
              selectedButton = tableElement.find('.cradmin-legacy-datetime-selector-daybuttoncell-selected button')
              if selectedButton.length > 0
                selectedButton.focus()
              else
                tableElement.find(
                  '.cradmin-legacy-datetime-selector-daybuttoncell-in-current-month button').first().focus()
          else if $scope.page == 2
            $scope.onClickUseTime()

        ###
        Returns the item we want to focus on when we tab forward from the last
        focusable item on the current page.
        ###
        __getFirstFocusableItemInCurrentPage = ->
          if $scope.page == 1
            return $element.find('.cradmin-legacy-datetime-selector-dateview ' +
                '.cradmin-legacy-datetime-selector-closebutton')
          else if $scope.page == 2
            return $element.find('.cradmin-legacy-datetime-selector-timeview ' +
                '.cradmin-legacy-datetime-selector-closebutton')

        ###
        Returns the item we want to focus on when we tab back from the first
        focusable item on the current page.
        ###
        __getLastFocusableItemInCurrentPage = ->
          if $scope.page == 1
            useButton = $element.find('.cradmin-legacy-datetime-selector-dateview ' +
              '.cradmin-legacy-datetime-selector-use-button')
            if useButton.is(":visible")
              return useButton
            else
              return $element.find('.cradmin-legacy-datetime-selector-table ' +
                  'td.cradmin-legacy-datetime-selector-daybuttoncell-in-current-month button').last()
          else if $scope.page == 2
            return $element.find('.cradmin-legacy-datetime-selector-timeview ' +
              '.cradmin-legacy-datetime-selector-use-button')

        ###
        Get the initial item to focus on when we open/show a page.
        ###
        __getInitialFocusItemForCurrentPage = ->
          if $scope.page == 1
            dayselectElement = $element.find('.cradmin-legacy-datetime-selector-dayselect')
            if dayselectElement.is(':visible')
              return dayselectElement
            else
              return $element.find('.cradmin-legacy-datetime-selector-monthselect')
          else if $scope.page == 2
            return $element.find('.cradmin-legacy-datetime-selector-timeview ' +
                '.cradmin-legacy-datetime-selector-hourselect')

        ###
        Get the item to focus on when we close the datetime picker.
        ###
        __getFocusItemAfterHide = ->
          return $scope.triggerButton

        ###
        Triggered when the user focuses on the hidden (sr-only) button we have
        added to the start of the datetime-selector div.
        ###
        $scope.onFocusHead = ->
          if $scope.page != null
            __getLastFocusableItemInCurrentPage().focus()
          return

        ###
        Triggered when the user focuses on the hidden (sr-only) button we have
        added to the end of the datetime-selector div.
        ###
        $scope.onFocusTail = ->
          if $scope.page != null
            __getFirstFocusableItemInCurrentPage().focus()
          return

        ###
        Called when a users selects a date using the mobile-only <select>
        menu to select a day.
        ###
        $scope.onSelectDayNumber = ->
          $scope.monthlyCalendarCoordinator.handleCurrentDayObjectChange()
          return

        ###
        Called when a user selects a date by clicking on a day
        in the calendar table.
        ###
        $scope.onClickCalendarDay = (calendarDay) ->
          $scope.monthlyCalendarCoordinator.handleCalendarDayChange(calendarDay)
          if $scope.config.include_time
            $scope.showPage2()
          else
            $scope.__useShownValue()
          return

        ###
        Called when a users focuses a date in the calendar table.
        ###
        $scope.onFocusCalendayDay = (calendarDay) ->
          $scope.monthlyCalendarCoordinator.handleFocusOnCalendarDay(calendarDay)
          return

        ###
        Called when a users selects a month using the month <select>
        menu.
        ###
        $scope.onSelectMonth = ->
          $scope.monthlyCalendarCoordinator.handleCurrentMonthChange()
          return

        ###
        Called when a users selects a year using the year <select>
        menu.
        ###
        $scope.onSelectYear = ->
          $scope.monthlyCalendarCoordinator.handleCurrentYearChange()
          return

        ###
        Called when a users selects an hour using the hour <select>
        menu.
        ###
        $scope.onSelectHour = ->
          $scope.monthlyCalendarCoordinator.handleCurrentHourChange()
          return

        ###
        Called when a users selects a minute using the minute <select>
        menu.
        ###
        $scope.onSelectMinute = ->
          $scope.monthlyCalendarCoordinator.handleCurrentMinuteChange()
          return

        ###
        Called when a user clicks the "Use" button on the time page.
        ###
        $scope.onClickUseTime = ->
          $scope.__useShownValue()
          return

        ###
        Used to get the preview of the selected date on page2 (above the time selector).
        ###
        $scope.getTimeselectorDatepreview = ->
          return $scope.calendarCoordinator.shownMomentObject.format(
            $scope.config.timeselector_datepreview_momentjs_format
          )

        ###
        This is used to get the aria-label attribute for the "Use" button.
        ###
        $scope.getUseButtonAriaLabel = ->
          if $scope.monthlyCalendarCoordinator?
            formattedDate = $scope.calendarCoordinator.shownMomentObject.format(
              $scope.config.usebutton_arialabel_momentjs_format)
            return "#{$scope.config.usebutton_arialabel_prefix} " +
              "#{formattedDate}"
          else
          return ''

        ###
        Get day-button (button in the calendar table) aria-label attribute.
        ###
        $scope.getDaybuttonAriaLabel = (calendarDay) ->
          label = "#{calendarDay.momentObject.format('MMMM D')}"
          if $scope.config.today_label_text != '' and calendarDay.isToday()
            label = "#{label} (#{$scope.config.today_label_text})"
          else
            isSelected = calendarDay.momentObject.isSame(
              $scope.calendarCoordinator.selectedMomentObject, 'day')
            if $scope.config.selected_day_label_text != '' and isSelected
              label = "#{label} (#{$scope.config.selected_day_label_text})"
          return label

        ###
        Returns ``true`` if we have any buttons in the buttonrow.
        ###
        $scope.hasShortcuts = ->
          if $scope.calendarCoordinator.nowIsValidValue()
            return true
          else if not $scope.config.required
            return true
          else
            return false

        $scope.onClickTodayButton = ->
          $scope.monthlyCalendarCoordinator.setToToday()
          if $scope.config.include_time
            $scope.showPage2()
          else
            $scope.__useShownValue()
          return

        $scope.onClickNowButton = ->
          $scope.calendarCoordinator.setToNow()
          $scope.__useShownValue()

        $scope.onClickClearButton = ->
          $scope.__clearSelectedValue()

        $scope.getTabindexForCalendarDay = (calendarDay) ->
          if calendarDay.isInCurrentMonth
            return "0"
          else
          return "-1"

        ###
        Update the preview text to reflect the selected value.
        ###
        $scope.__updatePreviewText = ->
          if $scope.calendarCoordinator.selectedMomentObject?
            templateScope = $rootScope.$new(true)  # Create new isolated scope
            # NOTE: We must clone the object, if we do not clone it, the value
            # will be reflected in the preview each time we change any value
            # in the date picker, and we only want the value to be applied when
            # the user confirms a value.
            templateScope.momentObject = $scope.calendarCoordinator.selectedMomentObject.clone()
            preview = $compile($scope.previewAngularjsTemplate)(templateScope)
            $scope.previewElement.empty()
            $scope.previewElement.append(preview)
            $scope.previewElement.show()
          else
            if $scope.config.no_value_preview_text? and $scope.config.no_value_preview_text != ''
              $scope.previewElement.html($scope.config.no_value_preview_text)
              $scope.previewElement.show()
            else
              $scope.previewElement.hide()

        ###
        Apply a css animation to indicate that the preview text has
        changed.

        The ``delay_milliseconds`` parameter is the number of milliseonds
        to delay starting the animation.
        ###
        $scope.__animatePreviewText = (delay_milliseconds) ->
          if $scope.config.preview_change_animation_cssclass?
            $scope.previewElement.addClass($scope.config.preview_change_animation_cssclass)
            $timeout(->
              $timeout(->
                $scope.previewElement.removeClass($scope.config.preview_change_animation_cssclass)

                # Tricks the browser into restarting the animation
                # the next time we add the class. Without this,
                # the animation would just run the first time
                # we add the class.
                # See: https://css-tricks.com/restart-css-animation/
                $scope.previewElement.first().offsetWidth = $scope.previewElement.first().offsetWidth
              , $scope.config.preview_change_animation_duration_milliseconds)
            , delay_milliseconds)

        ###
        Update the trigger button label to reflect the selected value.
        ###
        $scope.__updateTriggerButtonLabel = ->
          if $scope.calendarCoordinator.selectedMomentObject?
            label = $scope.config.buttonlabel
          else
            label = $scope.config.buttonlabel_novalue
          $scope.triggerButton.html(label)

        ###
        Update the value of the destination field to reflect the selected value.
        ###
        $scope.__updateDestinationFieldValue = ->
          if $scope.calendarCoordinator.selectedMomentObject?
            destinationFieldValue = $scope.calendarCoordinator.selectedMomentObject.format(
              $scope.config.destinationfield_momentjs_format
            )
          else
            destinationFieldValue = ''
          $scope.destinationField.val(destinationFieldValue)

        ###
        Update destination field value, preview text and trigger button label,
        and hide the datetime selector.
        ###
        $scope.__hideWithSelectedValueApplied = ->
          $scope.__updateDestinationFieldValue()
          $scope.__updatePreviewText()
          $scope.__updateTriggerButtonLabel()
          $scope.hide()
#          $scope.__animatePreviewText($scope.config.hide_animation_duration_milliseconds)

        ###
        Make the shown value the selected value and call
        ``$scope.__hideWithSelectedValueApplied()``.
        ###
        $scope.__useShownValue = ->
          $scope.calendarCoordinator.selectShownValue()
          $scope.__hideWithSelectedValueApplied()

        ###
        Clear the selected value and call ``$scope.__hideWithSelectedValueApplied()``.
        ###
        $scope.__clearSelectedValue = ->
          $scope.calendarCoordinator.clearSelectedMomentObject()
          $scope.__hideWithSelectedValueApplied()

        __addCommonHotkeys = ->
          hotkeys.add({
            combo: 'esc'
            callback: (event) ->
              $scope.hide()
            allowIn: ['BUTTON', 'SELECT', 'INPUT']
          })
          hotkeys.add({
            combo: 'up'
            callback: (event) ->
              $scope.__keyboardNavigation(event, 'up')
          })
          hotkeys.add({
            combo: 'down'
            callback: (event) ->
              $scope.__keyboardNavigation(event, 'down')
          })
          hotkeys.add({
            combo: 'left'
            callback: (event) ->
              $scope.__keyboardNavigation(event, 'left')
          })
          hotkeys.add({
            combo: 'right'
            callback: (event) ->
              $scope.__keyboardNavigation(event, 'right')
          })
          hotkeys.add({
            combo: 'home'
            callback: (event) ->
              $scope.__keyboardNavigation(event, 'home')
          })
          hotkeys.add({
            combo: 'end'
            callback: (event) ->
              $scope.__keyboardNavigation(event, 'end')
          })
          hotkeys.add({
            combo: 'pagedown'
            allowIn: ['BUTTON', 'SELECT', 'INPUT']
            callback: (event) ->
              $scope.__keyboardNavigation(event, 'pagedown')
          })
          hotkeys.add({
            combo: 'pageup'
            allowIn: ['BUTTON', 'SELECT', 'INPUT', 'BUTTON']
            callback: (event) ->
              $scope.__keyboardNavigation(event, 'pageup')
          })

        __addPage1Hotkeys = ->

        __removeHotkeys = ->
          hotkeys.del('esc')
          hotkeys.del('up')
          hotkeys.del('down')
          hotkeys.del('left')
          hotkeys.del('right')
          hotkeys.del('home')
          hotkeys.del('end')
          hotkeys.del('pagedown')
          hotkeys.del('pageup')

        $scope.__onMouseWheel = (e) ->
          e.preventDefault()
          e.stopPropagation()

        $scope.__adjustPosition = ->
          contentWrapperElement = $element.find('.cradmin-legacy-datetime-selector-contentwrapper')
          scrollTop = angular.element(window).scrollTop()
          windowHeight = angular.element(window).height()
          $scope.datetimeSelectorElement.css({
            top: scrollTop,
            height: "#{windowHeight}px"
          })

        $scope.onWindowResize = ->
          $scope.__adjustPosition()

        $scope.__show = ->
#          angular.element('body').addClass('cradmin-legacy-noscroll')
          __removeHotkeys()
          __addCommonHotkeys()
          $scope.__adjustPosition()

        $scope.showPage1 = ->
          angular.element('body').on 'mousewheel touchmove', $scope.__onMouseWheel
          $scope.page = 1

          # Use a timeout to ensure screenreaders are not stuck on the
          # last focused element.
          $timeout(->
            __getInitialFocusItemForCurrentPage().focus()
          , 150)

          $scope.__show()
          __addPage1Hotkeys()
          return

        $scope.showPage2 = ->
          $scope.page = 2

          # Update "selectedMomentObject" to reflect the change. This will mark this as
          # the selected value when we return from to page2.
          $scope.calendarCoordinator.selectShownValue()

          # Use a timeout to ensure screenreaders are not stuck on the
          # last focused element.
          $timeout(->
            __getInitialFocusItemForCurrentPage().focus()
          , 150)

          $scope.__show()
          return

        $scope.hide = ->
          angular.element('body').off 'mousewheel touchmove', $scope.__onMouseWheel
#          angular.element('body').removeClass('cradmin-legacy-noscroll')
          if $scope.page == 2
            # We use page3 to make it possible to have a custom animation for hiding
            # page2 (avoid that it animates sideways back to the starting point).
            $scope.page = 3
            $timeout(->
              $scope.page = null
            , $scope.config.hide_animation_duration_milliseconds)
          else
            $scope.page = null

          __removeHotkeys()

          # Apply preview animation after the box has been hidden.
          $timeout(->
            $scope.__animatePreviewText()
          , $scope.config.hide_animation_duration_milliseconds)

          # Use a timeout to ensure screenreaders are not stuck on the
          # last focused element.
          $timeout(->
            __getFocusItemAfterHide().focus()
          , 150)

          return

        $scope.initialize = ->
          currentDateIsoString = $scope.destinationField.val()
          if currentDateIsoString? and currentDateIsoString != ''
            selectedMomentObject = moment(currentDateIsoString)
            $scope.triggerButton.html($scope.config.buttonlabel)
          else
            selectedMomentObject = null
            $scope.triggerButton.html($scope.config.buttonlabel_novalue)

          minimumDatetime = null
          maximumDatetime = null
          if $scope.config.minimum_datetime?
            minimumDatetime = moment($scope.config.minimum_datetime)
          if $scope.config.maximum_datetime?
            maximumDatetime = moment($scope.config.maximum_datetime)

          $scope.calendarCoordinator = new cradminLegacyCalendarApi.CalendarCoordinator({
            selectedMomentObject: selectedMomentObject,
            minimumDatetime: minimumDatetime,
            maximumDatetime: maximumDatetime,
            defaultNowTime: $scope.config.default_now_time,
            nowMomentObject: moment($scope.config.now)
          })
          $scope.monthlyCalendarCoordinator = new cradminLegacyCalendarApi.MonthlyCalendarCoordinator({
            calendarCoordinator: $scope.calendarCoordinator
            yearselectValues: $scope.config.yearselect_values
            hourselectValues: $scope.config.hourselect_values
            minuteselectValues: $scope.config.minuteselect_values
            yearFormat: $scope.config.yearselect_momentjs_format
            monthFormat: $scope.config.monthselect_momentjs_format
            dayOfMonthSelectFormat: $scope.config.dayofmonthselect_momentjs_format
            dayOfMonthTableCellFormat: $scope.config.dayofmonthtablecell_momentjs_format
            hourFormat: $scope.config.hourselect_momentjs_format
            minuteFormat: $scope.config.minuteselect_momentjs_format
          })
          $scope.__updatePreviewText()

      link: ($scope, $element) ->
        body = angular.element('body')
        $element.appendTo(body)
        cradminLegacyWindowDimensions.register $scope
        $scope.$on '$destroy', ->
          cradminLegacyWindowDimensions.unregister $scope


        #
        # Validate required config
        #

        if not $scope.config.no_value_preview_text?
          $scope.config.no_value_preview_text = ''

        required_config_attributes = [
          'now'
          'destinationfieldid'
          'triggerbuttonid'
          'previewid'
          'previewtemplateid'
          'required'
          'usebuttonlabel'
          'usebutton_arialabel_prefix'
          'usebutton_arialabel_momentjs_format'
          'close_icon'
          'back_icon'
          'back_to_datepicker_screenreader_text'
          'destinationfield_momentjs_format'
          'timeselector_datepreview_momentjs_format'
          'year_screenreader_text'
          'month_screenreader_text'
          'day_screenreader_text'
          'hour_screenreader_text'
          'minute_screenreader_text'
          'dateselector_table_screenreader_caption'
          'today_label_text'
          'selected_day_label_text'
          'yearselect_values'
          'hourselect_values'
          'yearselect_momentjs_format'
          'monthselect_momentjs_format'
          'dayofmonthselect_momentjs_format'
          'dayofmonthtablecell_momentjs_format'
          'hourselect_momentjs_format'
          'minuteselect_momentjs_format'
          'minuteselect_values'
          'now_button_text'
          'today_button_text'
          'clear_button_text'
          'hide_animation_duration_milliseconds'
#          'date_label_text'
#          'time_label_text'
        ]
        for configname in required_config_attributes
          configvalue = $scope.config[configname]
          if not configvalue? or configvalue == ''
            console?.error? "The #{configname} config is required!"


        #
        # Find the required elements outside the datepicker:
        # - The (hidden) destination field
        # - The button that triggers the widget
        # - The element where we show the preview of the selected date/datetime
        # - The <script> tag containing the AngularJS template used to
        #   create the preview.
        #

        $scope.destinationField = angular.element("#" + $scope.config.destinationfieldid)
        if $scope.destinationField.length == 0
          console?.error? "Could not find the destinationField element with ID: #{$scope.config.destinationfieldid}"

        $scope.triggerButton = angular.element("#" + $scope.config.triggerbuttonid)
        if $scope.triggerButton.length > 0
          $scope.triggerButton.on 'click', ->
            $scope.initialize()
            $scope.showPage1()
            $scope.$apply()
            return
          labelElement = angular.element("label[for=#{$scope.config.destinationfieldid}]")
          if labelElement.length > 0
            if not labelElement.attr('id')
              labelElement.attr('id', "#{$scope.config.destinationfieldid}_label")
            $scope.triggerButton.attr('aria-labeledby', "#{labelElement.attr('id')} #{$scope.config.previewid}")
        else
          console?.warn? "Could not find the triggerButton element with ID: #{$scope.config.triggerbuttonid}"

        $scope.previewElement = angular.element("#" + $scope.config.previewid)
        if $scope.previewElement.length == 0
          console?.warn? "Could not find the previewElement element with ID: #{$scope.config.previewid}"

        previewTemplateScriptElement = angular.element("#" + $scope.config.previewtemplateid)
        if previewTemplateScriptElement.length == 0
          console?.warn? "Could not find the previewTemplateScriptElement element " +
              "with ID: #{$scope.config.previewtemplateid}"
        else
          $scope.previewAngularjsTemplate = previewTemplateScriptElement.html()

        $scope.datetimeSelectorElement = $element.find('.cradmin-legacy-datetime-selector')
        $scope.initialize()

        $scope.destinationField.on 'change', ->
          $scope.initialize()
          $scope.$apply()
          $scope.__animatePreviewText(0)

        # We need this timeout to ensure all the items are rendered.
        # it seems empty selects are not matched or something like that
        # The timeout should not matter unless a user somehow manages to open
        # the datepicker in 100ms (after page load)
        $timeout(->
          $element.find('select').on 'keydown', (e) ->
            if e.which == 13  # 13 is the enter key
              $scope.__onSelectEnterPressed()
              # Prevent form submit when hitting enter on any select in the datepicker
              e.preventDefault()
            return
        , 100)
        return
    }
]
