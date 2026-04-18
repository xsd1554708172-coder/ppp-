# Windows Auto Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Windows Task Scheduler based auto-sync so the local PPP manuscript workspace can update from GitHub without keeping Codex open.

**Architecture:** Reuse the existing safe sync scripts and wrap them in Windows scheduled tasks. One task runs at user logon for immediate catch-up; another runs every 5 minutes for continued checks. Both invoke the same guarded sync checker, which refuses to overwrite a dirty local working tree.

**Tech Stack:** PowerShell, Windows Task Scheduler (`schtasks`), existing Git sync scripts, tracked remote signal file, local ignored state files.

---

### Task 1: Add task registration wrappers and docs

**Files:**
- Create: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/修改稿/scripts/run_hidden_sync_check.cmd`
- Create: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/修改稿/scripts/register_windows_remote_sync_tasks.ps1`
- Create: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/修改稿/scripts/unregister_windows_remote_sync_tasks.ps1`
- Modify: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/00_环境说明与索引/03_Git与运行环境同步说明_20260419.md`
- Modify: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/00_环境说明与索引/02_文件定位清单_20260419.md`
- Modify: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/修改稿/README_版本留底与Git同步规则.md`

- [ ] **Step 1: Create a hidden launcher for scheduled tasks**
- [ ] **Step 2: Create a registration script that installs two tasks**
- [ ] **Step 3: Create an unregister script for cleanup**
- [ ] **Step 4: Update workspace docs and locator files**

### Task 2: Register and verify Windows scheduled tasks

**Files:**
- Test: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/修改稿/scripts/register_windows_remote_sync_tasks.ps1`
- Test: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/修改稿/scripts/check_remote_signal_and_sync.ps1`
- Test: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/00_环境说明与索引/LOCAL_SYNC_STATE.json`

- [ ] **Step 1: Register the on-logon task**
- [ ] **Step 2: Register the every-5-minutes task**
- [ ] **Step 3: Manually run the on-logon task once**
- [ ] **Step 4: Verify the task entries exist and the local sync state updates**

### Task 3: Commit and push the automation changes

**Files:**
- Modify: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/.gitignore` (only if needed)
- Test: `C:/Users/陈楚玲/Desktop/ppp论文数据/codex项目/.git`

- [ ] **Step 1: Verify working tree changes**
- [ ] **Step 2: Commit with a task-scheduler specific message**
- [ ] **Step 3: Push to `origin/main`**
- [ ] **Step 4: Re-run verification commands and report actual task names and status**
