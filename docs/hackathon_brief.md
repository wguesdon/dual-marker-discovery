# 2026 Built with Claude: Life Sciences — Participant Guide

Event page: https://cerebralvalley.ai/e/built-with-claude-life-sciences

## 1. Connect with the Community

### Discord
Join: https://anthropic.com/discord
A custom role is assigned to your Discord handle so you can see hackathon-specific channels. Ping @CV in `#hackathon-access` if you do not receive the Hackathon Participant role within a few hours.

## 2. Schedule (all times ET)

- **Tue July 7**
  - 12:00 PM — Virtual Kickoff (rules, prizes, judging, technical talks)
  - 12:30 PM — Hacking begins; team formation on Discord
  - 5:00–6:00 PM — Anthropic office hours (`#office-hours`)
- **Wed July 8**
  - 12:00–1:00 PM — Live Session One: Overview of Claude Science, Alexander Tarashansky (Member of Technical Staff, Anthropic)
  - 5:00–6:00 PM — Office hours
- **Thu July 9**
  - 5:00–6:00 PM — Office hours
- **Fri July 10**
  - 12:00–1:00 PM — Live Session Two: "From genome to inference without touching a pipette", Sukrit Silas (Assistant Investigator, Gladstone Institutes)
  - 5:00–6:00 PM — Office hours
- **Sat July 11** — Hacking continues
- **Sun July 12** — Hacking continues
- **Mon July 13**
  - **9:00 PM — Submissions due via CV platform**
- **Tue July 14** — First round judging
- **Wed July 15** — First round judging
- **Thu July 16**
  - 12:00 PM — Final round judging; top 6 teams announced (`#announcements`)
  - 1:30 PM — Closing ceremony; top 3 revealed

## 3. Rules

- **Open Source:** Everything submitted must be open-sourced under an approved OSS license.
- **New Work Only:** Projects must be started from scratch during the hackathon. Researchers may start from an existing question and public datasets, but the analysis must happen during the event.
- **Team Size:** Up to 2 members.
- **Banned Projects:** Disqualified if they violate legal, ethical, or platform policies, or use code/data/assets you do not have rights to.

## 4. Problem Statements & Example Projects

### [Researcher Track] Build From the Bench
Using Claude Science, start from a biological question you've been thinking through and find the existing datasets and tools needed to answer it. Submit something discrete — a finding, a trained model, an analysis others can reproduce — and show how Claude Science got you there.

