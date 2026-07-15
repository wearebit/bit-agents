// ESLint (flat config, ESLint 9+) enforcing the mechanically-checkable
// coding-standards rules for TypeScript/JavaScript. Install the peer deps and
// run `npx eslint .`:
//
//   npm i -D eslint typescript-eslint eslint-plugin-jsdoc
//
// The numeric limits below match the standard exactly (50 lines/function,
// 250 lines/file, <=5 params, <=3 nesting levels). See linting/SKILL.md
// for how each rule maps to a standard, and for the legacy .eslintrc form.

import tseslint from "typescript-eslint";
import jsdoc from "eslint-plugin-jsdoc";

export default tseslint.config(
  {
    files: ["**/*.{ts,tsx,js,jsx,mjs,cjs}"],
    plugins: { jsdoc },
    extends: [...tseslint.configs.recommended],
    rules: {
      // Size and shape -> rules 1, 3 and "few params / shallow nesting"
      "max-lines": ["warn", { max: 250, skipBlankLines: true, skipComments: true }],
      "max-lines-per-function": ["warn", { max: 50, skipBlankLines: true, skipComments: true }],
      "max-params": ["warn", 5],
      "max-depth": ["warn", 3],
      "complexity": ["warn", 8],

      // Named constants over magic numbers -> rule 11 (0/1/-1 and indexes are fine)
      "no-magic-numbers": ["warn", { ignore: [-1, 0, 1], ignoreArrayIndexes: true, enforceConst: true }],

      // Error handling -> rule 7: no silently-empty catch blocks
      "no-empty": ["warn", { allowEmptyCatch: false }],

      // Dead code -> "no dead code"
      "@typescript-eslint/no-unused-vars": "warn",

      // Naming -> rule 4: camelCase members, PascalCase types
      "@typescript-eslint/naming-convention": [
        "warn",
        { selector: "variableLike", format: ["camelCase", "UPPER_CASE"], leadingUnderscore: "allow" },
        { selector: "typeLike", format: ["PascalCase"] },
      ],

      // Docstring presence -> rules 5, 6 (content quality is left to the skill)
      "jsdoc/require-jsdoc": [
        "warn",
        { require: { FunctionDeclaration: true, MethodDefinition: true, ClassDeclaration: true } },
      ],
      "jsdoc/require-param": "warn",
      "jsdoc/require-returns": "warn",
    },
  },
);
