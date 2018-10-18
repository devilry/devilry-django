import Chart from 'chart.js'
import AbstractWidget from 'ievv_jsbase/lib/widget/AbstractWidget'
import HttpRequest from 'ievv_jsbase/lib/http/HttpRequest'
import HtmlParser from "ievv_jsbase/lib/dom/HtmlParser";

export default class ExaminerGroupResultWidget extends AbstractWidget {
  constructor(element, widgetInstanceId) {
    super(element, widgetInstanceId)
    this.loading_label = this.config.loading_label
    this.chartLabel = this.config.chart_label
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
      let request = new HttpRequest(`/devilry_statistics/assignment/examiner-group-results/${assignment_id}/${relatedexaminer_id}`)
      promises.push(request.get())
    }

    Promise.all(promises)
      .then((promiseData) => {
        let usernames = []
        let passed = []
        let failed = []
        let notCorrected = []
        Object.entries(promiseData).forEach(([key, response]) => {
          let responseData = JSON.parse(response.body)
          usernames.push(responseData.user_name)
          passed.push(responseData.groups_passed)
          failed.push(responseData.groups_failed)
          notCorrected.push(responseData.groups_not_corrected)
        })
        this.isLoading = false
        this.render(usernames, passed, failed, notCorrected)
      })
      .catch((error) => {
        console.error('Error:', error.toString());
      })
  }

  getChartOptions () {
    return {
      scales: {
        xAxes: [{
          scaleLabel: {
            display: true,
            labelString: this.config.x_axes_label,
          },
          stacked: true,
          ticks: {
            beginAtZero: true,
            max: 100,
            min: 0
          }
        }],
        yAxes: [{
          stacked: true
        }]
      }
    }
  }

  render (usernamesArray, passedArray, failedArray, notCorrectedArray) {
    let parser = new HtmlParser(`
      <canvas width="400" height="400"></canvas>
    `)
    const rootElement = parser.firstRootElement
    this.element.innerHTML = ''
    this.element.appendChild(rootElement)

    const chartData = {
      labels: usernamesArray,
      datasets: [
        {
          label: this.config.passed_label,
          data: passedArray,
          backgroundColor: '#5AA221',
          borderWidth: 1
        },
        {
          label: this.config.failed_label,
          data: failedArray,
          backgroundColor: '#a0372f',
          borderWidth: 1
        },
        {
          label: this.config.not_corrected_label,
          data: notCorrectedArray,
          backgroundColor: '#d6d6d6',
          borderWidth: 1
        }
      ]
    }
    const options = this.getChartOptions()
    this.chart = new Chart(rootElement, {
      type: 'horizontalBar',
      data: chartData,
      options: this.getChartOptions()
    })
  }
}
