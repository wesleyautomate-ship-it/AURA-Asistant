# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Fixed infinite loop issue in Dashboard component caused by improper Zustand store initialization
- Added proper window checks to prevent SSR issues with localStorage access in store initialization
- Added useEffect hook to Dashboard component to ensure proper store hydration on mount
- Fixed auth token initialization in authStore to prevent re-renders during store setup

### Technical Details
- Updated `commandStore.ts` to include `typeof window !== "undefined"` checks before accessing localStorage
- Updated `authStore.ts` to properly handle token initialization with localStorage safety checks
- Added initialization effect in `Dashboard.tsx` to prevent render-time store mutations

## [Previous Versions]
- For previous version history, see Git commit log