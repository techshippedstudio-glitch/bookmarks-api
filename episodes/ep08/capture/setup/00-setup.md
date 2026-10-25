# ep08 setup capture (coordinator)

$ specify version
              ███████╗██████╗ ███████╗ ██████╗██╗███████╗██╗   ██╗              
              ██╔════╝██╔══██╗██╔════╝██╔════╝██║██╔════╝╚██╗ ██╔╝              
              ███████╗██████╔╝█████╗  ██║     ██║█████╗   ╚████╔╝               
              ╚════██║██╔═══╝ ██╔══╝  ██║     ██║██╔══╝    ╚██╔╝                
              ███████║██║     ███████╗╚██████╗██║██║        ██║                 
              ╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝╚═╝        ╚═╝                 
                                                                                
               GitHub Spec Kit - Spec-Driven Development Toolkit                

╭────────────────────────── Specify CLI Information ───────────────────────────╮
│                                                                              │
│     CLI Version    1.2.2                                                     │
│                                                                              │
│          Python    3.13.17                                                   │
│        Platform    Linux                                                     │
│    Architecture    x86_64                                                    │
│      OS Version    #1 SMP PREEMPT_DYNAMIC @0                                 │
│         OpenSSL    OpenSSL 3.5.9 29 Sep 2026                                 │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯


$ git rev-parse --short HEAD
48f6e31

$ ls .specify
.
..
.gitignore
init-options.json
integration.json
integrations
memory
scripts
templates
workflows

$ specify extension add git

✓ Extension installed successfully!

Git Branching Workflow (v1.0.1)
  Feature branch creation, numbering (sequential/timestamp), templating, 
validation, and Git remote detection

Provided commands:
  • speckit-git-feature - Create a feature branch with sequential or timestamp 
numbering and optional templates
  • speckit-git-validate - Validate current branch follows feature branch naming
conventions
  • speckit-git-remote - Detect Git remote URL for GitHub integration
  • speckit-git-initialize - Initialize a Git repository with an initial commit
  • speckit-git-commit - Auto-commit changes after a Spec Kit command completes

Config files already exist (preserved): git-config.yml

$ git status --short
?? .claude/skills/speckit-git-commit/
?? .claude/skills/speckit-git-feature/
?? .claude/skills/speckit-git-initialize/
?? .claude/skills/speckit-git-remote/
?? .claude/skills/speckit-git-validate/
?? .specify/extensions.yml
?? .specify/extensions/

## Config change (coordinator): auto_commit enabled for after_specify, after_clarify, after_plan, after_tasks, after_implement, after_checklist; default false; after_analyze off

$ git diff --no-index .specify/extensions/git/config-template.yml .specify/extensions/git/git-config.yml
diff --git a/.specify/extensions/git/config-template.yml b/.specify/extensions/git/git-config.yml
index 2ea3471..c75c98a 100644
--- a/.specify/extensions/git/config-template.yml
+++ b/.specify/extensions/git/git-config.yml
@@ -54,22 +54,22 @@ auto_commit:
     enabled: false
     message: "[Spec Kit] Add project constitution"
   after_specify:
-    enabled: false
+    enabled: true
     message: "[Spec Kit] Add specification"
   after_clarify:
-    enabled: false
+    enabled: true
     message: "[Spec Kit] Clarify specification"
   after_plan:
-    enabled: false
+    enabled: true
     message: "[Spec Kit] Add implementation plan"
   after_tasks:
-    enabled: false
+    enabled: true
     message: "[Spec Kit] Add tasks"
   after_implement:
-    enabled: false
+    enabled: true
     message: "[Spec Kit] Implementation progress"
   after_checklist:
-    enabled: false
+    enabled: true
     message: "[Spec Kit] Add checklist"
   after_analyze:
     enabled: false

$ cat .specify/extensions.yml
installed:
- git
settings:
  auto_execute_hooks: true
