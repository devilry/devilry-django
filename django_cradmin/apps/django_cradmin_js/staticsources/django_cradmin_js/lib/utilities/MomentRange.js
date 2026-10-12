import moment from 'moment'

/**
 * Defines a range between two moment objects.
 */
export default class MomentRange {
  /**
   * Get the default range for our datetime range components.
   *
   * Can be used for a sane default datetime picker range by other
   * widgets/components.
   *
   * @returns {MomentRange}
   */
  static defaultForDatetimeSelect () {
    return new MomentRange(
      moment({
        year: 1900,
        month: 1,
        day: 1
      }),
      moment({
        year: 2100,
        month: 1,
        day: 1
      }).subtract(1, 'second')
    )
  }

  /**
   * @param start Moment object for the start of the range. Defaults to NOW if not provided.
   * @param end Moment object for the end of the range. Defaults to NOW if not provided.
   */
  constructor (start = null, end = null) {
    this.start = start || moment()
    this.end = end || moment().add(1, 'seconds')
    if (!this.end.isAfter(this.start)) {
      throw new Error('The end of a MomentRange must be after the start.')
    }
  }

  /**
   * Prettyformat the range.
   *
   * @param args Forwarded to moment.format() for formatting of both the endpoints in the range.
   * @returns {string}
   */
  format (...args) {
    return `${this.start.format(...args)} - ${this.end.format(...args)}`
  }

  /**
   * Is the provided moment object within the range?
   *
   * @param momentObject
   * @returns {boolean}
   */
  contains (momentObject) {
    return this.start.isSameOrBefore(momentObject) && this.end.isSameOrAfter(momentObject)
  }

  /**
   * Get the closes valid moment object within the range.
   *
   * @param momentObject
   * @returns {*} If the moment object is within the range, we return a clone of the provided
   *   moment object. Otherwise we return the start or end of the range (the one closest to ``momentObject``).
   */
  getClosestValid (momentObject) {
    if (this.contains(momentObject)) {
      return momentObject.clone()
    }
    const millisecondsToStart = Math.abs(this.start.diff(momentObject))
    const millisecondsToEnd = Math.abs(this.end.diff(momentObject))
    if (millisecondsToStart < millisecondsToEnd) {
      return this.start.clone()
    }
    return this.end.clone()
  }
}
