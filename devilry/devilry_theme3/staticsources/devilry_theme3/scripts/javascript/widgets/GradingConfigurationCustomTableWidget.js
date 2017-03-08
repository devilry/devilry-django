import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import HtmlParser from "ievv_jsbase/lib/dom/HtmlParser";
import SignalHandlerSingleton from 'ievv_jsbase/lib/SignalHandlerSingleton';
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";


export default class GradingConfigurationCustomTableWidget extends AbstractWidget {
  getDefaultConfig() {
    return {
      signalNameSpace: 'gradingConfiguration'
    }
  }

  constructor(element) {
    super(element);
    if(this.config.signalNameSpace == null) {
      throw new Error('The signalNameSpace config is required.');
    }
    this._name = `devilry.GradingConfigurationCustomTableWidget.${this.config.signalNameSpace}`;
    this.logger = new LoggerSingleton().getLogger(
      'devilry.GradingConfigurationCustomTableWidget');
    this._onRemoveRow = this._onRemoveRow.bind(this);
    this._onGradeInputChange = this._onGradeInputChange.bind(this);
    this._onPointInputChange = this._onPointInputChange.bind(this);
    this._onAddRowSignal = this._onAddRowSignal.bind(this);
    this._onSetRowsSignal = this._onSetRowsSignal.bind(this);
    this._signalHandler = new SignalHandlerSingleton();
    this._initializeSignalHandlers();
  }

  _initializeSignalHandlers() {
    this._signalHandler.addReceiver(
      `${this.config.signalNameSpace}.AddCustomTableRow`,
      this._name,
      this._onAddRowSignal);
    this._signalHandler.addReceiver(
      `${this.config.signalNameSpace}.SetCustomTableRows`,
      this._name,
      this._onSetRowsSignal);
  }

  destroy() {
    this._signalHandler.removeAllSignalsFromReceiver(this._name);
  }

  _getRowChildElements(rowElement) {
    let childElements = {
      gradeInput: rowElement.children[0].children[0],
      pointInput: rowElement.children[1].children[0],
    };
    if(rowElement.children.length > 2) {
      childElements['removeButton'] = rowElement.children[2].children[0];
    }
    return childElements;
  }

  _getPointsFromRowElement(rowElement) {
    const points = parseInt(rowElement.children[1].children[0].value, 10);
    if(isNaN(points)) {
      return null;
    }
    return points;
  }

  _getGradeFromRowElement(rowElement) {
    return rowElement.children[0].children[0].value;
  }

  _moveToCorrectPlace(rowElement) {
    const points = this._getPointsFromRowElement(rowElement);
    if(points != null) {
      for (let currentRowElement of Array.from(this.element.children)) {
        if (rowElement == currentRowElement) {
          continue;
        }
        let currentPoints = this._getPointsFromRowElement(currentRowElement);
        if (currentPoints == null || points < currentPoints) {
          this.element.insertBefore(rowElement, currentRowElement);
          return;
        }
      }
    }
    this.element.appendChild(rowElement);
  }

  _addRow(grade, minimumPoints) {
    let parser = new HtmlParser(`
      <div class="devilry-tabulardata-list__row">
        <div class="devilry-tabulardata-list__cell">
          <input class="textinput textInput form-control form-control"
                 maxlength="12"
                 value="${grade}"
                 type="text">
        </div>
        <div class="devilry-tabulardata-list__cell">
          <input class="numberinput form-control form-control"
                 value="${minimumPoints}"
                 type="number"
                 min="1" step="1">
        </div>
        <div class="devilry-tabulardata-list__cell">
          <button class="btn btn-danger" type="button">
              remove
          </button>
        </div>
      </div>
    `);
    const rowElement = parser.firstRootElement;
    this.element.appendChild(rowElement);
    let childElements = this._getRowChildElements(rowElement);
    childElements.pointInput.addEventListener('change', this._onPointInputChange);
    childElements.gradeInput.addEventListener('change', this._onGradeInputChange);
    if(childElements.removeButton) {
      childElements.removeButton.addEventListener('click', this._onRemoveRow);
    }
    if(this.element.children[0] == rowElement) {
      childElements.removeButton.parentElement.removeChild(childElements.removeButton);
      childElements.pointInput.removeAttribute('min');
      childElements.pointInput.disabled = true;
      childElements.pointInput.value = 0;
    }
    return rowElement;
  }

  _removeRow(rowElement) {
    let childElements = this._getRowChildElements(rowElement);
    if(childElements.removeButton) {
      childElements.removeButton.removeEventListener('click', this._onRemoveRow);
    }
    rowElement.parentElement.removeChild(rowElement);
    this._sendValueChangeSignal();
  }

  _clear() {
    for(let rowElement of Array.from(this.element.children)) {
      this._removeRow(rowElement);
    }
  }

  _buildTable(valueList) {
    this._clear();
    for(let valueObject of valueList) {
      this._addRow(valueObject[1], valueObject[0]);
    }
  }

  _getCurrentValueList() {
    let values = [];
    for(let rowElement of Array.from(this.element.children)) {
      let points = this._getPointsFromRowElement(rowElement);
      let grade = this._getGradeFromRowElement(rowElement) || '';
      grade = grade.trim();
      if(points != null && grade != '') {
        values.push([points, grade]);
      }
    }
    return values;
  }

  _sendValueChangeSignal() {
    this._signalHandler.send(
      `${this.config.signalNameSpace}.CustomTableValueChange`,
      this._getCurrentValueList());
  }

  _onGradeInputChange(event) {
    const value = event.target.value;
    this._sendValueChangeSignal();
  }

  _onPointInputChange(event) {
    let pointInputElement = event.target;
    let rowElement = pointInputElement.parentElement.parentElement;
    this._moveToCorrectPlace(rowElement);
    this._sendValueChangeSignal();
  }

  _onSetRowsSignal(receivedSignalInfo) {
    const valueList = receivedSignalInfo.data.valueList;
    const sendValueChangeSignal = receivedSignalInfo.data.sendValueChangeSignal;
    this._buildTable(valueList);
    if(sendValueChangeSignal) {
      this._sendValueChangeSignal();
    }
  }

  _onAddRowSignal(receivedSignalInfo) {
    let rowElement = this._addRow(receivedSignalInfo.data.grade, receivedSignalInfo.data.points);
    this._getRowChildElements(rowElement).gradeInput.focus();
  }

  _onRemoveRow(event) {
    event.preventDefault();
    let removeButton = event.target;
    let rowElement = removeButton.parentElement.parentElement;
    this._removeRow(rowElement);
  }
}
