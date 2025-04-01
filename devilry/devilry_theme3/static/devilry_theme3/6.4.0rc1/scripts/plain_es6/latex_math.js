import katex from "../katex/katex.mjs";

class DevilryLatexMath extends HTMLElement {
    constructor () {
        super();
        this._latexCode = this.getAttribute('data-latex-code');
        this._variant = this.getAttribute('data-variant');
    }

    connectedCallback () {
        this.setAttribute('class', `devilry-latexmath devilry-latexmath--${this._variant}`);
        katex.render(this._latexCode, this, {
            throwOnError: false
        });
    }
}

window.customElements.define('devilry-latex-math', DevilryLatexMath);
