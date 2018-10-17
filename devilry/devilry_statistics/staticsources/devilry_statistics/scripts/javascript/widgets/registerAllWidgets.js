import WidgetRegistrySingleton from "ievv_jsbase/lib/widget/WidgetRegistrySingleton"
import ExaminerAverageGradingPointsWidget from './ExaminerAverageGradingPointsWidget'
import ExaminerGroupResultWidget from './ExaminerGroupResultWidget'
import ExaminerDetailsWidget from './ExaminerDetailsWidget'

/**
 * Register all the statistics widgets in the ievv_jsbase WidgetRegistrySingleton.
 */
export default function registerAllWidgets() {
  const widgetRegistry = new WidgetRegistrySingleton()
  widgetRegistry.registerWidgetClass('examiner-average-grading-points', ExaminerAverageGradingPointsWidget)
  widgetRegistry.registerWidgetClass('examiner-group-results', ExaminerGroupResultWidget)
  widgetRegistry.registerWidgetClass('examiner-details', ExaminerDetailsWidget)
}
