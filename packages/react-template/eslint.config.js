import { fixupConfigRules, fixupPluginRules } from "@eslint/compat";
import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import tsParser from "@typescript-eslint/parser";
import _import from "eslint-plugin-import";
import preferArrow from "eslint-plugin-prefer-arrow";
import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
	baseDirectory: __dirname,
	recommendedConfig: js.configs.recommended,
	allConfig: js.configs.all,
});

// eslint-disable-next-line import/no-anonymous-default-export
export default [
	{
		ignores: [
			"**/node_modules/",
			"**/dist/",
			"**/.vite/",
			"eslint.config.js",
			"vite.config.ts",
		],
		settings: {
			"import/resolver": {
				typescript: {}, // uses tsconfig paths (including @)
				node: {
					extensions: [".js", ".jsx", ".ts", ".tsx"],
				},
			},
		},
	},
	...fixupConfigRules(
		compat.extends(
			"prettier",
			"eslint:recommended",
			"plugin:import/recommended",
		),
	),
	{
		plugins: {
			"prefer-arrow": preferArrow,
			import: fixupPluginRules(_import),
		},
		languageOptions: {
			globals: {
				...globals.node,
				...globals.browser,
			},
			ecmaVersion: 2021,
			sourceType: "module",
			parserOptions: {
				babelOptions: {
					presets: ["@vitejs/plugin-react"],
				},
			},
		},
		rules: {
			"import/extensions": "error",
			"import/no-unresolved": "error",
			"import/prefer-default-export": "error",
			"import/no-duplicates": "error",
			complexity: ["error", 20],
			"max-lines": ["error", 300],
			"max-depth": ["error", 4],
			"max-params": ["error", 4],
			eqeqeq: ["error", "smart"],
			"import/no-extraneous-dependencies": [
				"error",
				{
					devDependencies: true,
					optionalDependencies: false,
					peerDependencies: false,
				},
			],
			"no-shadow": [
				"error",
				{
					hoist: "all",
				},
			],
			"prefer-const": "error",
			"import/order": [
				"error",
				{
					pathGroups: [
						{
							pattern: "@lib/**",
							group: "unknown",
						},
					],
					groups: [
						["external", "builtin"],
						"unknown",
						"internal",
						["parent", "sibling", "index"],
					],
					alphabetize: {
						order: "asc",
						caseInsensitive: false,
					},
					"newlines-between": "always",
					pathGroupsExcludedImportTypes: ["builtin"],
				},
			],
			"import/namespace": "off",
			"sort-imports": [
				"error",
				{
					ignoreCase: true,
					ignoreDeclarationSort: true,
					ignoreMemberSort: false,
					memberSyntaxSortOrder: ["none", "all", "multiple", "single"],
				},
			],
			"padding-line-between-statements": [
				"error",
				{
					blankLine: "always",
					prev: "*",
					next: "return",
				},
			],
			"prefer-arrow/prefer-arrow-functions": [
				"error",
				{
					disallowPrototype: true,
					singleReturnOnly: false,
					classPropertiesAllowed: false,
				},
			],
			"no-restricted-imports": [
				"error",
				{
					patterns: [
						{
							group: ["./*", "../*"],
							message:
								"Use @/ for imports from src/ instead of relative paths.",
						},
					],
					paths: [
						{
							name: "lodash",
							message: "Please use lodash/{module} import instead",
						},
						{
							name: "aws-sdk",
							message: "Please use aws-sdk/{module} import instead",
						},
						{
							name: ".",
							message: "Please use explicit import file",
						},
					],
				},
			],
			curly: ["error", "all"],
		},
	},
	...fixupConfigRules(
		compat.extends(
			"plugin:@typescript-eslint/recommended",
			"plugin:@typescript-eslint/recommended-requiring-type-checking",
			"plugin:import/typescript",
		),
	).map(config => ({
		...config,
		files: ["**/*.ts?(x)", "!vite.config.ts", "!eslint.config.js"],
		rules: {
			...config.rules,
			"@typescript-eslint/prefer-optional-chain": "error",
			"no-shadow": "off",
			"@typescript-eslint/no-shadow": "error",
			"@typescript-eslint/prefer-nullish-coalescing": "error",
			"@typescript-eslint/strict-boolean-expressions": [
				"error",
				{
					allowString: false,
					allowNumber: false,
					allowNullableObject: true,
				},
			],
			"@typescript-eslint/ban-ts-comment": [
				"error",
				{
					"ts-ignore": "allow-with-description",
					minimumDescriptionLength: 10,
				},
			],
			"@typescript-eslint/explicit-function-return-type": 0,
			"@typescript-eslint/explicit-member-accessibility": 0,
			"@typescript-eslint/camelcase": 0,
			"@typescript-eslint/interface-name-prefix": 0,
			"@typescript-eslint/explicit-module-boundary-types": "error",
			"@typescript-eslint/no-explicit-any": "error",
			"@typescript-eslint/no-unused-vars": "error",
			"@typescript-eslint/no-restricted-types": [
				"error",
				{
					types: {
						FC: {
							message:
								"Use `const MyComponent = (props: Props): JSX.Element` instead",
							fixWith: "JSX.Element",
						},
						SFC: {
							message:
								"Use `const MyComponent = (props: Props): JSX.Element` instead",
							fixWith: "JSX.Element",
						},
						FunctionComponent: {
							message:
								"Use `const MyComponent = (props: Props): JSX.Element` instead",
							fixWith: "JSX.Element",
						},
						"React.FC": {
							message:
								"Use `const MyComponent = (props: Props): JSX.Element` instead",
							fixWith: "JSX.Element",
						},
						"React.SFC": {
							message:
								"Use `const MyComponent = (props: Props): JSX.Element` instead",
							fixWith: "JSX.Element",
						},
						"React.FunctionComponent": {
							message:
								"Use `const MyComponent = (props: Props): JSX.Element` instead",
							fixWith: "JSX.Element",
						},
						extendDefaults: true,
					},
				},
			],
			"@typescript-eslint/no-unnecessary-boolean-literal-compare": "error",
			"@typescript-eslint/no-unnecessary-condition": "error",
			"@typescript-eslint/no-unnecessary-type-arguments": "error",
			"@typescript-eslint/prefer-string-starts-ends-with": "error",
			"@typescript-eslint/switch-exhaustiveness-check": "error",
			"@typescript-eslint/restrict-template-expressions": [
				"error",
				{
					allowNumber: true,
					allowBoolean: true,
				},
			],
		},
		languageOptions: {
			...config.languageOptions,
			parser: tsParser,
			parserOptions: {
				...config.languageOptions?.parserOptions,
				project: "./tsconfig.eslint.json",
				tsconfigRootDir: ".",
			},
		},
	})),
	{
		files: ["eslint.config.js", "vite.config.ts"],
		languageOptions: {
			parser: tsParser,
			ecmaVersion: 2021,
			sourceType: "module",
			parserOptions: {},
		},
		rules: {
			"no-restricted-imports": [
				"error",
				{
					patterns: [
						{
							group: ["./src/*", "../src/*"],
							message: "Use @/ for imports from src/",
						},
					],
				},
			],
		},
	},
];
