import AbstractWidget from "ievv_jsbase/widget/AbstractWidget";
import SignalHandlerSingleton from 'ievv_jsbase/SignalHandlerSingleton';


export default class GradingConfigurationWidget extends AbstractWidget {

  getDefaultConfig() {
    return {
      // grading_system_plugin_id: 'devilry_gradingsystemplugin_approved',
      // points_to_grade_mapper: 'passed-failed',
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
    this.logger = new window.ievv_jsbase_core.LoggerSingleton().getLogger(
      'devilry.GradingConfigurationWidget');
    this._onPluginIdRadioChange = this._onPluginIdRadioChange.bind(this);
    this._onPointsToGradeMapperRadioChange = this._onPointsToGradeMapperRadioChange.bind(this);
    this._onRemoveCustomTableRow = this._onRemoveCustomTableRow.bind(this);
    this._onAddCustomTableRow = this._onAddCustomTableRow.bind(this);
    this._onSetupCustomTableAtoFExample = this._onSetupCustomTableAtoFExample.bind(this);
    this._onCustomTableValueChangeSignal = this._onCustomTableValueChangeSignal.bind(this);

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
    this.customTableAddRowButton = document.getElementById('id_custom_table_add_row_button');
    this.customTableSetuAtoFExampleButton = document.getElementById('id_custom_table_setup_atof_example_button');
    this.customTableValueListJsonElement = document.getElementById('id_custom_table_value_list_json');

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
    this._setState({
      // grading_system_plugin_id: initialPluginId,
      // points_to_grade_mapper: initialPointsToGradeMapper,
      grading_system_plugin_id: 'devilry_gradingsystemplugin_points',
      points_to_grade_mapper: 'custom-table',
      custom_table_value_list: this._getCustomTableAtoFExampleConfig()
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
    console.log('statePatch', statePatch);
    console.log('oldState', oldState);
    console.log('newState', this._state);

    if(initial) {
      this.pluginIdElements[this._state.grading_system_plugin_id].input.checked = true;
      this.pointsToGradeMapperElements[this._state.points_to_grade_mapper].input.checked = true;
      this._signalHandler.send(
        `${this.config.signalNameSpace}.SetCustomTableRows`, {
          valueList: this._state.custom_table_value_list,
          sendValueChangeSignal: false
        });
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
    if(this._state.custom_table_value_list != oldState.custom_table_value_list) {
      this.customTableValueListJsonElement.value = JSON.stringify(this._state.custom_table_value_list);
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
      {grade: 'F', points: 0},
      {grade: 'D', points: 25},
      {grade: 'C', points: 50},
      {grade: 'B', points: 75},
      {grade: 'A', points: 90},
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

  _onRemoveCustomTableRow(event) {
    event.preventDefault();
  }

  _onCustomTableValueChangeSignal(receivedSignalInfo) {
    const valueList = receivedSignalInfo.data;
    this._setState({
      custom_table_value_list: valueList
    })
  }
}
