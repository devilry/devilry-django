module.exports = (grunt) ->
  # Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json')
    watch:
      less:
        tasks: 'less'
        files: ['less/*.less', 'less/views/*.less']
    less:
      development:
        options:
          paths: ["less", "bower_components"]
        files:
          "css/styles.css": "less/styles.less"
  })

  grunt.loadNpmTasks('grunt-contrib-watch')
  grunt.loadNpmTasks('grunt-contrib-less')
  grunt.registerTask('default', [
    'less'
  ])
