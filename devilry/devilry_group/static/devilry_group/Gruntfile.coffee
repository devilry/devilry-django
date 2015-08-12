module.exports = (grunt) ->
  grunt.initConfig
    pkg: grunt.file.readJSON('package.json')
    uglify:
      build:
        src: 'src/js/<%= pkg.name %>.js'
        dest: 'build/<%= pkg.name %>.min.js'
    coffee:
      compileJoined:
        options:
          join: true
        files:
          'src/js/<%= pkg.name %>.js':
            [
              'src/coffee/*.coffee'
            ]
    watch:
      files: 'src/coffee/*.coffee'
      tasks:
        [
          'coffee',
          'uglify'
        ]

  grunt.loadNpmTasks 'grunt-contrib-coffee'
  grunt.loadNpmTasks 'grunt-contrib-watch'
  grunt.loadNpmTasks 'grunt-contrib-uglify'

  grunt.registerTask 'default', ['coffee', 'uglify', 'watch']

  return