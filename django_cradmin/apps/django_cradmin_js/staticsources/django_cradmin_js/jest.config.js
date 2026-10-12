module.exports = {
  verbose: false,
  roots: ['<rootDir>/lib/'],
  testPathIgnorePatterns: [
    "/node_modules/"
  ],
  transform: {
    "\\.jsx?$": "babel-jest",
  },
  transformIgnorePatterns: ['/node_modules/(?!(ievv_jsbase)/)'],
  // transformIgnorePatterns: ['/node_modules/(?!(sinon|module1|module2)/)'],
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ["<rootDir>/config/jest/test-setup.js"]
}
