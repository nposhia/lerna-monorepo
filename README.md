
# 📚 **Lerna Monorepo**

A **full-stack monorepo** managed with **Lerna** — combining a **React** frontend and a **FastAPI** backend.

---

## 📋 **Table of Contents**

* [Steps](#steps)

  * [Step 1: Create an empty monorepo](#step-1-create-an-empty-monorepo)
  * [Step 2: Bring in existing repos](#step-2-bring-in-existing-repos)
  * [Step 3: Check Node structure](#step-3-check-node-structure)
  * [Step 4: Install dependencies](#step-4-install-dependencies)
* [Usage](#usage)

  * [Run frontend](#run-frontend)
  * [Run backend](#run-backend)
  * [Run with Lerna](#run-with-lerna)

---

## ✅ **Steps**

---

### 📁 **Step 1: Create an empty monorepo**

```bash
# Create root folder
mkdir lerna-monorepo
cd lerna-monorepo

# Initialize Git
git init

# Initialize Lerna
npx lerna init
```

---

**Root `package.json`:**

```json
{
  "private": true,
  "workspaces": ["packages/*"]
}
```

---

**`lerna.json`:**

```json
{
  "packages": ["packages/*"],
  "version": "independent",
  "useWorkspaces": true
}
```

---

### 📂 **Step 2: Bring in existing repos**

```bash
cd packages

# Clone existing repos
git clone https://github.com/JeavioLLC/fastapi-base-template-repository.git
git clone https://github.com/JeavioLLC/react-template.git
```

---

### 🔍 **Step 3: Check Node structure**

✅ **Frontend:**

```plaintext
react-template/
 ├── package.json
 ├── src/
 ├── ...
```

* **Must** have a valid `package.json`. Lerna will auto-detect it as a workspace.

---

✅ **Backend (Python):**

* Does **not** need a `package.json` by default.
* **But**, if you want to run backend Docker commands via Lerna, add **one**:

**Example `packages/fastapi-base-template-repository/package.json`:**

```json
{
  "name": "fastapi-base-template-repository",
  "version": "1.0.0",
  "scripts": {
    "destroy": "docker compose -f devops/local/docker-compose.yml down -v",
    "dev": "docker compose -f devops/local/docker-compose.yml --env-file devops/local/.env.docker up --build"
  }
}
```

---

This lets you run backend Docker containers **via Lerna**:

```bash
npx lerna run dev --scope fastapi-base-template-repository
npx lerna run destroy --scope fastapi-base-template-repository
```

---

### 📦 **Step 4: Install dependencies**

At the monorepo root:

```bash
npm install
```

This will install root and workspace dependencies and link them.

---

## ⚙️ **Usage**

---

### ⚡ **Run frontend**

```bash
# From monorepo root:
cd packages/react-template

npm run dev
```

---

### ⚡ **Run backend**

```bash
# From monorepo root:
cd packages/fastapi-base-template-repository

# Or manually with Makefile
make up
```

---

### ⚡ **Run with Lerna**

```bash
# Run frontend build:
npx lerna run build --scope tailwindcss4

# Run backend Docker:
npx lerna run dev --scope fastapi-base-template-repository

# Destroy backend containers:
npx lerna run destroy --scope fastapi-base-template-repository
```

---

