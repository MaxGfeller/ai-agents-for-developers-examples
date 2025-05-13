const plugin = {
  rules: {
    // 'custom-rule': require('./src/create_lint_rule/generated/custom-rule.js')
  },
};

module.exports = [
  {
    name: 'local-rules',
    files: ['**/*.js', '**/*.jsx'],
    plugins: {
      example: plugin,
    },
    rules: {
      // 'example/custom-rule': 'error',
    },
  },
];