hooks:
  before_constitution:
  - extension: git
    command: speckit.git.initialize
    enabled: true
    optional: false
    priority: 10
    prompt: Execute speckit.git.initialize?
    description: Initialize Git repository before constitution setup
    condition: null
  before_specify:
  - extension: git
    command: speckit.git.feature
    enabled: true
    optional: false
    priority: 10
    prompt: Execute speckit.git.feature?
    description: Create feature branch before specification
    condition: null
  before_clarify:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit outstanding changes before clarification?
    description: Auto-commit before spec clarification
    condition: null
  before_plan:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit outstanding changes before planning?
    description: Auto-commit before implementation planning
    condition: null
  before_tasks:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit outstanding changes before task generation?
    description: Auto-commit before task generation
    condition: null
  before_implement:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit outstanding changes before implementation?
    description: Auto-commit before implementation
    condition: null
  before_checklist:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit outstanding changes before checklist?
    description: Auto-commit before checklist generation
    condition: null
  before_analyze:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit outstanding changes before analysis?
    description: Auto-commit before analysis
    condition: null
  before_taskstoissues:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit outstanding changes before issue sync?
    description: Auto-commit before tasks-to-issues conversion
    condition: null
  after_constitution:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit constitution changes?
    description: Auto-commit after constitution update
    condition: null
  after_specify:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit specification changes?
    description: Auto-commit after specification
    condition: null
  after_clarify:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit clarification changes?
    description: Auto-commit after spec clarification
    condition: null
  after_plan:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit plan changes?
    description: Auto-commit after implementation planning
    condition: null
  after_tasks:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit task changes?
    description: Auto-commit after task generation
    condition: null
  after_implement:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit implementation changes?
    description: Auto-commit after implementation
    condition: null
  after_checklist:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit checklist changes?
    description: Auto-commit after checklist generation
    condition: null
  after_analyze:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit analysis results?
    description: Auto-commit after analysis
    condition: null
  after_taskstoissues:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    priority: 10
    prompt: Commit after syncing issues?
    description: Auto-commit after tasks-to-issues conversion
    condition: null

$ git show --stat HEAD
ba2fdc9 Tech Shipped <techshippedstudio-glitch@users.noreply.github.com> ep08 setup: add Spec Kit git extension (1.2.2), auto-commit after specify, clarify, plan, checklist, tasks, implement

 .claude/skills/speckit-git-commit/SKILL.md         |  68 +++
 .claude/skills/speckit-git-feature/SKILL.md        |  87 +++
 .claude/skills/speckit-git-initialize/SKILL.md     |  54 ++
 .claude/skills/speckit-git-remote/SKILL.md         |  50 ++
 .claude/skills/speckit-git-validate/SKILL.md       |  54 ++
 .specify/extensions.yml                            | 167 ++++++
 .specify/extensions/.registry                      |  23 +
 .specify/extensions/git/README.md                  | 119 ++++
 .../extensions/git/commands/speckit.git.commit.md  |  63 ++
 .../extensions/git/commands/speckit.git.feature.md |  82 +++
 .../git/commands/speckit.git.initialize.md         |  49 ++
 .../extensions/git/commands/speckit.git.remote.md  |  45 ++
 .../git/commands/speckit.git.validate.md           |  49 ++
 .specify/extensions/git/config-template.yml        |  79 +++
 .specify/extensions/git/extension.yml              | 142 +++++
 .specify/extensions/git/git-config.yml             |  79 +++
 .../extensions/git/scripts/bash/auto-commit.sh     | 211 +++++++
 .../git/scripts/bash/create-new-feature-branch.sh  | 639 ++++++++++++++++++++
 .specify/extensions/git/scripts/bash/git-common.sh |  56 ++
 .../extensions/git/scripts/bash/initialize-repo.sh |  54 ++
 .../git/scripts/powershell/auto-commit.ps1         | 230 ++++++++
 .../powershell/create-new-feature-branch.ps1       | 594 +++++++++++++++++++
 .../git/scripts/powershell/git-common.ps1          |  52 ++
 .../git/scripts/powershell/initialize-repo.ps1     |  69 +++
 .../extensions/git/scripts/python/auto_commit.py   | 195 +++++++
 .../scripts/python/create_new_feature_branch.py    | 641 +++++++++++++++++++++
 .../extensions/git/scripts/python/git_common.py    |  81 +++
 .../git/scripts/python/initialize_repo.py          |  89 +++
 28 files changed, 4121 insertions(+)
