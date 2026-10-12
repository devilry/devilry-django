import ElementCreator from "../ElementCreator";

describe('ElementCreator', () => {
  it('ElementCreator.renderElement() plain element', () => {
    const elementCreator = new ElementCreator('div');
    const element = elementCreator.renderElement();
    expect(element.tagName).toBe('DIV');
  });

  it('ElementCreator.addCssClass() single css-class', () => {
    const elementCreator = new ElementCreator('div');
    elementCreator.addCssClass('this-is-a-test-class');
    const element = elementCreator.renderElement();
    expect(element.classList.contains('this-is-a-test-class')).toBe(true);
  });

  it('ElementCreator.addCssClass() multiple css-classes', () => {
    const elementCreator = new ElementCreator('div');
    const cssClasses = ['this-is-a-test-class', 'this-is-another-test-class', 'woopeeedoooooooo'];
    for (let cssClass of cssClasses) elementCreator.addCssClass(cssClass);
    const element = elementCreator.renderElement();
    for (let cssClass of cssClasses) expect(element.classList.contains(cssClass)).toBe(true);
  });

  it('ElementCreator.addAttribute() single attribute without value', () => {
    const elementCreator = new ElementCreator('div');
    elementCreator.addAttribute('this-is-a-test-attribute');
    const element = elementCreator.renderElement();
    expect(element.hasAttribute('this-is-a-test-attribute')).toBe(true);
  });

  it('ElementCreator.addAttribute() single attribute with value', () => {
    const elementCreator = new ElementCreator('div');
    elementCreator.addAttribute('this-is-a-test-attribute', 'woopeedooo');
    const element = elementCreator.renderElement();
    expect(element.hasAttribute('this-is-a-test-attribute')).toBe(true);
    expect(element.getAttribute('this-is-a-test-attribute')).toBe('woopeedooo');
  });

  it ('ElementCreator.addAttribute() multiple attributes with and without values', () => {
    const elementCreator = new ElementCreator('div');
    elementCreator.addAttribute('this');
    elementCreator.addAttribute('this-is', 'woopeedooo');
    elementCreator.addAttribute('this-is-a');
    elementCreator.addAttribute('this-is-a-test');
    elementCreator.addAttribute('this-is-a-test-attribute', 'maybe');
    const element = elementCreator.renderElement();
    expect(element.hasAttribute('this')).toBe(true);
    expect(element.getAttribute('this')).toBe('');
    expect(element.hasAttribute('this-is')).toBe(true);
    expect(element.getAttribute('this-is')).toBe('woopeedooo');
    expect(element.hasAttribute('this-is-a')).toBe(true);
    expect(element.getAttribute('this-is-a')).toBe('');
    expect(element.hasAttribute('this-is-a-test')).toBe(true);
    expect(element.getAttribute('this-is-a-test')).toBe('');
    expect(element.hasAttribute('this-is-a-test-attribute')).toBe(true);
    expect(element.getAttribute('this-is-a-test-attribute')).toBe('maybe');
  });

  it ('ElementCreator.renderElement() all functionality', () => {
    const elementCreator = new ElementCreator('div');
    const cssClasses = ['this-is-a-test-class', 'this-is-another-test-class', 'woopeeedoooooooo'];
    for (let cssClass of cssClasses) elementCreator.addCssClass(cssClass);
    elementCreator.addAttribute('this');
    elementCreator.addAttribute('this-is', 'woopeedooo');

    const element = elementCreator.renderElement();
    expect(element.tagName).toBe('DIV');
    for (let cssClass of cssClasses) expect(element.classList.contains(cssClass)).toBe(true);
    expect(element.hasAttribute('this')).toBe(true);
    expect(element.getAttribute('this')).toBe('');
    expect(element.hasAttribute('this-is')).toBe(true);
    expect(element.getAttribute('this-is')).toBe('woopeedooo');
  });
});
