import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";
import HtmlParser from "ievv_jsbase/lib/dom/HtmlParser";
import SignalHandlerSingleton from 'ievv_jsbase/lib/SignalHandlerSingleton';
import LoggerSingleton from "ievv_jsbase/lib/log/LoggerSingleton";


export default class GradingConfigurationWidget extends AbstractWidget {

  getDefaultConfig() {
    return {
      signalNameSpace: 'gradingConfiguration'
    };
  }

  constructor(element) {
    super(element);
    if(this.config.signalNameSpace == null) {
      throw new Error('The signalNameSpace config is required.');
    }
    this._name = `devilry.GradingConfigurationWidget.${this.config.signalNameSpace}`;
    this._signalHandler = new SignalHandlerSingleton();
    this.logger = new LoggerSingleton().getLogger(
      'devilry.GradingConfigurationWidget');
    this._onPluginIdRadioChange = this._onPluginIdRadioChange.bind(this);
    this._onPointsToGradeMapperRadioChange = this._onPointsToGradeMapperRadioChange.bind(this);
    this._onPassingGradeMinPointsChange = this._onPassingGradeMinPointsChange.bind(this);
    this._onAddCustomTableRow = this._onAddCustomTableRow.bind(this);
    this._onSetupCustomTableAtoFExample = this._onSetupCustomTableAtoFExample.bind(this);
    this._onCustomTableValueChangeSignal = this._onCustomTableValueChangeSignal.bind(this);

    this.pluginIdElements = this._getPluginIdElements();
    this.passingGradeMinPointsWrapperElement = document.getElementById('div_id_passing_grade_min_points');
    this.passingGradeMinPointsInputElement = document.getElementById('id_passing_grade_min_points');
    this.maxPointsLabelElement = this.element.querySelector('#div_id_max_points label');
    this.maxPointsHelpTextElement = document.getElementById('hint_id_max_points');
    this.maxPointsInputElement = document.getElementById('id_max_points');
    this.pointsToGradeMapperElements = this._getPointsToGradeMapperElements();
    this.customTableWrapperElement = document.getElementById(
      'id_custom_table_wrapper');
    this.customTableAddRowButton = document.getElementById('id_custom_table_add_row_button');
    this.customTableSetuAtoFExampleButton = document.getElementById('id_custom_table_setup_atof_example_button');
    this.pointToGradeMapJsonElement = document.getElementById('id_point_to_grade_map_json');

    this._state = {};
    this._initializeSignalHandlers();
  }

  useAfterInitializeAllWidgets() {
    return true;
  }

  afterInitializeAllWidgets() {
    const initialPluginId = this.element.querySelector(
      '#div_id_grading_system_plugin_id input[checked]').value;
    const initialPointsToGradeMapper = this.element.querySelector(
      '#div_id_points_to_grade_mapper input[checked]').value;
    const initialPointToGradeMapString = this.pointToGradeMapJsonElement.value;
    let initialPassingGradeMinPoints = parseInt(this.passingGradeMinPointsInputElement.value);
    if(isNaN(initialPassingGradeMinPoints)) {
      initialPassingGradeMinPoints = null;
    }
    let initialMaxPoints = parseInt(this.maxPointsInputElement.value);
    if(isNaN(initialMaxPoints)) {
      initialMaxPoints = null;
    }

    let initialPointToGradeMap = [];
    if(initialPointToGradeMapString != undefined && initialPointToGradeMapString != null && initialPointToGradeMapString != '') {
      initialPointToGradeMap = JSON.parse(initialPointToGradeMapString);
    }
    if(initialPointToGradeMap.length == 0 || initialPointToGradeMap[0][0] != 0) {
      initialPointToGradeMap = [[0, '']];
    }
    this._setState({
      // grading_system_plugin_id: 'devilry_gradingsystemplugin_points',
      // points_to_grade_mapper: 'custom-table',
      // point_to_grade_map: this._getCustomTableAtoFExampleConfig()
      grading_system_plugin_id: initialPluginId,
      points_to_grade_mapper: initialPointsToGradeMapper,
      point_to_grade_map: initialPointToGradeMap,
      passing_grade_min_points: initialPassingGradeMinPoints,
      max_points: initialMaxPoints
    }, true);
    this._addEventListeners();
  }

  _initializeSignalHandlers() {
    this._signalHandler.addReceiver(
      `${this.config.signalNameSpace}.CustomTableValueChange`,
      this._name,
      this._onCustomTableValueChangeSignal);
  }

