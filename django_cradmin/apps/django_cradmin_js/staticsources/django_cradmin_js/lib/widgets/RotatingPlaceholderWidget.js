import AbstractWidget from "ievv_jsbase/lib/widget/AbstractWidget";

/**
 * Rotating input field placeholders.
 *
 * You only have to send a comma separated list into the placeholder
 * attribute, and the widget will take care of splitting up the list
 * and rotate the placeholder between the items in the list.
 *
 * @example
 * <input type="text"
 *        placeholder="People, Animals, Monsters, Elves, ..."
 *        data-ievv-jsbase-widget="cradmin-rotating-placeholder">
 *
 * @example <caption>Using the available config options</caption>
 * <input type="text"
 *        placeholder="People; Animals; Monsters; Elves; ..."
 *        data-ievv-jsbase-widget="cradmin-rotating-placeholder"
 *        data-ievv-jsbase-widget-config='{
 *          "separator": ";",
 *          "intervalMilliseconds": 4000,
 *          "ignore": ["...", "..", "I", "we"],
 *          "prefix": "Search for",
 *          "suffix": "awesomeness"
 *        }'>
 *
 */
export default class RotatingPlaceholderWidget extends AbstractWidget {

  /**
   * @returns {Object} The default config.
   * @property {string} separator The separator to split the value of the placeholder
   *    attribute by. Defaults to ``","``.
   * @property {number} intervalMilliseconds Number of milliseconds to show each
   *    placeholder. Defaults to ``2000``.
   * @property {Array} ignore Array of items in the placeholder list to ignore
   *    Defaults to ``["..."]``.
   * @property {string} prefix A prefix to add to each placeholder.
   *    Lets say you have a search field. You may want to use
   *    ``Search for`` as prefix so that the placeholder is always
   *    ``Search for <placeholder>``.
   * @property {string} suffix Same as ``prefix``, but added at the end instead
   *    of at the beginning.
   * @property {string} placeholder Send a placeholder through config
   *    instead of using the placeholder attribute of the element. If this
   *    is specified, we read the placeholder from this config instead
   *    of from the placeholder attribute.
   *
   *    The primary reason for using this method is to avoid the placeholder
   *    flashing on load before the javascript takes over.
   */
  getDefaultConfig() {
    return {
      'separator': ',',
      'intervalMilliseconds': 2000,
      'prefix': '',
      'suffix': '',
      'ignore': ["..."],
      'placeholder': null
    }
  }

  constructor(element) {
    super(element);
    this._rotatePlaceholder = this._rotatePlaceholder.bind(this);
    this._intervalId = null;
    this._originalPlaceholder = this.element.getAttribute('placeholder');

    this._placeholderList = this.makePlaceholderList();
    if(this._placeholderList.length == 0) {
      return;
    }
    this._currentPlaceholderIndex = 0;
    this._setPlaceholder();
    if(this._placeholderList.length > 1) {
      this._intervalId = window.setInterval(
        this._rotatePlaceholder, this.config.intervalMilliseconds);
    }
  }

  destroy() {
    if(this._intervalId != null) {
      clearInterval(this._intervalId);
    }
    if(this._originalPlaceholder != null) {
      this.element.setAttribute(this._originalPlaceholder);
    }
  }

  /**
   * Get the prefix.
   *
   * Defaults to the ``prefix`` config with a single
   * whitespace appended if the prefix config is not empty.
   *
   * @returns {string} The prefix string. Should be empty string if
   *    you do not want a prefix (null or undefined does not work).
   */
  getPrefix() {
    let prefix = '';
    if(this.config.prefix != '') {
      prefix = `${this.config.prefix} `;
    }
    return prefix;
  }

  /**
   * Get the suffix. Defaults to the ``suffix`` config.
   *
   * Defaults to the ``suffix`` config with a single
   * whitespace appended if the suffix config is not empty.
   *
   * @returns {string} The prefix string. Should be empty string if
   *    you do not want a prefix (null or undefined does not work).
   */
  getSuffix() {
    let suffix = '';
    if(this.config.suffix != '') {
      suffix = ` ${this.config.suffix}`;
    }
    return suffix;
  }

  /**
   * Make the array of placeholders to rotate over.
   *
   * May be useful if you want to create a subclass that gets
   * placeholders from some other place (such as an API), or
   * if you just want to extract items from the placeholder attribute
   * in a smarter way.
   *
   * @returns {Array} Array of placeholder items to rotate.
   */
  makePlaceholderList() {
    let placeholder = this.config.placeholder;
    if(placeholder == null) {
      placeholder = this.element.getAttribute('placeholder');
    }
    if(placeholder == null) {
      return [];
    }
    placeholder = placeholder.trim();
    if(placeholder.trim() == '') {
      return [];
    }

    let placeholderList = [];
    let ignoreSet = new Set(this.config.ignore);
    for(let placeholderItem of placeholder.split(this.config.separator)) {
      placeholderItem = placeholderItem.trim();
      if(!ignoreSet.has(placeholderItem)) {
        placeholderList.push(placeholderItem);
      }
    }
    return placeholderList;
  }

  _setPlaceholder() {
    let placeholder = this._placeholderList[this._currentPlaceholderIndex];
    let placeholderText = `${this.getPrefix()}${placeholder}${this.getSuffix()}`;
    this.element.setAttribute('placeholder', placeholderText);
  }

  _rotatePlaceholder() {
    this._currentPlaceholderIndex ++;
    if(this._currentPlaceholderIndex >= this._placeholderList.length) {
      this._currentPlaceholderIndex = 0;
    }
    this._setPlaceholder();
  }
}
