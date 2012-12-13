/**
 * Extjs translation.
 *
 * See: http://docs.sencha.com/ext-js/4-1/extjs-build/locale/ext-lang-en.js
 */
Ext.onReady(function () {
    var cm = Ext.ClassManager,
        exists = Ext.Function.bind(cm.get, cm);

    if (Ext.Updater) {
        Ext.Updater.defaults.indicatorText = '<div class="loading-indicator">' + gettext('Loading') + ' ...</div>';
    }

//    Ext.define("Ext.locale.en.grid.plugin.DragDrop", {
//        override: "Ext.grid.plugin.DragDrop",
//        dragText: "{0} selected row{1}"
//    });

    // changing the msg text below will affect the LoadMask
    Ext.define("Ext.locale.en.view.AbstractView", {
        override:"Ext.view.AbstractView",
        msg:gettext('Loading') + '...'
    });

    if (Ext.Date) {
        Ext.Date.monthNames = [
            gettext("January"),
            gettext("February"),
            gettext("March"),
            gettext("April"),
            gettext("May"),
            gettext("June"),
            gettext("July"),
            gettext("August"),
            gettext("September"),
            gettext("October"),
            gettext("November"),
            gettext("December")];

        Ext.Date.getShortMonthName = function (month) {
            return Ext.Date.monthNames[month].substring(0, 3);
        };

        Ext.Date.monthNumbers = {
            Jan:0,
            Feb:1,
            Mar:2,
            Apr:3,
            May:4,
            Jun:5,
            Jul:6,
            Aug:7,
            Sep:8,
            Oct:9,
            Nov:10,
            Dec:11
        };

        Ext.Date.getMonthNumber = function (name) {
            return Ext.Date.monthNumbers[name.substring(0, 1).toUpperCase() + name.substring(1, 3).toLowerCase()];
        };

        Ext.Date.dayNames = [
            gettext("Sunday"),
            gettext("Monday"),
            gettext("Tuesday"),
            gettext("Wednesday"),
            gettext("Thursday"),
            gettext("Friday"),
            gettext("Saturday")];

        Ext.Date.getShortDayName = function (day) {
            return Ext.Date.dayNames[day].substring(0, 3);
        };

//        Ext.Date.parseCodes.S.s = "(?:st|nd|rd|th)";
    }

    if (Ext.MessageBox) {
        Ext.MessageBox.buttonText = {
            ok: gettext("OK"),
            cancel: gettext("Cancel"),
            yes: gettext("Yes"),
            no: gettext("No")
        };
    }

    if (exists('Ext.util.Format')) {
        Ext.apply(Ext.util.Format, {
            thousandSeparator: pgettext('thousandSeparator', ','),
            decimalSeparator: pgettext('decimalSeparator', '.'),
            currencySign: pgettext('currencySign', '$'),
            dateFormat: pgettext('extjs date output format', 'Y-m-d')
        });
    }

    Ext.define("Ext.locale.en.picker.Date", {
        override: "Ext.picker.Date",
        todayText: gettext("Today"),
        minText: gettext("This date is before the minimum date"),
        maxText: gettext("This date is after the maximum date"),
        disabledDaysText: "",
        disabledDatesText: "",
        monthNames: Ext.Date.monthNames,
        dayNames: Ext.Date.dayNames,
        nextText: gettext('Next Month (Control+Right)'),
        prevText: gettext('Previous Month (Control+Left)'),
        monthYearText: gettext('Choose a month (Control+Up/Down to move years)'),
        todayTip: pgettext('datepicker todayTip', "{0} (Spacebar)"),
        format: pgettext("extjs date input format", "Y-m-d"),
        startDay: 0
    });

    Ext.define("Ext.locale.en.picker.Month", {
        override:"Ext.picker.Month",
        okText: "&#160;" + gettext('OK') +"&#160;",
        cancelText: gettext("Cancel")
    });

    Ext.define("Ext.locale.en.toolbar.Paging", {
        override:"Ext.PagingToolbar",
        beforePageText: pgettext("beforePageText", "Page"),
        afterPageText: pgettext("afterPageText", "of {0}"),
        firstText: gettext('First Page'),
        prevText: gettext('Previous Page'),
        nextText: gettext('Next Page'),
        lastText: gettext('Last Page'),
        refreshText: gettext('Refresh'),
        displayMsg: gettext('Displaying {0} - {1} of {2}'),
        emptyMsg: gettext('No data to display')
    });

    Ext.define("Ext.locale.en.form.Basic", {
        override: "Ext.form.Basic",
        waitTitle: gettext("Please Wait...")
    });

    Ext.define("Ext.locale.en.form.field.Base", {
        override: "Ext.form.field.Base",
        invalidText: gettext("The value in this field is invalid")
    });

    Ext.define("Ext.locale.en.form.field.Text", {
        override:"Ext.form.field.Text",
        minLengthText: gettext("The minimum length for this field is {0}"),
        maxLengthText: gettext('The maximum length for this field is {0}'),
        blankText: gettext('This field is required'),
        regexText:"",
        emptyText:null
    });

    Ext.define("Ext.locale.en.form.field.Number", {
        override:"Ext.form.field.Number",
        decimalSeparator: pgettext('decimalSeparator', '.'),
        decimalPrecision: 2,
        minText: gettext('The minimum value for this field is {0}'),
        maxText: gettext('The maximum value for this field is {0}'),
        nanText: gettext('{0} is not a valid number')
    });

    Ext.define("Ext.locale.en.form.field.Date", {
        override:"Ext.form.field.Date",
        disabledDaysText: gettext('Disabled'),
        disabledDatesText: gettext('Disabled'),
        minText: gettext('The date in this field must be after {0}'),
        maxText: gettext('The date in this field must be before {0}'),
        invalidText: gettext('{0} is not a valid date - it must be in the format {1}'),
        format: pgettext("extjs date input format", "Y-m-d"),
        altFormats: "Y-m-d"
    });

    Ext.define("Ext.locale.en.form.field.ComboBox", {
        override:"Ext.form.field.ComboBox",
        valueNotFoundText:undefined
    }, function () {
        Ext.apply(Ext.form.field.ComboBox.prototype.defaultListConfig, {
            loadingText: gettext("Loading") + "..."
        });
    });

    if (exists('Ext.form.field.VTypes')) {
        Ext.apply(Ext.form.field.VTypes, {
            emailText: gettext('This field should be an e-mail address in the format "user@example.com"'),
            urlText: gettext('This field should be a URL in the format "http://www.example.com"'),
            alphaText: gettext('This field should only contain letters and _'),
            alphanumText: gettext('This field should only contain letters, numbers and _')
        });
    }

//    Ext.define("Ext.locale.en.form.field.HtmlEditor", {
//        override:"Ext.form.field.HtmlEditor",
//        createLinkText: 'Please enter the URL for the link:'
//    }, function () {
//        Ext.apply(Ext.form.field.HtmlEditor.prototype, {
//            buttonTips:{
//                bold:{
//                    title:'Bold (Ctrl+B)',
//                    text:'Make the selected text bold.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                italic:{
//                    title:'Italic (Ctrl+I)',
//                    text:'Make the selected text italic.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                underline:{
//                    title:'Underline (Ctrl+U)',
//                    text:'Underline the selected text.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                increasefontsize:{
//                    title:'Grow Text',
//                    text:'Increase the font size.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                decreasefontsize:{
//                    title:'Shrink Text',
//                    text:'Decrease the font size.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                backcolor:{
//                    title:'Text Highlight Color',
//                    text:'Change the background color of the selected text.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                forecolor:{
//                    title:'Font Color',
//                    text:'Change the color of the selected text.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                justifyleft:{
//                    title:'Align Text Left',
//                    text:'Align text to the left.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                justifycenter:{
//                    title:'Center Text',
//                    text:'Center text in the editor.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                justifyright:{
//                    title:'Align Text Right',
//                    text:'Align text to the right.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                insertunorderedlist:{
//                    title:'Bullet List',
//                    text:'Start a bulleted list.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                insertorderedlist:{
//                    title:'Numbered List',
//                    text:'Start a numbered list.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                createlink:{
//                    title:'Hyperlink',
//                    text:'Make the selected text a hyperlink.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                },
//                sourceedit:{
//                    title:'Source Edit',
//                    text:'Switch to source editing mode.',
//                    cls:Ext.baseCSSPrefix + 'html-editor-tip'
//                }
//            }
//        });
//    });

    Ext.define("Ext.locale.en.grid.header.Container", {
        override:"Ext.grid.header.Container",
        sortAscText: gettext('Sort Ascending'),
        sortDescText: gettext('Sort Descending'),
        columnsText: gettext('Columns')
    });

    Ext.define("Ext.locale.en.grid.GroupingFeature", {
        override:"Ext.grid.GroupingFeature",
        emptyGroupText: gettext('(None)'),
        groupByText: gettext('Group By This Field'),
        showGroupsText: gettext('Show in Groups')
    });

    Ext.define("Ext.locale.en.grid.PropertyColumnModel", {
        override:"Ext.grid.PropertyColumnModel",
        nameText: gettext('Name'),
        valueText: gettext('Value'),
        dateFormat: pgettext("extjs date input format", "Y-m-d"),
        trueText: gettext('true'),
        falseText: gettext('false')
    });

    Ext.define("Ext.locale.en.grid.BooleanColumn", {
        override:"Ext.grid.BooleanColumn",
        trueText: gettext("true"),
        falseText: gettext("false"),
        undefinedText:'&#160;'
    });

    Ext.define("Ext.locale.en.grid.NumberColumn", {
        override:"Ext.grid.NumberColumn",
        format: pgettext('extjs number format', '0,000.00')
    });

    Ext.define("Ext.locale.en.grid.DateColumn", {
        override:"Ext.grid.DateColumn",
        format: pgettext('extjs date output format', 'Y-m-d')
    });

    Ext.define("Ext.locale.en.form.field.Time", {
        override:"Ext.form.field.Time",
        minText:"The time in this field must be equal to or after {0}",
        maxText:"The time in this field must be equal to or before {0}",
        invalidText:"{0} is not a valid time",
        format:"H:i",
        altFormats:"H"
    });

    Ext.define("Ext.locale.en.form.CheckboxGroup", {
        override:"Ext.form.CheckboxGroup",
        blankText: gettext("You must select at least one item in this group")
    });

    Ext.define("Ext.locale.en.form.RadioGroup", {
        override:"Ext.form.RadioGroup",
        blankText: gettext("You must select one item in this group")
    });
});