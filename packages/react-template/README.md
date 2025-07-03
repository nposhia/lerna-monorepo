# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:


```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```

## React Router v6+
This project demonstrates the usage of **React Router v6+** with examples of **static**, **dynamic**, **nested**, and **protected** routes using simple dummy components like `Home`, `About`, `Dashboard`, and more.

Feel free to **add**, **update**, or **remove** routes and components as per your project needs.

---

## 📁 Route Types Implemented

### ✅ Static Routes
Routes that load fixed components.

- `/` → `Home`
- `/about` → `About`

### ✅ Dynamic Routes
Routes that take parameters from the URL.

- `/user/:id` → `UserProfile` (displays user based on dynamic `id`)

### ✅ Nested Routes
Routes within a layout (e.g. Dashboard).

- `/dashboard/user` → `UserDashboard`

### ✅ Protected Routes
Routes that require authentication before access.

- `/admin` → Renders `AdminDashboard` only if user is admin
  - Uses `ProtectedRoute` wrapper

### ✅ Catch-All Route (404)
Handles unknown paths.

- `*` → `NotFound`

---

## 🧱 Dummy Components Included

- `Home.tsx` – Landing page
- `About.tsx` – Static content
- `UserProfile.tsx` – Dynamic user info
- `Dashboard.tsx` – Layout with nested `<Outlet />`
- `UserDashboard.tsx` - Child for nested
- `AdminDashboard.tsx` – Example of protected content
- `NotFound.tsx` – 404 page

---

## 🔐 Protected Route Logic

The `ProtectedRoute.tsx` is a wrapper to protecte routes to check of user is admin or not. Currently the admin values is set to true but we can use a variable as per our need.

