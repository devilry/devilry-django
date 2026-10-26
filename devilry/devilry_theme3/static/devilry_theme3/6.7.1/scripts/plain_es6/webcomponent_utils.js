export function devilryParseDomString (domString) {
    return new DOMParser().parseFromString(domString, 'text/html').body.firstChild;
}