  _setState(statePatch, initial=false) {
    let oldState = Object.assign({}, this._state);
    this._state = Object.assign({}, this._state, statePatch);
    // console.log('statePatch', statePatch);
    // console.log('oldState', oldState);
    // console.log('newState', this._state);

    if(initial) {
      this.pluginIdElements[this._state.grading_system_plugin_id].input.checked = true;
      this.pointsToGradeMapperElements[this._state.points_to_grade_mapper].input.checked = true;
      this._signalHandler.send(
        `${this.config.signalNameSpace}.SetCustomTableRows`, {
          valueList: this._state.point_to_grade_map,
          sendValueChangeSignal: false
        });
    }
    if(this._state.grading_system_plugin_id == 'devilry_gradingsystemplugin_approved' && this._state.points_to_grade_mapper == 'custom-table') {
      this._state.points_to_grade_mapper = 'passed-failed';
    }

    if(this._state.grading_system_plugin_id != oldState.grading_system_plugin_id) {
      this._updateUiForPlugin();
    }
    if(this._state.points_to_grade_mapper != oldState.points_to_grade_mapper) {
      this._updateUiForPointsToGradeMapper();
    }
    if(this._state.point_to_grade_map != oldState.point_to_grade_map) {
      this.pointToGradeMapJsonElement.value = JSON.stringify(this._state.point_to_grade_map);
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


  _renderPassingGradeMinPointsField() {
    let parentElement = this.passingGradeMinPointsInputElement.parentElement;
    parentElement.removeChild(this.passingGradeMinPointsInputElement);
    let fieldHtml = '';
    if(this._state.points_to_grade_mapper == 'custom-table') {
      fieldHtml = this._getPassingGradeMinPointsCustomTableSelectFieldHtml();
    } else {
      fieldHtml = this._getPassingGradeMinPointsInputFieldHtml();
    }
    let parser = new HtmlParser(fieldHtml);
    const selectElement = parser.firstRootElement;
    this.passingGradeMinPointsInputElement = selectElement;
    parentElement.insertBefore(selectElement, parentElement.children[0]);
    selectElement.addEventListener('change', this._onPassingGradeMinPointsChange);
  }

  _getPassingGradeMinPointsCustomTableSelectFieldHtml() {
    let options = '<option value=""></option>';
    let hasSelectedOption = false;
    for(let pointToGrade of this._state.point_to_grade_map) {
      let points = pointToGrade[0];
      let grade = pointToGrade[1];
      let selected = '';
      if(points == this._state.passing_grade_min_points && !hasSelectedOption) {
        selected = 'selected';
        hasSelectedOption = true;
      }
      options += `<option value="${points}" ${selected}>${points} (${grade})</option>`;
    }
    return `<select name="passing_grade_min_points" class="form-control">${options}</select>`;
  }

  _getPassingGradeMinPointsInputFieldHtml() {
    let value = this._state.passing_grade_min_points;
    if(value == null) {
      value = '';
    }
    return `<input type="number" name="passing_grade_min_points" 
                   value="${value}"
                   min="0" step="1"
                   class="form-control"/>`;
  }

  _updateUiForPointsToGradeMapper() {
    let mapper = this._state.points_to_grade_mapper;
    if(mapper == 'custom-table') {
      this.customTableWrapperElement.style.display = 'block';
    } else {
      this.customTableWrapperElement.style.display = 'none';
    }
    this._renderPassingGradeMinPointsField();
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

  _onAddCustomTableRow(event) {
    event.preventDefault();
    this._signalHandler.send(`${this.config.signalNameSpace}.AddCustomTableRow`, {
      grade: '',
      points: ''
    });
  }

  _getCustomTableAtoFExampleConfig() {
    return [
      [0, 'F'],
      [25, 'D'],
      [50, 'C'],
      [75, 'B'],
      [90, 'A']
    ];
  }

  _onSetupCustomTableAtoFExample(event) {
    event.preventDefault();
    if (window.confirm(
        'Are you sure you want to setup the A-F example? Clears the table and inserts new rows.')) {
      this._signalHandler.send(
        `${this.config.signalNameSpace}.SetCustomTableRows`,{
          valueList: this._getCustomTableAtoFExampleConfig(),
          sendValueChangeSignal: true
        });
    }
  }

  _onCustomTableValueChangeSignal(receivedSignalInfo) {
    const valueList = receivedSignalInfo.data;
    this._setState({
      point_to_grade_map: valueList
    })
  }

  _onPassingGradeMinPointsChange(event) {
    let value = parseInt(event.target.value);
    if(isNaN(value)) {
      value = null;
    }
    this._setState({
      passing_grade_min_points: value
    });
  }
}
