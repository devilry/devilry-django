# About the styleguide

Style guides require compliance and conformity; in return they provide stability and cohesion.
A style guide and code standards document is a way of ensuring brand and code consistency.
By maintaining all of a website's primary elements on a single page, we can see how modular 
components can be reused, as well as how changes to those elements will affect the site overall. 
The style guide also serves as a curated, archival collection for design and UX/UI decisions 
made during the course of the site's development - creating a code base that can resist
arbitrary decisions since a predefined choice presents itself.
CSS is written in SASS with [BEM](http://csswizardry.com/2013/01/mindbemding-getting-your-head-round-bem-syntax/) 
naming convention. And separated into the following categories:

## 1 Settings
This is where all `variables` and `mixins` go.

## 2 Generic
Generic stuff like reset, clearfix goes here.

## 3 Base
This is where the base design is applied. Form-fields, typography, icons etc.

## 4 Components
This is all the components and modules, stuff like `.card` or `.modal`

## 5 Trumps
This is the stuff that has to be loaded last. Mostly used for utility stuff.
