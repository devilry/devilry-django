import AbstractWidget from "ievv_jsbase/widget/AbstractWidget";
import HtmlParser from "ievv_jsbase/dom/HtmlParser";

export default class GradingConfigurationWidget extends AbstractWidget {
  _getCustomTableAtoFExampleConfig() {
    return [
      ['F', 0],
      ['D', 25],
      ['C', 50],
      ['B', 75],
      ['A', 90],
    ];
  }

  getDefaultConfig() {
    return {
      // grading_system_plugin_id: 'devilry_gradingsystemplugin_approved',
      // points_to_grade_mapper: 'passed-failed',
      grading_system_plugin_id: 'devilry_gradingsystemplugin_points',
      points_to_grade_mapper: 'custom-table',
      custom_table_data: this._getCustomTableAtoFExampleConfig()
    };
  }

  constructor(element) {
    super(element);
    this.logger = new window.ievv_jsbase_core.LoggerSingleton().getLogger(
      'devilry.GradingConfigurationWidget');
    this._onPluginIdRadioChange = this._onPluginIdRadioChange.bind(this);
    this._onPointsToGradeMapperRadioChange = this._onPointsToGradeMapperRadioChange.bind(this);
    this._onRemoveCustomTableRow = this._onRemoveCustomTableRow.bind(this);
    this._onAddCustomTableRow = this._onAddCustomTableRow.bind(this);
    this._onCustomTablePointInputBlur = this._onCustomTablePointInputBlur.bind(this);
    this._onCustomTableGradeInputChange = this._onCustomTableGradeInputChange.bind(this);
    this._onCustomTablePointInputChange = this._onCustomTablePointInputChange.bind(this);
    this._onSetupCustomTableAtoFExample = this._onSetupCustomTableAtoFExample.bind(this);

    this.pluginIdElements = this._getPluginIdElements();
    this.passingGradeMinPointsWrapperElement = document.getElementById(
      'div_id_passing_grade_min_points');
    this.maxPointsLabelElement = this.element.querySelector(
      '#div_id_max_points label');
    this.maxPointsHelpTextElement = document.getElementById(
      'hint_id_max_points');
    this.pointsToGradeMapperElements = this._getPointsToGradeMapperElements();
    this.customTableWrapperElement = document.getElementById(
      'id_custom_table_wrapper');

    // const initialPluginId = this.element.querySelector(
    //   '#div_id_grading_system_plugin_id input[checked]').value;
    this.customTableBodyElement = document.getElementById('id_custom_table_body');
    this.customTableAddRowButton = document.getElementById('id_custom_table_add_row_button');
    this.customTableSetuAtoFExampleButton = document.getElementById('id_custom_table_setup_atof_example_button');

    this._state = {};
    this._setState({
      grading_system_plugin_id: this.config.grading_system_plugin_id,
      points_to_grade_mapper: this.config.points_to_grade_mapper,
      custom_table_data: this.config.custom_table_data
    }, true);
    this._addEventListeners();
  }

  _setState(statePatch, initial=false) {
    let oldState = Object.assign({}, this._state);
    this._state = Object.assign({}, this._state, statePatch);
    console.log('statePatch', statePatch);
    console.log('oldState', oldState);
    console.log('newState', this._state);

    if(initial) {
      this.pluginIdElements[this._state.grading_system_plugin_id].input.checked = true;
      this.pointsToGradeMapperElements[this._state.points_to_grade_mapper].input.checked = true;
    }
    if(this._state.grading_system_plugin_id == 'devilry_gradingsystemplugin_approved' && this._state.points_to_grade_mapper == 'custom-points') {
      this._state.points_to_grade_mapper = 'passed-failed';
    }

    if(this._state.grading_system_plugin_id != oldState.grading_system_plugin_id) {
      this._updateUiForPlugin();
    }
    if(this._state.points_to_grade_mapper != oldState.points_to_grade_mapper) {
      this._updateUiForPointsToGradeMapper();
    }
  }

