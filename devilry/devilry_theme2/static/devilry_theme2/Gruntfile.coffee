module.exports = (grunt) ->
  # Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json')
    delta:
      less:
        tasks: 'less'
        files: ['less/*.less', 'less/**/*.less']
    less:
      development:
        options:
          paths: ["less", "bower_components"]
        files:
          "css/styles.css": "less/styles.less"
  })

  grunt.loadNpmTasks('grunt-contrib-watch')
  grunt.loadNpmTasks('grunt-contrib-less')

  grunt.registerTask('build', [
    'less'
  ])

  grunt.renameTask('watch', 'delta')
  grunt.registerTask('watch', [
    'build'
    'delta'
  ])

  grunt.registerTask('default', [
    'build'
  ])
