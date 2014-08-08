# $ext_path: This should be the path of the Ext JS SDK relative to this file
#$ext_path = "../../../../extjshelpers/static/extjshelpers/extjs"
#$ext_path = "../../../../../devilry/devilry/apps/extjshelpers/static/extjshelpers/extjs"
$ext_path = "../../../../../../../devenv/parts/omelette/extjs4/static/extjs4/"

this_dir = File.dirname(__FILE__)

# sass_path: the directory your Sass files are in. THIS file should also be in the Sass folder
# Generally this will be in a resources/sass folder
# <root>/resources/sass
sass_path = File.join(this_dir)

# css_path: the directory you want your CSS files to be.
# Generally this is a folder in the parent directory of your Sass files
# <root>/resources/css
#css_path = File.join(this_dir, "stylesheets")
css_path = File.join(this_dir, "..",  "stylesheets")

# output_style: The output style for your compiled CSS
# nested, expanded, compact, compressed
# More information can be found here http://sass-lang.com/docs/yardoc/file.SASS_REFERENCE.html#output_style
output_style = :expanded

$django_extjs4_images_dir = "../images/";

# We need to load in the Ext4 themes folder, which includes all it's default styling, images, variables and mixins
load File.join(File.dirname(__FILE__), $ext_path, 'resources', 'themes')
