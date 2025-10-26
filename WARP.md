# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This repository generates a French-language weekly newsletter called **"Growth Weekly"** that aggregates and summarizes growth marketing news from 13+ curated sources. The project is AI-assisted, using tools to scan emails and scrape web sources, then format the content into a clean, responsive HTML newsletter.

## Repository Structure

```
.
├── prompt revue fr.md        # AI instructions for newsletter generation
├── revue fr template.html    # HTML/CSS/JS template for newsletter output
└── WARP.md                   # This file
```

### Key Files

**`prompt revue fr.md`**
- Contains the complete workflow instructions for newsletter generation
- Defines 13+ growth marketing sources to aggregate (TLDR Marketing, Elena Verna, Demand Curve, Kyle Poyar, etc.)
- Specifies output requirements: 25+ news items in French, categorized by priority
- Lists fallback URLs for web scraping if email sources aren't available

**`revue fr template.html`**
- Self-contained, single-file HTML template with embedded CSS and JavaScript
- Uses inline Tailwind-like utility classes for responsive design
- JavaScript dynamically renders news items from a data structure
- Three-category layout: Critical (red), Important (yellow), Good to Know (green)
- Includes fade-in animations and mobile-responsive breakpoints

## Newsletter Generation Workflow

### Content Sources Priority
1. **Primary**: Scan Gmail for newsletters from the week that just ended
2. **Fallback**: Scrape websites if email newsletters aren't found

### Required Tools
When generating newsletters, use these MCP/scraping tools:
- `firecrawl_scrape` or `firecrawl_search` (preferred for web scraping)
- `tavily-search` or `tavily-extract` (for additional content)
- `fetch` (basic URL fetching)
- `scrape_as_markdown` or `scrape_batch` (alternative scrapers)
- `browser_*` tools (Playwright browser automation if needed)
- `sequentialthinking` (for complex multi-source aggregation)

### Content Requirements

**Output Format**:
- Language: French
- Title: "Growth Weekly" (fixed)
- 25+ news items minimum
- Three priority categories with 8-16 items each:
  - **Critical** (8 items): Red accent, most important news
  - **Important** (8 items): Yellow accent, significant updates
  - **Good to Know** (9+ items): Green accent, noteworthy information

**Each News Item Must Include**:
- Numbered ranking (01-25+)
- Title with hyperlink to original source (precise, unique URL)
- Two-line description/summary
- Source attribution

**Header Section**:
- Title: "Growth Weekly"
- Byline: "by Dagorsey & Claude"
- Week date range (start and end dates)
- Note: "Sources available at end of newsletter"

**Footer Section**:
- List all sources used for the specific newsletter edition

### Source Balance
The prompt emphasizes **balanced representation** across all 13+ sources. When generating content, ensure:
- All newsletters/sources are scanned
- No single source dominates the output
- Distribution is roughly equal across categories

## Curated Growth Marketing Sources

### Email Newsletters
- TLDR Marketing
- Elena Verna / Elena's Growth Scoop
- Demand Curve
- Maja Voje
- Kyle Poyar (Growth Unhinged)
- Timothe from How They Build
- Kate Syuma (Growth Mates)
- Ben at Next Play
- Kevin DePopas
- The Growth Newsletter
- Yann Leonardi - La GROWTH Semaine
- Growth with Sean Ellis
- Indie Hackers
- Amanda at SparkToro

### Web Sources (with URLs)
When emails aren't available, scrape these sites:
- Elena Verna: https://substack.com/@plggrowth, https://www.elenaverna.com/
- Demand Curve: https://www.demandcurve.com/playbooks, /blog, /newsletter, /growth/intro
- Maja Voje: https://knowledge.gtmstrategist.com/
- Kyle Poyar: https://www.growthunhinged.com/
- Timothe: https://timfrin.substack.com/
- Kate Syuma: https://www.growthmates.news/
- Ben: https://nextplayso.substack.com/
- Yann Leonardi: https://lagrowthsemaine.substack.com/
- Sean Ellis: https://seanellis.substack.com/
- Indie Hackers: https://www.indiehackers.com/
- TLDR Marketing: https://tldr.tech/
- Amanda: https://sparktoro.com/audience-research-newsletter

## HTML Template Architecture

