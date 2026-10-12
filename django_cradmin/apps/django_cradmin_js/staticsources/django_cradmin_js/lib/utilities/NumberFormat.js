export default class NumberFormat {
  static zeroPaddedString(number, min, max) {
    if(max != undefined && number > max) {
      number = max;
    }
    if(min != undefined && number < min) {
      number = min;
    }
    if(number < 10) {
      return `0${number}`;
    } else {
      return `${number}`;
    }
  }
}
