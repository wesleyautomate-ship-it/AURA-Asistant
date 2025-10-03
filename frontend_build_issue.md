# Frontend Docker Build Investigation

## Context
- Objective: build the unified web frontend inside Docker Desktop and run Playwright for visual validation.
- Workspace: client/ monorepo with npm workspaces (@propertypro/* packages).
- Build path: staging working dir C:\temp\realtor_workspace_build, Dockerfile targets client/apps/web using npm workspaces.

## What we tried
- Generated workspace-aware installs locally (
pm install --workspaces --include-workspace-root).
- Replaced workspace:* specifiers with ile: links so npm can install inside Docker without a root lockfile.
- Ensured Vite’s aliases resolve to the new shared packages and added a compat shim for eact-native-web.
- Rebuilt the Docker image repeatedly with the updated workspace tree.

## Blocking issue
- During the Docker 
pm run build --workspace @propertypro/web step, Vite/rollup fails to resolve the eact-native-web import (required transitively by expo-constants).
- The module exists in 
ode_modules, but when Vite runs in the container it treats eact-native-web as a bare module and looks for a file named exactly eact-native-web, not the compiled entry.
- Attempts to alias eact-native-web to 
ode_modules/react-native-web/dist/index.js (or our shim) still result in Vite’s load-fallback complaining because it bypasses the alias when processing dependency code.

## Current state
- Local 
pm run build --workspace @propertypro/web succeeds outside Docker after the alias adjustments.
- Inside Docker, the build consistently stops with ENOENT: no such file or directory, open 'react-native-web' while bundling expo-constants.
- Without a successful container build we cannot launch the frontend service via Docker nor run Playwright against it.

## Next steps we paused on
1. Decide whether to vendor or pre-bundle eact-native-web (or remove the expo dependency) so the container build can resolve the module.
2. Once Docker builds cleanly, rerun the Playwright suite using the containerized frontend as the target.
