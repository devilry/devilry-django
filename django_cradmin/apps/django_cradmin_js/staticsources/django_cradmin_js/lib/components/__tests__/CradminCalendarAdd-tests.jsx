import React from 'react';
import {shallow, mount} from 'enzyme';
import CradminCalendarAdd from '../CradminCalendarAdd';

test('CradminCalendarAdd changes the class when hovered', () => {
  const component = mount(
    <CradminCalendarAdd signalNameSpace="test"/>
  );
  // expect(component.text()).toEqual('TODO');
  // console.log(component.html());
});
