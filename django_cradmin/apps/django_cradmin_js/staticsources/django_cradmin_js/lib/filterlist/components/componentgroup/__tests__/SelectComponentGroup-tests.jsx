/* eslint-env jest */
import { shallow } from 'enzyme'
import SelectComponentGroup from '../SelectComponentGroup'
import { renderComponentGroup } from '../testHelpers'
import { ChildExposedApiMock } from '../../filterlists/testHelpers'

function render (props = {}) {
  return renderComponentGroup(
    SelectComponentGroup, Object.assign({
      domIdPrefix: 'test',
      name: 'test'
    }, props))
}

describe('SelectComponentGroup', () => {

  beforeEach(() => {
    jest.restoreAllMocks()
  })

  test('no selectable componentgroups - do not render anything', () => {
    console.warn = jest.fn() // prevent warning from logging in test - see next test..
    const component = shallow(render())
    expect(component.type()).toBeNull()
  })

  test('no selectable componentgroups - warning logged to console', () => {
    console.warn = jest.fn()
    shallow(render())
    expect(console.warn).toBeCalled()
  })

  test('single selectable componentgroup - render something', () => {
    const props = {
      selectableComponentGroups: [
        {
          name: 'testgroup1',
          label: 'test group 1'
        }
      ]
    }
    const component = shallow(render(props))
    expect(component.type()).not.toBeNull()
  })

  test('two selectable componentgroups - render two radiobuttons', () => {
    const props = {
      selectableComponentGroups: [
        {
          name: 'testgroup1',
          label: 'test group 1'
        }, {
          name: 'testgroup2',
          label: 'test group 2'
        }
      ]
    }
    const component = shallow(render(props))
    expect(component.find('label.radio.radio--block > span.radio__control-indicator').length).toBe(2)
    expect(component.find('label.radio.radio--block > input[type="radio"]').length).toBe(2)
  })

  test('two selectable componentgroups - rendered radiobuttons have given', () => {
    const props = {
      name: 'testname',
      selectableComponentGroups: [
        {
          name: 'testgroup1',
          label: 'test group 1'
        }, {
          name: 'testgroup2',
          label: 'test group 2'
        }
      ]
    }
    const component = shallow(render(props))
    expect(component.find('input[name="testname"]').length).toBe(2)
  })

  test('two selectable componentgroups - rendered radiobuttons have componentgroup values', () => {
    const props = {
      selectableComponentGroups: [
        {
          name: 'testgroup1',
          label: 'test group 1'
        }, {
          name: 'testgroup2',
          label: 'test group 2'
        }
      ]
    }
    const component = shallow(render(props))
    expect(component.find('label.radio.radio--block > input[value="testgroup1"]').length).toBe(1)
    expect(component.find('label.radio.radio--block > input[value="testgroup2"]').length).toBe(1)
  })

  test('mount calls selectComponentGroup with initialEnabled', () => {
    const props = {
      selectableComponentGroups: [
        {
          name: 'testgroup1',
          label: 'test group 1'
        }, {
          name: 'testgroup2',
          label: 'test group 2'
        }
      ],
      initialEnabled: 'testgroup1'
    }
    const selectComponentGroup = jest.spyOn(SelectComponentGroup, 'selectComponentGroup')
    shallow(render(props))
    expect(selectComponentGroup).toHaveBeenCalledTimes(1)
    expect(selectComponentGroup).toHaveBeenCalledWith('testgroup1', expect.anything())
  })

  test('clicking radiobutton runs selectComponentGroup', () => {
    const props = {
      selectableComponentGroups: [
        {
          name: 'testgroup1',
          label: 'test group 1'
        }, {
          name: 'testgroup2',
          label: 'test group 2'
        }
      ],
      initialEnabled: 'testgroup1'
    }
    const selectComponentGroup = jest.spyOn(SelectComponentGroup, 'selectComponentGroup')
    const component = shallow(render(props))
    expect(selectComponentGroup).toHaveBeenCalledWith('testgroup1', expect.anything())
    component.find('input[value="testgroup2"]').first().simulate('change', {target: {value: 'testgroup2'}})
    expect(selectComponentGroup).toHaveBeenLastCalledWith('testgroup2', expect.anything())
  })

  test('selectComponentGroup enables given componentGroup if not already enabled', () => {
    const childExposedApi = new ChildExposedApiMock()
    childExposedApi.componentGroupIsEnabled = jest.fn((componentGroupName) => {
      return componentGroupName === 'isEnabled'
    })

    const props = {
      selectableComponentGroups: [
        {
          name: 'testgroup1',
          label: 'test group 1'
        }, {
          name: 'testgroup2',
          label: 'test group 2'
        }
      ],
      initialEnabled: 'testgroup1',
      childExposedApi: childExposedApi
    }
    const component = shallow(render(props))
    component.find('input[value="testgroup2"]').first().simulate('change', {target: {value: 'testgroup2'}})
    expect(childExposedApi.enableComponentGroup).toBeCalledWith('testgroup2')
  })

  test('selectComponentGroup disable already enabled componentGroup if not the one given', () => {
    const childExposedApi = new ChildExposedApiMock()
    childExposedApi.componentGroupIsEnabled = jest.fn((componentGroupName) => {
      return componentGroupName === 'isEnabled'
    })

    const props = {
      selectableComponentGroups: [
        {
          name: 'testgroup1',
          label: 'test group 1'
        }, {
          name: 'isEnabled',
          label: 'test group 2'
        }
      ],
      initialEnabled: 'testgroup1',
      childExposedApi: childExposedApi
    }
    const component = shallow(render(props))
    component.find('input[value="testgroup1"]').first().simulate('change', {target: {value: 'testgroup1'}})
    expect(childExposedApi.disableComponentGroup).toBeCalledWith('isEnabled')
  })
})
