import RotatingPlaceholderWidget from "../RotatingPlaceholderWidget";


describe('RotatingPlaceholderWidget', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  it('no placeholder', () => {
    document.body.innerHTML = `<input id="id_test">`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(widget._placeholderList.length).toBe(0);
    expect(element.getAttribute('placeholder')).toBe(null);
  });

  it('has single placeholder item', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test">`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(widget._placeholderList.length).toBe(1);
    expect(widget._placeholderList).toEqual(['test']);
    expect(element.getAttribute('placeholder')).toEqual('test');
  });

  it('has multiple placeholder items', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test1, test2, test3">`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(widget._placeholderList.length).toBe(3);
    expect(widget._placeholderList).toEqual(['test1', 'test2', 'test3']);
    expect(element.getAttribute('placeholder')).toEqual('test1');
  });

  it('placeholder from config', () => {
    document.body.innerHTML = `<input id="id_test"
        data-ievv-jsbase-widget-config='{"placeholder": "test1, test2"}'>`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(widget._placeholderList.length).toBe(2);
    expect(widget._placeholderList).toEqual(['test1', 'test2']);
  });

  it('placeholder from config overrides placeholder attribute', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="ignored"
        data-ievv-jsbase-widget-config='{"placeholder": "test"}'>`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(widget._placeholderList.length).toBe(1);
    expect(widget._placeholderList).toEqual(['test']);
  });

  it('rotates placeholder items', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test1, test2, test3">`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(element.getAttribute('placeholder')).toEqual('test1');
    jest.advanceTimersByTime(2000);
    expect(element.getAttribute('placeholder')).toEqual('test2');
    jest.advanceTimersByTime(2000);
    expect(element.getAttribute('placeholder')).toEqual('test3');
    jest.advanceTimersByTime(2000);
    expect(element.getAttribute('placeholder')).toBe('test1');
  });

  it('custom rotation interval', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test1, test2, test3"
       data-ievv-jsbase-widget-config='{"intervalMilliseconds": 100}'>`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(element.getAttribute('placeholder')).toEqual('test1');
    jest.advanceTimersByTime(100);
    expect(element.getAttribute('placeholder')).toEqual('test2');
    jest.advanceTimersByTime(100);
    expect(element.getAttribute('placeholder')).toEqual('test3');
    jest.advanceTimersByTime(100);
    expect(element.getAttribute('placeholder')).toBe('test1');
  });

  it('prefix sanity', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test"
       data-ievv-jsbase-widget-config='{"prefix": "The prefix"}'>`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(element.getAttribute('placeholder')).toEqual('The prefix test');
  });

  it('prefix works with rotation', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test1, test2"
       data-ievv-jsbase-widget-config='{"prefix": "The prefix"}'>`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(element.getAttribute('placeholder')).toEqual('The prefix test1');
    jest.advanceTimersByTime(2000);
    expect(element.getAttribute('placeholder')).toEqual('The prefix test2');
  });

  it('suffix sanity', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test"
       data-ievv-jsbase-widget-config='{"suffix": "the suffix"}'>`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(element.getAttribute('placeholder')).toEqual('test the suffix');
  });

  it('suffix works with rotation', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test1, test2"
       data-ievv-jsbase-widget-config='{"suffix": "the suffix"}'>`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(element.getAttribute('placeholder')).toEqual('test1 the suffix');
    jest.advanceTimersByTime(2000);
    expect(element.getAttribute('placeholder')).toEqual('test2 the suffix');
  });

  it('custom separator', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test1; test2; test3"
       data-ievv-jsbase-widget-config='{"separator": ";"}'>`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(widget._placeholderList).toEqual(['test1', 'test2', 'test3']);
  });

  it('default ignore', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test1, test2, ...">`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(widget._placeholderList).toEqual(['test1', 'test2']);
  });

  it('custom ignore', () => {
    document.body.innerHTML = `<input id="id_test" placeholder="test1, test2, test3"
       data-ievv-jsbase-widget-config='{"ignore": ["test2", "test3"]}'>`;
    const element = document.getElementById('id_test');
    const widget = new RotatingPlaceholderWidget(element);
    expect(widget._placeholderList).toEqual(['test1']);
  });

});
