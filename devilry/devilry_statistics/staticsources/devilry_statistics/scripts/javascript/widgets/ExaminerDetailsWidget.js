import Chart from 'chart.js'
import AbstractWidget from 'ievv_jsbase/lib/widget/AbstractWidget'
import HttpRequest from 'ievv_jsbase/lib/http/HttpRequest'
import HtmlParser from "ievv_jsbase/lib/dom/HtmlParser";

export default class ExaminerDetailsWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId)
    this.loading_label = this.config.loading_label
    this.chartLabel = this.config.chart_label
    this.assignmentMaxPoints = this.config.assignment_max_points
    this.groups_corrected_count_label = this.config.groups_corrected_count_label
    this.groups_with_passing_grade_count_label = this.config.groups_with_passing_grade_count_label
    this.groups_with_failing_grade_count_label = this.config.groups_with_failing_grade_count_label
    this.groups_waiting_for_feedback_count_label = this.config.groups_waiting_for_feedback_count_label
    this.groups_waiting_for_deadline_to_expire_count_label = this.config.groups_waiting_for_deadline_to_expire_count_label
    this.points_label = this.config.points_label
    this.points_average_label = this.config.points_average_label
    this.points_highest_label = this.config.points_highest_label
    this.points_lowest_label = this.config.points_lowest_label

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
      <div class="col-sm-6"></div>
    `)
    let colRight = new HtmlParser(`
      <div class="col-sm-6"></div>
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
    const groups_corrected_count = examinerDetails.groups_corrected_count
    const groups_with_passing_grade_count = examinerDetails.groups_with_passing_grade_count
    const groups_with_failing_grade_count = examinerDetails.groups_with_failing_grade_count
    const groups_waiting_for_feedback_count = examinerDetails.groups_waiting_for_feedback_count
    const groups_waiting_for_deadline_to_expire_count = examinerDetails.groups_waiting_for_deadline_to_expire_count
    const points_average = examinerDetails.points_average
    const points_highest = examinerDetails.points_highest
    const points_lowest = examinerDetails.points_lowest

    let dataParser = new HtmlParser(`
      <div>
        <h2>${examinerDetails.user_name}</h2>

        <p class="paragraph--nomargin"><strong>${this.groups_corrected_count_label}</strong></p>
        <p>${groups_corrected_count}/${totalGroupCount}</p>

        <p class="paragraph--nomargin"><strong>${this.groups_with_passing_grade_count_label}</strong></p>
        <p>${groups_with_passing_grade_count}/${totalGroupCount}</p>

        <p class="paragraph--nomargin"><strong>${this.groups_with_failing_grade_count_label}</strong></p>
        <p>${groups_with_failing_grade_count}/${totalGroupCount}</p>

        <p class="paragraph--nomargin"><strong>${this.groups_waiting_for_feedback_count_label}</strong></p>
        <p>${groups_waiting_for_feedback_count}/${totalGroupCount}</p>

        <p class="paragraph--nomargin"><strong>${this.groups_waiting_for_deadline_to_expire_count_label}</strong></p>
        <p>${groups_waiting_for_deadline_to_expire_count}/${totalGroupCount}</p>

        <p class="paragraph--nomargin"><strong>${this.points_label}</strong></p>
        <p>
            ${this.points_average_label}: ${points_average}
            (${this.points_highest_label}: ${points_highest}, ${this.points_lowest_label}: ${points_lowest})
        </p>
      </div>
    `)

    let chartParser = new HtmlParser(`
      <canvas width="400" height="400"></canvas>
    `)
    const chartRootElement = chartParser.firstRootElement

    const rowRootElement = this._buildRowLayout(dataParser.firstRootElement, chartRootElement)
    this.element.appendChild(rowRootElement)

    new Chart(chartRootElement, {
      type: 'pie',
      data: {
        labels: [
          this.groups_with_passing_grade_count_label,
          this.groups_with_failing_grade_count_label,
          this.groups_waiting_for_feedback_count_label
        ],
        datasets: [{
          data: [
            groups_with_passing_grade_count,
            groups_with_failing_grade_count,
            groups_waiting_for_feedback_count
          ],
          backgroundColor: [
            'rgba(187, 241, 166, 1)',
            'rgba(232, 139, 139, 1)',
            'rgba(214, 214, 214, 1)'
          ]
        }]
      },
      options: {
        responsive: false
      }
    })
  }
}
