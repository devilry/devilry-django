import Chart from 'chart.js'
import AbstractWidget from 'ievv_jsbase/lib/widget/AbstractWidget'
import HttpRequest from 'ievv_jsbase/lib/http/HttpRequest'
import HtmlParser from "ievv_jsbase/lib/dom/HtmlParser";

export default class ExaminerDetailsWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId)
    this.loadingLabel = this.config.loading_label
    this.groupsCorrectedCountLabel = this.config.groups_corrected_count_label
    this.groupsWithPassingGradeCountLabel = this.config.groups_with_passing_grade_count_label
    this.groupsWithFailingGradeCountLabel = this.config.groups_with_failing_grade_count_label
    this.groupsWaitingForFeedbackCountLabel = this.config.groups_waiting_for_feedback_count_label
    this.groupsWaitingForDeadlineToExpireCountLabel = this.config.groups_waiting_for_deadline_to_expire_count_label
    this.pointsLabel = this.config.points_label
    this.pointsAverageLabel = this.config.points_average_label
    this.pointsHighestLabel = this.config.points_highest_label
    this.pointsLowestLabel = this.config.points_lowest_label

    // Fetch data from API
    this.requestData()

    // Set loading text.
    let parser = new HtmlParser(`
      <p>${this.loading_label} ...</p>
    `)
    this.element.appendChild(parser.firstRootElement)
  }

  requestData () {
    const assignment_id = this.config.assignment_id
    const relatedexaminer_ids = this.config.relatedexaminer_ids
    let promises = []
    for (let relatedexaminer_id of relatedexaminer_ids) {
      let request = new HttpRequest(`/devilry_statistics/assignment/examiner-details/${assignment_id}/${relatedexaminer_id}`)
      promises.push(request.get())
    }

    Promise.all(promises)
      .then((promiseData) => {
        this.element.innerHTML = ''
        Object.entries(promiseData).forEach(([key, response]) => {
          let responseData = JSON.parse(response.body)
          this._addExaminerDetail(responseData)
        })
        this.isLoading = false
      })
      .catch((error) => {
        console.error('Error:', error.toString());
      })
  }

  _buildRowLayout (leftRootElement, rightRootElement) {
    let colLeft = new HtmlParser(`
      <div class="col-sm-7 col-md-8"></div>
    `)
    let colRight = new HtmlParser(`
      <div class="col-sm-5 col-md-4"></div>
    `)
    let row = new HtmlParser(`
      <div class="row" style="margin-top: 100px;"></div>
    `)
    colLeft.firstRootElement.appendChild(leftRootElement)
    colRight.firstRootElement.appendChild(rightRootElement)
    row.firstRootElement.appendChild(colLeft.firstRootElement)
    row.firstRootElement.appendChild(colRight.firstRootElement)
    return row.firstRootElement
  }

  _addExaminerDetail (examinerDetails) {
    const totalGroupCount = examinerDetails.total_group_count
    const groupsCorrectedCount = examinerDetails.groups_corrected_count
    const groupsWithPassingGradeCount = examinerDetails.groups_with_passing_grade_count
    const groupsWithFailingGradeCount = examinerDetails.groups_with_failing_grade_count
    const groupsWaitingForFeedbackCount = examinerDetails.groups_waiting_for_feedback_count
    const groupsWaitingForDeadlineToExpireCount = examinerDetails.groups_waiting_for_deadline_to_expire_count
    const pointsAverage = examinerDetails.points_average
    const pointsHighest = examinerDetails.points_highest
    const pointsLowest = examinerDetails.points_lowest

    let dataParser = new HtmlParser(`
      <div>
        <h2>${examinerDetails.user_name}</h2>

        <p class="paragraph--nomargin"><strong>${this.groupsCorrectedCountLabel}</strong></p>
        <p>${groupsCorrectedCount}/${totalGroupCount}</p>

        <p class="paragraph--nomargin"><strong>${this.groupsWithPassingGradeCountLabel}</strong></p>
        <p>${groupsWithPassingGradeCount}/${totalGroupCount}</p>

        <p class="paragraph--nomargin"><strong>${this.groupsWithFailingGradeCountLabel}</strong></p>
        <p>${groupsWithFailingGradeCount}/${totalGroupCount}</p>
        
        <p class="paragraph--nomargin"><strong>${this.groupsWaitingForFeedbackCountLabel}</strong></p>
        <p>${groupsWaitingForFeedbackCount}/${totalGroupCount}</p>

        <p class="paragraph--nomargin"><strong>${this.groupsWaitingForDeadlineToExpireCountLabel}</strong></p>
        <p>${groupsWaitingForDeadlineToExpireCount}/${totalGroupCount}</p>

        <p class="paragraph--nomargin"><strong>${this.pointsLabel}</strong></p>
        <p>
            ${this.pointsAverageLabel}: ${pointsAverage}
            (${this.pointsHighestLabel}: ${pointsHighest}, ${this.pointsLowestLabel}: ${pointsLowest})
        </p>
      </div>
    `)

    let chartParser = new HtmlParser(`
      <canvas width="400" height="400" style="max-width: 450px;"></canvas>
    `)
    const chartRootElement = chartParser.firstRootElement

    const rowRootElement = this._buildRowLayout(dataParser.firstRootElement, chartRootElement)
    this.element.appendChild(rowRootElement)

    new Chart(chartRootElement, {
      type: 'pie',
      data: {
        labels: [
          this.groupsWithPassingGradeCountLabel,
          this.groupsWithFailingGradeCountLabel,
          this.groupsWaitingForFeedbackCountLabel,
          this.groupsWaitingForDeadlineToExpireCountLabel
        ],
        datasets: [{
          data: [
            groupsWithPassingGradeCount,
            groupsWithFailingGradeCount,
            groupsWaitingForFeedbackCount,
            groupsWaitingForDeadlineToExpireCount
          ],
          backgroundColor: [
            '#5AA221',
            '#a0372f',
            '#d6d6d6',
            '#474747'
          ]
        }]
      }
    })
  }
}
