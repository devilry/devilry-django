**************************
Devilry flavoured Markdown
**************************

When you write feedback to your students, you use the Markdown text formatting language.

With Markdown, you to write using an easy-to-read, easy-to-write plain text
format, and let someone else (Devilry) worry about how the results will look.
This makes it possible to write feedback text that Devilry can optimize for
anything from smartphones to large desktop displays.


Basics
======

Paragraphs
----------
Paragraphs are just one or more lines of consecutive text followed by one or more blank lines::

    Maecenas faucibus mollis interdum. Vestibulum id ligula porta felis euismod
    semper. Vestibulum id ligula porta felis euismod semper. Aenean lacinia
    bibendum nulla sed consectetur.

    Donec id elit non mi porta gravida at eget metus. Vestibulum id ligula
    porta felis euismod semper. Praesent commodo cursus magna, vel scelerisque
    nisl consectetur et.


Headings
--------
.. code-block:: none

    # Largest heading
    ## Second largest heading
    ...
    ##### Very small heading


Text styles
-----------
::

    *Italic text*
    **Bold text**

Links
-----
::

    Check out [http://devilry.org](The devilry website).


Lists
-----

Unordered lists (bullet lists)::

    * This
    * is
    * a
    * test

Ordered lists (numbered lists)::

    1. Item one
    2. Item two
    3. Item three


Blockquotes
-----------
::

    As stated on the first page of the 101 guide:
    
    > You have to learn to walk before you can learn how to run



Advanced
========

Escape Markdown characters
--------------------------
If you want to use a special Markdown character in your document (such as
displaying literal asterisks), you can escape the character with a backslash.
Markdown will ignore the character directly after a backslash. Example::

    This is how the \_ (underscore) and \* asterisks characters look.


LaTeX Math
----------
Devilry Markdown supports LaTeX math through the MathJAX library/renderer. Examples::

    A simple example:
    $mathblock$
    ^3/_7
    $/mathblock$

    The Lorenz Equations:
    $mathblock$
    \begin{aligned}
    \dot{x} & = \sigma(y-x) \\\\
    \dot{y} & = \rho x - y - xz \\\\
    \dot{z} & = -\beta z + xy
    \end{aligned}
    $/mathblock$

You have to escape special Markdown characters such as ``\``, which
is why we have ``\\\\`` at the end of our lines in the example above instead of
just ``\\``.


Code blocks
-----------
You can easily show syntax highlighted code blocks::

    Java code:
    ``` java
    class HelloWorld {
        public static void main(String[] args) {
            System.out.println("Hello world");
        }
    }
    ```

    Python code:
    ``` python
    if __name__ == "__main__":
        print "Hello world"
    ```

    C code:
    ``` c
    #include<stdio.h>
    int main() {
        printf("Hello World");
        return 0;
    }
    ```

    C++ code:
    ``` c++
    #include <iostream>
    int main() {
        std::cout << "Hello World!";
        return 0;
    }
    ```

    HTML example:
    ``` html
    <html>
        <body>
            <h1>Hello world</h1>
        </body>
    </html>
    ```

    CSS example:
    ``` css
    body {
        background-color: pink;
        color: green;
        font-size: 80px;
    }
    ```

    Any code:
    ```
    for x in 1 through 3
        show x
    ```

Devilry supports `all languages supported by Pygments <http://pygments.org/languages/>`_.
