export default class ElementCreator {
  constructor(tagName=null) {
    this.reset(tagName);
  }

  reset(newTagName=this._tagName) {
    this._destroy();
    this._tagName = newTagName;
    this._cssClasses = [];
    this._attributes = new Map();
    this._value = null;
    this._hasChanges = false;
  }

  _hasValidElement() {
    return this._element != null && !this._hasChanges;
  }

  addCssClass(className) {
    this._hasChanges = true;
    this._cssClasses.push(className);
  }

  changeTagName(tagName) {
    this._hasChanges = true;
    this._tagName = tagName;
  }

  addAttribute(attribute, attributeValue="") {
    this._hasChanges = true;
    this._attributes.set(attribute, attributeValue);
  }

  setValue(value) {
    this._hasChanges = true;
    this._value = value;
  }

  useElement(element) {
    this._destroy();
    this._element = element;
  }

  renderElement() {
    if (this._hasValidElement()) {
      return this._element;
    }

    this._destroy();
    this._hasChanges = false;
    if (this._tagName == null) {
      throw new Error(`Cannot create element without valid tagName! got: ${this._tagName}`);
    }
    let element = document.createElement(this._tagName);

    if (this._value != null) {
      element.value = this._value;
    }

    for (let className of this._cssClasses) {
      element.classList.add(className);
    }
    for (let [attribute, value] of this._attributes) {
      element.setAttribute(attribute, value);
    }
    this._element = element;
    return this._element;
  }

  _destroy() {
    if (this._element != null && this._element != undefined) {
      this._element.remove();
    }
    this._element = null;
  }
}