  _updateUiForPlugin() {
    let pluginId = this._state.grading_system_plugin_id;
    if(pluginId == 'devilry_gradingsystemplugin_approved') {
      this._updateUiForApprovedPlugin();
    } else if(pluginId == 'devilry_gradingsystemplugin_points') {
      this._updateUiForPointsPlugin();
    } else {
      throw new Error(`Unsupported grading_system_plugin: "${pluginId}"`);
    }
  }

  _updateUiForPointsToGradeMapper() {
    let mapper = this._state.points_to_grade_mapper;
    if(mapper == 'custom-table') {
      this.customTableWrapperElement.style.display = 'block';
    } else {
      this.customTableWrapperElement.style.display = 'none';
    }
  }

  _getPluginIdElements() {
    const inputElements = Array.from(this.element.querySelectorAll(
      '#div_id_grading_system_plugin_id input[type="radio"]'));
    let pluginIdElements = {};
    for(let inputElement of inputElements) {
      pluginIdElements[inputElement.value] = {
        input: inputElement
      };
    }
    return pluginIdElements;
  }

  _getPointsToGradeMapperElements() {
    const inputElements = Array.from(this.element.querySelectorAll(
      '#div_id_points_to_grade_mapper input[type="radio"]'));
    let pointsToGradeMapperElements = {};
    for(let inputElement of inputElements) {
      pointsToGradeMapperElements[inputElement.value] = {
        input: inputElement,
        wrapper: inputElement.parentElement.parentElement
      };
    }
    return pointsToGradeMapperElements;
  }

  _addEventListeners() {
    for(let value of Object.keys(this.pluginIdElements)) {
      let inputElement = this.pluginIdElements[value].input;
      inputElement.addEventListener(
        'change', this._onPluginIdRadioChange);
    }
    for(let value of Object.keys(this.pointsToGradeMapperElements)) {
      let inputElement = this.pointsToGradeMapperElements[value].input;
      inputElement.addEventListener(
        'change', this._onPointsToGradeMapperRadioChange);
    }
    this.customTableAddRowButton.addEventListener('click', this._onAddCustomTableRow);
    this.customTableSetuAtoFExampleButton.addEventListener('click', this._onSetupCustomTableAtoFExample);
  }

  destroy() {}

  _hidePointsToGradeMapperCustomTableChoice() {
    this.pointsToGradeMapperElements['custom-table'].wrapper.style.display = 'none';
    if(this.pointsToGradeMapperElements['custom-table'].input.checked) {
      this.pointsToGradeMapperElements['passed-failed'].input.checked = true;
    }
  }

  _showPointsToGradeMapperCustomTableChoice() {
    this.pointsToGradeMapperElements['custom-table'].wrapper.style.display = 'block';
  }

  _updateUiLabels(pluginConfig) {
    this.maxPointsLabelElement.innerHTML = pluginConfig['max_points_label'] || '';
    if(pluginConfig['max_points_help_text'] == '') {
      this.maxPointsHelpTextElement.style.display = 'none';
    } else {
      this.maxPointsHelpTextElement.style.display = 'block';
      this.maxPointsHelpTextElement.innerHTML = pluginConfig['max_points_help_text'] || '';
    }
  }

  _updateUiForApprovedPlugin() {
    this.passingGradeMinPointsWrapperElement.style.display = 'none';
    this._hidePointsToGradeMapperCustomTableChoice();
    const pluginConfig = this.config['devilry_gradingsystemplugin_approved'];
    this._updateUiLabels(pluginConfig);
  }

  _updateUiForPointsPlugin() {
    this.passingGradeMinPointsWrapperElement.style.display = 'block';
    this._showPointsToGradeMapperCustomTableChoice();
    const pluginConfig = this.config['devilry_gradingsystemplugin_points'];
    this._updateUiLabels(pluginConfig);
  }

  _getRowChildElements(rowElement) {
    return {
      gradeInput: rowElement.children[0],
      minimumPointsInput: rowElement.children[1],
      removeButton: rowElement.children[2]
    }
  }

