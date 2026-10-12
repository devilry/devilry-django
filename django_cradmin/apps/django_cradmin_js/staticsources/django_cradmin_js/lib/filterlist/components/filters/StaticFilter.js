import AbstractFilter from './AbstractFilter'

/**
 * Static filter.
 *
 * @example
 * {
 *    "component": "StaticFilter",
 *    "initialValue": 2,
 *    "props": {
 *      "name": "parentnode"
 *    }
 * }
 */
export default class StaticFilter extends AbstractFilter {
  render () {
    return null
  }
}
