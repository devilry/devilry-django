import Chart from 'chart.js'
import AbstractWidget from 'ievv_jsbase/lib/widget/AbstractWidget'
import HttpRequest from 'ievv_jsbase/lib/http/HttpRequest'
import HtmlParser from "ievv_jsbase/lib/dom/HtmlParser";

export default class ExaminerAverageGradingPointsWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId)
    this.loading_label = this.config.loading_label
    this.assignmentMaxPoints = this.config.assignment_max_points
    this.chart = null

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
      let request = new HttpRequest(`/devilry_statistics/assignment/examiner-average-points/${assignment_id}/${relatedexaminer_id}`)
      promises.push(request.get())
    }

    Promise.all(promises)
      .then((promiseData) => {
        let labels = []
        let data = []
        Object.entries(promiseData).forEach(([key, response]) => {
          let responseData = JSON.parse(response.body)
          labels.push(responseData.user_name)
          data.push(responseData.average_grading_points_given)
        })
        this.isLoading = false
        this.render(labels, data)
      })
      .catch((error) => {
        console.error('Error:', error.toString());
      })
  }

  getChartOptions () {
    return {
      tooltips: {
        tooltipCaretSize: 0
      },
      scales: {
        xAxes: [{
          ticks: {
            beginAtZero: true,
            max: this.assignmentMaxPoints,
            min: 0
          }
        }]
      }
    }
  }

  render (labelArray, dataArray) {
    let parser = new HtmlParser(`
      <canvas width="400" height="400"></canvas>
    `)
    const rootElement = parser.firstRootElement
    this.element.innerHTML = ''
    this.element.appendChild(rootElement)

    const chartData = {
      labels: labelArray,
      datasets: [{
        label: this.config.chart_label,
        data: dataArray,
        backgroundColor: 'rgba(54, 162, 235, 1)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    }
    const options = this.getChartOptions()
    this.chart = new Chart(rootElement, {
      type: 'horizontalBar',
      data: chartData,
      options: options
    })
  }
}