  _reindexCustomTable() {
    let index = 0;
    for(let rowElement of Array.from(this.customTableBodyElement.children)) {
      let childElements = this._getRowChildElements(rowElement);
      childElements.gradeInput.id = `id_custom_table_grade_${index}`;
      childElements.gradeInput.name = `custom_table_grade_${index}`;
      childElements.minimumPointsInput.id = `id_custom_table_minpoints_${index}`;
      childElements.minimumPointsInput.name = `id_custom_table_minpoints_${index}`;
      if(index == 0 && childElements.removeButton) {
        rowElement.removeChild(childElements.removeButton);
        childElements.minimumPointsInput.disabled = true;
        childElements.minimumPointsInput.value = 0;
      }
      index ++;
    }
  }

  _addCustomTableRow(grade, minimumPoints) {
    let index = 9999999;
    let parser = new HtmlParser(`
      <div class="">
        <input class="textinput textInput form-control form-control"
               id="id_custom_table_grade_${index}"
               name="custom_table_grade_${index}"
               maxlength="12"
               value="${grade}"
               type="text">
        <input class="numberinput form-control form-control"
               id="id_custom_table_minpoints_${index}"
               name="id_custom_table_minpoints_${index}"
               value="${minimumPoints}"
               type="number"
               aria-label="TODO: Dynamically generate">
        <button class="btn btn-danger">
            Remove row
        </button>
      </div>
    `);
    const rowElement = parser.firstRootElement;
    this.customTableBodyElement.appendChild(rowElement);
    let childElements = this._getRowChildElements(rowElement);
    childElements.removeButton.addEventListener('click', this._onRemoveCustomTableRow);
    childElements.minimumPointsInput.addEventListener('blur', this._onCustomTablePointInputBlur);
    childElements.minimumPointsInput.addEventListener('change', this._onCustomTablePointInputChange);
    childElements.gradeInput.addEventListener('change', this._onCustomTableGradeInputChange);
    this._reindexCustomTable();
    return rowElement;
  }

  _removeCustomTableRow(rowElement) {
    let childElements = this._getRowChildElements(rowElement);
    if(childElements.removeButton) {
      childElements.removeButton.removeEventListener('click', this._onRemoveCustomTableRow);
    }
    rowElement.parentNode.removeChild(rowElement);
  }

  _clearCustomTable() {
    for(let rowElement of Array.from(this.customTableBodyElement.children)) {
      this._removeCustomTableRow(rowElement);
    }
  }

  _buildCustomTable(rows) {
    this._clearCustomTable();
    for(let row of rows) {
      this._addCustomTableRow(row[0], row[1]);
    }
  }

  _onPluginIdRadioChange(event) {
    const pluginId = event.target.value;
    this._setState({
      grading_system_plugin_id: pluginId
    });
  }

  _onPointsToGradeMapperRadioChange(event) {
    const value = event.target.value;
    this._setState({
      points_to_grade_mapper: value
    });
  }

  _onCustomTableGradeInputChange(event) {
    const value = event.target.value;
    console.log('Change', value);
  }

  _onCustomTablePointInputChange(event) {
    const value = event.target.value;
    console.log('Change', value);
  }

  _onCustomTablePointInputBlur(event) {
    console.log('BLUR');
  }

  _onAddCustomTableRow(event) {
    event.preventDefault();
    console.log('Add');
    let rowElement = this._addCustomTableRow('', '');
    this._getRowChildElements(rowElement).gradeInput.focus();
  }

  _onSetupCustomTableAtoFExample(event) {
    event.preventDefault();
    if (window.confirm(
        'Are you sure you want to setup the A-F example? Clears the table and inserts new rows.')) {
      this._buildCustomTable(this._getCustomTableAtoFExampleConfig());
    }
  }

  _onRemoveCustomTableRow(event) {
    event.preventDefault();
    let removeButton = event.target;
    let rowElement = removeButton.parentElement;
    this._removeCustomTableRow(rowElement);
    this._reindexCustomTable();
  }

}