Optional Gladstone starting datasets:
- New drug targets in the CD4+ T cell Perturb-seq data (Alex Marson's lab). Dataset: https://virtualcellmodels.cziscience.com/dataset/genome-scale-tcell-perturb-seq — code: https://github.com/emdann/GWT_perturbseq_analysis_2025 — preprint: https://www.biorxiv.org/content/10.64898/2025.12.23.696273v1
- Predict what a noncoding variant does to chromatin in a cell type you care about (Ryan Corces's lab). Corces Resources: https://www.corceslab.com/pages/Resources/ — ChromBPNet: https://github.com/kundajelab/chrombpnet — ENCODE: https://www.encodeproject.org/
- Regions deeply conserved across mammals but changed rapidly in humans (Katie Pollard's Zoonomia constraint scores): https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons241way — Human Accelerated Regions: https://www.biorxiv.org/content/10.1101/2022.10.04.510859v1

### [Builder Track] Build Beyond the Bench
Using Claude Code, start from a named user (scientist, lab, clinic, biotech) and build the tool they're missing: working software they could use without you in the room.

Optional Gladstone idea starters:
- A lab notebook companion turning voice memos / rough bench notes into structured, searchable experiment records with protocols, reagents, and outcomes auto-tagged.
- A clinical trial matcher taking free-text patient notes and surfacing eligible trials from ClinicalTrials.gov with inclusion/exclusion reasoning per match.
- A pipeline translator wrapping an existing command-line analysis pipeline in an interface a bench scientist can run without the terminal.

## 5. Anthropic-Provided Resources

### Quickstarts
- Claude Science Get Started: https://claude.com/docs/claude-science/get-started
- Claude Code Quickstart: https://code.claude.com/docs/en/quickstart
- Claude API Quickstart: https://platform.claude.com/docs/en/get-started
- Claude Models Overview: https://platform.claude.com/docs/en/about-claude/models/overview

### Docs
- Claude Science Docs: https://claude.com/docs/claude-science/overview
- Claude Code Docs: https://code.claude.com/docs
- Claude API Docs: https://platform.claude.com/docs/en/home
- MCP Docs: https://modelcontextprotocol.io/docs/getting-started/intro
- Agent Skills Docs: https://agentskills.io/home

### Blogs
- Claude Science announcement: https://www.anthropic.com/news/claude-science-ai-workbench
- Claude Code Best Practices: https://code.claude.com/docs/en/best-practices
- Building Effective Agents: https://www.anthropic.com/engineering/building-effective-agents
- Building Agents with the Claude Agent SDK: https://claude.com/blog/building-agents-with-the-claude-agent-sdk
- Building multi-agent systems: https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them
- Best practices for prompt engineering: https://claude.com/blog/best-practices-for-prompt-engineering
- Effective Context Engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Extending Claude's capabilities with skills and MCP servers: https://claude.com/blog/extending-claude-capabilities-with-skills-mcp-servers
- Skills explained: https://claude.com/blog/skills-explained
- Building agents with Skills: https://claude.com/blog/building-agents-with-skills-equipping-agents-for-specialized-work
- How to configure hooks: https://claude.com/blog/how-to-configure-hooks

### Courses
- Claude Code in Action: https://anthropic.skilljar.com/claude-code-in-action
- Agent Skills with Anthropic: https://www.deeplearning.ai/short-courses/agent-skills-with-anthropic/
- Claude Code Courses GitHub: https://github.com/anthropics/courses

### Other
- Claude Quickstarts: https://github.com/anthropics/claude-quickstarts
- Claude Science Product overview: https://claude.com/product/claude-science
- A Complete Guide to Building Skills for Claude (eBook): https://claude.com/blog/complete-guide-to-building-skills-for-claude
- Claude Cookbooks: https://platform.claude.com/cookbook/ — repo: https://github.com/anthropics/claude-cookbooks
- Agent Skills GitHub Repo: https://github.com/anthropics/skills

## 6. Judging

Two stages.

### Stage 1 — Asynchronous Judging (Tue July 14 – Wed July 15)
Judges review submitted projects asynchronously via the judging platform. Each team uploads:
1. Short demo video (3 minute maximum)
2. Open-source project repository, notebook, or research write-up
3. Written summary (100–200 words)

Judges independently evaluate using standardized criteria. Scores aggregate to determine the Top 3 projects per track for the final round.

**Criteria:**
1. **Impact (25%)** — Real-world potential. Who benefits, how much does it matter? Builder: could people use this? Researcher: is this a finding or analysis others can build on? Does it fit the track's problem statement?
2. **Claude Use (25%)** — How creatively the team used Claude Code. Beyond a basic application? Surfaced surprising capabilities?
3. **Depth & Execution (20%)** — Pushed past the first idea? Sound, refined engineering? Real craft, not a quick hack.
4. **Demo (30%)** — Working, compelling demo. Does it hold up as software or as trustworthy findings? Cool to watch?

### Stage 2 — Final Round Live Judging (Thu July 16, 12:00 PM ET)
Pre-recorded demos play (3 minutes per team). Judges deliberate to determine winners and runners-up per category. Winners, runners-up, and special prize winners announced at the 1:30 PM closing ceremony.

## 7. Submission Instructions

Required:
- 3-minute demo video (YouTube, Loom, or similar)
- GitHub repository, notebook, or research write-up
- Written description / summary

Deadline: **July 13, 9:00 PM ET.** Project must be built entirely during the hackathon; no pre-existing work. Researchers may start from an existing question and public datasets, but the analysis must happen during the event.

## 8. Prizes

### Research Track
- 1st — $30,000 in usage credits
- 2nd — $10,000 in usage credits
- 3rd — $5,000 in usage credits

### Builder Track
- 1st — $30,000 in API credits
- 2nd — $10,000 in API credits
- 3rd — $5,000 in API credits

### Gladstone Institutes Award — $10k usage credits
Recognizes the research project with the most potential to advance the field. Hand-selected by the Gladstone Institutes team.

Questions: `#questions` or the moderators.