### Design Philosophy
- **Self-contained**: All CSS and JavaScript inline (no external dependencies)
- **Responsive**: Mobile-first with breakpoint at 768px
- **Minimalist**: Clean typography, generous whitespace, subtle animations
- **Accessible**: Semantic HTML, clear hierarchy, readable contrast

### Technical Structure

**CSS Organization**:
```
Utility Classes (Tailwind-like)
├── Layout: flex, grid, spacing (px-*, py-*, mb-*, mt-*)
├── Typography: text-{size}, font-{weight}, leading-*
├── Colors: text-{color}-{shade}, category-specific accents
└── Components: category sections, dividers, article cards
```

**JavaScript Rendering**:
- Data structure: `newsData` object with three arrays (critical, important, goodToKnow)
- Each item: `{id, title, summary, category, rank, source, timeAgo}`
- Dynamic HTML generation via template literals
- Color-coded numbering based on rank (1-8 red, 9-16 yellow, 17+ green)
- Staggered fade-in animations (0.1s delay per item)

**Responsive Breakpoints**:
```css
Desktop (default): 48rem max-width, 2rem padding, 4rem spacing
Mobile (<768px): Full-width, 1rem padding, 2rem spacing, smaller fonts
```

### Modifying the Template

**To change newsletter theme** (e.g., from AI to Growth):
1. Update `<title>` tag (line 6)
2. Change header `<h1>` text (line 162)
3. Adjust categories in `newsData` if needed (lines 177-408)
4. Update color scheme by modifying category colors (lines 51-54, 84-86)

**To adjust category thresholds**:
- Modify `getNumberColor()` function (lines 411-416)
- Update rank boundaries: currently 1-8 (critical), 9-16 (important), 17+ (good to know)

**To add/remove categories**:
- Add new array to `newsData` object
- Create new category section in render function
- Define new category color variables

## Common Tasks

### Generating a New Newsletter
```bash
# No build commands - this is a template-driven project
# Use AI tools (Claude, ChatGPT with appropriate plugins) to:
# 1. Run the prompt from `prompt revue fr.md`
# 2. Provide the end date of the week to review
# 3. Let AI scan Gmail and scrape sources
# 4. AI will populate `revue fr template.html` with data
# 5. Save output as new HTML file (e.g., `growth-weekly-2025-10-26.html`)
```

### Testing Newsletter Output
```bash
# Open generated HTML file in browser
open growth-weekly-[date].html

# Or use Python's simple HTTP server for testing
python3 -m http.server 8000
# Then visit http://localhost:8000/
```

### Version Control
```bash
# Check current status
git status

# Add new newsletter edition
git add [newsletter-file].html

# Commit with descriptive message
git commit -m "Add Growth Weekly newsletter for [date range]"

# Push to remote
git push origin master
```

## AI Agent Guidelines

When assisting with this repository:

1. **Newsletter Generation**:
   - Always follow instructions in `prompt revue fr.md` exactly
   - Use configured MCP tools (firecrawl, tavily, etc.) for web scraping
   - Ensure balanced source representation (critical requirement)
   - Output must be in French
   - Maintain 25+ items with proper categorization

2. **HTML Output**:
   - Use `revue fr template.html` as the base structure
   - Populate `newsData` object with real content (replace example data)
   - Each news item MUST have a unique, precise URL as hyperlink in title
   - Preserve responsive design and animation features
   - Update header with correct dates and attribution

3. **Quality Checks**:
   - Verify all 13+ sources are represented
   - Confirm French language output
   - Validate all hyperlinks are working
   - Check categorization logic (priority ranking)
   - Ensure mobile responsiveness is maintained

## Project Context

- **Audience**: French-speaking growth marketing professionals
- **Frequency**: Weekly (reviews the week that just ended)
- **Format**: Single HTML file, email-ready or web-viewable
- **Branding**: "Dagorsey & Claude" collaboration
- **Focus**: Product-led growth, SaaS growth strategies, marketing tactics

## Notes for Future Development

- Consider adding RSS feed generation for newsletter archives
- Could implement automated email sending via SendGrid/Mailchimp
- Template could be templated further (Jinja2, Handlebars) for easier content injection
- Newsletter archive page could showcase all past editions
- Analytics/tracking could be added for link clicks
